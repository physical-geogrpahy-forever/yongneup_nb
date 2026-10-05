from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "pb4_chelsa21k"
CANON = BASE / "model" / "PB4Studio_v6.6.3_CHELSA21K.zip"
WORK = Path("/tmp/pb4_temperate_grass_candidate")
RESULT = BASE / "results" / "temperate_grass_candidate_20261006"
CANDIDATE_ZIP = BASE / "model_candidates" / "PB4Studio_v6.6.3_CHELSA21K_JACKSON_LIFEFORM_SUB30_GRASS_CANDIDATE.zip"

DEPTHS = [0.01,0.02,0.03,0.04,0.05,0.06,0.08,0.10,0.12,0.15,0.20,0.30,0.50,1.50]
AGES = [5.0,4.0,3.0,2.7,2.5,2.3,2.2,2.0]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sh(args, cwd=None, stdout=None):
    print("+", " ".join(map(str, args)), flush=True)
    return subprocess.run(args, cwd=cwd, check=True, text=True, stdout=stdout)


def extract() -> Path:
    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir(parents=True)
    with zipfile.ZipFile(CANON) as z:
        z.extractall(WORK)
    roots = [p for p in WORK.iterdir() if p.is_dir() and p.name.startswith("PB4Studio")]
    if len(roots) != 1:
        raise RuntimeError(f"Unexpected package roots: {roots}")
    return roots[0]


def patch_backend(root: Path) -> None:
    p = root / "pb4studio" / "biome4_backend.py"
    s = p.read_text(encoding="utf-8")

    old_decl = "       real pb4_soildepth,root0,xi,rd,rtop_eff,rbot_eff\\n"
    new_decl = (
        "       real pb4_soildepth,root0,xi,rd,rtop_eff,rbot_eff\\n"
        "       real beta_lf,denom_lf\\n"
    )
    if old_decl not in s:
        raise RuntimeError("root declaration marker missing")
    s = s.replace(old_decl, new_decl, 1)

    old = (
        "       if (rd.gt.0.0) then\\n"
        "        rtop_eff=1.0-exp(-min(rd,0.30)/xi)\\n"
        "        if (rd.gt.0.30) then\\n"
        "         rbot_eff=exp(-0.30/xi)-exp(-rd/xi)\\n"
        "        else\\n"
        "         rbot_eff=0.0\\n"
        "        end if\\n"
        "       else\\n"
        "        rtop_eff=0.0\\n"
        "        rbot_eff=0.0\\n"
        "       end if\\n"
    )
    new = (
        "c      PB4 candidate: Jackson et al. (1996) life-form sub-30cm shape.\\n"
        "c      Preserve native BIOME4 r30 exactly at 0.30 m, but distinguish\\n"
        "c      root concentration within topsoil by Jackson life form.\\n"
        "c      grasses/herbs beta=.952, shrubs=.978, trees=.970.\\n"
        "       if ((pft.eq.8).or.(pft.eq.9).or.(pft.eq.12).or.\\n"
        "     >     (pft.eq.13)) then\\n"
        "        beta_lf=0.952\\n"
        "       else if ((pft.eq.10).or.(pft.eq.11)) then\\n"
        "        beta_lf=0.978\\n"
        "       else\\n"
        "        beta_lf=0.970\\n"
        "       end if\\n"
        "       denom_lf=1.0-beta_lf**30.0\\n"
        "       if (rd.gt.0.0) then\\n"
        "        if (rd.le.0.30) then\\n"
        "         rtop_eff=root0*\\n"
        "     >    (1.0-beta_lf**(100.0*rd))/denom_lf\\n"
        "         rbot_eff=0.0\\n"
        "        else\\n"
        "         rtop_eff=root0\\n"
        "         rbot_eff=exp(-0.30/xi)-exp(-rd/xi)\\n"
        "        end if\\n"
        "       else\\n"
        "        rtop_eff=0.0\\n"
        "        rbot_eff=0.0\\n"
        "       end if\\n"
    )
    if old not in s:
        raise RuntimeError("root block marker missing")
    s = s.replace(old, new, 1)
    p.write_text(s, encoding="utf-8")

    (root / "JACKSON_LIFEFORM_SUB30_ROOT_CANDIDATE_2026-10-06.md").write_text(
        """# Jackson life-form sub-30 cm root-profile candidate

Candidate only, not production.

The native BIOME4 PFT-specific cumulative root fraction at 0.30 m is preserved.
For soil depth <= 0.30 m, the within-topsoil root profile is refined using
Jackson et al. (1996) life-form beta values:

- grasses and herbs: beta = 0.952
- shrubs: beta = 0.978
- trees: beta = 0.970

For depth > 0.30 m, the existing PB4 McKenzie/Jackson tail is retained.

This is not calibrated to Park et al. (2021), Jang et al. (2011), or any
Yongneup pollen score. It tests whether the previous use of identical
sub-30-cm shape for PFT7 and PFT8 suppressed shallow-soil grass competition.
""",
        encoding="utf-8",
    )


def run_depth_sweep(root: Path) -> pd.DataFrame:
    RESULT.mkdir(parents=True, exist_ok=True)
    out = RESULT / "JACKSON_LIFEFORM_SUB30_DEPTH_SWEEP.csv"
    cmd = [
        sys.executable, "tools/mckenzie2003_depth_sensitivity.py",
        "--climate", "embedded_inputs/yongneup_exact20m/YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv",
        "--elevation-m", "1162.08",
        "--depths", *[str(x) for x in DEPTHS],
        "--ages", *[str(x) for x in AGES],
        "--threads", "4",
        "--output", str(out),
    ]
    sh(cmd, cwd=root)
    df = pd.read_csv(out)
    df = df[df["variant"].astype(str).eq("mckenzie2003")].copy()
    rows = []
    for age, g in df.groupby("target_age_ka"):
        h = g[g["optpft"].astype(int).eq(8)]
        rows.append({
            "age_ka": age,
            "n_depths": len(g),
            "n_pft8_opt_depths": len(h),
            "pft8_depth_min_m": h["depth_m"].min() if len(h) else np.nan,
            "pft8_depth_max_m": h["depth_m"].max() if len(h) else np.nan,
            "optpfts": ";".join(map(str, sorted(set(g["optpft"].astype(int))))),
        })
    summary = pd.DataFrame(rows)
    summary.to_csv(RESULT / "DEPTH_SWEEP_SUMMARY.csv", index=False)
    print(summary.to_string(index=False))
    return df


def run_full(root: Path) -> Path:
    log = RESULT / "FULL_21KA.log"
    with log.open("w", encoding="utf-8") as f:
        sh([sys.executable, "tools/run_yongneup_21ka_chelsa_selfcontained.py"], cwd=root, stdout=f)
    outroot = root / "outputs_CHELSA21K"
    if not outroot.is_dir():
        raise RuntimeError("full-run output directory missing")
    return outroot


def jang_summary(outroot: Path) -> pd.DataFrame:
    target = {
        "95_01": ("broadleaf", "basin_count_broadleaf"),
        "95_02": ("mixed", "basin_count_mixed"),
        "95_03": ("broadleaf", "basin_count_broadleaf"),
        "95_04": ("mixed", "basin_count_mixed"),
    }
    rows = []
    detail = []
    for mode in ("static", "dynamic"):
        p = outroot / f"model_{mode}" / "validation_per_output_time.csv"
        df = pd.read_csv(p, encoding="utf-8-sig")
        df = df[df["record_id"].astype(str).isin(target)].copy()
        df["target_class"] = df["record_id"].astype(str).map(lambda x: target[x][0])
        df["target_count"] = df.apply(lambda r: r[target[str(r["record_id"])][1]], axis=1)
        df["target_fraction"] = df["target_count"] / df["valid_basin_cell_count"]
        df["correct_1pct"] = df["target_fraction"] >= 0.01 - 1e-15
        rows.append({
            "mode": mode,
            "n": len(df),
            "correct_n": int(df["correct_1pct"].sum()),
            "accuracy_pct": 100.0 * float(df["correct_1pct"].mean()),
        })
        keep = [
            "record_id", "model_ka_bp", "valid_basin_cell_count",
            "basin_count_conifer", "basin_count_broadleaf",
            "basin_count_mixed", "basin_count_herbaceous",
            "target_class", "target_fraction", "correct_1pct",
        ]
        x = df[keep].copy()
        x.insert(0, "mode", mode)
        detail.append(x)
    s = pd.DataFrame(rows)
    s.to_csv(RESULT / "JANG_1PCT_SUMMARY.csv", index=False)
    pd.concat(detail, ignore_index=True).to_csv(RESULT / "JANG_1PCT_ROWS.csv", index=False)
    return s


def pft8_occurrence(outroot: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    frames = []
    for mode in ("static", "dynamic"):
        candidates = []
        for p in (outroot / f"model_{mode}").rglob("*.csv"):
            try:
                x = pd.read_csv(p, encoding="utf-8-sig")
            except Exception:
                continue
            cols = set(x.columns)
            if len(x) == 211 and ("ka_bp" in cols or "model_ka_bp" in cols):
                if any("pft08" in str(c).lower() for c in cols):
                    candidates.append((p, x))
        if not candidates:
            raise RuntimeError(f"No 211-row PFT diagnostic table for {mode}")
        p, x = max(candidates, key=lambda px: len(px[1].columns))
        agecol = "ka_bp" if "ka_bp" in x.columns else "model_ka_bp"
        p8cols = [c for c in x.columns if "pft08" in c.lower() and "count" in c.lower()]
        if not p8cols:
            raise RuntimeError(f"No PFT8 count column for {mode}")
        p8 = p8cols[0]
        y = pd.DataFrame({
            "mode": mode,
            "ka_bp": pd.to_numeric(x[agecol], errors="coerce"),
            "pft8_count": pd.to_numeric(x[p8], errors="coerce").fillna(0),
        })
        y["source_csv"] = str(p.relative_to(outroot))
        frames.append(y)
    ts = pd.concat(frames, ignore_index=True)
    ts.to_csv(RESULT / "PFT8_21KA_TIMESERIES.csv", index=False)

    rows = []
    for mode, g in ts.groupby("mode"):
        late = g[g["ka_bp"].between(0.5, 3.2)]
        rows.append({
            "mode": mode,
            "n_timesteps": len(g),
            "n_timesteps_pft8_present": int((g["pft8_count"] > 0).sum()),
            "max_pft8_cells": float(g["pft8_count"].max()),
            "late_holocene_0p5_3p2_n_pft8_steps": int((late["pft8_count"] > 0).sum()),
            "late_holocene_0p5_3p2_max_pft8_cells": float(late["pft8_count"].max()),
        })
    s = pd.DataFrame(rows)
    s.to_csv(RESULT / "PFT8_OCCURRENCE_SUMMARY.csv", index=False)
    return ts, s


def park_window_extract(outroot: Path) -> pd.DataFrame:
    # Extract model PFT composition for the exact 0.5-2.1 ka Park Zone-2 windows.
    rows = []
    for mode in ("static", "dynamic"):
        candidates = []
        for p in (outroot / f"model_{mode}").rglob("*.csv"):
            try:
                x = pd.read_csv(p, encoding="utf-8-sig")
            except Exception:
                continue
            if len(x) != 211:
                continue
            if "ka_bp" not in x.columns:
                continue
            needed = [
                "reich_lai_sapwood_pft04_count",
                "reich_lai_sapwood_pft06_count",
                "reich_lai_sapwood_pft07_count",
                "reich_lai_sapwood_pft08_count",
            ]
            if all(c in x.columns for c in needed):
                candidates.append((p, x))
        if not candidates:
            continue
        p, x = max(candidates, key=lambda px: len(px[1].columns))
        sub = x[x["ka_bp"].between(0.5, 2.1)].copy()
        for _, r in sub.iterrows():
            tree = sum(float(r.get(c, 0) or 0) for c in [
                "reich_lai_sapwood_pft04_count",
                "reich_lai_sapwood_pft06_count",
                "reich_lai_sapwood_pft07_count",
            ])
            grass = float(r.get("reich_lai_sapwood_pft08_count", 0) or 0)
            rows.append({
                "mode": mode,
                "ka_bp": float(r["ka_bp"]),
                "pft4_count": float(r.get("reich_lai_sapwood_pft04_count", 0) or 0),
                "pft6_count": float(r.get("reich_lai_sapwood_pft06_count", 0) or 0),
                "pft7_count": float(r.get("reich_lai_sapwood_pft07_count", 0) or 0),
                "pft8_count": grass,
                "tree_plus_pft8_total": tree + grass,
                "pft8_fraction_tree_plus_pft8": grass / (tree + grass) if tree + grass > 0 else np.nan,
            })
    out = pd.DataFrame(rows)
    out.to_csv(RESULT / "PARK_WINDOW_MODEL_PFT_COMPOSITION.csv", index=False)
    return out


def archive(root: Path) -> str:
    CANDIDATE_ZIP.parent.mkdir(parents=True, exist_ok=True)
    if CANDIDATE_ZIP.exists():
        CANDIDATE_ZIP.unlink()
    with zipfile.ZipFile(CANDIDATE_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(root.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(WORK).as_posix())
    h = sha256(CANDIDATE_ZIP)
    (RESULT / "CANDIDATE_SHA256.txt").write_text(f"{h}  {CANDIDATE_ZIP.name}\\n", encoding="utf-8")
    return h


def main():
    if not CANON.is_file():
        raise SystemExit(f"Missing canonical package: {CANON}")

    root = extract()
    patch_backend(root)
    depth = run_depth_sweep(root)
    n_pft8 = int((depth["optpft"].astype(int) == 8).sum())

    md = [
        "# Temperate-grass candidate result",
        "",
        "## Candidate process",
        "",
        "The native BIOME4 cumulative root fraction at 0.30 m is preserved.",
        "Only the within-top-30-cm root-profile shape is refined with Jackson et al. (1996) life-form beta values.",
        "No Park or Jang vegetation score is used to set a threshold or coefficient.",
        "",
        f"Depth-sweep PFT8 optimum cells across tested age-depth combinations: {n_pft8}",
        "",
    ]

    if n_pft8 <= 0:
        md += [
            "Candidate rejected before the full 21 ka run because PFT8 never became the optimum PFT.",
            "",
        ]
        (RESULT / "CANDIDATE_RESULT_KO.md").write_text("\\n".join(md), encoding="utf-8")
        print("\\n".join(md))
        return

    outroot = run_full(root)
    jang = jang_summary(outroot)
    _, p8sum = pft8_occurrence(outroot)
    park = park_window_extract(outroot)
    h = archive(root)

    md += [
        "## Jang 1% validation",
        "",
        jang.to_markdown(index=False),
        "",
        "## PFT8 occurrence",
        "",
        p8sum.to_markdown(index=False),
        "",
        "## Park-window model composition",
        "",
        park.to_markdown(index=False) if len(park) else "No Park-window PFT table found.",
        "",
        f"Candidate SHA-256: {h}",
        "",
        "This remains a candidate until the Jang validation and Park holdout implications are reviewed.",
    ]
    (RESULT / "CANDIDATE_RESULT_KO.md").write_text("\\n".join(md), encoding="utf-8")
    print(jang.to_string(index=False))
    print(p8sum.to_string(index=False))


if __name__ == "__main__":
    main()
