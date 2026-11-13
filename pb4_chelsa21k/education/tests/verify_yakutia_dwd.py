#!/usr/bin/env python3
"""Run the actual teaching notebook cells using the packaged Yakutsk forcing."""
import json, os, sys, time, traceback
from pathlib import Path
os.environ["MPLBACKEND"] = "Agg"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "2"

def main():
    root = Path(__file__).resolve().parents[3]
    path = root / "pb4_chelsa21k/education/ECO_GEOGRAPHY_LAB4_GLOBAL_120KA_FIXED_20261106.ipynb"
    nb = json.loads(path.read_text(encoding="utf-8"))
    scope = {"__name__":"__main__", "__file__":str(path)}
    outpath = Path("yakutia_verification.json")
    t0 = time.monotonic()
    try:
        for i in (1,3,5,7,9):
            print("EXECUTING CELL", i, flush=True)
            code = "".join(nb["cells"][i]["source"])
            exec(compile(code,f"notebook-cell-{i}","exec"),scope,scope)
        scope["scenario_count_widget"].value=2
        scope["start_ka_widget"].value=120
        scope["end_ka_widget"].value=118
        for i,mode in enumerate(["동적","정적"]):
            c=scope["scenario_controls"][i]
            c["name"].value=["yakutsk_dynamic","yakutsk_static"][i]
            c["koppen"].value="Dwd"
            c["representative"].value="RU_YAKUTSK"
            c["model"].value=mode
        for i in (11,13):
            print("EXECUTING CELL",i,flush=True)
            code="".join(nb["cells"][i]["source"])
            exec(compile(code,f"notebook-cell-{i}","exec"),scope,scope)
        import numpy as np, pandas as pd
        result={"status":"passed","location":"RU_YAKUTSK","ages_ka":[120,119,118],
                "basin":scope["virtual_basin_config"],"scenarios":{}}
        for name,p in scope["scenario_paths"].items():
            f=p["work"]/"output"/("model_dynamic" if name.endswith("_dynamic") else "model_static")/"summary_timeseries.csv"
            df=pd.read_csv(f)
            assert len(df)==3,df.shape
            assert np.isfinite(df[["mean_elevation_m","mean_soil_depth_m","mean_npp"]].to_numpy()).all()
            clim=pd.read_csv(p["rawcsv"])
            c=clim[clim.ka_bp==120].sort_values("month")
            cold=float(c.temp_C.min())
            tmin=0.006*cold**2+1.316*cold-21.9
            assert np.allclose(c.tmin_C.to_numpy(),tmin,atol=1e-4)
            result["scenarios"][name]={
                "mean_120ka_temp_C":float(c.temp_C.mean()),
                "precip_120ka_mm":float(c.precip_mm.sum()),
                "subzero_120ka_months":int((c.temp_C<=0).sum()),
                "coldest_month_mean_C":cold,
                "biome4_tmin_C":tmin,
                "summary":df.to_dict(orient="records"),
            }
        result["wall_time_s"]=time.monotonic()-t0
        outpath.write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str),encoding="utf-8")
        print("VALIDATION_RESULT", json.dumps(result,ensure_ascii=False,default=str),flush=True)
        return 0
    except BaseException as e:
        err={"status":"failed","reason":str(e),"traceback":traceback.format_exc(),"elapsed_s":time.monotonic()-t0}
        outpath.write_text(json.dumps(err,ensure_ascii=False,indent=2),encoding="utf-8")
        print("VALIDATION_FAILURE",json.dumps(err,ensure_ascii=False),flush=True)
        return 1
if __name__=="__main__":
    sys.exit(main())
