from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import pandas as pd

REPO=Path(__file__).resolve().parents[2]
BASE=REPO/"pb4_chelsa21k"
SOURCE=BASE/"model"/"PB4Studio_v6.6.3_CHELSA21K.zip"
OLD="""      if (wdom.eq.7) then
       if (optnpp(wdom).lt.120.0) then
        optpft=grasspft"""

def sh(args,cwd=None,env=None):
    subprocess.run(args,cwd=cwd,env=env,check=True)

def patch(root:Path,th:float):
    src=root/"fortran_src"/"biome4_original_4_2b2.f"
    txt=src.read_text(encoding="latin-1")
    if OLD not in txt:
        raise RuntimeError("PFT7 block not found")
    new=f"""      if (wdom.eq.7) then
c PB4 PFT8 threshold sensitivity candidate, not original BIOME4.
       if (grasspft.eq.8.and.grassnpp.gt.0.0.and.
     >     grasslai.ge.2.0.and.woodylai.lt.{th:.2f}) then
        optpft=grasspft
       else if (optnpp(wdom).lt.120.0) then
        optpft=grasspft"""
    src.write_text(txt.replace(OLD,new,1),encoding="latin-1")
    for p in (root/"fortran_src").glob("*"):
        if p.suffix in {".so",".o",".mod"}:
            p.unlink()

def jang(out:Path):
    target={
      "95_01":("broadleaf","basin_count_broadleaf"),
      "95_02":("mixed","basin_count_mixed"),
      "95_03":("broadleaf","basin_count_broadleaf"),
      "95_04":("mixed","basin_count_mixed"),
    }
    ans={}
    for mode in ("static","dynamic"):
        df=pd.read_csv(out/f"model_{mode}"/"validation_per_output_time.csv",encoding="utf-8-sig")
        df=df[df.record_id.astype(str).isin(target)].copy()
        df["target_count"]=df.apply(lambda r:r[target[str(r.record_id)][1]],axis=1)
        ok=(df.target_count/df.valid_basin_cell_count)>=0.01-1e-15
        ans[mode]={
          "n":int(len(df)),
          "correct":int(ok.sum()),
          "herb_sum":int(df.basin_count_herbaceous.sum()),
          "herb_max":int(df.basin_count_herbaceous.max()),
        }
    return ans

def timeseries(out:Path,mode:str):
    hits=[]
    for p in (out/f"model_{mode}").rglob("*.csv"):
        try: df=pd.read_csv(p,encoding="utf-8-sig")
        except Exception: continue
        if {"ka_bp","reich_lai_sapwood_pft08_count","n_cells"}.issubset(df.columns):
            hits.append((p,df))
    if not hits: raise RuntimeError("timeseries missing")
    return max(hits,key=lambda x:len(x[1]))[1]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--threshold",type=float,required=True)
    args=ap.parse_args()
    th=args.threshold
    work=Path(tempfile.mkdtemp(prefix=f"pft8_{th:.2f}_"))
    with zipfile.ZipFile(SOURCE) as z:z.extractall(work)
    root=next(work.glob("PB4Studio*"))
    patch(root,th)
    env=os.environ.copy();env["OMP_NUM_THREADS"]="4"
    sh([sys.executable,"tools/run_yongneup_21ka_chelsa_selfcontained.py"],cwd=root,env=env)
    out=root/"outputs_CHELSA21K"
    js=jang(out)
    dyn=timeseries(out,"dynamic")
    ages=pd.to_numeric(dyn.ka_bp)
    p8=pd.to_numeric(dyn.reich_lai_sapwood_pft08_count).fillna(0)
    n=pd.to_numeric(dyn.n_cells)
    park=(ages>=2.2)&(ages<=2.7)
    result={
      "threshold":th,
      "jang_static_correct":js["static"]["correct"],
      "jang_dynamic_correct":js["dynamic"]["correct"],
      "jang_dynamic_herb_sum":js["dynamic"]["herb_sum"],
      "jang_dynamic_herb_max":js["dynamic"]["herb_max"],
      "pft8_timesteps_positive_21ka":int((p8>0).sum()),
      "pft8_max_cells_21ka":int(p8.max()),
      "pft8_max_fraction_21ka":float((p8/n).max()),
      "park_2p2_2p7_pft8_steps":int((p8[park]>0).sum()),
      "park_2p2_2p7_pft8_cells_sum":int(p8[park].sum()),
      "park_2p2_2p7_pft8_cells_max":int(p8[park].max()),
    }
    print("PFT8_THRESHOLD_RESULT="+json.dumps(result,sort_keys=True))

if __name__=="__main__":
    main()
