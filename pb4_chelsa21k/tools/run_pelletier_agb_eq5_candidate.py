from __future__ import annotations

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
TMP = Path("/tmp/pb4_pelletier_agb_eq5")
TMP_RUN = Path("/tmp/pb4_pelletier_agb_eq5_run")
RUN_LOG = Path("/tmp/pelletier_agb_eq5_21ka.log")
PATCH = Path("/tmp/pelletier_agb_eq5.patch")
OUTDST = BASE / "results" / "pelletier_agb_candidate_20261005"
CANDIDATE_ZIP = BASE / "model_candidates" / "PB4Studio_v6.6.3_CHELSA21K_PELLETIER_AGB_EQ5.zip"


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
    config = root / "pb4studio" / "config.py"
    runner = root / "pb4studio" / "runner.py"
    init = root / "pb4studio" / "__init__.py"

    c0 = climate.read_text(encoding="utf-8")
    old = '    # NPP->AGB is the intentional coupling proxy; remove hidden min/max clipping.\n    agb = np.maximum(npp_gC, 0.0) * float(cfg.agb_from_npp_scale)\n'
    new = '''    # Pelletier et al. (2013) Eq. (5), used without Yongneup refitting or clipping:\n    # AGB = e * exp(f * EEMT), e=1 kg m^-2, f=0.1 yr m^2 MJ^-1.\n    # This candidate deliberately restores the published Pelletier AGB bridge.\n    agb = float(getattr(cfg, "pelletier_agb_e_kg_m2", 1.0)) * np.exp(\n        float(getattr(cfg, "pelletier_agb_f_yr_m2_per_mj", 0.1)) * eemt\n    )\n'''
    if old not in c0:
        raise SystemExit("current NPP->AGB bridge not found exactly")
    c1 = c0.replace(old, new, 1)
    climate.write_text(c1, encoding="utf-8")

    g0 = config.read_text(encoding="utf-8")
    anchor = '    agb_from_npp_scale: float = 0.010\n'
    add = '''    agb_from_npp_scale: float = 0.010  # legacy baseline only; unused by Pelletier-Eq5 candidate\n    pelletier_agb_e_kg_m2: float = 1.0\n    pelletier_agb_f_yr_m2_per_mj: float = 0.1\n'''
    if anchor not in g0:
        raise SystemExit("config AGB anchor not found")
    g1 = g0.replace(anchor, add, 1)
    config.write_text(g1, encoding="utf-8")

    r0 = runner.read_text(encoding="utf-8")
    anchor1 = '        veg_code = vegetation_array(veg, igrid.shape, igrid.land, bare_bedrock=bare_bedrock).astype("float32")\n'
    add1 = anchor1 + '''\n        # Independent Wang et al. (2011) BIOME4 steady-state vegetation-carbon diagnostic.\n        # This diagnostic does NOT feed geomorphology. It is retained only for comparison\n        # with Pelletier Eq. (5) AGB. NPP is converted gC -> kgC before multiplying tau_veg.\n        full_biome = np.asarray(veg.get("biome4_full_id_node", np.full(igrid.shape, np.nan)), dtype="float64")\n        wang_tau_yr = np.full(igrid.shape, np.nan, dtype="float64")\n        wang_tau_yr[np.isin(full_biome, [1, 2, 3])] = 24.0       # tropical forest\n        wang_tau_yr[full_biome == 6] = 15.0                      # warm-temperate forest\n        wang_tau_yr[np.isin(full_biome, [4, 5, 7, 8, 9])] = 10.0 # temperate forest\n        wang_tau_yr[np.isin(full_biome, [10, 11])] = 26.0        # boreal forest\n        wang_tau_yr[np.isin(full_biome, [12, 15, 16, 17])] = 4.0 # savanna/dry woodland\n        wang_tau_yr[np.isin(full_biome, [13, 14, 19, 20])] = 4.0 # grassland/dry shrubland\n        wang_tau_yr[full_biome == 21] = 9.0                      # desert\n        wang_tau_yr[full_biome == 22] = 20.0                     # dry tundra\n        wang_tau_yr[np.isin(full_biome, [23, 24, 25, 26])] = 11.0 # tundra\n        wang_cveg = (np.maximum(np.asarray(npp, dtype="float64"), 0.0) / 1000.0) * wang_tau_yr\n        wang_cveg = np.where(bare_bedrock, np.nan, wang_cveg)\n        wang_cveg = np.where(igrid.land & np.isfinite(wang_cveg), wang_cveg, np.nan)\n        agb_diag = np.where(igrid.land & np.isfinite(agb), np.asarray(agb, dtype="float64"), np.nan)\n'''
    if anchor1 not in r0:
        raise SystemExit("runner veg_code anchor missing")
    r1 = r0.replace(anchor1, add1, 1)

    anchor2 = '''        row.update({\n            "case": output_subdir,\n            "geomorph_dynamic": dynamic_on,\n            "biome4_variant": str(run_config.science.biome4_variant),\n        })\n'''
    add2 = anchor2 + '''        agb_vals = agb_diag[igrid.land & np.isfinite(agb_diag)]\n        wang_vals = wang_cveg[igrid.land & np.isfinite(wang_cveg)]\n        both = igrid.land & np.isfinite(agb_diag) & np.isfinite(wang_cveg)\n        if np.count_nonzero(both) >= 2:\n            corr_aw = float(np.corrcoef(agb_diag[both], wang_cveg[both])[0, 1])\n        else:\n            corr_aw = float("nan")\n        row.update({\n            "pelletier_agb_eq5_mean_kg_m2": float(np.mean(agb_vals)) if agb_vals.size else float("nan"),\n            "pelletier_agb_eq5_median_kg_m2": float(np.median(agb_vals)) if agb_vals.size else float("nan"),\n            "pelletier_agb_eq5_p05_kg_m2": float(np.percentile(agb_vals, 5)) if agb_vals.size else float("nan"),\n            "pelletier_agb_eq5_p95_kg_m2": float(np.percentile(agb_vals, 95)) if agb_vals.size else float("nan"),\n            "pelletier_agb_eq5_max_kg_m2": float(np.max(agb_vals)) if agb_vals.size else float("nan"),\n            "wang_cveg_mean_kgC_m2": float(np.mean(wang_vals)) if wang_vals.size else float("nan"),\n            "wang_cveg_median_kgC_m2": float(np.median(wang_vals)) if wang_vals.size else float("nan"),\n            "wang_cveg_p05_kgC_m2": float(np.percentile(wang_vals, 5)) if wang_vals.size else float("nan"),\n            "wang_cveg_p95_kgC_m2": float(np.percentile(wang_vals, 95)) if wang_vals.size else float("nan"),\n            "wang_cveg_max_kgC_m2": float(np.max(wang_vals)) if wang_vals.size else float("nan"),\n            "pelletier_agb_vs_wang_cveg_cell_corr": corr_aw,\n            "wang_cveg_valid_cell_fraction": float(np.count_nonzero(np.isfinite(wang_cveg) & igrid.land) / max(np.count_nonzero(igrid.land), 1)),\n        })\n'''
    if anchor2 not in r1:
        raise SystemExit("runner row anchor missing")
    r1 = r1.replace(anchor2, add2, 1)

    anchor3 = '                "vegetation_code": veg_code, "npp": npp, "eemt": eemt,\n'
    add3 = '                "vegetation_code": veg_code, "npp": npp, "eemt": eemt,\n                "agb_pelletier_eq5": agb_diag.astype("float32"), "wang_cveg": wang_cveg.astype("float32"),\n                "biome4_full_id": full_biome.astype("float32"),\n'
    if anchor3 not in r1:
        raise SystemExit("runner snapshot anchor missing")
    r1 = r1.replace(anchor3, add3, 1)
    runner.write_text(r1, encoding="utf-8")

    v0 = init.read_text(encoding="utf-8")
    v1 = re.sub(r"__version__\s*=\s*['\"][^'\"]+['\"]",
                "__version__ = '6.6.3-CHELSA21K-nativeclimate-pelletierAGB-eq5'",
                v0, count=1)
    if v1 == v0:
        raise SystemExit("version update failed")
    init.write_text(v1, encoding="utf-8")

    note = root / "PELLETIER_AGB_EQ5_CANDIDATE_2026-10-05.md"
    note.write_text("""# Pelletier AGB Eq. (5) candidate\n\nThis is an experimental candidate, NOT the canonical production package.\n\nOnly the AGB bridge is changed relative to PB4-McKenzie-nativeClimate:\n\nAGB = e exp(f EEMT), with e=1 kg m^-2 and f=0.1 yr m^2 MJ^-1,\nfollowing Pelletier et al. (2013) Eq. (5). No Yongneup refitting or AGB clipping is used.\n\nWang et al. (2011) Cveg=NPP*tau_veg is calculated for diagnostics only and never feeds geomorphology.\n""", encoding="utf-8")

    import difflib
    parts = []
    for name, before, after in [
        ("pb4studio/climate.py", c0, c1),
        ("pb4studio/config.py", g0, g1),
        ("pb4studio/runner.py", r0, r1),
        ("pb4studio/__init__.py", v0, v1),
    ]:
        parts.append("".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                                  fromfile=name+".baseline", tofile=name+".candidate")))
    PATCH.write_text("\n".join(parts), encoding="utf-8")
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
            cwd=run_root, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1
        )
        assert p.stdout is not None
        for line in p.stdout:
            print(line, end="")
            log.write(line)
        rc = p.wait()
        if rc != 0:
            raise SystemExit(f"candidate full run failed: exit {rc}")
    return run_root / "outputs_CHELSA21K"


def jang_summary(out: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    target = {
        "95_01": ("broadleaf", "basin_count_broadleaf"),
        "95_02": ("mixed", "basin_count_mixed"),
        "95_03": ("broadleaf", "basin_count_broadleaf"),
        "95_04": ("mixed", "basin_count_mixed"),
    }
    summaries, zones = [], []
    for mode in ("static", "dynamic"):
        p = out / f"model_{mode}" / "validation_per_output_time.csv"
        df = pd.read_csv(p, encoding="utf-8-sig")
        df = df[df["record_id"].astype(str).isin(target)].copy()
        df["target_class"] = df["record_id"].astype(str).map(lambda x: target[x][0])
        df["target_count"] = df.apply(lambda r: r[target[str(r["record_id"])][1]], axis=1)
        df["target_fraction"] = df["target_count"] / df["valid_basin_cell_count"]
        df["correct_1pct"] = df["target_fraction"] >= 0.01 - 1e-15
        summaries.append({
            "model":"PB4-McKenzie-nativeClimate-PelletierAGB-Eq5",
            "mode":mode, "n":len(df), "correct_n":int(df["correct_1pct"].sum()),
            "accuracy_pct":100*float(df["correct_1pct"].mean()), "threshold_fraction":0.01
        })
        for rid,g in df.groupby(df["record_id"].astype(str),sort=False):
            zones.append({
                "mode":mode, "record_id":rid, "target_class":target[rid][0],
                "n":len(g), "correct_n":int(g["correct_1pct"].sum()),
                "accuracy_pct":100*float(g["correct_1pct"].mean()),
                "target_fraction_min":float(g["target_fraction"].min()),
                "target_fraction_max":float(g["target_fraction"].max())
            })
    return pd.DataFrame(summaries), pd.DataFrame(zones)


def collect_timeseries(out: Path) -> pd.DataFrame:
    frames = []
    for mode in ("static","dynamic"):
        found = []
        for p in (out / f"model_{mode}").rglob("*.csv"):
            try:
                df = pd.read_csv(p, encoding="utf-8-sig")
            except Exception:
                continue
            if "pelletier_agb_eq5_mean_kg_m2" in df.columns:
                found.append((p,df))
        if not found:
            raise SystemExit(f"no diagnostic timeseries CSV found for {mode}")
        # choose the longest table, which is the 211-step summary rather than snapshots.
        p,df=max(found,key=lambda x:len(x[1]))
        df=df.copy()
        df.insert(0,"mode",mode)
        df.insert(1,"source_csv",str(p.relative_to(out)))
        frames.append(df)
    return pd.concat(frames,ignore_index=True)


def build_candidate_zip(root: Path) -> str:
    CANDIDATE_ZIP.parent.mkdir(parents=True, exist_ok=True)
    fixed=(2026,10,5,0,0,0)
    with zipfile.ZipFile(CANDIDATE_ZIP,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(root.rglob("*")):
            if not p.is_file():
                continue
            rel=p.relative_to(TMP).as_posix()
            info=zipfile.ZipInfo(rel,date_time=fixed)
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o644 & 0xFFFF)<<16
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return sha256(CANDIDATE_ZIP)


def save_results(out: Path, cand_sha: str):
    OUTDST.mkdir(parents=True,exist_ok=True)
    s,z=jang_summary(out)
    s.to_csv(OUTDST/"PELLETIER_AGB_EQ5_JANG1PCT_SUMMARY.csv",index=False,encoding="utf-8-sig")
    z.to_csv(OUTDST/"PELLETIER_AGB_EQ5_JANG1PCT_BY_ZONE.csv",index=False,encoding="utf-8-sig")
    ts=collect_timeseries(out)
    ts.to_csv(OUTDST/"PELLETIER_AGB_EQ5_WANG_DIAGNOSTIC_TIMESERIES.csv",index=False,encoding="utf-8-sig")

    # Compact summary of Pelletier AGB vs Wang vegetation carbon. Units are kept distinct.
    metrics=[]
    for mode,g in ts.groupby("mode"):
        metrics.append({
            "mode":mode,
            "n_timesteps":len(g),
            "pelletier_agb_time_mean_of_cell_means_kg_m2":float(g["pelletier_agb_eq5_mean_kg_m2"].mean()),
            "pelletier_agb_min_time_mean_kg_m2":float(g["pelletier_agb_eq5_mean_kg_m2"].min()),
            "pelletier_agb_max_time_mean_kg_m2":float(g["pelletier_agb_eq5_mean_kg_m2"].max()),
            "pelletier_agb_absolute_max_kg_m2":float(g["pelletier_agb_eq5_max_kg_m2"].max()),
            "wang_cveg_time_mean_of_cell_means_kgC_m2":float(g["wang_cveg_mean_kgC_m2"].mean()),
            "wang_cveg_min_time_mean_kgC_m2":float(g["wang_cveg_mean_kgC_m2"].min()),
            "wang_cveg_max_time_mean_kgC_m2":float(g["wang_cveg_mean_kgC_m2"].max()),
            "mean_cellwise_corr":float(g["pelletier_agb_vs_wang_cveg_cell_corr"].mean()),
            "min_cellwise_corr":float(g["pelletier_agb_vs_wang_cveg_cell_corr"].min()),
            "max_cellwise_corr":float(g["pelletier_agb_vs_wang_cveg_cell_corr"].max()),
            "mean_wang_valid_fraction":float(g["wang_cveg_valid_cell_fraction"].mean()),
        })
    pd.DataFrame(metrics).to_csv(OUTDST/"PELLETIER_AGB_EQ5_VS_WANG_SUMMARY.csv",index=False,encoding="utf-8-sig")

    prov={
        "execution_status":"new_full_21ka_candidate_run",
        "baseline_model":"PB4-McKenzie-nativeClimate",
        "baseline_canonical_sha256":CANON_SHA,
        "candidate_model":"PB4-McKenzie-nativeClimate-PelletierAGB-Eq5",
        "candidate_zip":str(CANDIDATE_ZIP.relative_to(REPO)),
        "candidate_sha256":cand_sha,
        "climate":"YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv",
        "period_ka_bp":"21.0-0.0",
        "interval_kyr":0.1,
        "only_scientific_change_for_geomorphology":"AGB bridge: legacy 0.010*NPP -> Pelletier et al. (2013) Eq.5 AGB=1*exp(0.1*EEMT)",
        "pelletier_agb":{"e_kg_m2":1.0,"f_yr_m2_per_mj":0.1,"clipping":"none","refit":"none"},
        "wang_diagnostic":{
            "equation":"Cveg=NPP*tau_veg",
            "feeds_geomorphology":False,
            "units":"kg C m^-2",
            "tau_yr":{"tropical_forest":24,"warm_temperate_forest":15,"temperate_forest":10,"boreal_forest":26,
                      "savanna_dry_woodland":4,"grassland_dry_shrubland":4,"desert":9,"dry_tundra":20,"tundra":11},
            "note":"AGB kg dry biomass m^-2 and Cveg kg C m^-2 are not treated as identical quantities."
        },
        "validation":"Jang 2011 corrected reduced mapping, n=62, 1% basin presence"
    }
    (OUTDST/"PELLETIER_AGB_EQ5_PROVENANCE.json").write_text(json.dumps(prov,ensure_ascii=False,indent=2),encoding="utf-8")
    shutil.copy2(PATCH,OUTDST/"PELLETIER_AGB_EQ5.patch")
    shutil.copy2(RUN_LOG,OUTDST/"PELLETIER_AGB_EQ5_21KA_RUN.log")

    md=f"""# Pelletier Eq. (5) AGB candidate — full 21–0 ka test\n\n## Status\n\nThis is a candidate only. The canonical PB4-McKenzie-nativeClimate package was not overwritten.\n\n- baseline SHA-256: `{CANON_SHA}`\n- candidate SHA-256: `{cand_sha}`\n- candidate ZIP: `{CANDIDATE_ZIP.relative_to(REPO)}`\n\n## Candidate change\n\nThe legacy PB4 bridge `AGB=0.010*NPP` was replaced by Pelletier et al. (2013) Eq. (5) without Yongneup refitting or clipping:\n\n```text\nAGB = 1.0 * exp(0.1 * EEMT)\n```\n\nAll other production settings remain native-climate PB4-McKenzie.\n\n## Wang comparison\n\nWang et al. (2011) `Cveg=NPP*tau_veg` is computed independently as a diagnostic. It does not feed geomorphology. Its units are kg C m^-2, whereas Pelletier AGB is kg live dry biomass m^-2, so they are compared in magnitude/pattern/correlation without silently treating them as the same variable.\n\n## Jang 1% result\n\n{s.to_markdown(index=False)}\n\n## Wang diagnostic summary\n\n{pd.DataFrame(metrics).to_markdown(index=False)}\n\nPromotion decision remains pending scientific comparison with the canonical baseline.\n"""
    (OUTDST/"PELLETIER_AGB_EQ5_RESULTS_KO.md").write_text(md,encoding="utf-8")


def main():
    z=reconstruct()
    root=patch_candidate(z)
    cand_sha=build_candidate_zip(root)
    out=run_full(root)
    save_results(out,cand_sha)
    print("CANDIDATE_SHA256="+cand_sha)
    print(pd.read_csv(OUTDST/"PELLETIER_AGB_EQ5_JANG1PCT_SUMMARY.csv").to_string(index=False))
    print(pd.read_csv(OUTDST/"PELLETIER_AGB_EQ5_VS_WANG_SUMMARY.csv").to_string(index=False))


if __name__=="__main__":
    main()
