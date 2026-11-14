"""H3: 우점 수준 검증. Jang zone 식생과 유역 다수 범주, Park 최다 그룹과 유역 다수 PFT 그룹."""
import pandas as pd,numpy as np,sys
S=sys.argv[1] if len(sys.argv)>1 else '/home/claude/sc07/PB4Studio_v6.6.3_CHELSA21K/outputs_CHELSA21K/'
v=pd.read_csv(S+'/validation_per_output_time_static_dynamic.csv',encoding='utf-8-sig')
cnt=['basin_count_conifer','basin_count_broadleaf','basin_count_mixed','basin_count_herbaceous','basin_count_nonvegetated']
code={'conifer':0,'broadleaf':1,'mixed':2,'herbaceous':3,'nonvegetated':4}
v['majority']=v[cnt].idxmax(axis=1).str.replace('basin_count_','')
v['majority_ok']=v.majority.map(code)==v.expected_vegetation_code
j=v.groupby(['case','age_start_ka_bp','age_end_ka_bp','vegetation_original_ko','expected_label']).agg(windows=('majority_ok','size'),majority_match=('majority_ok','sum')).reset_index()
grp={3:'TBE',4:'TBD',5:'CON',6:'CON',7:'BDE',8:'GRS',10:'DWD'}
o=pd.read_csv(S+'/model_dynamic/pft_validation_per_output_time.csv',encoding='utf-8-sig')
dom=o.loc[o.groupby('ka_bp').obs_pct.idxmax()].set_index('ka_bp')
rows=[]
for m in ('static','dynamic'):
    d=pd.read_csv(S+f'/model_{m}/pft_model_cells_per_output_time.csv',encoding='utf-8-sig').set_index('ka_bp')
    for ka in dom.index:
        g={}
        for p,k in grp.items(): g[k]=g.get(k,0)+d.loc[ka,f'optpft_p{p:02d}']
        mg=max(g,key=g.get)
        rows.append(dict(model=m,ka_bp=ka,pollen_dominant=dom.loc[ka,'pft_group'],pollen_pct=dom.loc[ka,'obs_pct'],model_dominant=mg,model_share=g[mg]/d.loc[ka,'n_cells'],match=mg==dom.loc[ka,'pft_group']))
p=pd.DataFrame(rows)
j.to_csv('h3_jang_majority.csv',index=False,encoding='utf-8-sig'); p.round(3).to_csv('h3_park_dominant.csv',index=False,encoding='utf-8-sig')
print(j.to_string(index=False)); print(p.groupby('model').match.sum())
