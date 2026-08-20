from __future__ import annotations
from pathlib import Path
import argparse, json, sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from python.pb4lite.pelletier_geomorph import PelletierStrictConfig
from python.pb4lite.boundary import BoundaryConfig
from python.adaptive_geomorph import _advance_geomorph_interval_adaptive

def assemble(summary,monthly,shape):
    npp=np.full(shape,np.nan,float); aet=np.full((12,)+shape,np.nan,float); lai=np.full(shape,np.nan,float); htrait=np.full(shape,np.nan,float); all_yr=np.full(shape,np.nan,float); cleaf=np.full(shape,np.nan,float)
    cols=set(summary.columns)
    for x in summary.itertuples(index=False):
        rr,cc=int(x.row),int(x.col); npp[rr,cc]=float(x.NPP_gC_m2_yr)
        if 'LAI' in cols: lai[rr,cc]=float(x.LAI)
        if 'H_m' in cols: htrait[rr,cc]=float(x.H_m)
        if 'a_ll_yr' in cols: all_yr[rr,cc]=float(x.a_ll_yr)
        if 'C_leaf_gC_individual' in cols: cleaf[rr,cc]=float(x.C_leaf_gC_individual)
    for x in monthly.itertuples(index=False): aet[int(x.month)-1,int(x.row),int(x.col)]=float(x.aet_actual_mm)
    return npp,aet,lai,htrait,all_yr,cleaf

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--state',required=True); ap.add_argument('--forcing',required=True); ap.add_argument('--summary',required=True); ap.add_argument('--monthly',required=True); ap.add_argument('--next-state',required=True); ap.add_argument('--age',type=float,required=True); ap.add_argument('--interval-kyr',type=float,default=1.0); ap.add_argument('--metrics',required=True); ap.add_argument('--snapshot',default=''); a=ap.parse_args()
    st=np.load(a.state,allow_pickle=True); z=np.asarray(st['z'],float); h=np.asarray(st['h'],float); b=np.asarray(st['b'],float) if 'b' in st.files else z-h; land=np.asarray(st['land'],bool)
    dx=float(st['model_resolution_m']); outlet=tuple(int(x) for x in st['outlet_row_col'])
    forcing=pd.read_csv(a.forcing); summary=pd.read_csv(a.summary); monthly=pd.read_csv(a.monthly)
    if len(summary)!=int(land.sum()): raise ValueError(f'summary cells {len(summary)} != land {land.sum()}')
    npp,aet,lai,htrait,all_yr,cleaf=assemble(summary,monthly,z.shape)
    temp=np.full((12,)+z.shape,np.nan,float); prec=np.full_like(temp,np.nan)
    for x in forcing.itertuples(index=False):
        m=int(x.month)-1; rr,cc=int(x.row),int(x.col); temp[m,rr,cc]=float(x.tair_C); prec[m,rr,cc]=float(x.precip_mm_month)
    peff=prec-aet
    eppt=np.nansum(temp*4186.0*peff,axis=0)/1e6
    ebio=np.maximum(npp,0.0)/1000.0*22.0e6/1e6
    eemt=np.where(land & np.isfinite(eppt+ebio),eppt+ebio,np.nan)
    agb=np.where(land,np.maximum(npp,0.0)*0.010,np.nan)
    bc=BoundaryConfig.from_legacy_single_outlet(z.shape,outlet,eps_m=0.001)
    z2,b2,h2,stats=_advance_geomorph_interval_adaptive(PelletierStrictConfig(),z,b,h,land,bc,eemt,agb,interval_kyr=float(a.interval_kyr),dx_m=dx,
        max_substep_kyr=0.1,min_substep_kyr=1e-10,fluvial_max_change_tolerance_m=0.025,adaptive=True)
    out=Path(a.next_state); out.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(out,z=z2,b=b2,h=h2,land=land,texture=np.asarray(st['texture']),transform=np.asarray(st['transform']),crs=np.asarray(st['crs']),model_resolution_m=np.asarray(dx),outlet_row_col=np.asarray(outlet))
    met={'age_ka_bp':float(a.age),'interval_kyr':float(a.interval_kyr),'cells':int(land.sum()),'mean_z_m':float(np.mean(z[land])),'mean_h_m':float(np.mean(h[land])),'mean_npp_gC_m2_yr':float(np.nanmean(npp[land])),'mean_aet_mm_yr':float(np.nansum(aet[:,land],axis=0).mean()),'mean_eemt_MJ_m2_yr':float(np.nanmean(eemt[land])),'mean_LAI':float(np.nanmean(lai[land])),'mean_trait_H_m':float(np.nanmean(htrait[land])),'mean_a_ll_yr':float(np.nanmean(all_yr[land])),'mean_C_leaf_gC_individual':float(np.nanmean(cleaf[land])),'next_mean_z_m':float(np.mean(z2[land])),'next_mean_h_m':float(np.mean(h2[land])),'max_abs_dH_m':float(np.max(np.abs((h2-h)[land]))),'accepted_substeps':int(stats['accepted_substeps']),'rejected_substeps':int(stats['rejected_or_halved_substeps'])}
    mp=Path(a.metrics); mp.parent.mkdir(parents=True,exist_ok=True)
    if mp.suffix.lower()=='.csv': pd.DataFrame([met]).to_csv(mp,index=False)
    else: mp.write_text(json.dumps(met,indent=2),encoding='utf-8')
    if a.snapshot:
        rows=[]
        for rr,cc in zip(*np.where(land)):
            rows.append({'row':rr,'col':cc,'age_ka_bp':float(a.age),'z_m':z[rr,cc],'soil_depth_m':h[rr,cc],'NPP_gC_m2_yr':npp[rr,cc],'AET_mm_yr':np.nansum(aet[:,rr,cc]),'EEMT_MJ_m2_yr':eemt[rr,cc],'LAI':lai[rr,cc],'trait_H_m':htrait[rr,cc],'a_ll_yr':all_yr[rr,cc],'C_leaf_gC_individual':cleaf[rr,cc]})
        Path(a.snapshot).parent.mkdir(parents=True,exist_ok=True); pd.DataFrame(rows).to_csv(a.snapshot,index=False)
    print(json.dumps(met))
if __name__=='__main__': main()
