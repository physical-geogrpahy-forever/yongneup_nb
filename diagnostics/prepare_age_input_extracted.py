from __future__ import annotations
from pathlib import Path
import argparse, math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DAYS=np.array([31,28,31,30,31,30,31,31,30,31,30,31],dtype=float)
MIDDAY=np.array([16,44,75,105,136,166,197,228,258,289,319,350],dtype=float)
REF_ELEV=590.4
DOY15=np.array([15,46,74,105,135,166,196,227,258,288,319,349],dtype=float)
LAPSE=-(0.00688+0.0015*np.cos(0.0172*(DOY15-60.0)))

def radiation(latitude_deg, cloud_pct):
    dip=math.pi/180.0; lat=latitude_deg*dip; out=[]
    for day,cloud in zip(MIDDAY,np.asarray(cloud_pct,float)):
        sunshine=np.clip((100.0-cloud)/100.0,0.0,1.0)
        qo=1360.0*(1.0+2.0*0.01675*math.cos(dip*(360.0*day/365.0)))
        rs_dn=qo*(0.25+0.5*sunshine)
        decl=-dip*23.4*math.cos(dip*360.0*(day+10.0)/365.0)
        cla=math.cos(lat)*math.cos(decl); sla=math.sin(lat)*math.sin(decl)
        us=rs_dn*sla; vs=rs_dn*cla
        if us>=vs: hos=math.pi
        elif us<=-vs: hos=0.0
        else: hos=math.acos(-us/vs)
        j_day=2.0*(rs_dn*sla*hos+rs_dn*cla*math.sin(hos))*(3600.0*12.0/math.pi)
        out.append(max(0.0,j_day)/86400.0)
    return np.asarray(out)

def climate_at_age(df, age):
    ages=np.sort(df.ka_bp.unique().astype(float))
    if age < ages[0]-1e-9 or age > ages[-1]+1e-9: raise ValueError(age)
    hi=int(np.searchsorted(ages,age,'left'))
    if hi<len(ages) and abs(ages[hi]-age)<=1e-10: loage=hiage=ages[hi]; w=0.0
    elif hi==0: loage=hiage=ages[0]; w=0.0
    elif hi>=len(ages): loage=hiage=ages[-1]; w=0.0
    else: loage=ages[hi-1]; hiage=ages[hi]; w=(age-loage)/(hiage-loage)
    a=df[np.isclose(df.ka_bp,loage)].sort_values('month'); b=df[np.isclose(df.ka_bp,hiage)].sort_values('month')
    if len(a)!=12 or len(b)!=12: raise ValueError('monthly climate slice incomplete')
    def col(c):
        av=a[c].to_numpy(float); bv=b[c].to_numpy(float); return av if hiage==loage else (1-w)*av+w*bv
    return col('temp_C'),col('precip_mm'),col('cloud_pct')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--age',type=float,required=True); ap.add_argument('--state',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
    state=np.load(a.state,allow_pickle=True); z=np.asarray(state['z'],float); h=np.asarray(state['h'],float); land=np.asarray(state['land'],bool)
    cells=pd.read_csv(ROOT/'inputs/cells.csv'); clim=pd.read_csv(ROOT/'inputs/climate.csv'); co2tab=pd.read_csv(ROOT/'inputs/co2_1ka.csv')
    tref,prec,cloud=climate_at_age(clim,float(a.age)); co2=float(np.interp(a.age,co2tab.ka_bp,co2tab.co2_ppm))
    rows=[]
    for r in cells.itertuples(index=False):
        rr,cc=int(r.row),int(r.col); temp=tref+LAPSE*(z[rr,cc]-REF_ELEV); rsds=radiation(float(r.lat_deg),cloud)
        for m in range(12):
            rows.append({'cell_id':int(r.cell_id),'row':rr,'col':cc,'month':m+1,'days':int(DAYS[m]),'lon_deg':float(r.lon_deg),'lat_deg':float(r.lat_deg),
                         'elevation_m':float(z[rr,cc]),'soil_depth_m':float(h[rr,cc]),'tair_C':float(temp[m]),'precip_mm_month':float(prec[m]),
                         'precip_mean_mm_day':float(prec[m]/DAYS[m]),'precip_m_day_for_TREED_env':float(prec[m]/DAYS[m]/1000.0),
                         'cloud_pct':float(cloud[m]),'cloud_fraction':float(cloud[m]/100.0),'rsds_W_m2_BIOME4_bridge':float(rsds[m]),'co2_ppm':co2})
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); pd.DataFrame(rows).to_csv(out,index=False)
    print(f'PREP age={a.age:g} cells={len(cells)} rows={len(rows)} zmean={z[land].mean():.6f} hmean={h[land].mean():.6f} co2={co2:.3f}')
if __name__=='__main__': main()
