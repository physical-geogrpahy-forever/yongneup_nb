import sys, os, numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/final/PB4Studio_v6.6.3_CHELSA21K')
os.environ['OMP_NUM_THREADS']='1'
from pb4studio import biome4_backend as B, climate as C
f=pd.read_csv('/home/claude/physical-geogrpahy-forever/yongneup_nb/pb4_chelsa21k/results/final_fab30_20261113/reference_run/model_dynamic/monthly_forcing_timeseries.csv',encoding='utf-8-sig')
core=B.Biome4FortranBatchCore('/home/claude/firecheck/libdiag.so', nvars=B._variant_nvars('mckenzie2003'), biome4_variant='mckenzie2003')
p=101325*(1-2.25577e-5*1217)**5.25588
cols=['pft','d','w1','w2','wrn','prec','melt','aet','T','perc']
mdays=np.cumsum([0,31,28,31,30,31,30,31,31,30,31,30,31]); mon=np.searchsorted(mdays[1:],np.arange(365),side='right')+1
rows=[]
for KA in [2.8, 8.0]:
  s=f[np.isclose(f.ka_bp,KA)].sort_values('month')
  T=s.temperature_C_mean.values; P=s.precipitation_mm_mean.values; cl=s.cloud_pct_mean.values; co2=s.co2_ppm.values[0]
  tc=T.min(); tmin=0.006*tc**2+1.316*tc-21.9
  for h in [0.07,0.20,0.30]:
    wt,wb=C._mckenzie2003_yongneup_awc_stores(np.array([h]),1.5)
    v=np.zeros((core.nvars,1),np.float32,order='F')
    v[0]=38.218; v[1]=co2; v[2]=p; v[3]=tmin; v[4:16,0]=T; v[16:28,0]=P; v[28:40,0]=100-cl
    v[40]=4; v[41]=4; v[42]=wt[0]; v[43]=wb[0]; v[48]=128.1265; v[49]=1; v[50]=h
    n77=sum(1 for _ in open('fort.77')) if os.path.exists('fort.77') else 0
    n78=sum(1 for _ in open('fort.78')) if os.path.exists('fort.78') else 0
    out=core.run_vars(v)
    d77=pd.read_csv('fort.77',sep=r'\s+',names=cols,skiprows=n77)
    d78=pd.read_csv('fort.78',sep=r'\s+',names=['d','snow','T','drain'],skiprows=n78)
    snow=d78['snow'].to_numpy()[-365:]
    blk=d77[d77['pft']==7].iloc[-365:]
    dry=blk['wrn'].to_numpy()<0.33
    nosnow=snow<=0.0
    r=dict(ka=KA,H=h,fire_out=int(out[198,0]),dry=int(dry.sum()),dry_snowfree=int((dry&nosnow).sum()),snowfree_days_DecMar=int(nosnow[np.isin(mon,[12,1,2,3])].sum()),max_snow_mm=round(float(snow.max()),1))
    r['snow_cover_months']=[int((snow[mon==k]>0).sum()) for k in range(1,13)]
    rows.append(r)
print(pd.DataFrame(rows).to_string(index=False))
