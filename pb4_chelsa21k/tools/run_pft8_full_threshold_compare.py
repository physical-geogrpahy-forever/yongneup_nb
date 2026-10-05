from __future__ import annotations
import hashlib, json, os, re, shutil, subprocess, sys, zipfile
from pathlib import Path
import pandas as pd

REPO=Path(__file__).resolve().parents[2]
BASE=REPO/"pb4_chelsa21k"
SOURCE=BASE/"model"/"PB4Studio_v6.6.3_CHELSA21K.zip"
SOURCE_SHA="a1d0df12eb8f3644ff4aae41588bfaaa171b45d5ff69cb86f69864e1fb9bff34"
THRESHOLDS=[3.0,3.5]

OLD="""      if (wdom.eq.7) then
       if (optnpp(wdom).lt.120.0) then
        optpft=grasspft"""

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def sh(cmd,cwd=None,log=None):
    print("+"," ".join(map(str,cmd)),flush=True)
    if log:
        with open(log,"w",encoding="utf-8") as fh:
            p=subprocess.Popen(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
            assert p.stdout
            for line in p.stdout: print(line,end=""); fh.write(line)
            if p.wait(): raise SystemExit("run failed")
    else:
        subprocess.run(cmd,cwd=cwd,check=True)

def patch(root,threshold):
    src=root/"fortran_src"/"biome4_original_4_2b2.f"
    txt=src.read_text(encoding="latin-1")
    new=f"""      if (wdom.eq.7) then
c PB4 experimental PFT8 shallow-canopy competition extension.
c Not an original BIOME4 v4.2b2 rule.
       if (grasspft.eq.8.and.grassnpp.gt.0.0.and.
     >     grasslai.ge.2.0.and.woodylai.lt.{threshold:.1f}) then
        optpft=grasspft
       else if (optnpp(wdom).lt.120.0) then
        optpft=grasspft"""
    if OLD not in txt: raise SystemExit("competition block not found")
    src.write_text(txt.replace(OLD,new,1),encoding="latin-1")
    for p in (root/"fortran_src").glob("*"):
        if p.suffix in {".so",".o",".mod"}: p.unlink()

def find_ts(out,mode):
    hits=[]
    for p in (out/f"model_{mode}").rglob("*.csv"):
        try:d=pd.read_csv(p,encoding="utf-8-sig")
        except:continue
        if {"ka_bp","reich_lai_sapwood_pft08_count","n_cells"}.issubset(d.columns):
            hits.append((p,d))
    if not hits: raise SystemExit("no timeseries")
    return max(hits,key=lambda x:len(x[1]))[1]

def audit(root,threshold,dst):
    out=root/"outputs_CHELSA21K"
    target={"95_01":("broadleaf","basin_count_broadleaf"),"95_02":("mixed","basin_count_mixed"),
            "95_03":("broadleaf","basin_count_broadleaf"),"95_04":("mixed","basin_count_mixed")}
    sums=[]; rows=[]
    for mode in ["static","dynamic"]:
        d=pd.read_csv(out/f"model_{mode}"/"validation_per_output_time.csv",encoding="utf-8-sig")
        d=d[d.record_id.astype(str).isin(target)].copy()
        d["target_count"]=d.apply(lambda r:r[target[str(r.record_id)][1]],axis=1)
        d["target_fraction"]=d.target_count/d.valid_basin_cell_count
        d["correct_1pct"]=d.target_fraction>=0.01-1e-15
        d["herbaceous_fraction"]=d.basin_count_herbaceous/d.valid_basin_cell_count
        sums.append({"threshold":threshold,"mode":mode,"n":len(d),"correct_n":int(d.correct_1pct.sum()),
                     "accuracy_pct":100*d.correct_1pct.mean(),"max_herbaceous_fraction":d.herbaceous_fraction.max(),
                     "n_herb_ge_1pct":int((d.herbaceous_fraction>=.01).sum())})
        d.insert(0,"mode",mode); rows.append(d)
    pd.DataFrame(sums).to_csv(dst/f"LAI{threshold:.1f}_JANG_SUMMARY.csv",index=False)
    pd.concat(rows).to_csv(dst/f"LAI{threshold:.1f}_JANG_ROWS.csv",index=False)

    ts=[]
    for mode in ["static","dynamic"]:
        d=find_ts(out,mode).copy()
        z=d[["ka_bp","reich_lai_sapwood_pft08_count","n_cells","dominant_vegetation_code","vegetation_class_counts"]].copy()
        z.insert(0,"mode",mode); z["pft8_fraction"]=z.reich_lai_sapwood_pft08_count/z.n_cells
        ts.append(z)
    ts=pd.concat(ts); ts.to_csv(dst/f"LAI{threshold:.1f}_PFT8_21KA.csv",index=False)
    park=ts[(ts["mode"]=="dynamic")&(ts.ka_bp>=.5)&(ts.ka_bp<=3.2)].copy()
    park.to_csv(dst/f"LAI{threshold:.1f}_PARK_INTERVAL.csv",index=False)

    return sums,park

def main():
    if sha(SOURCE)!=SOURCE_SHA: raise SystemExit("source sha mismatch")
    dst=BASE/"results"/"pft8_full_threshold_compare_20261006"
    dst.mkdir(parents=True,exist_ok=True)
    allsum=[]
    for th in THRESHOLDS:
        work=Path(f"/tmp/pb4_pft8_full_{str(th).replace('.','p')}")
        shutil.rmtree(work,ignore_errors=True); work.mkdir()
        with zipfile.ZipFile(SOURCE) as z:z.extractall(work)
        root=next(work.glob("PB4Studio*"))
        patch(root,th)
        sh([sys.executable,"tools/run_yongneup_21ka_chelsa_selfcontained.py"],cwd=root,
           log=dst/f"LAI{th:.1f}_RUN.log")
        sums,park=audit(root,th,dst)
        allsum.extend(sums)
    pd.DataFrame(allsum).to_csv(dst/"THRESHOLD_FULL_JANG_COMPARISON.csv",index=False)
    print(pd.DataFrame(allsum).to_string(index=False))

if __name__=="__main__":main()
