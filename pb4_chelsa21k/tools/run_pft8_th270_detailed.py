from __future__ import annotations

import json, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path
import pandas as pd
import numpy as np

REPO=Path(__file__).resolve().parents[2]
BASE=REPO/"pb4_chelsa21k"
SOURCE=BASE/"model"/"PB4Studio_v6.6.3_CHELSA21K.zip"
OUT=BASE/"results"/"pft8_threshold_selected_20261006"
TH=2.70

OLD="""      if (wdom.eq.7) then
       if (optnpp(wdom).lt.120.0) then
        optpft=grasspft"""

NEW=f"""      if (wdom.eq.7) then
c PB4 PFT8 canopy-opening sensitivity candidate, NOT original BIOME4.
       if (grasspft.eq.8.and.grassnpp.gt.0.0.and.
     >     grasslai.ge.2.0.and.woodylai.lt.{TH:.2f}) then
        optpft=grasspft
       else if (optnpp(wdom).lt.120.0) then
        optpft=grasspft"""

def sh(args,cwd=None,env=None):
    subprocess.run(args,cwd=cwd,env=env,check=True)

def find_ts(out:Path,mode:str):
    hits=[]
    for p in (out/f"model_{mode}").rglob("*.csv"):
        try:d=pd.read_csv(p,encoding="utf-8-sig")
        except:continue
        if {"ka_bp","reich_lai_sapwood_pft08_count","n_cells"}.issubset(d.columns):
            hits.append((p,d))
    if not hits: raise RuntimeError(f"timeseries missing {mode}")
    return max(hits,key=lambda x:len(x[1]))

def jang_rows(out:Path,mode:str):
    p=out/f"model_{mode}"/"validation_per_output_time.csv"
    d=pd.read_csv(p,encoding="utf-8-sig")
    target={
      "95_01":("broadleaf","basin_count_broadleaf"),
      "95_02":("mixed","basin_count_mixed"),
      "95_03":("broadleaf","basin_count_broadleaf"),
      "95_04":("mixed","basin_count_mixed"),
    }
    d=d[d.record_id.astype(str).isin(target)].copy()
    d["target_class"]=d.record_id.astype(str).map(lambda x:target[x][0])
    d["target_count"]=d.apply(lambda r:r[target[str(r.record_id)][1]],axis=1)
    d["target_fraction"]=d.target_count/d.valid_basin_cell_count
    d["correct_1pct"]=d.target_fraction>=0.01-1e-15
    return d

def main():
    work=Path(tempfile.mkdtemp(prefix="pft8_selected_"))
    with zipfile.ZipFile(SOURCE) as z:z.extractall(work)
    root=next(work.glob("PB4Studio*"))
    src=root/"fortran_src"/"biome4_original_4_2b2.f"
    txt=src.read_text(encoding="latin-1")
    if OLD not in txt: raise RuntimeError("PFT7 source block not found")
    src.write_text(txt.replace(OLD,NEW,1),encoding="latin-1")
    for p in (root/"fortran_src").glob("*"):
        if p.suffix in {".so",".o",".mod"}:p.unlink()

    env=os.environ.copy();env["OMP_NUM_THREADS"]="4"
    sh([sys.executable,"tools/run_yongneup_21ka_chelsa_selfcontained.py"],cwd=root,env=env)
    out=root/"outputs_CHELSA21K"
    OUT.mkdir(parents=True,exist_ok=True)

    summaries=[]
    for mode in ("static","dynamic"):
        p,ts=find_ts(out,mode)
        ts.to_csv(OUT/f"PFT8_TH270_{mode.upper()}_21KA_TIMESERIES.csv",index=False,encoding="utf-8-sig")
        p8=pd.to_numeric(ts.reich_lai_sapwood_pft08_count,errors="coerce").fillna(0)
        n=pd.to_numeric(ts.n_cells,errors="coerce")
        hit=ts[p8>0].copy()
        hit["pft8_fraction"]=p8[p8>0].to_numpy()/n[p8>0].to_numpy()
        keep=[c for c in ["ka_bp","reich_lai_sapwood_pft08_count","pft8_fraction","dominant_vegetation_code",
                          "vegetation_class_counts","mean_npp","reich_lai_sapwood_agb_mean_kg_m2"] if c in hit.columns]
        hit[keep].to_csv(OUT/f"PFT8_TH270_{mode.upper()}_POSITIVE.csv",index=False,encoding="utf-8-sig")
        j=jang_rows(out,mode)
        j.to_csv(OUT/f"PFT8_TH270_JANG_{mode.upper()}_ROWS.csv",index=False,encoding="utf-8-sig")
        summaries.append({
            "mode":mode,"jang_correct":int(j.correct_1pct.sum()),"jang_n":len(j),
            "pft8_positive_steps":int((p8>0).sum()),"pft8_max_cells":int(p8.max()),
            "pft8_max_fraction":float((p8/n).max()),
            "park_2p2_2p7_positive_steps":int(((pd.to_numeric(ts.ka_bp)>=2.2)&(pd.to_numeric(ts.ka_bp)<=2.7)&(p8>0)).sum())
        })

    s=pd.DataFrame(summaries)
    s.to_csv(OUT/"PFT8_TH270_SUMMARY.csv",index=False)

    dyn=pd.read_csv(OUT/"PFT8_TH270_DYNAMIC_21KA_TIMESERIES.csv",encoding="utf-8-sig")
    ages=pd.to_numeric(dyn.ka_bp)
    p8=pd.to_numeric(dyn.reich_lai_sapwood_pft08_count).fillna(0)
    park=dyn[(ages>=2.2)&(ages<=2.7)].copy()
    park["pft8_fraction"]=pd.to_numeric(park.reich_lai_sapwood_pft08_count).fillna(0)/pd.to_numeric(park.n_cells)
    park.to_csv(OUT/"PFT8_TH270_PARK_2P2_2P7.csv",index=False,encoding="utf-8-sig")

    md=f"""# PFT8 canopy-opening threshold 2.70 detailed candidate

This is a sensitivity candidate, not yet production and not original BIOME4.

Rule:

    if PFT7 is woody dominant
    and best grass PFT is PFT8
    and PFT8 NPP > 0
    and PFT8 LAI >= 2.0
    and PFT7 woody LAI < {TH:.2f}:
        select PFT8

Full 21-0 ka run summary:

{s.to_markdown(index=False)}

Selection principle: this candidate is retained for detailed inspection because it is the largest tested threshold that preserves the existing Jang dynamic 55/62 result while allowing more PFT8 than the 2.65 candidate. Park is not used to tune the threshold.
"""
    (OUT/"PFT8_TH270_DETAILED_KO.md").write_text(md,encoding="utf-8")
    print(s.to_string(index=False))
    print(park[["ka_bp","reich_lai_sapwood_pft08_count","pft8_fraction"]].to_string(index=False))

if __name__=="__main__":main()
