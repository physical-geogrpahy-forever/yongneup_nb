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
OUTDST = BASE / "results" / "jules_lai_ipcccf_agb_candidate_20261005"

# JULES-C2 / JULES9 PFT parameters.
# LMA: kg dry leaf m-2 leaf area (Harper et al. 2016)
# awl: kg C m-2, Cwood = awl * Lbal^(5/3) (Harper et al. 2018)
# BIOME4 dominant optLAI is used as the Lbal analogue.
PARAM_COMMON = {
    4: ("BDT", 0.0823, 0.78),
    5: ("NET", 0.2263, 0.65),
    6: ("NET", 0.2263, 0.65),
    10: ("ESH", 0.1515, 0.13),
}
PFT7_SCENARIOS = {
    "BDT": ("BDT", 0.0823, 0.78),
    "NDT": ("NDT", 0.1006, 0.80),
}
BWL = 5.0 / 3.0
WOOD_ABOVE_FRAC = 0.75  # Wolf et al. (2011) Triffid forest wood split; shrub use is sensitivity extrapolation.
WOOD_C_FRACTION_COMMON = {4: 0.48, 5: 0.51, 6: 0.51, 10: 0.47}
WOOD_C_FRACTION_PFT7 = {"BDT": 0.48, "NDT": 0.51}
# IPCC 2006 Guidelines Vol.4 Ch.4 Table 4.3:
# broad-leaved 0.48, conifers 0.51, default aboveground biomass 0.47.
SUPPORTED = {0, 4, 5, 6, 7, 10}


def sh(args, cwd=None, env=None):
    print("+", " ".join(map(str, args)), flush=True)
    return subprocess.run(args, cwd=cwd, env=env, check=True, text=True)


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


def patch_candidate(z: Path, pft7_mode: str) -> tuple[Path, Path, Path]:
    tag = pft7_mode.lower()
    tmp = Path(f"/tmp/pb4_jules_lai_ipcccf_agb_{tag}")
    runlog = Path(f"/tmp/jules_lai_ipcccf_agb_{tag}_21ka.log")
    patch = Path(f"/tmp/jules_lai_ipcccf_agb_{tag}.patch")
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    with zipfile.ZipFile(z) as zz:
        zz.extractall(tmp)
    root = tmp / ROOT_NAME
    climate = root / "pb4studio" / "climate.py"
    runner = root / "pb4studio" / "runner.py"
    init = root / "pb4studio" / "__init__.py"

    p7_name, p7_lma, p7_awl = PFT7_SCENARIOS[pft7_mode]

    c0 = climate.read_text(encoding="utf-8")
    old = (
        "    # NPP->AGB is the intentional coupling proxy; remove hidden min/max clipping.\n"
        "    agb = np.maximum(npp_gC, 0.0) * float(cfg.agb_from_npp_scale)\n"
    )
    new = f"""    # Experimental BIOME4 optLAI -> JULES/TRIFFID dry AGB bridge
    # with IPCC PFT-specific carbon fractions (2026-10-05).
    # leaf dry biomass = LMA * Lbal
    # Cwood = awl * Lbal^(5/3)
    # dry aboveground wood = 0.75*Cwood/fCwood(PFT)
    # PFT7 scenario: {p7_name}. PFT10 uses IPCC default 0.47 as fallback;
    # the 75:25 above/below woody split for shrub is an explicit sensitivity extrapolation.
    optpft = np.asarray(veg.get("optpft_node", np.full(shape, np.nan)), dtype="float64")
    lai_bal = np.asarray(veg.get("lai_node", np.full(shape, np.nan)), dtype="float64")
    pft_round = np.rint(np.where(np.isfinite(optpft), optpft, -999.0)).astype("int16")
    active = land & (~bare_bedrock) & np.isfinite(lai_bal) & (lai_bal > 0.0)
    supported = np.isin(pft_round, [0, 4, 5, 6, 7, 10])
    unsupported = active & (~supported)
    if np.any(unsupported):
        vals, counts = np.unique(pft_round[unsupported], return_counts=True)
        detail = {{int(v): int(n) for v, n in zip(vals, counts)}}
        raise RuntimeError("JULES-LAI AGB candidate encountered unsupported PFT(s): " + repr(detail))

    lma = np.zeros(shape, dtype="float64")
    awl = np.zeros(shape, dtype="float64")
    lma[pft_round == 4] = 0.0823
    awl[pft_round == 4] = 0.78
    lma[pft_round == 5] = 0.2263
    awl[pft_round == 5] = 0.65
    lma[pft_round == 6] = 0.2263
    awl[pft_round == 6] = 0.65
    lma[pft_round == 7] = {p7_lma:.4f}
    awl[pft_round == 7] = {p7_awl:.2f}
    lma[pft_round == 10] = 0.1515
    awl[pft_round == 10] = 0.13

    f_c_wood = np.ones(shape, dtype="float64")
    f_c_wood[pft_round == 4] = 0.48
    f_c_wood[pft_round == 5] = 0.51
    f_c_wood[pft_round == 6] = 0.51
    f_c_wood[pft_round == 7] = 0.48 if pft7_mode == "BDT" else 0.51
    f_c_wood[pft_round == 10] = 0.47

    L = np.maximum(lai_bal, 0.0)
    leaf_dry = lma * L
    wood_c = awl * np.power(L, 5.0 / 3.0)
    agb_jules = leaf_dry + 0.75 * wood_c / f_c_wood
    agb = np.where(pft_round == 0, 0.0, agb_jules)
    agb = np.where(bare_bedrock, 0.0, np.where(land & np.isfinite(agb), agb, np.nan))
"""
    if old not in c0:
        raise SystemExit("canonical NPP->AGB bridge not found exactly")
    c1 = c0.replace(old, new, 1)
    climate.write_text(c1, encoding="utf-8")

    r0 = runner.read_text(encoding="utf-8")
    anchor1 = '        veg_code = vegetation_array(veg, igrid.shape, igrid.land, bare_bedrock=bare_bedrock).astype("float32")\n'
    add1 = anchor1 + f"""
        # JULES-LAI candidate diagnostics.
        optpft_j = np.asarray(veg.get("optpft_node", np.full(igrid.shape, np.nan)), dtype="float64")
        lai_j = np.asarray(veg.get("lai_node", np.full(igrid.shape, np.nan)), dtype="float64")
        pft_j = np.rint(np.where(np.isfinite(optpft_j), optpft_j, -999.0)).astype("int16")
        agb_jules_lai = np.where(igrid.land & np.isfinite(agb), np.asarray(agb, dtype="float64"), np.nan)
        agb_legacy_0010 = np.maximum(np.asarray(npp, dtype="float64"), 0.0) * 0.010
        agb_legacy_0010 = np.where(
            bare_bedrock, 0.0,
            np.where(igrid.land & np.isfinite(agb_legacy_0010), agb_legacy_0010, np.nan)
        )
        # fCwood=0.40 sensitivity diagnostic only; does not feed geomorphology.
        _lma = np.zeros(igrid.shape, dtype="float64")
        _awl = np.zeros(igrid.shape, dtype="float64")
        _lma[pft_j == 4] = 0.0823; _awl[pft_j == 4] = 0.78
        _lma[pft_j == 5] = 0.2263; _awl[pft_j == 5] = 0.65
        _lma[pft_j == 6] = 0.2263; _awl[pft_j == 6] = 0.65
        _lma[pft_j == 7] = {p7_lma:.4f}; _awl[pft_j == 7] = {p7_awl:.2f}
        _lma[pft_j == 10] = 0.1515; _awl[pft_j == 10] = 0.13
        _L = np.maximum(lai_j, 0.0)
        agb_jules_fc04 = _lma * _L + 0.75 * (_awl * np.power(_L, 5.0/3.0)) / 0.40
        agb_jules_fc04 = np.where(pft_j == 0, 0.0, agb_jules_fc04)
        agb_jules_fc04 = np.where(
            bare_bedrock, 0.0,
            np.where(igrid.land & np.isfinite(agb_jules_fc04), agb_jules_fc04, np.nan)
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
    add2 = anchor2 + f"""        _m = igrid.land & np.isfinite(agb_jules_lai)
        _new = agb_jules_lai[_m]
        _old = agb_legacy_0010[_m]
        _fc04 = agb_jules_fc04[_m]
        _lm = igrid.land & np.isfinite(lai_j)
        row.update({{
            "jules_pft7_mode": "{pft7_mode}",
            "jules_lai_agb_mean_kg_m2": float(np.mean(_new)) if _new.size else float("nan"),
            "jules_lai_agb_median_kg_m2": float(np.median(_new)) if _new.size else float("nan"),
            "jules_lai_agb_p05_kg_m2": float(np.percentile(_new, 5)) if _new.size else float("nan"),
            "jules_lai_agb_p95_kg_m2": float(np.percentile(_new, 95)) if _new.size else float("nan"),
            "jules_lai_agb_max_kg_m2": float(np.max(_new)) if _new.size else float("nan"),
            "jules_lai_agb_fc04_mean_kg_m2": float(np.mean(_fc04)) if _fc04.size else float("nan"),
            "legacy_0010_agb_mean_kg_m2": float(np.mean(_old)) if _old.size else float("nan"),
            "jules_balance_lai_mean": float(np.mean(lai_j[_lm])) if np.any(_lm) else float("nan"),
            "jules_balance_lai_p95": float(np.percentile(lai_j[_lm], 95)) if np.any(_lm) else float("nan"),
            "jules_balance_lai_max": float(np.max(lai_j[_lm])) if np.any(_lm) else float("nan"),
        }})
        for _p in [0, 4, 5, 6, 7, 10]:
            _pm = igrid.land & (pft_j == _p) & np.isfinite(agb_jules_lai)
            row[f"jules_pft{{_p:02d}}_count"] = int(np.count_nonzero(_pm))
            row[f"jules_pft{{_p:02d}}_agb_sum_kg_m2_cells"] = float(np.nansum(agb_jules_lai[_pm])) if np.any(_pm) else 0.0
            row[f"jules_pft{{_p:02d}}_lai_sum"] = float(np.nansum(lai_j[_pm])) if np.any(_pm) else 0.0
"""
    # replace accidental formatting token safely
    add2 = add2.replace("{p7_mode if False else pft7_mode}", pft7_mode)
    if anchor2 not in r1:
        raise SystemExit("runner summary row anchor missing")
    r1 = r1.replace(anchor2, add2, 1)

    anchor3 = '                "vegetation_code": veg_code, "npp": npp, "eemt": eemt,\n'
    add3 = (
        '                "vegetation_code": veg_code, "npp": npp, "eemt": eemt,\n'
        '                "agb_jules_lai": agb_jules_lai.astype("float32"),\n'
        '                "agb_jules_fc04": agb_jules_fc04.astype("float32"),\n'
        '                "agb_legacy_0010": agb_legacy_0010.astype("float32"),\n'
        '                "optpft": optpft_j.astype("float32"),\n'
        '                "lai_bal": lai_j.astype("float32"),\n'
    )
    if anchor3 not in r1:
        raise SystemExit("runner snapshot anchor missing")
    r1 = r1.replace(anchor3, add3, 1)
    runner.write_text(r1, encoding="utf-8")

    v0 = init.read_text(encoding="utf-8")
    v1 = re.sub(
        r"__version__\s*=\s*['\"][^'\"]+['\"]",
        f"__version__ = '6.6.3-CHELSA21K-nativeclimate-julesLAIIPCCCFAGB-{tag}'",
        v0,
        count=1,
    )
    init.write_text(v1, encoding="utf-8")

    parts = []
    for name, before, after in [
        ("pb4studio/climate.py", c0, c1),
        ("pb4studio/runner.py", r0, r1),
        ("pb4studio/__init__.py", v0, v1),
    ]:
        parts.append("".join(difflib.unified_diff(
            before.splitlines(True), after.splitlines(True),
            fromfile=name + ".baseline", tofile=name + f".jules_{tag}"
        )))
    patch.write_text("\n".join(parts), encoding="utf-8")
    return root, runlog, patch


def build_zip(root: Path, mode: str) -> tuple[Path, str]:
    tag = mode.lower()
    out = BASE / "model_candidates" / f"PB4Studio_v6.6.3_CHELSA21K_JULES_LAI_IPCCCF_AGB_PFT7_{mode}.zip"
    out.parent.mkdir(parents=True, exist_ok=True)
    fixed = (2026, 10, 5, 0, 0, 0)
    root_parent = root.parent
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(root.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(root_parent).as_posix()
            info = zipfile.ZipInfo(rel, date_time=fixed)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o644 & 0xFFFF) << 16
            z.writestr(info, p.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return out, sha256(out)


def run_full(root: Path, runlog: Path) -> Path:
    env = os.environ.copy()
    env.setdefault("OMP_NUM_THREADS", "4")
    with runlog.open("w", encoding="utf-8") as log:
        p = subprocess.Popen(
            [sys.executable, "tools/run_yongneup_21ka_chelsa_selfcontained.py"],
            cwd=root,
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
            raise SystemExit(f"JULES-LAI-IPCCCF AGB run failed: exit {rc}")
    return root / "outputs_CHELSA21K"


def find_timeseries(out: Path, mode: str) -> pd.DataFrame:
    found = []
    for p in (out / f"model_{mode}").rglob("*.csv"):
        try:
            df = pd.read_csv(p, encoding="utf-8-sig")
        except Exception:
            continue
        if "jules_lai_agb_mean_kg_m2" in df.columns:
            found.append((p, df))
    if not found:
        raise SystemExit(f"no JULES-LAI summary found for {mode}")
    p, df = max(found, key=lambda x: len(x[1]))
    if len(df) != 211:
        raise SystemExit(f"expected 211 steps, got {len(df)} in {p}")
    df = df.copy()
    df.insert(0, "mode", mode)
    df.insert(1, "source_csv", str(p.relative_to(out)))
    return df


def jang_summary(out: Path, model_name: str) -> pd.DataFrame:
    target = {
        "95_01": "basin_count_broadleaf",
        "95_02": "basin_count_mixed",
        "95_03": "basin_count_broadleaf",
        "95_04": "basin_count_mixed",
    }
    rows = []
    for mode in ("static", "dynamic"):
        p = out / f"model_{mode}" / "validation_per_output_time.csv"
        df = pd.read_csv(p, encoding="utf-8-sig")
        df = df[df["record_id"].astype(str).isin(target)].copy()
        df["target_count"] = df.apply(lambda r: r[target[str(r["record_id"])]], axis=1)
        df["target_fraction"] = df["target_count"] / df["valid_basin_cell_count"]
        df["correct_1pct"] = df["target_fraction"] >= 0.01 - 1e-15
        rows.append({
            "model": model_name, "mode": mode, "n": len(df),
            "correct_n": int(df["correct_1pct"].sum()),
            "accuracy_pct": 100.0 * float(df["correct_1pct"].mean()),
            "threshold_fraction": 0.01,
        })
    return pd.DataFrame(rows)


def summarize_scenario(out: Path, pft7_mode: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ts = pd.concat([find_timeseries(out, "static"), find_timeseries(out, "dynamic")], ignore_index=True)
    metrics = []
    contrib = []
    for mode, g in ts.groupby("mode"):
        metrics.append({
            "scenario": pft7_mode,
            "mode": mode,
            "n_timesteps": len(g),
            "candidate_time_mean_of_cell_means_kg_m2": float(g["jules_lai_agb_mean_kg_m2"].mean()),
            "candidate_min_time_mean_kg_m2": float(g["jules_lai_agb_mean_kg_m2"].min()),
            "candidate_max_time_mean_kg_m2": float(g["jules_lai_agb_mean_kg_m2"].max()),
            "candidate_absolute_max_kg_m2": float(g["jules_lai_agb_max_kg_m2"].max()),
            "fc04_time_mean_of_cell_means_kg_m2": float(g["jules_lai_agb_fc04_mean_kg_m2"].mean()),
            "legacy_time_mean_of_cell_means_kg_m2": float(g["legacy_0010_agb_mean_kg_m2"].mean()),
            "mean_lai": float(g["jules_balance_lai_mean"].mean()),
            "max_lai": float(g["jules_balance_lai_max"].max()),
        })
        for pft in [0, 4, 5, 6, 7, 10]:
            c = f"jules_pft{pft:02d}_count"
            a = f"jules_pft{pft:02d}_agb_sum_kg_m2_cells"
            l = f"jules_pft{pft:02d}_lai_sum"
            n = pd.to_numeric(g[c], errors="coerce").fillna(0).sum()
            contrib.append({
                "scenario": pft7_mode, "mode": mode, "pft": pft,
                "total_cell_observations": int(n),
                "sum_agb_over_cell_observations_kg_m2": float(pd.to_numeric(g[a], errors="coerce").fillna(0).sum()),
                "cell_weighted_mean_agb_kg_m2": (
                    float(pd.to_numeric(g[a], errors="coerce").fillna(0).sum()) / float(n) if n else np.nan
                ),
                "cell_weighted_mean_lai": (
                    float(pd.to_numeric(g[l], errors="coerce").fillna(0).sum()) / float(n) if n else np.nan
                ),
            })
    return ts, pd.DataFrame(metrics), pd.DataFrame(contrib)


def main():
    OUTDST.mkdir(parents=True, exist_ok=True)
    z = reconstruct()
    all_ts, all_metrics, all_contrib, all_jang = [], [], [], []
    provenance = {
        "execution_status": "new_full_21ka_two_scenario_candidate_run",
        "baseline_model": "PB4-McKenzie-nativeClimate",
        "baseline_canonical_sha256": CANON_SHA,
        "climate": "YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv",
        "period_ka_bp": "21.0-0.0",
        "interval_kyr": 0.1,
        "agb_units": "kg dry biomass m^-2",
        "formula": "AGBdry = LMA*LAI + 0.75*(awl*LAI^(5/3))/fCwood(PFT)",
        "bwl": BWL,
        "wood_above_fraction": WOOD_ABOVE_FRAC,
        "wood_carbon_fraction_common": WOOD_C_FRACTION_COMMON,
        "wood_carbon_fraction_pft7": WOOD_C_FRACTION_PFT7,
        "wood_carbon_fraction_source": "IPCC 2006 Guidelines Vol.4 Ch.4 Table 4.3",
        "pft7_scenarios": list(PFT7_SCENARIOS),
        "pft10_note": "BIOME4 woody desert evergreen mapped to JULES evergreen shrub; 75:25 woody split is explicit sensitivity extrapolation",
        "references": [
            "Harper et al. 2016 GMD 9:2415-2440",
            "Harper et al. 2018 GMD 11:2857-2873",
            "Wolf et al. 2011 GBC 25 GB2009",
        ],
    }

    for pft7_mode in ("BDT", "NDT"):
        root, runlog, patch = patch_candidate(z, pft7_mode)
        zip_path, zip_sha = build_zip(root, pft7_mode)
        out = run_full(root, runlog)
        ts, metrics, contrib = summarize_scenario(out, pft7_mode)
        jang = jang_summary(out, f"PB4-McKenzie-nativeClimate-JULES-LAI-IPCCCF-AGB-PFT7-{pft7_mode}")
        all_ts.append(ts.assign(scenario=pft7_mode))
        all_metrics.append(metrics)
        all_contrib.append(contrib)
        all_jang.append(jang.assign(scenario=pft7_mode))
        shutil.copy2(patch, OUTDST / f"JULES_LAI_IPCCCF_AGB_PFT7_{pft7_mode}.patch")
        shutil.copy2(runlog, OUTDST / f"JULES_LAI_IPCCCF_AGB_PFT7_{pft7_mode}_21KA_RUN.log")
        provenance[f"{pft7_mode}_candidate_zip"] = str(zip_path.relative_to(REPO))
        provenance[f"{pft7_mode}_candidate_sha256"] = zip_sha

    ts = pd.concat(all_ts, ignore_index=True)
    metrics = pd.concat(all_metrics, ignore_index=True)
    contrib = pd.concat(all_contrib, ignore_index=True)
    jang = pd.concat(all_jang, ignore_index=True)
    ts.to_csv(OUTDST / "JULES_LAI_IPCCCF_AGB_21KA_TIMESERIES.csv", index=False, encoding="utf-8-sig")
    metrics.to_csv(OUTDST / "JULES_LAI_IPCCCF_AGB_VS_LEGACY_SUMMARY.csv", index=False, encoding="utf-8-sig")
    contrib.to_csv(OUTDST / "JULES_LAI_IPCCCF_AGB_PFT_CONTRIBUTIONS.csv", index=False, encoding="utf-8-sig")
    jang.to_csv(OUTDST / "JULES_LAI_IPCCCF_AGB_JANG1PCT_SUMMARY.csv", index=False, encoding="utf-8-sig")

    ibis_path = BASE / "results" / "pft_ibis_agb_candidate_20261005" / "PFT_IBIS_AGB_VS_LEGACY_SUMMARY.csv"
    if ibis_path.exists():
        ibis = pd.read_csv(ibis_path, encoding="utf-8-sig")
        ibis.insert(0, "scenario", "IBIS_XUE")
        ibis.to_csv(OUTDST / "REFERENCE_IBIS_XUE_SUMMARY.csv", index=False, encoding="utf-8-sig")

    (OUTDST / "JULES_LAI_IPCCCF_AGB_PROVENANCE.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = f"""# BIOME4 optLAI -> JULES/TRIFFID dry AGB candidate with IPCC carbon fractions

## 실행 상태
- 새 21-0 ka 전체 실행
- static 211 + dynamic 211, PFT7 BDT/NDT 두 시나리오
- canonical baseline은 변경하지 않음
- AGB bridge만 교체

## 식
AGBdry = LMA * LAI + 0.75 * [awl * LAI^(5/3)] / fCwood(PFT)

BIOME4 dominant PFT의 optLAI(lai_node)를 JULES balanced/full-leaf seasonal maximum LAI의 analogue로 사용한다.

## PFT mapping
- PFT4 -> BDT: LMA 0.0823, awl 0.78
- PFT5 -> NET: LMA 0.2263, awl 0.65
- PFT6 -> NET: LMA 0.2263, awl 0.65
- PFT7 -> BDT and NDT both executed
- PFT10 -> evergreen shrub: LMA 0.1515, awl 0.13
- wood carbon fractions: BDT 0.48, NET/NDT 0.51, PFT10 fallback 0.47 (IPCC 2006 Table 4.3)

PFT10의 75:25 above/below woody split은 forest-derived Wolf et al. 관계를 shrub에 확장한 sensitivity 가정이며 최종 채택 근거로 간주하지 않는다.

## AGB summary
{metrics.to_markdown(index=False)}

## Jang 2011 corrected 1% validation
{jang.to_markdown(index=False)}

## PFT contribution
{contrib.to_markdown(index=False)}

## 판정
이 실행은 JULES 기본 allometry를 BIOME4 optLAI에 전이한 sensitivity candidate이다. production 채택은 독립 LAI-AGB 검증과 PFT10 처리 검토 뒤 별도 판단한다.
"""
    (OUTDST / "JULES_LAI_IPCCCF_AGB_RESULTS_KO.md").write_text(md, encoding="utf-8")
    print("=== METRICS ===")
    print(metrics.to_string(index=False))
    print("=== JANG ===")
    print(jang.to_string(index=False))


if __name__ == "__main__":
    main()
