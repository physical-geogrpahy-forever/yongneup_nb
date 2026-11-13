#!/usr/bin/env python3
"""Probe published raster estimates at the embedded RU_YAKUTSK climate cell.

Research audit only. The virtual 20 m classroom DEM is NOT georeferenced to this
real-world coordinate. Raster estimates are for geological present, not 120 ka.
"""
import json, os, requests, math, warnings
from pathlib import Path
import rasterio
import numpy as np
lat, lon = 62.25, 129.75
points = {"embedded_beyer_cell":[lon,lat],"city_yakutsk":[129.75,62.08],
          "neleger_fieldsite":[129.5166667,62.3166667]}
sources = {
"pelletier_2016_upland_soil_m": [
 "https://ornl-cumulus-prod-public.s3.us-west-2.amazonaws.com/global_soil/Global_Soil_Regolith_Sediment/data/upland_hill-slope_soil_thickness.tif",
 "https://data.ornldaac.earthdata.nasa.gov/public/global_soil/Global_Soil_Regolith_Sediment/data/upland_hill-slope_soil_thickness.tif",
],
"pelletier_2016_mixed_soil_sediment_m": [
 "https://ornl-cumulus-prod-public.s3.us-west-2.amazonaws.com/global_soil/Global_Soil_Regolith_Sediment/data/average_soil_and_sedimentary-deposit_thickness.tif"
],
"soilgrids_2017_absolute_bedrock_mm": [
 "https://data.naturalcapitalalliance.stanford.edu/download/global/isric-soil-grids/depth_to_bedrock/isric_soil_absolute_depth_to_bedrock_250m_mm.tif",
],
}
out={"points":points,"sources":{},"interpretation":{"permafrost_active_layer_is_not_soil_depth":True,"classroom_dem_is_not_georeferenced":True}}
for key,urls in sources.items():
    run={"samples":{},"probes":[],"success":False}
    for u in urls:
        print("PROBING",key,u,flush=True)
        try:
            head=requests.head(u,allow_redirects=True,timeout=18)
            run["probes"].append({"url":u,"status":head.status_code,"type":head.headers.get("Content-Type"),
                                 "length":head.headers.get("Content-Length"),"accept_ranges":head.headers.get("Accept-Ranges")})
            print("HTTP",head.status_code,head.headers.get("Content-Length"),flush=True)
            if head.status_code!=200: continue
            os.environ["GDAL_DISABLE_READDIR_ON_OPEN"]="EMPTY_DIR"
            os.environ["CPL_VSIL_CURL_ALLOWED_EXTENSIONS"]=".tif"
            os.environ["GDAL_HTTP_MAX_RETRY"]="2"
            os.environ["GDAL_HTTP_RETRY_DELAY"]="1"
            with rasterio.open(u) as src:
                run["crs"]=str(src.crs)
                run["resolution"]=list(src.res)
                run["nodata"]=src.nodata
                from rasterio.warp import transform
                x,y=zip(*points.values())
                x2,y2=transform("EPSG:4326",src.crs,list(x),list(y))
                for p,xx,yy in zip(points,x2,y2):
                    rr,cc=src.index(xx,yy)
                    data=src.read(1,window=((rr,rr+1),(cc,cc+1)),masked=True)
                    val=None if np.ma.is_masked(data[0,0]) else float(data[0,0])
                    run["samples"][p]={"value":val,"row":int(rr),"col":int(cc)}
                    print("SAMPLE",key,p,val,flush=True)
                run["success"]=True
                run["source_url"]=u
                break
        except Exception as e:
            print("SOURCE_ERROR",repr(e),flush=True)
            run["probes"].append({"url":u,"error":str(e)})
    out["sources"][key]=run
Path("yakutia_soil_point_audit.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print("AUDIT_RESULT",json.dumps({k:{"success":v["success"],"samples":v["samples"]} for k,v in out["sources"].items()},ensure_ascii=False),flush=True)
