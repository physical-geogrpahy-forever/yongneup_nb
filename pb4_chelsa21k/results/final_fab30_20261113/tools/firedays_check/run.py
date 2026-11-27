import sys, os, numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/final/PB4Studio_v6.6.3_CHELSA21K')
os.environ['OMP_NUM_THREADS']='1'
from pb4studio import biome4_backend as B, climate as C
KA=float(sys.argv[1]) if len(sys.argv)>1 else 2.8
f=pd.read_csv('/home/claude/physical-geogrpahy-forever/yongneup_nb/pb4_chelsa21k/results/final_fab30_20261113/reference_run/model_dynamic/monthly_forcing_timeseries.csv',encoding='utf-8-sig')
f=f[np.isclose(f.ka_bp,KA)].sort_values('month')
T=f.temperature_C_mean.values; P=f.precipitation_mm_mean.values; cl=f.cloud_pct_mean.values; co2=f.co2_ppm.values[0]
tc=T.min(); tmin=0.006*tc**2+1.316*tc-21.9
H=np.array([0.02,0.04,0.07,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.5,0.7,1.0,1.94])
whc_t,whc_b=C._mckenzie2003_yongneup_awc_stores(H,1.5)
core=B.Biome4FortranBatchCore('/home/claude/firecheck/libdiag.so', nvars=B._variant_nvars('mckenzie2003'), biome4_variant='mckenzie2003')
p=101325*(1-2.25577e-5*1217)**5.25588
rows=[]
for h,wt,wb in zip(H,whc_t,whc_b):
    v=np.zeros((core.nvars,1),np.float32,order='F')
    v[0]=38.218; v[1]=co2; v[2]=p; v[3]=tmin; v[4:16,0]=T; v[16:28,0]=P; v[28:40,0]=100-cl
    v[40]=4; v[41]=4; v[42]=wt; v[43]=wb; v[48]=128.1265; v[49]=1; v[50]=h
    n0=sum(1 for _ in open('fort.77')) if os.path.exists('fort.77') else 0
    out=core.run_vars(v)
    lines=open('fort.77').read().splitlines()[n0:]
    open(f'daily_H{h:.2f}.txt','w').write('\n'.join(lines))
    rows.append(dict(H=h,whc_top=wt,whc_bot=wb,optpft=int(out[11,0]),wdom=int(out[454,0]),npp=out[2,0],fire=out[198,0],
        fire4=out[277,0],fire7=out[280,0],fire6=out[279,0],npp4=out[303,0],npp7=out[306,0]))
df=pd.DataFrame(rows); print(f'ka {KA} Tc {tc:.2f} P {P.sum():.0f} co2 {co2:.0f}'); print(df.round(2).to_string(index=False))
