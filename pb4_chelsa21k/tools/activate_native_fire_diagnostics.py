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
CANON = BASE / "model" / "PB4Studio_v6.6.3_CHELSA21K.zip"
RESULT = BASE / "results" / "native_fire_20261006"
CANDIDATE = BASE / "model_candidates" / "PB4Studio_v6.6.3_CHELSA21K_FIREACTIVE.zip"
WORK = Path("/tmp/pb4_native_fire")
RUNWORK = Path("/tmp/pb4_native_fire_run")
FIRE_AGES = [3.5,3.4,3.3,3.2,3.1,3.0,2.9,2.8,2.7,2.6,2.5,2.4,2.3,2.2,2.1,2.0]
DEPTHS = [0.01,0.02,0.03,0.04,0.05,0.06,0.08,0.10,0.12,0.15,0.20,0.30,0.50,1.50]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(args, cwd=None, env=None, stdout=None):
    print("+", " ".join(map(str,args)), flush=True)
    return subprocess.run(args, cwd=cwd, env=env, check=True, text=True, stdout=stdout, stderr=subprocess.STDOUT if stdout else None)


def extract_current() -> Path:
    if not CANON.is_file():
        raise SystemExit(f"missing canonical package: {CANON}")
    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir(parents=True)
    with zipfile.ZipFile(CANON) as z:
        z.extractall(WORK)
    roots=[p for p in WORK.iterdir() if p.is_dir() and p.name.startswith("PB4Studio")]
    if len(roots)!=1:
        raise SystemExit(f"expected one PB4 root, found {roots}")
    return roots[0]


def audit_native_fire(root: Path) -> dict:
    src=(root/"fortran_src"/"biome4_original_4_2b2.f").read_text(encoding="utf-8",errors="replace")
    low=src.lower()
    required={
        "fire_call": "call fire (wet,pft,maxlai,npp,firedays)",
        "fire_subroutine": "subroutine fire (wet,pft,lai,npp,firedays)",
        "pft6_fire_threshold": "firedays.gt.90",
        "fire_output": "outv(199)=nint(firedays)",
    }
    status={k:(v in low) for k,v in required.items()}
    if not all(status.values()):
        raise SystemExit(f"native BIOME4 fire contract missing: {status}")
    return status


def patch_runner(root: Path) -> None:
    p=root/"pb4studio"/"runner.py"
    s=p.read_text(encoding="utf-8")
    if "FIREACTIVE diagnostic export" not in s:
        anchor='''        row = summarize_snapshot(int(round(igrid.resolution_m)), float(ka), z, h, veg_code, npp, eemt, igrid.land)\n        row.update({\n'''
        insert='''        row = summarize_snapshot(int(round(igrid.resolution_m)), float(ka), z, h, veg_code, npp, eemt, igrid.land)\n        # FIREACTIVE diagnostic export: native BIOME4 v4.2b2 already computes\n        # PFT-specific potential fire days and uses them in competition2.\n        # This patch exposes the native variables without changing thresholds,\n        # moisture equations, NPP scaling, or vegetation competition.\n        fire_dom = np.asarray(veg.get("firedays_node", np.full(igrid.shape, np.nan)), dtype="float64")\n        valid_fire = igrid.land & np.isfinite(fire_dom)\n        row["mean_dominant_firedays"] = float(np.nanmean(fire_dom[valid_fire])) if np.any(valid_fire) else np.nan\n        row["max_dominant_firedays"] = float(np.nanmax(fire_dom[valid_fire])) if np.any(valid_fire) else np.nan\n        for pft in range(1, 14):\n            key = f"pft{pft:02d}_firedays_node"\n            parr = np.asarray(veg.get(key, np.full(igrid.shape, np.nan)), dtype="float64")\n            valid = igrid.land & np.isfinite(parr)\n            row[f"mean_pft{pft:02d}_firedays"] = float(np.nanmean(parr[valid])) if np.any(valid) else np.nan\n            row[f"max_pft{pft:02d}_firedays"] = float(np.nanmax(parr[valid])) if np.any(valid) else np.nan\n        row.update({\n'''
        if anchor not in s:
            raise SystemExit("runner summary anchor not found")
        s=s.replace(anchor,insert,1)
    if '"biome4_fire_module": "native_v4.2b2_active"' not in s:
        anchor='''            "biome4_variant": str(run_config.science.biome4_variant),\n'''
        if anchor not in s:
            raise SystemExit("runner metadata anchor not found")
        s=s.replace(anchor,anchor+'''            "biome4_fire_module": "native_v4.2b2_active",\n''',1)
    if 'snapshot_fields["firedays"]' not in s:
        anchor='''            if "lai_node" in veg:\n                snapshot_fields["lai"] = np.asarray(veg["lai_node"], dtype="float32")\n'''
        insert=anchor+'''            if "firedays_node" in veg:\n                snapshot_fields["firedays"] = np.asarray(veg["firedays_node"], dtype="float32")\n            if "pft06_firedays_node" in veg:\n                snapshot_fields["pft06_firedays"] = np.asarray(veg["pft06_firedays_node"], dtype="float32")\n            if "pft07_firedays_node" in veg:\n                snapshot_fields["pft07_firedays"] = np.asarray(veg["pft07_firedays_node"], dtype="float32")\n'''
        if anchor not in s:
            raise SystemExit("runner snapshot anchor not found")
        s=s.replace(anchor,insert,1)
    p.write_text(s,encoding="utf-8")


def add_note(root: Path, canon_sha: str) -> None:
    (root/"BIOME4_NATIVE_FIRE_ACTIVE_2026-10-06.md").write_text(f"""# BIOME4 native fire activation/audit

Base canonical ZIP SHA-256: {canon_sha}

The native BIOME4 v4.2b2 fire calculation was already present and active in the
science core. This candidate does not retune or replace it. It makes the native
fire diagnostics visible in normal PB4 outputs so the late-Holocene fire signal
can be audited directly against CHELSA-TraCE21k forcing and Park et al. (2021).

Unchanged native science:
- PFT-dependent soil-moisture fire thresholds in subroutine fire
- NPP scaling of potential fire days
- competition2 fire rules, including PFT6 firedays > 90 d
- all current PB4-McKenzie-nativeClimate and BIOME4-derived AGB* coupling

New diagnostics only:
- summary_timeseries.csv: mean/max dominant firedays and PFT01-PFT13 firedays
- snapshots/cell_values: firedays, pft06_firedays, pft07_firedays

No climate values, fire thresholds, PFT climate limits, NPP equations, AGB*
equations, or geomorphic parameters are changed by this diagnostic candidate.
""",encoding="utf-8")


def zip_tree(root: Path) -> None:
    CANDIDATE.parent.mkdir(parents=True,exist_ok=True)
    if CANDIDATE.exists():
        CANDIDATE.unlink()
    with zipfile.ZipFile(CANDIDATE,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(root.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts and ".pytest_cache" not in p.parts:
                z.write(p, Path(root.name)/p.relative_to(root))


def run_depth_audit(root: Path) -> Path:
    """Run the current package BIOME4 core directly; no legacy helper required."""
    out=Path("/tmp/NATIVE_FIRE_DEPTH_SWEEP.csv")
    climate_path=root/"embedded_inputs"/"yongneup_exact20m"/"YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv"
    if not climate_path.is_file():
        raise SystemExit(f"embedded CHELSA forcing missing: {climate_path}")

    sys.path.insert(0,str(root))
    from pb4studio import biome4_backend
    from pb4studio.climate import load_climate, climate_arrays_for_time, build_soil_arrays, run_biome4_dynamic_step
    from pb4studio.config import ScienceConfig, _LegacyCfgShim

    biome4_backend.FORTRAN_SOURCE_DIR=root/"fortran_src"
    climate=load_climate(climate_path,lon_value=128.1236,lat_value=38.2153)
    available=np.asarray(sorted(climate["ka_bp"].unique()),float)
    land=np.array([[True]])
    tex=np.array([[2.0]])
    lat=np.array([[38.2153]])
    lon=np.array([[128.1236]])
    elev=np.array([[1162.08]],float)
    sci=ScienceConfig(biome4_variant="mckenzie2003")
    cfg=_LegacyCfgShim(sci,2)
    rows=[]
    for target in FIRE_AGES:
        age=float(available[np.argmin(np.abs(available-float(target)))])
        temp,prec,cloud,tmin,co2=climate_arrays_for_time(cfg,climate,age,elev,land)
        for h in DEPTHS:
            soil=build_soil_arrays(cfg,np.array([[float(h)]],float),land,tex)
            veg=run_biome4_dynamic_step(cfg,temp,prec,cloud,tmin,co2,soil,lat,lon,elev,land)
            row={
                "variant":"mckenzie2003","target_age_ka":float(target),"climate_age_ka":age,"depth_m":float(h),
                "whc_top_mm":float(soil["whc_top_mm"][0,0]),"whc_bottom_mm":float(soil["whc_bottom_mm"][0,0]),
                "whc_total_mm":float(soil["whc_top_mm"][0,0]+soil["whc_bottom_mm"][0,0]),
                "biome_id":int(veg["biome4_full_id_node"][0,0]),"optpft":int(veg["optpft_node"][0,0]),
                "npp_gC_m2_yr":float(veg["npp_node"][0,0]),"lai":float(veg["lai_node"][0,0]),
                "firedays":float(veg.get("firedays_node",np.array([[np.nan]]))[0,0]),
            }
            for pft in range(1,14):
                for src,sfx in ((f"pft{pft:02d}_raw_npp_node","npp"),
                                (f"pft{pft:02d}_raw_lai_node","lai"),
                                (f"pft{pft:02d}_wetness_node","wetness"),
                                (f"pft{pft:02d}_aet_node","aet"),
                                (f"pft{pft:02d}_firedays_node","firedays"),
                                (f"pft{pft:02d}_greendays_node","greendays")):
                    if src in veg:
                        row[f"pft{pft:02d}_{sfx}"]=float(veg[src][0,0])
            rows.append(row)
    pd.DataFrame(rows).to_csv(out,index=False,encoding="utf-8-sig")
    return out


def full_run(root: Path) -> Path:
    shutil.rmtree(RUNWORK,ignore_errors=True)
    shutil.copytree(root,RUNWORK/root.name)
    rr=RUNWORK/root.name
    env=os.environ.copy(); env.setdefault("OMP_NUM_THREADS","4")
    log=Path("/tmp/NATIVE_FIRE_21KA_RUN.log")
    with log.open("w",encoding="utf-8") as fh:
        p=subprocess.Popen([sys.executable,"tools/run_yongneup_21ka_chelsa_selfcontained.py"],cwd=rr,env=env,
                           stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
        assert p.stdout is not None
        for line in p.stdout:
            print(line,end="")
            fh.write(line)
        rc=p.wait()
        if rc!=0:
            raise SystemExit(f"full fire-audit run failed: {rc}")
    return rr/"outputs_CHELSA21K"


def age_col(df: pd.DataFrame) -> str:
    for c in ("ka_bp","model_ka_bp","age_ka","time_ka"):
        if c in df.columns:
            return c
    raise KeyError(f"no age column in {list(df.columns)}")


def annual_precip(root: Path) -> pd.DataFrame:
    p=root/"embedded_inputs"/"yongneup_exact20m"/"YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv"
    df=pd.read_csv(p)
    pr=[f"pr_raw_{m:02d}" for m in range(1,13)]
    out=df[["ka_bp"]].copy()
    out["annual_precip_mm"]=df[pr].sum(axis=1)
    out["winter_spring_precip_mm"]=df[[f"pr_raw_{m:02d}" for m in (11,12,1,2,3,4,5)]].sum(axis=1)
    return out


def summarize_depth(depth_csv: Path, root: Path) -> pd.DataFrame:
    d=pd.read_csv(depth_csv,encoding="utf-8-sig")
    d=d[d["variant"].astype(str).eq("mckenzie2003")].copy()
    pr=annual_precip(root)
    rows=[]
    for age in FIRE_AGES:
        g=d[np.isclose(d["target_age_ka"],age)]
        if g.empty: continue
        p6=pd.to_numeric(g["pft06_firedays"],errors="coerce")
        p7=pd.to_numeric(g["pft07_firedays"],errors="coerce")
        p4=pd.to_numeric(g["pft04_firedays"],errors="coerce")
        p8=pd.to_numeric(g["pft08_firedays"],errors="coerce")
        shallow=g.iloc[(g["depth_m"]-0.05).abs().argmin()]
        deep=g.iloc[(g["depth_m"]-1.50).abs().argmin()]
        rr={
            "age_ka":age,
            "annual_precip_mm":float(pr.iloc[(pr["ka_bp"]-age).abs().argmin()]["annual_precip_mm"]),
            "winter_spring_precip_mm":float(pr.iloc[(pr["ka_bp"]-age).abs().argmin()]["winter_spring_precip_mm"]),
            "pft06_firedays_max_across_depths":float(p6.max()),
            "pft07_firedays_max_across_depths":float(p7.max()),
            "pft04_firedays_max_across_depths":float(p4.max()),
            "pft08_firedays_max_across_depths":float(p8.max()),
            "pft06_exceeds_native_90d_any_depth":bool((p6>90).any()),
            "depth0p05_optpft":int(shallow["optpft"]),
            "depth0p05_pft06_firedays":float(shallow["pft06_firedays"]),
            "depth0p05_pft07_firedays":float(shallow["pft07_firedays"]),
            "depth1p50_optpft":int(deep["optpft"]),
            "depth1p50_pft06_firedays":float(deep["pft06_firedays"]),
            "depth1p50_pft07_firedays":float(deep["pft07_firedays"]),
        }
        rows.append(rr)
    return pd.DataFrame(rows)


def summarize_full(out: Path, root: Path) -> pd.DataFrame:
    pr=annual_precip(root)
    frames=[]
    for mode in ("static","dynamic"):
        p=out/f"model_{mode}"/"summary_timeseries.csv"
        df=pd.read_csv(p,encoding="utf-8-sig")
        ac=age_col(df)
        df[ac]=pd.to_numeric(df[ac],errors="coerce")
        sub=df[(df[ac]>=1.999999)&(df[ac]<=3.500001)].copy()
        sub["mode"]=mode
        sub["age_ka"]=sub[ac]
        keep=["mode","age_ka","mean_dominant_firedays","max_dominant_firedays",
              "mean_pft04_firedays","max_pft04_firedays",
              "mean_pft06_firedays","max_pft06_firedays",
              "mean_pft07_firedays","max_pft07_firedays",
              "mean_pft08_firedays","max_pft08_firedays"]
        frames.append(sub[keep])
    allf=pd.concat(frames,ignore_index=True)
    allf=allf.merge(pr.rename(columns={"ka_bp":"age_ka"}),on="age_ka",how="left")
    allf["pft06_exceeds_native_90d_any_cell"]=allf["max_pft06_firedays"]>90
    return allf.sort_values(["mode","age_ka"],ascending=[True,False])


def jang_score(out: Path) -> pd.DataFrame:
    target={
        "95_01":"basin_count_broadleaf",
        "95_02":"basin_count_mixed",
        "95_03":"basin_count_broadleaf",
        "95_04":"basin_count_mixed",
    }
    rows=[]
    for mode in ("static","dynamic"):
        p=out/f"model_{mode}"/"validation_per_output_time.csv"
        df=pd.read_csv(p,encoding="utf-8-sig")
        df=df[df["record_id"].astype(str).isin(target)].copy()
        ok=[]
        for _,r in df.iterrows():
            cnt=float(r[target[str(r["record_id"])]])
            den=float(r["valid_basin_cell_count"])
            ok.append((cnt/den)>=0.01-1e-15)
        rows.append({"mode":mode,"n":len(df),"correct_1pct":int(sum(ok)),
                     "accuracy_pct":100*sum(ok)/len(df) if len(df) else np.nan})
    return pd.DataFrame(rows)


def write_results(root: Path, audit: dict, depth: pd.DataFrame, full: pd.DataFrame, score: pd.DataFrame, canon_sha: str, cand_sha: str) -> None:
    RESULT.mkdir(parents=True,exist_ok=True)
    depth.to_csv(RESULT/"NATIVE_FIRE_DEPTH_3P5_2P0.csv",index=False,encoding="utf-8-sig")
    full.to_csv(RESULT/"NATIVE_FIRE_SPATIAL_3P5_2P0.csv",index=False,encoding="utf-8-sig")
    score.to_csv(RESULT/"NATIVE_FIRE_JANG_REGRESSION.csv",index=False,encoding="utf-8-sig")
    shutil.copy2("/tmp/NATIVE_FIRE_DEPTH_SWEEP.csv",RESULT/"NATIVE_FIRE_DEPTH_SWEEP_RAW.csv")
    shutil.copy2("/tmp/NATIVE_FIRE_21KA_RUN.log",RESULT/"NATIVE_FIRE_21KA_RUN.log")
    (RESULT/"PROVENANCE.json").write_text(json.dumps({
        "base_canonical_sha256":canon_sha,
        "candidate_sha256":cand_sha,
        "science_change":"none; native BIOME4 fire preserved, diagnostics exported",
        "forcing":"YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv",
        "forcing_interval_kyr":0.1,
        "native_fire_contract":audit,
        "park_fire_windows_ka":[[2.9,2.7],[2.4,2.3]],
    },ensure_ascii=False,indent=2),encoding="utf-8")

    p6max=float(full["max_pft06_firedays"].max())
    firehits=full[full["pft06_exceeds_native_90d_any_cell"]]
    md=[
        "# BIOME4 native fire module audit, CHELSA21K",
        "",
        f"- Base canonical SHA-256: `{canon_sha}`",
        f"- FIREACTIVE candidate SHA-256: `{cand_sha}`",
        "- Forcing: YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv, 0.1 kyr",
        "- Science equations changed: none",
        "- Native BIOME4 fire calculation/competition retained; fire diagnostics added to standard outputs.",
        "",
        "## Native fire source audit",
        "",
        *[f"- {k}: {v}" for k,v in audit.items()],
        "",
        "## 3.5-2.0 ka spatial result",
        "",
        f"- Maximum PFT6 firedays in static/dynamic fire window: **{p6max:.2f} d yr-1**",
        f"- Rows/cases exceeding native PFT6 90-day competition threshold: **{len(firehits)}**",
        "",
        full.to_markdown(index=False),
        "",
        "## Controlled soil-depth audit",
        "",
        depth.to_markdown(index=False),
        "",
        "## Jang 2011 1% regression",
        "",
        score.to_markdown(index=False),
        "",
        "Interpretation: the native fire module itself was not disabled. This candidate makes its",
        "existing fire signal explicit. If the CHELSA late-Holocene oscillation does not push",
        "native firedays across competition thresholds, no fire threshold or climate value is",
        "silently tuned here; an event-based disturbance extension must be evaluated separately.",
    ]
    (RESULT/"NATIVE_FIRE_RESULT_KO.md").write_text("\n".join(md),encoding="utf-8")


def main():
    RESULT.mkdir(parents=True,exist_ok=True)
    canon_sha=sha256(CANON)
    root=extract_current()
    audit=audit_native_fire(root)
    patch_runner(root)
    add_note(root,canon_sha)
    zip_tree(root)
    cand_sha=sha256(CANDIDATE)

    depth_raw=run_depth_audit(root)
    depth=summarize_depth(depth_raw,root)
    out=full_run(root)
    full=summarize_full(out,root)
    score=jang_score(out)

    # This is a diagnostic-only candidate: ecological results must regress exactly.
    expect={"static":24,"dynamic":55}
    for _,r in score.iterrows():
        if int(r["n"])!=62 or int(r["correct_1pct"])!=expect[str(r["mode"])]:
            raise SystemExit(f"Jang regression changed unexpectedly: {score.to_dict('records')}")

    write_results(root,audit,depth,full,score,canon_sha,cand_sha)
    print(score.to_string(index=False))
    print(full.to_string(index=False))
    print(f"candidate={CANDIDATE} sha256={cand_sha}")


if __name__=="__main__":
    main()
