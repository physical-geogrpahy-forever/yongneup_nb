from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "pb4_chelsa21k"
SRC_ZIP = BASE / "model" / "PB4Studio_v6.6.3_CHELSA21K.zip"
TMP = Path("/tmp/pb4pft8")
DST = BASE / "results" / "pft8_shallow_canopy_candidate_20261006"
PKG = BASE / "model_candidates" / "PB4Studio_v6.6.3_CHELSA21K_PFT8_SHALLOW_CANOPY.zip"


def run(cmd, cwd=None):
    print("+", " ".join(map(str, cmd)), flush=True)
    subprocess.run(cmd, cwd=cwd, check=True)


def patch_source(root: Path) -> None:
    sources = list(root.rglob("biome4_original_4_2b2.f"))
    if not sources:
        raise SystemExit("biome4.f not found")
    old = """      if (wdom.eq.7) then
       if (optnpp(wdom).lt.120.0) then
        optpft=grasspft"""
    new = """      if (wdom.eq.7) then
       if (grasspft.eq.8.and.woodylai.lt.3.0) then
        optpft=grasspft
       else if (optnpp(wdom).lt.120.0) then
        optpft=grasspft"""
    n = 0
    for p in sources:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        if old in txt:
            p.write_text(txt.replace(old, new, 1), encoding="utf-8")
            print("PATCHED", p)
            n += 1
    if n != 1:
        raise SystemExit(f"expected exactly one competition patch, got {n}")

    (root / "PFT8_SHALLOW_CANOPY_COMPETITION_CANDIDATE_2026-10-06.md").write_text(
        """# PFT8 shallow-canopy competition candidate

Status: experimental candidate, not canonical.

Change:
Within the original BIOME4 competition2 branch for wdom=7
(boreal deciduous tree), select PFT8 temperate grass when
grasspft=8 and woody LAI < 3.0.

The LAI=3.0 threshold is not fitted to Park et al. (2021).
It reuses a tree-grass competition threshold already present
in the original BIOME4 PFT4 branch. No climate limits, NPP,
LAI, McKenzie/Jackson hydrology, AGB*, or Pelletier coefficients
are changed.
""",
        encoding="utf-8",
    )


def depth_sweep(root: Path) -> Path:
    out = Path("/tmp/PFT8_SHALLOW_CANOPY_DEPTH_SWEEP.csv")
    run(
        [
            sys.executable,
            "tools/mckenzie2003_depth_sensitivity.py",
            "--climate",
            "embedded_inputs/yongneup_exact20m/YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv",
            "--elevation-m",
            "1162.08",
            "--depths",
            "0.01",
            "0.02",
            "0.03",
            "0.04",
            "0.05",
            "0.06",
            "0.08",
            "0.10",
            "0.12",
            "0.15",
            "0.20",
            "0.30",
            "0.50",
            "1.50",
            "--ages",
            "5.0",
            "4.0",
            "3.0",
            "2.7",
            "2.5",
            "2.3",
            "2.2",
            "2.0",
            "--threads",
            "4",
            "--output",
            str(out),
        ],
        cwd=root,
    )
    return out


def run_full(root: Path) -> Path:
    log = Path("/tmp/PFT8_SHALLOW_CANOPY_21KA.log")
    with log.open("w", encoding="utf-8") as f:
        p = subprocess.Popen(
            [sys.executable, "tools/run_yongneup_21ka_chelsa_selfcontained.py"],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        assert p.stdout is not None
        for line in p.stdout:
            print(line, end="")
            f.write(line)
        rc = p.wait()
        if rc:
            raise SystemExit(f"full run failed: {rc}")
    return log


def find_pft_timeseries(out: Path, mode: str) -> tuple[Path, pd.DataFrame]:
    found = []
    for p in (out / f"model_{mode}").rglob("*.csv"):
        try:
            df = pd.read_csv(p, encoding="utf-8-sig")
        except Exception:
            continue
        if "reich_lai_sapwood_pft08_count" in df.columns and "ka_bp" in df.columns:
            found.append((p, df))
    if not found:
        raise SystemExit(f"no PFT timeseries for {mode}")
    return max(found, key=lambda x: len(x[1]))


def audit(root: Path, sweep_path: Path, log_path: Path) -> None:
    DST.mkdir(parents=True, exist_ok=True)
    shutil.copy2(sweep_path, DST / sweep_path.name)
    shutil.copy2(log_path, DST / log_path.name)

    sw = pd.read_csv(sweep_path)
    if "variant" in sw.columns:
        sw = sw[sw["variant"].astype(str).eq("mckenzie2003")].copy()

    focus = sw[
        sw["target_age_ka"].isin([5.0, 4.0, 3.0, 2.7, 2.5, 2.3, 2.2, 2.0])
        & sw["depth_m"].round(6).isin([0.03, 0.04, 0.05, 0.06, 0.08, 0.10])
    ].copy()
    cols = [
        "target_age_ka",
        "depth_m",
        "biome_id",
        "optpft",
        "pft04_npp",
        "pft04_lai",
        "pft07_npp",
        "pft07_lai",
        "pft08_npp",
        "pft08_lai",
    ]
    focus[cols].to_csv(DST / "DEPTH_SWEEP_FOCUS.csv", index=False)

    out = root / "outputs_CHELSA21K"
    target = {
        "95_01": ("broadleaf", "basin_count_broadleaf"),
        "95_02": ("mixed", "basin_count_mixed"),
        "95_03": ("broadleaf", "basin_count_broadleaf"),
        "95_04": ("mixed", "basin_count_mixed"),
    }
    jsum = []
    jrows = []
    for mode in ["static", "dynamic"]:
        p = out / f"model_{mode}" / "validation_per_output_time.csv"
        df = pd.read_csv(p, encoding="utf-8-sig")
        df = df[df["record_id"].astype(str).isin(target)].copy()
        df["target_class"] = df["record_id"].astype(str).map(lambda x: target[x][0])
        df["target_count"] = df.apply(
            lambda r: r[target[str(r["record_id"])][1]], axis=1
        )
        df["target_fraction"] = df["target_count"] / df["valid_basin_cell_count"]
        df["correct_1pct"] = df["target_fraction"] >= 0.01 - 1e-15
        df["herbaceous_fraction"] = (
            df["basin_count_herbaceous"] / df["valid_basin_cell_count"]
        )
        jsum.append(
            {
                "mode": mode,
                "n": len(df),
                "correct_n": int(df["correct_1pct"].sum()),
                "accuracy_pct": 100.0 * float(df["correct_1pct"].mean()),
                "max_herbaceous_fraction": float(df["herbaceous_fraction"].max()),
                "n_rows_herbaceous_ge_1pct": int(
                    (df["herbaceous_fraction"] >= 0.01).sum()
                ),
            }
        )
        keep = [
            "record_id",
            "model_ka_bp",
            "valid_basin_cell_count",
            "basin_count_conifer",
            "basin_count_broadleaf",
            "basin_count_mixed",
            "basin_count_herbaceous",
            "herbaceous_fraction",
            "target_class",
            "target_fraction",
            "correct_1pct",
        ]
        x = df[keep].copy()
        x.insert(0, "mode", mode)
        jrows.append(x)

    jsum = pd.DataFrame(jsum)
    jrows = pd.concat(jrows, ignore_index=True)
    jsum.to_csv(DST / "JANG_SUMMARY.csv", index=False)
    jrows.to_csv(DST / "JANG_ROWS.csv", index=False)

    frames = []
    for mode in ["static", "dynamic"]:
        p, df = find_pft_timeseries(out, mode)
        z = df[
            [
                "ka_bp",
                "reich_lai_sapwood_pft08_count",
                "n_cells",
                "dominant_vegetation_code",
                "vegetation_class_counts",
            ]
        ].copy()
        z.insert(0, "mode", mode)
        z["pft8_fraction"] = z["reich_lai_sapwood_pft08_count"] / z["n_cells"]
        frames.append(z)
    ts = pd.concat(frames, ignore_index=True)
    ts.to_csv(DST / "PFT8_21KA_TIMESERIES.csv", index=False)

    park = ts[
        (ts["mode"].eq("dynamic")) & (ts["ka_bp"] >= 0.5) & (ts["ka_bp"] <= 3.2)
    ].copy()
    park.to_csv(DST / "PFT8_PARK_INTERVAL.csv", index=False)

    summary = {
        "jang": jsum.to_dict(orient="records"),
        "dynamic_pft8_max_fraction_21ka": float(
            ts.loc[ts["mode"].eq("dynamic"), "pft8_fraction"].max()
        ),
        "dynamic_pft8_n_timesteps_positive_21ka": int(
            (
                ts.loc[
                    ts["mode"].eq("dynamic"), "reich_lai_sapwood_pft08_count"
                ]
                > 0
            ).sum()
        ),
        "dynamic_pft8_max_fraction_park_0p5_3p2ka": float(
            park["pft8_fraction"].max()
        ),
        "dynamic_pft8_n_timesteps_positive_park_0p5_3p2ka": int(
            (park["reich_lai_sapwood_pft08_count"] > 0).sum()
        ),
    }
    (DST / "SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# PFT8 shallow-canopy competition candidate",
        "",
        "Experimental candidate only. Canonical PB4 is unchanged.",
        "",
        "Patch: when wdom=PFT7, grasspft=PFT8, and woody LAI < 3.0, select PFT8.",
        "The LAI=3.0 threshold reuses an existing BIOME4 PFT4 tree-grass competition threshold and was not fitted to Park et al. (2021).",
        "",
        "## Jang",
        "",
        jsum.to_markdown(index=False),
        "",
        "## PFT8 occurrence",
        "",
        f"- dynamic max PFT8 fraction over 21 ka: {summary['dynamic_pft8_max_fraction_21ka']:.6f}",
        f"- dynamic positive PFT8 timesteps over 21 ka: {summary['dynamic_pft8_n_timesteps_positive_21ka']}",
        f"- dynamic max PFT8 fraction over 3.2-0.5 ka: {summary['dynamic_pft8_max_fraction_park_0p5_3p2ka']:.6f}",
        f"- dynamic positive PFT8 timesteps over 3.2-0.5 ka: {summary['dynamic_pft8_n_timesteps_positive_park_0p5_3p2ka']}",
        "",
        "## Focused depth sweep",
        "",
        focus[cols].to_markdown(index=False),
    ]
    (DST / "PFT8_SHALLOW_CANOPY_CANDIDATE_RESULT_KO.md").write_text(
        "\n".join(md), encoding="utf-8"
    )


def package(root: Path) -> str:
    PKG.parent.mkdir(parents=True, exist_ok=True)
    if PKG.exists():
        PKG.unlink()
    with zipfile.ZipFile(PKG, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(root.rglob("*")):
            if p.is_file() and "outputs_CHELSA21K" not in p.parts:
                z.write(p, p.relative_to(root.parent))
    h = hashlib.sha256(PKG.read_bytes()).hexdigest()
    (DST / "CANDIDATE_SHA256.txt").write_text(
        f"{h}  {PKG.name}\n", encoding="utf-8"
    )
    return h


def main() -> None:
    shutil.rmtree(TMP, ignore_errors=True)
    TMP.mkdir(parents=True)
    with zipfile.ZipFile(SRC_ZIP) as z:
        z.extractall(TMP)
    roots = [p for p in TMP.iterdir() if p.is_dir() and p.name.startswith("PB4Studio")]
    if len(roots) != 1:
        raise SystemExit(f"unexpected package roots: {roots}")
    root = roots[0]

    patch_source(root)
    sweep = depth_sweep(root)
    log = run_full(root)
    audit(root, sweep, log)
    h = package(root)
    print("candidate sha256", h)


if __name__ == "__main__":
    main()
