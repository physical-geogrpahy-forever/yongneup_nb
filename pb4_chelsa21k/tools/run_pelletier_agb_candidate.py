from __future__ import annotations

import difflib
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
OUT = BASE / "results" / "pelletier_agb_candidate_20261005"
TMP = Path("/tmp/pb4_pelletier_agb_full")
RUN_LOG = OUT / "PELLETIER_AGB_21KA_RUN.log"
EXPECTED_SHA = "eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def reconstruct() -> Path:
    subprocess.run([sys.executable, str(BASE / "reconstruct_pb4.py")], cwd=REPO, check=True)
    z = BASE / "PB4Studio_v6.6.3_CHELSA21K.zip"
    got = sha256(z)
    if got != EXPECTED_SHA:
        raise SystemExit(f"canonical SHA mismatch: {got} != {EXPECTED_SHA}")
    return z


def patch_candidate(z: Path) -> Path:
    shutil.rmtree(TMP, ignore_errors=True)
    TMP.mkdir(parents=True)
    with zipfile.ZipFile(z) as zz:
        zz.extractall(TMP)
    roots = [p for p in TMP.iterdir() if p.is_dir()]
    if len(roots) != 1:
        raise SystemExit(f"unexpected extracted roots: {roots}")
    root = roots[0]

    climate = root / "pb4studio" / "climate.py"
    before_climate = climate.read_text(encoding="utf-8")
    old = '''    # NPP->AGB is the intentional coupling proxy; remove hidden min/max clipping.
    agb = np.maximum(npp_gC, 0.0) * float(cfg.agb_from_npp_scale)
    agb = np.where(bare_bedrock, 0.0, agb)
    agb = np.where(land & np.isfinite(agb), agb, np.nan)
'''
    new = '''    # Pelletier et al. (2013), Eq. (5), restored without a PB4 NPP->AGB bridge:
    # AGB = e * exp(f * EEMT), with e=1 kg m^-2 and
    # f=0.1 yr m^2 MJ^-1. EEMT is in MJ m^-2 yr^-1 here.
    # The coefficients are the original Arizona Sky Islands empirical values;
    # this run is therefore an explicit transferability candidate, not a Yongneup fit.
    agb = 1.0 * np.exp(0.1 * eemt)
    agb = np.where(bare_bedrock, 0.0, agb)
    agb = np.where(land & np.isfinite(agb), agb, np.nan)
'''
    if old not in before_climate:
        raise SystemExit("current NPP->AGB bridge block not found exactly")
    after_climate = before_climate.replace(old, new, 1)
    climate.write_text(after_climate, encoding="utf-8")

    runner = root / "pb4studio" / "runner.py"
    before_runner = runner.read_text(encoding="utf-8")
    anchor = '''        row.update({
            "case": output_subdir,
            "geomorph_dynamic": dynamic_on,
            "biome4_variant": str(run_config.science.biome4_variant),
        })
        summary_rows.append(row)
'''
    replacement = '''        row.update({
            "case": output_subdir,
            "geomorph_dynamic": dynamic_on,
            "biome4_variant": str(run_config.science.biome4_variant),
        })

        # AGB candidate diagnostics. Wang et al. (2011) is used only as an
        # independent BIOME4 steady-state vegetation-carbon comparison, not as
        # a geomorphic forcing. Forest mega-biome mapping follows the BIOME4
        # biome names listed by Wang et al.: 4 warm-temperate, 5-8 temperate,
        # 9-11 boreal. tau_veg = 15, 10, 26 yr respectively (their Table 1).
        agb64 = np.asarray(agb, dtype="float64")
        valid_agb = igrid.land & np.isfinite(agb64)
        if np.any(valid_agb):
            vals = agb64[valid_agb]
            row.update({
                "pelletier_agb_mean_kg_m2": float(np.mean(vals)),
                "pelletier_agb_median_kg_m2": float(np.median(vals)),
                "pelletier_agb_p05_kg_m2": float(np.quantile(vals, 0.05)),
                "pelletier_agb_p95_kg_m2": float(np.quantile(vals, 0.95)),
                "pelletier_agb_min_kg_m2": float(np.min(vals)),
                "pelletier_agb_max_kg_m2": float(np.max(vals)),
            })

        full = np.asarray(
            veg.get("biome4_full_id_node", np.full(igrid.shape, np.nan)),
            dtype="float64",
        )
        tau = np.full(igrid.shape, np.nan, dtype="float64")
        tau[full == 4] = 15.0
        tau[np.isin(full, [5, 6, 7, 8])] = 10.0
        tau[np.isin(full, [9, 10, 11])] = 26.0
        wang_cveg = (np.maximum(np.asarray(npp, dtype="float64"), 0.0) / 1000.0) * tau
        wang_mask = igrid.land & np.isfinite(wang_cveg)
        row["wang_forest_cell_count"] = int(np.count_nonzero(wang_mask))
        row["wang_forest_cell_fraction"] = (
            float(np.count_nonzero(wang_mask) / np.count_nonzero(igrid.land))
            if np.count_nonzero(igrid.land) else np.nan
        )
        if np.any(wang_mask):
            wv = wang_cveg[wang_mask]
            av = agb64[wang_mask]
            row.update({
                "wang_cveg_forest_mean_kgC_m2": float(np.mean(wv)),
                "wang_cveg_forest_median_kgC_m2": float(np.median(wv)),
                "wang_cveg_forest_p05_kgC_m2": float(np.quantile(wv, 0.05)),
                "wang_cveg_forest_p95_kgC_m2": float(np.quantile(wv, 0.95)),
                "wang_cveg_forest_min_kgC_m2": float(np.min(wv)),
                "wang_cveg_forest_max_kgC_m2": float(np.max(wv)),
                "pelletier_agb_forest_mean_kg_m2": float(np.mean(av)),
            })
            if np.count_nonzero(wang_mask) >= 2 and np.std(wv) > 0 and np.std(av) > 0:
                row["pelletier_agb_vs_wang_cveg_forest_pearson_r"] = float(
                    np.corrcoef(av, wv)[0, 1]
                )
            else:
                row["pelletier_agb_vs_wang_cveg_forest_pearson_r"] = np.nan

        summary_rows.append(row)
'''
    if anchor not in before_runner:
        raise SystemExit("runner summary anchor not found")
    after_runner = before_runner.replace(anchor, replacement, 1)

    snap_anchor = '''                "vegetation_code": veg_code, "npp": npp, "eemt": eemt,
                "bare_bedrock": bare_bedrock.astype("float32"),
'''
    snap_repl = '''                "vegetation_code": veg_code, "npp": npp, "eemt": eemt,
                "agb_pelletier": np.asarray(agb, dtype="float32"),
                "bare_bedrock": bare_bedrock.astype("float32"),
'''
    if snap_anchor not in after_runner:
        raise SystemExit("snapshot anchor not found")
    after_runner = after_runner.replace(snap_anchor, snap_repl, 1)
    runner.write_text(after_runner, encoding="utf-8")

    init = root / "pb4studio" / "__init__.py"
    iv = init.read_text(encoding="utf-8")
    iv2 = re.sub(
        r"__version__\s*=\s*['\"][^'\"]+['\"]",
        "__version__ = '6.6.3-CHELSA21K-nativeClimate-PelletierEq5AGB-candidate'",
        iv,
        count=1,
    )
    init.write_text(iv2, encoding="utf-8")

    OUT.mkdir(parents=True, exist_ok=True)
    diff = "".join(difflib.unified_diff(
        before_climate.splitlines(True), after_climate.splitlines(True),
        fromfile="climate.py.baseline", tofile="climate.py.PelletierEq5AGB"
    ))
    diff += "".join(difflib.unified_diff(
        before_runner.splitlines(True), after_runner.splitlines(True),
        fromfile="runner.py.baseline", tofile="runner.py.PelletierEq5AGB_diagnostics"
    ))
    (OUT / "PELLETIER_AGB_CANDIDATE.patch").write_text(diff, encoding="utf-8")
    return root


def run_full(root: Path) -> Path:
    env = os.environ.copy()
    env.setdefault("OMP_NUM_THREADS", "4")
    OUT.mkdir(parents=True, exist_ok=True)
    with RUN_LOG.open("w", encoding="utf-8") as log:
        p = subprocess.Popen(
            [sys.executable, "tools/run_yongneup_21ka_chelsa_selfcontained.py"],
            cwd=root, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
        )
        assert p.stdout is not None
        for line in p.stdout:
            print(line, end="")
            log.write(line)
        rc = p.wait()
    if rc != 0:
        raise SystemExit(f"candidate full run failed with exit code {rc}")
    out = root / "outputs_CHELSA21K"
    if not out.is_dir():
        raise SystemExit("outputs_CHELSA21K missing")
    return out


def summarize(out: Path):
    target = {
        "95_01": ("broadleaf", "basin_count_broadleaf"),
        "95_02": ("mixed", "basin_count_mixed"),
        "95_03": ("broadleaf", "basin_count_broadleaf"),
        "95_04": ("mixed", "basin_count_mixed"),
    }
    summaries = []
    zones = []
    for mode in ("static", "dynamic"):
        p = out / f"model_{mode}" / "validation_per_output_time.csv"
        df = pd.read_csv(p, encoding="utf-8-sig")
        df = df[df["record_id"].astype(str).isin(target)].copy()
        df["target_class"] = df["record_id"].astype(str).map(lambda x: target[x][0])
        df["target_count"] = df.apply(lambda r: r[target[str(r["record_id"])][1]], axis=1)
        df["target_fraction"] = df["target_count"] / df["valid_basin_cell_count"]
        df["correct_1pct"] = df["target_fraction"] >= 0.01 - 1e-15
        n = len(df)
        c = int(df["correct_1pct"].sum())
        summaries.append({
            "model": "PB4-McKenzie-nativeClimate-PelletierEq5AGB-candidate",
            "mode": mode, "n": n, "correct_n": c,
            "accuracy_pct": 100.0 * c / n if n else float("nan"),
            "threshold_fraction": 0.01,
        })
        for rid, g in df.groupby(df["record_id"].astype(str), sort=False):
            zones.append({
                "mode": mode, "record_id": rid,
                "target_class": target[rid][0],
                "n": len(g), "correct_n": int(g["correct_1pct"].sum()),
                "accuracy_pct": 100.0 * float(g["correct_1pct"].mean()),
                "target_fraction_min": float(g["target_fraction"].min()),
                "target_fraction_max": float(g["target_fraction"].max()),
            })
        df.to_csv(OUT / f"PELLETIER_AGB_{mode}_JANG1PCT_ROWS.csv", index=False, encoding="utf-8-sig")

    sdf = pd.DataFrame(summaries)
    zdf = pd.DataFrame(zones)
    sdf.to_csv(OUT / "PELLETIER_AGB_JANG1PCT_SUMMARY.csv", index=False, encoding="utf-8-sig")
    zdf.to_csv(OUT / "PELLETIER_AGB_JANG1PCT_BY_ZONE.csv", index=False, encoding="utf-8-sig")

    diag_frames = []
    for p in out.rglob("*.csv"):
        try:
            df = pd.read_csv(p, encoding="utf-8-sig")
        except Exception:
            continue
        if "pelletier_agb_mean_kg_m2" in df.columns:
            df = df.copy()
            df.insert(0, "source_csv", p.relative_to(out).as_posix())
            diag_frames.append(df)
    if diag_frames:
        diag = pd.concat(diag_frames, ignore_index=True)
        diag.to_csv(OUT / "PELLETIER_AGB_WANG_TIMESERIES_DIAGNOSTIC.csv", index=False, encoding="utf-8-sig")
        cols = [c for c in [
            "source_csv","ka_bp","model_ka_bp","case","geomorph_dynamic",
            "mean_npp","mean_eemt",
            "pelletier_agb_mean_kg_m2","pelletier_agb_median_kg_m2",
            "pelletier_agb_p05_kg_m2","pelletier_agb_p95_kg_m2",
            "pelletier_agb_min_kg_m2","pelletier_agb_max_kg_m2",
            "wang_forest_cell_count","wang_forest_cell_fraction",
            "wang_cveg_forest_mean_kgC_m2","wang_cveg_forest_median_kgC_m2",
            "wang_cveg_forest_p05_kgC_m2","wang_cveg_forest_p95_kgC_m2",
            "pelletier_agb_forest_mean_kg_m2",
            "pelletier_agb_vs_wang_cveg_forest_pearson_r",
            "mean_soil_depth_m","min_soil_depth_m","max_soil_depth_m",
        ] if c in diag.columns]
        diag[cols].to_csv(OUT / "PELLETIER_AGB_WANG_TIMESERIES_COMPACT.csv", index=False, encoding="utf-8-sig")

    prov = {
        "execution_status": "new_full_21ka_candidate_run",
        "baseline_sha256": EXPECTED_SHA,
        "candidate": "PB4-McKenzie-nativeClimate-PelletierEq5AGB",
        "climate": "CHELSA-TraCE21k/EnviCloud 21.0-0.0 ka BP, 0.1 kyr",
        "only_process_change": "replace PB4 AGB=0.010*NPP bridge with Pelletier et al. 2013 Eq.5 AGB=1*exp(0.1*EEMT)",
        "pelletier_coefficients": {"e_kg_m2": 1.0, "f_yr_m2_MJ": 0.1},
        "retained": [
            "BIOME4 v4.2b2 native climate limits",
            "McKenzie AWC coupling",
            "Jackson finite-depth root accessibility",
            "51% reduced-class majority rule",
            "existing EEMT calculation",
            "Pelletier geomorphic c,d,K0 and other process parameters",
        ],
        "wang_diagnostic": {
            "role": "diagnostic only, no geomorphic forcing",
            "formula": "Cveg=NPP*tau_veg",
            "units": "kg C m^-2",
            "forest_mapping": {
                "BIOME4_4": {"mega_biome": "warm-temperate forest", "tau_yr": 15},
                "BIOME4_5_8": {"mega_biome": "temperate forest", "tau_yr": 10},
                "BIOME4_9_11": {"mega_biome": "boreal forest", "tau_yr": 26},
            },
            "note": "No dry-mass conversion is applied; Pelletier AGB and Wang Cveg are compared as distinct quantities.",
        },
        "validation": "Jang et al. 2011 corrected mapping, n=62, basin presence >=1%",
    }
    (OUT / "PELLETIER_AGB_PROVENANCE.json").write_text(
        json.dumps(prov, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    note = """# Pelletier Eq. (5) AGB candidate

This is a candidate experiment, not a production replacement.

The canonical PB4-McKenzie-nativeClimate package is reconstructed and SHA-verified.
The only geomorphic-process bridge changed is:

baseline: AGB = 0.010 * max(BIOME4 NPP_C, 0)

candidate: AGB = 1 kg m^-2 * exp(0.1 yr m^2 MJ^-1 * EEMT)

The candidate therefore restores Pelletier et al. (2013) Eq. (5) and its original
e and f coefficients without fitting them to Yongneup. All other production
settings are retained.

Wang et al. (2011) Cveg = NPP * tau_veg is computed as a diagnostic only for
warm-temperate, temperate, and boreal forest BIOME4 classes. It is not substituted
for AGB and does not affect geomorphology. Because Wang Cveg is carbon mass while
Pelletier AGB is live dry mass, no direct equality or ratio is interpreted without
a separate carbon-fraction assumption.
"""
    (OUT / "PELLETIER_AGB_CANDIDATE_README.md").write_text(note, encoding="utf-8")

    print(sdf.to_string(index=False))
    print(zdf.to_string(index=False))


def main():
    z = reconstruct()
    root = patch_candidate(z)
    out = run_full(root)
    summarize(out)


if __name__ == "__main__":
    main()
