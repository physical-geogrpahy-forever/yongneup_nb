import pandas as pd,numpy as np,sys
S='/home/claude/sc07/PB4Studio_v6.6.3_CHELSA21K/outputs_CHELSA21K/'
times=[round(21-0.1*i,1) for i in range(211)]
rows=[];cells=[]
for ka in times:
    a=pd.read_csv(S+f'model_static/snapshot_{ka:g}ka/cell_values.csv',encoding='utf-8-sig')
    b=pd.read_csv(S+f'model_dynamic/snapshot_{ka:g}ka/cell_values.csv',encoding='utf-8-sig')
    assert (a.row.values==b.row.values).all() and (a['col'].values==b['col'].values).all()
    dopt=(a.optpft.fillna(-1).round()!=b.optpft.fillna(-1).round()).values
    dveg=(a.vegetation_code.fillna(-1)!=b.vegetation_code.fillna(-1)).values
    diff=dopt|dveg
    clim={}
    for c in ['annual_mean_temp_C','annual_precip_mm','gdd5','tcm_C','absolute_min_temp_C','annual_mean_cloud_pct']:
        clim[c+'_range_static']=a[c].max()-a[c].min(); clim[c+'_range_dyn']=b[c].max()-b[c].min()
        clim[c+'_maxdiff_models']=np.nanmax(np.abs(a[c].values-b[c].values))
    h=b.soil_depth_m.values; w=b.whc_total_dynamic_mm.values
    rows.append(dict(ka=ka,n_diff=int(diff.sum()),n_diff_opt=int(dopt.sum()),n_diff_veg=int(dveg.sum()),
        static_soil=a.soil_depth_m.mean(),diff_soil_max=np.nanmax(h[diff]) if diff.any() else np.nan,
        diff_whc_max=np.nanmax(w[diff]) if diff.any() else np.nan,
        same_soil_min=np.nanmin(h[~diff & (b.optpft.fillna(-1).round()>0).values]),
        same_whc_min=np.nanmin(w[~diff & (b.optpft.fillna(-1).round()>0).values]),**clim))
    if diff.any():
        t=pd.DataFrame(dict(ka=ka,row=b.row[diff],col=b['col'][diff],soil_dyn=h[diff],whc_dyn=w[diff],soil_static=a.soil_depth_m[diff],
            opt_static=a.optpft[diff],opt_dyn=b.optpft[diff],veg_static=a.vegetation_code[diff],veg_dyn=b.vegetation_code[diff]))
        cells.append(t)
r=pd.DataFrame(rows); c=pd.concat(cells)
r.to_csv('h1_by_time.csv',index=False); c.to_csv('h1_diff_cells.csv',index=False)
pd.set_option('display.width',250)
print(r[['ka','n_diff','n_diff_opt','n_diff_veg','diff_soil_max','diff_whc_max','same_soil_min','same_whc_min']].iloc[::10].round(3).to_string(index=False))
cl=[x for x in r.columns if 'range' in x or 'maxdiff' in x]
print(r[cl].max().round(4).to_string())
