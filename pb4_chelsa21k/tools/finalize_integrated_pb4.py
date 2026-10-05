# final-builder-revision: 20261006b
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "pb4_chelsa21k"
ROOT_NAME = "PB4Studio_v6.6.3_CHELSA21K"

OLD_CANON_SHA = "eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d"
AGB_CANDIDATE_SHA = "1a4a7e07b9387c38f21019e9bc781a499b7c5864f949abf7075ea779e435a05c"

CANDIDATE_ZIP = BASE / "model_candidates" / "PB4Studio_v6.6.3_CHELSA21K_REICH_LAI_SAPWOOD_AGB.zip"
TMP = Path("/tmp/pb4_final_integrated")
TMP_RUN = Path("/tmp/pb4_final_integrated_run")
FINAL_ZIP = Path("/tmp/PB4Studio_v6.6.3_CHELSA21K_FINAL_INTEGRATED.zip")
RUN_LOG = Path("/tmp/pb4_final_integrated_21ka.log")
OUTDST = BASE / "results" / "final_integrated_20261006"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sh(args, cwd=None, env=None, stdout=None):
    print("+", " ".join(map(str, args)), flush=True)
    return subprocess.run(args, cwd=cwd, env=env, check=True, text=True, stdout=stdout)


def verify_inputs() -> Path:
    if not CANDIDATE_ZIP.is_file():
        raise SystemExit(f"missing selected AGB candidate: {CANDIDATE_ZIP}")
    got = sha256(CANDIDATE_ZIP)
    if got != AGB_CANDIDATE_SHA:
        raise SystemExit(f"candidate SHA mismatch: {got} != {AGB_CANDIDATE_SHA}")

    sh([sys.executable, str(BASE / "reconstruct_pb4.py")], cwd=REPO)
    old = BASE / "PB4Studio_v6.6.3_CHELSA21K.zip"
    got_old = sha256(old)
    if got_old != OLD_CANON_SHA:
        raise SystemExit(f"old canonical SHA mismatch: {got_old} != {OLD_CANON_SHA}")
    return old


def prepare_final_tree() -> Path:
    shutil.rmtree(TMP, ignore_errors=True)
    TMP.mkdir(parents=True)
    with zipfile.ZipFile(CANDIDATE_ZIP) as z:
        z.extractall(TMP)

    root = TMP / ROOT_NAME
    if not root.is_dir():
        raise SystemExit(f"package root missing: {root}")

    climate = (root / "pb4studio" / "climate.py").read_text(encoding="utf-8")
    required = [
        "Reich et al. (1992)",
        "Haxeltine & Prentice (1996) Eq. 34",
        "leaf_months",
        "sapwood_present",
        "leaf_dry_coef",
    ]
    for token in required:
        if token not in climate:
            raise SystemExit(f"final AGB implementation token missing: {token}")

    if "agb = np.maximum(npp_gC, 0.0) * float(cfg.agb_from_npp_scale)" in climate:
        raise SystemExit("legacy 0.010*NPP still feeds geomorphology")

    init = root / "pb4studio" / "__init__.py"
    v0 = init.read_text(encoding="utf-8")
    v1 = re.sub(
        r"__version__\s*=\s*['\"][^'\"]+['\"]",
        "__version__ = '6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB'",
        v0,
        count=1,
    )
    if v1 == v0:
        raise SystemExit("version replacement failed")
    init.write_text(v1, encoding="utf-8")

    candidate_note = root / "REICH_LAI_SAPWOOD_AGB_CANDIDATE_2026-10-05.md"
    if candidate_note.exists():
        candidate_note.unlink()

    final_note = root / "FINAL_INTEGRATED_MODEL_2026-10-06.md"
    final_note.write_text(
        """# PB4Studio CHELSA21K final integrated model

Status: FINAL production science configuration.

Core:
- BIOME4 v4.2b2 native PFT climate limits
- McKenzie soil-depth/AWC coupling
- finite-depth PFT root accessibility
- 51% reduced-class rule for Jang validation
- dynamic Pelletier geomorphic coupling

Final vegetation biomass proxy:
AGB*_dry,p = LAI_p [ S_p + 0.03630780547701014 L_m,p^0.43 ]

The leaf term follows Reich et al. (1992) SLA-life-span regression.
The sapwood relation follows Haxeltine & Prentice (1996) Eq. 34,
with BIOME4 v4.2b2 stemcarbon=0.5 and explicit fC=0.50 dry-mass conversion.

Final hillslope coupling:
kd = 0.033 EEMT + 0.05 AGB*

Pelletier et al. (2013) direct exponential EEMT-to-AGB Eq. (5)
is not used for Yongneup.

Primary validation:
Jang et al. (2011), corrected reduced mapping, n=62,
1% basin-presence criterion.

Park et al. (2021):
independent holdout validation only. It is not included in the Jang
62-item score and is not used to retune model parameters.
Sample-level Supplementary pollen data are required for that evaluation.
""",
        encoding="utf-8",
    )

    return root


def run_full(root: Path) -> Path:
    shutil.rmtree(TMP_RUN, ignore_errors=True)
    shutil.copytree(TMP, TMP_RUN)
    run_root = TMP_RUN / ROOT_NAME
    env = os.environ.copy()
    env.setdefault("OMP_NUM_THREADS", "4")

    with RUN_LOG.open("w", encoding="utf-8") as log:
        p = subprocess.Popen(
            [sys.executable, "tools/run_yongneup_21ka_chelsa_selfcontained.py"],
            cwd=run_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert p.stdout is not None
        for line in p.stdout:
            print(line, end="")
            log.write(line)
        rc = p.wait()
        if rc != 0:
            raise SystemExit(f"final integrated run failed: {rc}")

    return run_root / "outputs_CHELSA21K"


def validate_jang(out: Path):
    target = {
        "95_01": ("broadleaf", "basin_count_broadleaf"),
        "95_02": ("mixed", "basin_count_mixed"),
        "95_03": ("broadleaf", "basin_count_broadleaf"),
        "95_04": ("mixed", "basin_count_mixed"),
    }
    summary = []
    rows = []

    for mode, expected in (("static", 24), ("dynamic", 55)):
        p = out / f"model_{mode}" / "validation_per_output_time.csv"
        df = pd.read_csv(p, encoding="utf-8-sig")
        df = df[df["record_id"].astype(str).isin(target)].copy()
        df["target_class"] = df["record_id"].astype(str).map(lambda x: target[x][0])
        df["target_count"] = df.apply(lambda r: r[target[str(r["record_id"])][1]], axis=1)
        df["target_fraction"] = df["target_count"] / df["valid_basin_cell_count"]
        df["correct_1pct"] = df["target_fraction"] >= 0.01 - 1e-15

        n = len(df)
        correct = int(df["correct_1pct"].sum())
        if n != 62 or correct != expected:
            raise SystemExit(f"Jang regression failed for {mode}: {correct}/{n}")

        summary.append({
            "model": "PB4-FINAL-nativeClimate-BIOME4AGB",
            "mode": mode,
            "n": n,
            "correct_n": correct,
            "accuracy_pct": 100.0 * correct / n,
            "threshold_fraction": 0.01,
        })

        keep = [
            "record_id", "model_ka_bp", "valid_basin_cell_count",
            "basin_count_conifer", "basin_count_broadleaf",
            "basin_count_mixed", "basin_count_herbaceous",
            "target_class", "target_fraction", "correct_1pct",
        ]
        part = df[keep].copy()
        part.insert(0, "mode", mode)
        rows.append(part)

    return pd.DataFrame(summary), pd.concat(rows, ignore_index=True)


def collect_agb(out: Path) -> pd.DataFrame:
    frames = []
    for mode in ("static", "dynamic"):
        found = []
        for p in (out / f"model_{mode}").rglob("*.csv"):
            try:
                df = pd.read_csv(p, encoding="utf-8-sig")
            except Exception:
                continue
            if "reich_lai_sapwood_agb_mean_kg_m2" in df.columns:
                found.append((p, df))
        if not found:
            raise SystemExit(f"AGB diagnostics missing for {mode}")
        p, df = max(found, key=lambda x: len(x[1]))
        if len(df) != 211:
            raise SystemExit(f"expected 211 AGB rows for {mode}, got {len(df)}")
        d = df.copy()
        d.insert(0, "mode", mode)
        d.insert(1, "source_csv", str(p.relative_to(out)))
        frames.append(d)
    return pd.concat(frames, ignore_index=True)


def agb_summary(ts: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for mode, g in ts.groupby("mode"):
        ages = pd.to_numeric(g["ka_bp"], errors="coerce").abs()
        modern = g.loc[ages.idxmin()]
        rows.append({
            "mode": mode,
            "n_timesteps": len(g),
            "time_mean_agb_kg_m2": float(g["reich_lai_sapwood_agb_mean_kg_m2"].mean()),
            "min_time_mean_agb_kg_m2": float(g["reich_lai_sapwood_agb_mean_kg_m2"].min()),
            "max_time_mean_agb_kg_m2": float(g["reich_lai_sapwood_agb_mean_kg_m2"].max()),
            "absolute_max_agb_kg_m2": float(g["reich_lai_sapwood_agb_max_kg_m2"].max()),
            "modern_0ka_agb_kg_m2": float(modern["reich_lai_sapwood_agb_mean_kg_m2"]),
            "modern_0ka_agb_t_ha": 10.0 * float(modern["reich_lai_sapwood_agb_mean_kg_m2"]),
        })
    out = pd.DataFrame(rows)

    expected = {
        "static": (3.199793926229944, 3.48349),
        "dynamic": (3.1159989710181155, 3.46620),
    }
    for _, row in out.iterrows():
        mode = row["mode"]
        mean_exp, modern_exp = expected[mode]
        if abs(float(row["time_mean_agb_kg_m2"]) - mean_exp) > 5e-4:
            raise SystemExit(f"{mode} AGB time mean drifted")
        if abs(float(row["modern_0ka_agb_kg_m2"]) - modern_exp) > 5e-3:
            raise SystemExit(f"{mode} 0 ka AGB drifted")
    return out


def build_zip(root: Path) -> str:
    fixed = (2026, 10, 6, 0, 0, 0)
    with zipfile.ZipFile(FINAL_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(root.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(TMP).as_posix()
            info = zipfile.ZipInfo(rel, date_time=fixed)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o644 & 0xFFFF) << 16
            z.writestr(info, p.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return sha256(FINAL_ZIP)


def write_results(final_sha: str, jang: pd.DataFrame, jang_rows: pd.DataFrame, ts: pd.DataFrame, agb: pd.DataFrame):
    OUTDST.mkdir(parents=True, exist_ok=True)
    jang.to_csv(OUTDST / "FINAL_JANG1PCT_SUMMARY.csv", index=False, encoding="utf-8-sig")
    jang_rows.to_csv(OUTDST / "FINAL_JANG1PCT_ROWS.csv", index=False, encoding="utf-8-sig")
    ts.to_csv(OUTDST / "FINAL_AGB_21KA_TIMESERIES.csv", index=False, encoding="utf-8-sig")
    agb.to_csv(OUTDST / "FINAL_AGB_SUMMARY.csv", index=False, encoding="utf-8-sig")
    shutil.copy2(RUN_LOG, OUTDST / "FINAL_21KA_RUN.log")

    provenance = {
        "status": "final_integrated_production",
        "source_candidate_sha256": AGB_CANDIDATE_SHA,
        "previous_canonical_sha256": OLD_CANON_SHA,
        "final_sha256": final_sha,
        "model_version": "6.6.3-CHELSA21K-FINAL-nativeClimate-BIOME4AGB",
        "climate": "YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv",
        "period_ka_bp": "21.0-0.0",
        "interval_kyr": 0.1,
        "vegetation": "BIOME4 v4.2b2 native climate limits + McKenzie/Jackson soil-root coupling",
        "agb": "BIOME4-derived AGB*: Reich 1992 leaf SLA-life-span + Haxeltine & Prentice 1996 Eq.34 sapwood + BIOME4 stemcarbon=0.5",
        "pelletier_coupling": "kd=0.033*EEMT+0.05*AGB*",
        "primary_validation": "Jang et al. 2011 corrected reduced mapping, n=62, 1% basin presence",
        "park2021": "independent holdout only; excluded from tuning and Jang score; raw Supplementary pollen table required",
    }
    (OUTDST / "FINAL_PROVENANCE.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8")

    md = "# PB4 final integrated production result\n\n"
    md += f"Final SHA-256: {final_sha}\n\n"
    md += "## Scientific configuration\n\n"
    md += "- BIOME4 v4.2b2 native PFT climate limits\n"
    md += "- McKenzie AWC and finite-depth root coupling\n"
    md += "- BIOME4-derived AGB*\n"
    md += "- Pelletier geomorphic coupling with kd=0.033 EEMT + 0.05 AGB*\n"
    md += "- Pelletier direct exponential EEMT-to-AGB equation not used\n\n"
    md += "## Primary Jang validation\n\n"
    md += jang.to_markdown(index=False) + "\n\n"
    md += "## AGB\n\n"
    md += agb.to_markdown(index=False) + "\n\n"
    md += "## Park et al. (2021)\n\n"
    md += "Park is an independent holdout evaluation. It is not included in the Jang 62-item accuracy and is not used for parameter tuning. Sample-level Supplementary pollen composition will be evaluated in 100-year windows without interpolation after the raw Supplementary table is archived.\n"
    (OUTDST / "FINAL_INTEGRATED_DECISION_KO.md").write_text(md, encoding="utf-8")


def update_repo(old_canonical: Path, final_sha: str):
    model = BASE / "model"
    archive = model / "archive"
    archive.mkdir(parents=True, exist_ok=True)

    old_archive = archive / "PB4Studio_v6.6.3_CHELSA21K_NATIVECLIMATE_PRE_AGB.zip"
    shutil.copy2(old_canonical, old_archive)
    if sha256(old_archive) != OLD_CANON_SHA:
        raise SystemExit("old archive hash mismatch")

    canonical = model / "PB4Studio_v6.6.3_CHELSA21K.zip"
    alias_native = model / "PB4Studio_v6.6.3_CHELSA21K_NATIVECLIMATE_FINAL.zip"
    alias_final = model / "PB4Studio_v6.6.3_CHELSA21K_FINAL_INTEGRATED.zip"
    for dst in (canonical, alias_native, alias_final):
        shutil.copy2(FINAL_ZIP, dst)
        if sha256(dst) != final_sha:
            raise SystemExit(f"copy hash mismatch: {dst}")

    payload = BASE / "payload"
    payload.mkdir(parents=True, exist_ok=True)
    for p in payload.glob("PB4Studio_v6.6.3_CHELSA21K.zip.b64.part*"):
        p.unlink()
    encoded = base64.b64encode(FINAL_ZIP.read_bytes()).decode("ascii")
    chunk = 120000
    for k, i in enumerate(range(0, len(encoded), chunk), 1):
        (payload / f"PB4Studio_v6.6.3_CHELSA21K.zip.b64.part{k:03d}").write_text(encoded[i:i+chunk], encoding="ascii")

    rec = BASE / "reconstruct_pb4.py"
    txt = rec.read_text(encoding="utf-8")
    txt = txt.replace(OLD_CANON_SHA, final_sha)
    rec.write_text(txt, encoding="utf-8")

    sums = BASE / "SHA256SUMS.txt"
    existing = sums.read_text(encoding="utf-8").splitlines()
    keep = [x for x in existing if "PB4Studio_v6.6.3_CHELSA21K" not in x]
    lines = [
        f"{final_sha}  model/PB4Studio_v6.6.3_CHELSA21K.zip",
        f"{final_sha}  model/PB4Studio_v6.6.3_CHELSA21K_NATIVECLIMATE_FINAL.zip",
        f"{final_sha}  model/PB4Studio_v6.6.3_CHELSA21K_FINAL_INTEGRATED.zip",
        f"{OLD_CANON_SHA}  model/archive/PB4Studio_v6.6.3_CHELSA21K_NATIVECLIMATE_PRE_AGB.zip",
    ] + keep
    sums.write_text("\n".join(lines) + "\n", encoding="utf-8")

    sh([sys.executable, str(BASE / "reconstruct_pb4.py")], cwd=REPO)
    rebuilt = BASE / "PB4Studio_v6.6.3_CHELSA21K.zip"
    if sha256(rebuilt) != final_sha:
        raise SystemExit("payload reconstruction failed")
    rebuilt.unlink()


def main():
    old = verify_inputs()
    root = prepare_final_tree()
    out = run_full(root)
    jang, jang_rows = validate_jang(out)
    ts = collect_agb(out)
    agb = agb_summary(ts)
    final_sha = build_zip(root)
    write_results(final_sha, jang, jang_rows, ts, agb)
    update_repo(old, final_sha)
    print("FINAL_INTEGRATED_SHA256=" + final_sha)
    print(jang.to_string(index=False))
    print(agb.to_string(index=False))


if __name__ == "__main__":
    main()
