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

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "pb4_chelsa21k"
ROOT_NAME = "PB4Studio_v6.6.3_CHELSA21K"
CANON_SHA = "eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d"
TMP = Path("/tmp/pb4_jules_lai_ndt_agb")
TMP_RUN = Path("/tmp/pb4_jules_lai_ndt_agb_run")
RUN_LOG = Path("/tmp/jules_lai_ndt_agb_21ka.log")
PATCH = Path("/tmp/jules_lai_ndt_agb.patch")
OUTDST = BASE / "results" / "jules_lai_ndt_agb_candidate_20261005"
CANDIDATE_ZIP = BASE / "model_candidates" / "PB4Studio_v6.6.3_CHELSA21K_JULES_LAI_NDT_AGB.zip"

# JULES/TRIFFID full-leaf static allometry transferred to BIOME4 optLAI.
# AGB_dry = LMA*Lbal + stem_fraction*awl*Lbal^(5/3)/fC_wood.
# Harper et al. (2016, 2018) parameters; Wolf et al. (2011) 75:25 stem:coarse-root split.
FC_WOOD = 0.5
STEM_FRACTION = 0.75
PARAMS = {
    4: (0.0823, 0.78, "BDT"),
    5: (0.2263, 0.65, "NET"),
    6: (0.2263, 0.65, "NET"),
    7: (0.1006, 0.80, "NDT"),
    10: (0.1515, 0.13, "ESH"),
}
SUPPORTED_VEGETATED = {4, 5, 6, 7, 10}


def sh(args, cwd=None, env=None, stdout=None):
    print("+", " ".join(map(str, args)), flush=True)
    return subprocess.run(args, cwd=cwd, env=env, check=True, text=True, stdout=stdout)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def reconstruct() -> Path:
    sh([sys.executable, str(BASE / "reconstruct_pb4.py")], cwd=REPO)
    z = BASE / "PB4Studio_v6.6.3_CHELSA21K.zip"
    got = sha256(z)
    if got != CANON_SHA:
        raise SystemExit(f"canonical SHA mismatch: {got} != {CANON_SHA}")
    return z


def patch_candidate(z: Path) -> Path:
    shutil.rmtree(TMP, ignore_errors=True)
    TMP.mkdir(parents=True)
    with zipfile.ZipFile(z) as zz:
        zz.extractall(TMP)
    root = TMP / ROOT_NAME
    if not root.is_dir():
        raise SystemExit(f"missing root {root}")

    climate = root / "pb4studio" / "climate.py"
    runner = root / "pb4studio" / "runner.py"
    init = root / "pb4studio" / "__init__.py"

    c0 = climate.read_text(encoding="utf-8")
    old = (
        "    # NPP->AGB is the intentional coupling proxy; remove hidden min/max clipping.\n"
        "    agb = np.maximum(npp_gC, 0.0) * float(cfg.agb_from_npp_scale)\n"
    )
    new = """    # Experimental BIOME4 optLAI -> JULES/TRIFFID full-leaf dry AGB bridge.
    # AGB_dry = LMA*Lbal + 0.75*awl*Lbal^(5/3)/0.5 for trees and shrubs.
    # Harper et al. (2016, 2018); Wolf et al. (2011) stem:coarse-root split.
    optpft = np.asarray(veg.get("optpft_node", np.full(shape, np.nan)), dtype="float64")
    lai = np.asarray(veg.get("lai_node", np.full(shape, np.nan)), dtype="float64")
    pft_round = np.rint(np.where(np.isfinite(optpft), optpft, -999.0)).astype("int16")
    active = land & (~bare_bedrock) & (pft_round != 0)
    supported = np.isin(pft_round, [4, 5, 6, 7, 10])
    unsupported = active & (~supported)
    if np.any(unsupported):
        vals, counts = np.unique(pft_round[unsupported], return_counts=True)
        detail = {int(v): int(n) for v, n in zip(vals, counts)}
        raise RuntimeError(
            "JULES-LAI-NDT AGB candidate encountered unsupported vegetated BIOME4 PFT(s): "
            + repr(detail)
        )
    bad_lai = active & ((~np.isfinite(lai)) | (lai < 0.0))
    if np.any(bad_lai):
        vals, counts = np.unique(pft_round[bad_lai], return_counts=True)
        detail = {int(v): int(n) for v, n in zip(vals, counts)}
        raise RuntimeError("JULES-LAI-NDT AGB candidate encountered invalid optLAI: " + repr(detail))

    L = np.maximum(np.where(np.isfinite(lai), lai, 0.0), 0.0)
    agb = np.zeros(shape, dtype="float64")
    _m = pft_round == 4
    agb[_m] = 0.0823 * L[_m] + (0.75 * 0.78 / 0.5) * L[_m] ** (5.0 / 3.0)
    _m = pft_round == 5
    agb[_m] = 0.2263 * L[_m] + (0.75 * 0.65 / 0.5) * L[_m] ** (5.0 / 3.0)
    _m = pft_round == 6
    agb[_m] = 0.2263 * L[_m] + (0.75 * 0.65 / 0.5) * L[_m] ** (5.0 / 3.0)
    _m = pft_round == 7
    agb[_m] = 0.1006 * L[_m] + (0.75 * 0.80 / 0.5) * L[_m] ** (5.0 / 3.0)
    _m = pft_round == 10
    agb[_m] = 0.1515 * L[_m] + (0.75 * 0.13 / 0.5) * L[_m] ** (5.0 / 3.0)
"""
    if old not in c0:
        raise SystemExit("canonical NPP->AGB bridge not found exactly")
    c1 = c0.replace(old, new, 1)
    climate.write_text(c1, encoding="utf-8")

    r0 = runner.read_text(encoding="utf-8")
    anchor1 = '        veg_code = vegetation_array(veg, igrid.shape, igrid.land, bare_bedrock=bare_bedrock).astype("float32")\n'
    add1 = anchor1 + """
        # PFT-specific AGB diagnostics. The candidate AGB above feeds the same
        # geomorphic coupling as the legacy AGB; legacy 0.010*NPP is diagnostic only.
        optpft_agb = np.asarray(
            veg.get("optpft_node", np.full(igrid.shape, np.nan)), dtype="float64"
        )
        lai_agb = np.asarray(
            veg.get("lai_node", np.full(igrid.shape, np.nan)), dtype="float64"
        )
        optpft_round_agb = np.rint(
            np.where(np.isfinite(optpft_agb), optpft_agb, -999.0)
        ).astype("int16")
        agb_pft_ibis = np.where(
            igrid.land & np.isfinite(agb), np.asarray(agb, dtype="float64"), np.nan
        )
        agb_legacy_0010 = np.maximum(np.asarray(npp, dtype="float64"), 0.0) * 0.010
        agb_legacy_0010 = np.where(
            bare_bedrock, 0.0,
            np.where(igrid.land & np.isfinite(agb_legacy_0010), agb_legacy_0010, np.nan)
        )
"""
    if anchor1 not in r0:
        raise SystemExit("runner vegetation anchor missing")
    r1 = r0.replace(anchor1, add1, 1)

    anchor2 = """        row.update({
            "case": output_subdir,
            "geomorph_dynamic": dynamic_on,
            "biome4_variant": str(run_config.science.biome4_variant),
        })
"""
    add2 = anchor2 + """        _m = igrid.land & np.isfinite(agb_pft_ibis)
        _new = agb_pft_ibis[_m]
        _old = agb_legacy_0010[_m]
        _ratio_mask = _m & np.isfinite(agb_legacy_0010) & (agb_legacy_0010 > 0.0)
        _ratio = agb_pft_ibis[_ratio_mask] / agb_legacy_0010[_ratio_mask]
        row.update({
            "jules_lai_ndt_agb_mean_kg_m2": float(np.mean(_new)) if _new.size else float("nan"),
            "jules_lai_ndt_agb_median_kg_m2": float(np.median(_new)) if _new.size else float("nan"),
            "jules_lai_ndt_agb_p05_kg_m2": float(np.percentile(_new, 5)) if _new.size else float("nan"),
            "jules_lai_ndt_agb_p95_kg_m2": float(np.percentile(_new, 95)) if _new.size else float("nan"),
            "jules_lai_ndt_agb_max_kg_m2": float(np.max(_new)) if _new.size else float("nan"),
            "legacy_0010_agb_mean_kg_m2": float(np.mean(_old)) if _old.size else float("nan"),
            "legacy_0010_agb_median_kg_m2": float(np.median(_old)) if _old.size else float("nan"),
            "legacy_0010_agb_p95_kg_m2": float(np.percentile(_old, 95)) if _old.size else float("nan"),
            "pft_ibis_to_legacy_ratio_mean": float(np.mean(_ratio)) if _ratio.size else float("nan"),
            "pft_ibis_to_legacy_ratio_median": float(np.median(_ratio)) if _ratio.size else float("nan"),
        })
        for _p in [0, 4, 5, 6, 7, 10]:
            _pm = igrid.land & (optpft_round_agb == _p) & np.isfinite(agb_pft_ibis)
            row[f"pft_ibis_pft{_p:02d}_count"] = int(np.count_nonzero(_pm))
            row[f"pft_ibis_pft{_p:02d}_agb_sum_kg_m2_cells"] = float(
                np.nansum(agb_pft_ibis[_pm])
            ) if np.any(_pm) else 0.0
"""
    if anchor2 not in r1:
        raise SystemExit("runner summary row anchor missing")
    r1 = r1.replace(anchor2, add2, 1)

    anchor3 = '                "vegetation_code": veg_code, "npp": npp, "eemt": eemt,\n'
    add3 = (
        '                "vegetation_code": veg_code, "npp": npp, "eemt": eemt,\n'
        '                "agb_pft_ibis": agb_pft_ibis.astype("float32"),\n'
        '                "agb_legacy_0010": agb_legacy_0010.astype("float32"),\n'
        '                "optpft": optpft_agb.astype("float32"),\n'
    )
    if anchor3 not in r1:
        raise SystemExit("runner snapshot anchor missing")
    r1 = r1.replace(anchor3, add3, 1)
    runner.write_text(r1, encoding="utf-8")

    v0 = init.read_text(encoding="utf-8")
    v1 = re.sub(
        r"__version__\s*=\s*['\"][^'\"]+['\"]",
        "__version__ = '6.6.3-CHELSA21K-nativeclimate-pftIBISAGB'",
        v0,
        count=1,
    )
    if v1 == v0:
        raise SystemExit("version update failed")
    init.write_text(v1, encoding="utf-8")

    note = root / "JULES_LAI_NDT_AGB_CANDIDATE_2026-10-05.md"
    note.write_text(
        """# BIOME4 optLAI to JULES/TRIFFID dry AGB candidate (NDT PFT7 scenario)

Experimental candidate only. Canonical production package is not overwritten.

AGB_dry [kg dry m-2] = LMA*Lbal + 0.75*awl*Lbal^(5/3)/0.5

PFT4 -> BDT: LMA=0.0823, awl=0.78
PFT5 -> NET: LMA=0.2263, awl=0.65
PFT6 -> NET: LMA=0.2263, awl=0.65
PFT7 -> NDT: LMA=0.1006, awl=0.80
PFT10 -> ESH: LMA=0.1515, awl=0.13

Lbal is BIOME4 dominant-PFT optLAI (lai_node). The 0.75 factor is the
Wolf et al. (2011) stem:coarse-root split applied to the integrated woody pool.
fC_wood=0.5 is an explicit dry-mass conversion assumption.
Unsupported vegetated PFTs abort rather than being approximated.
""",
        encoding="utf-8",
    )

    parts = []
    for name, before, after in [
        ("pb4studio/climate.py", c0, c1),
        ("pb4studio/runner.py", r0, r1),
        ("pb4studio/__init__.py", v0, v1),
    ]:
        parts.append(
            "".join(
                difflib.unified_diff(
                    before.splitlines(True),
                    after.splitlines(True),
                    fromfile=name + ".baseline",
                    tofile=name + ".candidate",
                )
            )
        )
    PATCH.write_text("\n".join(parts), encoding="utf-8")
    return root


def build_candidate_zip(root: Path) -> str:
    CANDIDATE_ZIP.parent.mkdir(parents=True, exist_ok=True)
    fixed = (2026, 10, 5, 0, 0, 0)
    with zipfile.ZipFile(
        CANDIDATE_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as z:
        for p in sorted(root.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(TMP).as_posix()
            info = zipfile.ZipInfo(rel, date_time=fixed)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o644 & 0xFFFF) << 16
            z.writestr(
                info,
                p.read_bytes(),
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )
    return sha256(CANDIDATE_ZIP)


def run_full() -> Path:
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
            raise SystemExit(f"JULES-LAI-NDT AGB full run failed: exit {rc}")
    return run_root / "outputs_CHELSA21K"


def jang_summary(out: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
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
        df["target_count"] = df.apply(
            lambda r: r[target[str(r["record_id"])][1]], axis=1
        )
        df["target_fraction"] = df["target_count"] / df["valid_basin_cell_count"]
        df["correct_1pct"] = df["target_fraction"] >= 0.01 - 1e-15
        summaries.append({
            "model": "PB4-McKenzie-nativeClimate-JULES-LAI-NDT-AGB",
            "mode": mode,
            "n": len(df),
            "correct_n": int(df["correct_1pct"].sum()),
            "accuracy_pct": 100 * float(df["correct_1pct"].mean()),
            "threshold_fraction": 0.01,
        })
        for rid, g in df.groupby(df["record_id"].astype(str), sort=False):
            zones.append({
                "mode": mode,
                "record_id": rid,
                "target_class": target[rid][0],
                "n": len(g),
                "correct_n": int(g["correct_1pct"].sum()),
                "accuracy_pct": 100 * float(g["correct_1pct"].mean()),
                "target_fraction_min": float(g["target_fraction"].min()),
                "target_fraction_max": float(g["target_fraction"].max()),
            })
    return pd.DataFrame(summaries), pd.DataFrame(zones)


def collect_timeseries(out: Path) -> pd.DataFrame:
    frames = []
    for mode in ("static", "dynamic"):
        found = []
        for p in (out / f"model_{mode}").rglob("*.csv"):
            try:
                df = pd.read_csv(p, encoding="utf-8-sig")
            except Exception:
                continue
            if "jules_lai_ndt_agb_mean_kg_m2" in df.columns:
                found.append((p, df))
        if not found:
            raise SystemExit(f"no JULES-LAI-NDT AGB diagnostic timeseries found for {mode}")
        p, df = max(found, key=lambda x: len(x[1]))
        if len(df) != 211:
            raise SystemExit(f"expected 211 timesteps for {mode}, got {len(df)} in {p}")
        df = df.copy()
        df.insert(0, "mode", mode)
        df.insert(1, "source_csv", str(p.relative_to(out)))
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def compact_metrics(ts: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for mode, g in ts.groupby("mode"):
        rows.append({
            "mode": mode,
            "n_timesteps": len(g),
            "candidate_time_mean_of_cell_means_kg_m2": float(g["jules_lai_ndt_agb_mean_kg_m2"].mean()),
            "candidate_min_time_mean_kg_m2": float(g["jules_lai_ndt_agb_mean_kg_m2"].min()),
            "candidate_max_time_mean_kg_m2": float(g["jules_lai_ndt_agb_mean_kg_m2"].max()),
            "candidate_absolute_max_kg_m2": float(g["jules_lai_ndt_agb_max_kg_m2"].max()),
            "legacy_time_mean_of_cell_means_kg_m2": float(g["legacy_0010_agb_mean_kg_m2"].mean()),
            "legacy_min_time_mean_kg_m2": float(g["legacy_0010_agb_mean_kg_m2"].min()),
            "legacy_max_time_mean_kg_m2": float(g["legacy_0010_agb_mean_kg_m2"].max()),
            "mean_candidate_to_legacy_ratio": float(g["pft_ibis_to_legacy_ratio_mean"].mean()),
            "median_candidate_to_legacy_ratio_across_steps": float(g["pft_ibis_to_legacy_ratio_median"].median()),
        })
    return pd.DataFrame(rows)


def pft_contribution(ts: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for mode, g in ts.groupby("mode"):
        for pft in [0, 4, 5, 6, 7, 10]:
            c = f"pft_ibis_pft{pft:02d}_count"
            a = f"pft_ibis_pft{pft:02d}_agb_sum_kg_m2_cells"
            rows.append({
                "mode": mode,
                "pft": pft,
                "total_cell_observations": int(pd.to_numeric(g[c], errors="coerce").fillna(0).sum()),
                "sum_agb_over_cell_observations_kg_m2": float(pd.to_numeric(g[a], errors="coerce").fillna(0).sum()),
                "timesteps_present": int((pd.to_numeric(g[c], errors="coerce").fillna(0) > 0).sum()),
            })
    return pd.DataFrame(rows)


def save_results(out: Path, cand_sha: str):
    OUTDST.mkdir(parents=True, exist_ok=True)

    summary, zones = jang_summary(out)
    summary.to_csv(OUTDST / "JULES_LAI_NDT_AGB_JANG1PCT_SUMMARY.csv", index=False, encoding="utf-8-sig")
    zones.to_csv(OUTDST / "JULES_LAI_NDT_AGB_JANG1PCT_BY_ZONE.csv", index=False, encoding="utf-8-sig")

    ts = collect_timeseries(out)
    ts.to_csv(OUTDST / "JULES_LAI_NDT_AGB_21KA_TIMESERIES.csv", index=False, encoding="utf-8-sig")

    metrics = compact_metrics(ts)
    metrics.to_csv(OUTDST / "JULES_LAI_NDT_AGB_VS_LEGACY_SUMMARY.csv", index=False, encoding="utf-8-sig")

    contributions = pft_contribution(ts)
    contributions.to_csv(OUTDST / "JULES_LAI_NDT_AGB_PFT_CONTRIBUTIONS.csv", index=False, encoding="utf-8-sig")

    provenance = {
        "execution_status": "new_full_21ka_candidate_run",
        "baseline_model": "PB4-McKenzie-nativeClimate",
        "baseline_canonical_sha256": CANON_SHA,
        "candidate_model": "PB4-McKenzie-nativeClimate-JULES-LAI-NDT-AGB",
        "candidate_zip": str(CANDIDATE_ZIP.relative_to(REPO)),
        "candidate_sha256": cand_sha,
        "climate": "YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv",
        "period_ka_bp": "21.0-0.0",
        "interval_kyr": 0.1,
        "only_scientific_change_for_geomorphology": "AGB bridge: legacy 0.010*NPP -> BIOME4 optLAI + JULES/TRIFFID full-leaf allometry (NDT PFT7 scenario)",
        "agb_units": "kg dry biomass m^-2",
        "lai_input": "BIOME4 dominant-PFT optLAI via lai_node",
        "fC_wood": FC_WOOD,
        "stem_fraction_of_integrated_wood_pool": STEM_FRACTION,
        "jules_parameters": {str(k): {"lma": v[0], "awl": v[1], "jules_pft": v[2]} for k, v in PARAMS.items()},
        "pft10_correspondence": "BIOME4 woody desert evergreen -> JULES evergreen shrub (ESH) structural analogue",
        "unsupported_pft_policy": "abort on any positive-NPP vegetated unsupported dominant PFT",
        "legacy_0010": "diagnostic only; does not feed candidate geomorphology",
        "validation": "Jang 2011 corrected reduced mapping, n=62, 1% basin presence",
    }
    (OUTDST / "JULES_LAI_NDT_AGB_PROVENANCE.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    shutil.copy2(PATCH, OUTDST / "JULES_LAI_NDT_AGB.patch")
    shutil.copy2(RUN_LOG, OUTDST / "JULES_LAI_NDT_AGB_21KA_RUN.log")

    md = """# BIOME4 optLAI to JULES/TRIFFID dry AGB candidate (NDT PFT7): full 21-0 ka test

## Status

This is a new full candidate execution. The canonical PB4-McKenzie-nativeClimate package is not overwritten.

- baseline SHA-256: {base_sha}
- candidate SHA-256: {cand_sha}
- candidate ZIP: {zip_path}
- climate: YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv
- period: 21.0-0.0 ka BP
- interval: 0.1 kyr
- static and dynamic: 211 steps each

## Candidate bridge

AGB_dry [kg dry m-2] = LMA(PFT)*optLAI + 0.75*awl(PFT)*optLAI^(5/3)/0.5

PFT4=BDT; PFT5/6=NET; PFT7=NDT; PFT10=ESH. Exact parameters are recorded in provenance.

Only this AGB bridge changes the geomorphic coupling. EEMT and all other production settings are unchanged. Legacy 0.010*NPP is retained only as a diagnostic comparator.

## Jang corrected 1% validation

{jang}

## AGB comparison with legacy 0.010*NPP

{metrics}

## PFT contributions

{contrib}

## Promotion status

Candidate only. Promotion requires checking physical AGB magnitude, dynamic geomorphic response, and validation relative to the canonical baseline.
""".format(
        base_sha=CANON_SHA,
        cand_sha=cand_sha,
        zip_path=CANDIDATE_ZIP.relative_to(REPO),
        jang=summary.to_markdown(index=False),
        metrics=metrics.to_markdown(index=False),
        contrib=contributions.to_markdown(index=False),
    )
    (OUTDST / "JULES_LAI_NDT_AGB_RESULTS_KO.md").write_text(md, encoding="utf-8")


def main():
    z = reconstruct()
    root = patch_candidate(z)
    cand_sha = build_candidate_zip(root)
    out = run_full()
    save_results(out, cand_sha)
    print("CANDIDATE_SHA256=" + cand_sha)
    print("=== JANG ===")
    print(pd.read_csv(OUTDST / "JULES_LAI_NDT_AGB_JANG1PCT_SUMMARY.csv").to_string(index=False))
    print("=== AGB VS LEGACY ===")
    print(pd.read_csv(OUTDST / "JULES_LAI_NDT_AGB_VS_LEGACY_SUMMARY.csv").to_string(index=False))
    print("=== PFT CONTRIBUTIONS ===")
    print(pd.read_csv(OUTDST / "JULES_LAI_NDT_AGB_PFT_CONTRIBUTIONS.csv").to_string(index=False))


if __name__ == "__main__":
    main()
