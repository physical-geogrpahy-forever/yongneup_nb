"""Jang/Park 검증을 출현 기준별로 계산: 1개 격자, 유역 1-5%, 거리 가중(1/d, 1/d^2, 화분 기준 적용)."""
import sys, math
import numpy as np, pandas as pd
R=sys.argv[1].rstrip('/')+'/'; LABEL=sys.argv[2]
CX,CY=123245.19,624269.79
GP={'TBD':[4],'BDE':[7],'TBE':[3],'GRS':[8],'DWD':[10]}
jv=pd.read_csv(R+'validation_per_output_time_static_dynamic.csv',encoding='utf-8-sig')
rows=[]
cache={}
def cells(m,k):
    if (m,k) not in cache: cache[(m,k)]=pd.read_csv(R+f'model_{m}/snapshot_{k:g}ka/cell_values.csv',encoding='utf-8-sig')
    return cache[(m,k)]
for m,case in [('static','정적모델'),('dynamic','동적모델')]:
    o=pd.read_csv(R+f'model_{m}/pft_validation_per_output_time.csv',encoding='utf-8-sig')
    x=jv[jv.case_label==case]; N=int(x.valid_basin_cell_count.iloc[0])
    def park(pres):
        ob=o.obs_present==1; tp=int((pres&ob).sum()); fp=int((pres&~ob).sum()); fn=int((~pres&ob).sum()); tn=int((~pres&~ob).sum())
        return (tp+tn)/len(o), tp/(tp+fn)+tn/(tn+fp)-1, int(pres[o.pft_group=='BDE'].sum()), int(pres[o.pft_group=='DWD'].sum())
    rules=[('1 cell',1)]+[(f'{p}%',math.ceil(p/100*N)) for p in (1,2,3,4,5)]
    for lab,mc in rules:
        frac=mc/N
        jang=int((x.accepted_class_basin_cell_count_sum>=mc).sum())
        a,t,b,dw=park(o.model_cells>=mc)
        rows.append(dict(run=LABEL,model=m,rule=lab,min_cells=mc,jang=jang,park_acc=round(a,3),park_TSS=round(t,3),BDE_present=b,DWD_present=dw))
    for pw in (1,2):
        pres=[]
        for _,r in o.iterrows():
            if r.pft_group=='CON': pres.append(r.model_cells>=1); continue
            c=cells(m,r.ka_bp); d=np.maximum(np.hypot(c.x-CX,c.y-CY),50.0).values; w=d**-pw
            opt=np.rint(c.optpft.fillna(-1).values).astype(int)
            pres.append(100*w[np.isin(opt,GP[r.pft_group])].sum()/w.sum()>=r.threshold_pct)
        pres=pd.Series(pres,index=o.index)
        jang=0
        for _,r in x.iterrows():
            c=cells(m,round(r.model_ka_bp,2)); d=np.maximum(np.hypot(c.x-CX,c.y-CY),50.0).values; w=d**-pw
            jang+=int(100*w[(c.vegetation_code==int(r.expected_vegetation_code)).values].sum()/w.sum()>=2.0)
        a,t,b,dw=park(pres)
        rows.append(dict(run=LABEL,model=m,rule=f'distance 1/d^{pw}',min_cells=None,jang=jang,park_acc=round(a,3),park_TSS=round(t,3),BDE_present=b,DWD_present=dw))
df=pd.DataFrame(rows); df.to_csv(sys.argv[3],index=False,encoding='utf-8-sig'); print(df.to_string(index=False))
