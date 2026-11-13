import pandas as pd, numpy as np, sys, json, os
RUNS=dict(A_negative_included='/home/claude/cand/pkg/outputs_negative_included/',
          B_freeze_zero_final='/home/claude/sc07/PB4Studio_v6.6.3_CHELSA21K/outputs_CHELSA21K/',
          C_biome4_snow='/home/claude/cand/pkg/outputs_biome4_snow/')
if len(sys.argv)>1 and sys.argv[1]=='verify':
    RUNS={'final_sc07':RUNS['B_freeze_zero_final'],'cand_default':'/home/claude/cand/pkg/outputs_freeze_zero/'}
OUT=sys.argv[2] if len(sys.argv)>2 else '/home/claude/cand/cmp'
KAS=[21.0,18.0,15.0,12.0,9.0,6.0,4.0,3.0,2.7,2.0,1.0,0.0]
def lab(k): return ('%g'%k)
def cells(P,m,k): return pd.read_csv(P+f'model_{m}/snapshot_{lab(k)}ka/cell_values.csv')
rows=[];eem=[];pft=[];p7=[]
for name,P in RUNS.items():
    va=pd.read_csv(P+'validation_accuracy_static_dynamic.csv')
    r=dict(run=name,Jang_static=int(va.correct_n.iloc[0]),Jang_dynamic=int(va.correct_n.iloc[1]))
    for m in ['static','dynamic']:
        s=pd.read_csv(P+f'model_{m}/pft_validation_summary.csv')
        r[f'TSS_{m}']=float(s[s.pft_group=='ALL'].TSS.iloc[0])
        t=s[~s.pft_group.isin(['ALL','DWD'])]; TP,FP,FN,TN=[t[c].sum() for c in ['TP','FP','FN','TN']]
        r[f'TSS_noDWD_{m}']=TP/(TP+FN)+TN/(TN+FP)-1
    for m in ['static','dynamic']:
        d=pd.read_csv(P+f'model_{m}/summary_timeseries.csv').set_index('ka_bp')
        r[f'EEMT_mean_all_{m}']=d.mean_eemt.mean()
        for k in KAS: eem.append(dict(run=name,model=m,ka=k,mean_eemt=d.loc[k,'mean_eemt'],min_eemt=d.loc[k,'min_eemt'],max_eemt=d.loc[k,'max_eemt'],
                                    mean_soil=d.loc[k,'mean_soil_depth_m'],min_soil=d.loc[k,'min_soil_depth_m'],max_soil=d.loc[k,'max_soil_depth_m']))
    d=pd.read_csv(P+'model_dynamic/summary_timeseries.csv').set_index('ka_bp')
    r.update(soil0_mean=d.loc[0.0,'mean_soil_depth_m'],soil0_min=d.loc[0.0,'min_soil_depth_m'],soil0_max=d.loc[0.0,'max_soil_depth_m'],
             soil_min_alltime=d.min_soil_depth_m.min(),soil_min_ka=float(d.min_soil_depth_m.idxmin()),soil_max_alltime=d.max_soil_depth_m.max())
    n7=[]
    for k in d.index:
        c=cells(P,'dynamic',k); o=np.rint(c.optpft.fillna(-1)).astype(int); n7.append((k,int((o==7).sum())))
        if any(abs(k-x)<1e-9 for x in KAS):
            u,cn=np.unique(o,return_counts=True); pft.append(dict(run=name,ka=k,**{f'pft{a}':b for a,b in zip(u,cn)}))
            ebio=np.maximum(c.npp.values,0)/1000/0.5*22; eem[-0]  # noop
            p7.append(dict(run=name,ka=k,EEMT=c.eemt.mean(),EBIO=ebio.mean(),EPPT=(c.eemt.values-ebio).mean(),pft7=int((o==7).sum())))
    n7=np.array(n7); r.update(pft7_min=int(n7[:,1].min()),pft7_max=int(n7[:,1].max()),pft7_mean=float(n7[:,1].mean()),
                            pft7_peak_ka=float(n7[n7[:,1].argmax(),0]))
    f=json.load(open(P+'model_dynamic/../model_dynamic/firedays_summary.json')) if os.path.exists(P+'model_dynamic/firedays_summary.json') else None
    rows.append(r)
S=pd.DataFrame(rows).set_index('run').T
S.to_csv(OUT+'/summary.csv'); pd.DataFrame(eem).to_csv(OUT+'/eemt_soil_by_ka.csv',index=False)
pd.DataFrame(pft).fillna(0).to_csv(OUT+'/pft_counts_by_ka.csv',index=False); pd.DataFrame(p7).to_csv(OUT+'/eemt_components_by_ka.csv',index=False)
pd.set_option('display.width',250); print(S.round(3).to_string())
E=pd.DataFrame(eem); print(E[E.model=='dynamic'].pivot(index='ka',columns='run',values='mean_eemt').sort_index(ascending=False).round(1).to_string())
print(pd.DataFrame(p7).round(1).to_string())
print(pd.DataFrame(pft).fillna(0).astype({'ka':float}).round(0).to_string())
