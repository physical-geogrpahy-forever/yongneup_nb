from __future__ import annotations
from pathlib import Path
import argparse, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def grid_from(df,col,shape=(20,23)):
    a=np.full(shape,np.nan,float)
    for r in df.itertuples(index=False): a[int(r.row),int(r.col)]=float(getattr(r,col))
    return a

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--dynamic',required=True); ap.add_argument('--frozen',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
    dd=Path(a.dynamic); ff=Path(a.frozen); out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    td=pd.read_csv(dd/'timeseries.csv').sort_values('age_ka_bp',ascending=False); tf=pd.read_csv(ff/'timeseries.csv').sort_values('age_ka_bp',ascending=False)
    merged=td.merge(tf,on='age_ka_bp',suffixes=('_dynamic','_frozen'))
    for base in ['mean_h_m','mean_npp_gC_m2_yr','mean_aet_mm_yr','mean_eemt_MJ_m2_yr','mean_LAI','mean_trait_H_m','mean_a_ll_yr','mean_C_leaf_gC_individual']:
        merged[f'{base}_difference']=merged[f'{base}_dynamic']-merged[f'{base}_frozen']
    merged.to_csv(out/'comparison_timeseries.csv',index=False)
    vars_ts=[('mean_h_m','Mean soil depth (m)'),('mean_npp_gC_m2_yr','Mean NPP (gC m$^{-2}$ yr$^{-1}$)'),('mean_eemt_MJ_m2_yr','Mean EEMT (MJ m$^{-2}$ yr$^{-1}$)'),('mean_LAI','Mean LAI'),('mean_trait_H_m','Mean optimized/frozen height (m)'),('mean_aet_mm_yr','Mean AET (mm yr$^{-1}$)')]
    fig,axs=plt.subplots(3,2,figsize=(13,12),constrained_layout=True)
    for ax,(v,label) in zip(axs.flat,vars_ts):
        ax.plot(merged.age_ka_bp,merged[f'{v}_dynamic'],label='Trait-dynamic')
        ax.plot(merged.age_ka_bp,merged[f'{v}_frozen'],label='Traits frozen at 120 ka')
        ax.set_xlim(120,0); ax.set_xlabel('Age (ka BP)'); ax.set_ylabel(label); ax.grid(alpha=.25); ax.legend()
    fig.suptitle('Yongneup 120 ka TREED–Pelletier spatial means')
    fig.savefig(out/'mean_timeseries_120ka.png',dpi=180); plt.close(fig)
    ages=[120,80,40,0]
    variables=[('soil_depth_m','Soil depth (m)'),('NPP_gC_m2_yr','NPP (gC m$^{-2}$ yr$^{-1}$)'),('EEMT_MJ_m2_yr','EEMT (MJ m$^{-2}$ yr$^{-1}$)'),('LAI','LAI'),('trait_H_m','Trait height (m)')]
    for col,label in variables:
        fig,axs=plt.subplots(len(ages),3,figsize=(12,14),constrained_layout=True)
        for i,age in enumerate(ages):
            d=pd.read_csv(dd/'snapshots'/f'snapshot_{age:03d}ka.csv'); f=pd.read_csv(ff/'snapshots'/f'snapshot_{age:03d}ka.csv')
            gd=grid_from(d,col); gf=grid_from(f,col); dif=gd-gf
            vv=np.concatenate([gd[np.isfinite(gd)],gf[np.isfinite(gf)]])
            vmin,vmax=float(np.min(vv)),float(np.max(vv)); md=float(np.nanmax(np.abs(dif))) or 1e-12
            im0=axs[i,0].imshow(gd,vmin=vmin,vmax=vmax); im1=axs[i,1].imshow(gf,vmin=vmin,vmax=vmax); im2=axs[i,2].imshow(dif,vmin=-md,vmax=md,cmap='coolwarm')
            axs[i,0].set_ylabel(f'{age} ka BP');
            for ax in axs[i]: ax.set_xticks([]); ax.set_yticks([])
            fig.colorbar(im0,ax=axs[i,0],fraction=.046); fig.colorbar(im1,ax=axs[i,1],fraction=.046); fig.colorbar(im2,ax=axs[i,2],fraction=.046)
        axs[0,0].set_title('Trait-dynamic'); axs[0,1].set_title('Traits frozen at 120 ka'); axs[0,2].set_title('Dynamic − frozen')
        fig.suptitle(f'Yongneup 120 ka comparison: {label}')
        safe=col.replace('/','_'); fig.savefig(out/f'map_{safe}_120_80_40_0ka.png',dpi=180); plt.close(fig)
    # final 0 ka cell-by-cell difference table
    d0=pd.read_csv(dd/'snapshots'/'snapshot_000ka.csv'); f0=pd.read_csv(ff/'snapshots'/'snapshot_000ka.csv')
    keys=['row','col']; q=d0.merge(f0,on=keys,suffixes=('_dynamic','_frozen'))
    for col,_ in variables: q[f'{col}_difference']=q[f'{col}_dynamic']-q[f'{col}_frozen']
    q.to_csv(out/'final_0ka_cell_comparison.csv',index=False)
    summary={'ages':len(merged),'start_ka':float(merged.age_ka_bp.max()),'end_ka':float(merged.age_ka_bp.min()),'final_mean_soil_depth_dynamic_m':float(merged.iloc[-1].mean_h_m_dynamic),'final_mean_soil_depth_frozen_m':float(merged.iloc[-1].mean_h_m_frozen),'final_mean_npp_dynamic':float(merged.iloc[-1].mean_npp_gC_m2_yr_dynamic),'final_mean_npp_frozen':float(merged.iloc[-1].mean_npp_gC_m2_yr_frozen),'final_mean_eemt_dynamic':float(merged.iloc[-1].mean_eemt_MJ_m2_yr_dynamic),'final_mean_eemt_frozen':float(merged.iloc[-1].mean_eemt_MJ_m2_yr_frozen)}
    (out/'comparison_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
