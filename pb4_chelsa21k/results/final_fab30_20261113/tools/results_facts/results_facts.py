"""결과 절 작성을 위한 수치 정리 (최종 실행 L, 30 m, 59.0 ha).
사용: python results_facts.py <outputs_CHELSA21K 경로>
"""
import sys, json, heapq
import numpy as np, pandas as pd, rasterio
from pathlib import Path
P = Path(sys.argv[1])
N8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
times = np.round(np.arange(21.0,-0.001,-0.1),1)
def rd(mode,t,name):
    lab=('%g'%t) if t>1e-9 else '0'
    a=rasterio.open(P/mode/f'snapshot_{lab}ka'/f'{name}.tif').read(1).astype(float)
    a[a<-1e3]=np.nan; return a
z0=rd('model_dynamic',21.0,'elevation_m'); land=np.isfinite(z0)
def flood(z):
    ny,nx=z.shape; m=np.isfinite(z); F=np.full(z.shape,np.nan); done=np.zeros(z.shape,bool); pq=[]
    for i in range(ny):
        for j in range(nx):
            if m[i,j] and any(not(0<=i+a<ny and 0<=j+b<nx) or not m[i+a,j+b] for a,b in N8):
                F[i,j]=z[i,j]; done[i,j]=True; heapq.heappush(pq,(z[i,j],i,j))
    while pq:
        e,i,j=heapq.heappop(pq)
        for a,b in N8:
            p,q=i+a,j+b
            if 0<=p<ny and 0<=q<nx and m[p,q] and not done[p,q]:
                done[p,q]=True; F[p,q]=max(z[p,q],e+1e-4); heapq.heappush(pq,(F[p,q],p,q))
    return F
def acc_d8(z):
    F=flood(z); ny,nx=F.shape; d=-np.ones(F.shape,int)
    for i in range(ny):
        for j in range(nx):
            if not np.isfinite(F[i,j]): continue
            bs=0
            for k,(a,b) in enumerate(N8):
                p,q=i+a,j+b
                if 0<=p<ny and 0<=q<nx and np.isfinite(F[p,q]):
                    s=(F[i,j]-F[p,q])/np.hypot(a,b)
                    if s>bs: bs,d[i,j]=s,k
    acc=np.where(np.isfinite(F),1.0,0.0)
    for k in np.argsort(-np.nan_to_num(F,nan=-1e9).ravel()):
        i,j=divmod(int(k),nx)
        if d[i,j]>=0: a,b=N8[d[i,j]]; acc[i+a,j+b]+=acc[i,j]
    return acc*900/1e4  # ha
out={}
A0=acc_d8(z0)
zE=rd('model_dynamic',0.0,'elevation_m'); dz=zE-z0
out['elev_change_21_0']=dict(mean=float(np.nanmean(dz)),min=float(np.nanmin(dz)),max=float(np.nanmax(dz)),
    n_lower=int(np.nansum(dz<0)),n_higher=int(np.nansum(dz>0)),uplift_total=0.08*21)
# 토심 시계열 통계
rows=[]
for t in times:
    H=rd('model_dynamic',t,'soil_depth_m')[land]; op=rd('model_dynamic',t,'optpft')[land]
    Hs=rd('model_static',t,'soil_depth_m')[land]
    rows.append(dict(ka=t,mean=H.mean(),median=np.median(H),p05=np.percentile(H,5),p95=np.percentile(H,95),
        n_bare=int((H<=1e-6).sum()),n_lt01=int((H<0.1).sum()),n_lt03=int((H<0.3).sum()),n_lt1=int((H<1).sum()),
        n_gt194=int((H>1.94).sum()),max=H.max(),pft7=int((op==7).sum()),pft4=int((op==4).sum()),pft6=int((op==6).sum()),pft10=int((op==10).sum()),pft0=int((op==0).sum())))
TS=pd.DataFrame(rows); TS.to_csv('soil_pft_timeseries.csv',index=False)
# 0 ka 토심과 기여면적, 경사
H=rd('model_dynamic',0.0,'soil_depth_m')
A=acc_d8(zE)
q=pd.qcut(A[land],[0,.5,.75,.9,.95,1.0],duplicates='drop')
g=pd.DataFrame({'A':A[land],'H':H[land]}).groupby(q,observed=True)['H'].agg(['count','mean','median','min','max'])
g.to_csv('soil_depth_by_drainage_0ka.csv')
out['soil_vs_area_0ka_spearman']=float(pd.Series(A[land]).corr(pd.Series(H[land]),method='spearman'))
# 홀로세 PFT7 격자의 위치
hol=[t for t in times if t<=11.7]
pf=[];
for t in hol:
    op=rd('model_dynamic',t,'optpft'); Hh=rd('model_dynamic',t,'soil_depth_m'); zt=rd('model_dynamic',t,'elevation_m')
    m=(op==7)&land
    if m.sum()==0: continue
    At=acc_d8(zt) if abs(t-round(t))<1e-9 else None
    pf.append(dict(ka=t,n=int(m.sum()),H_med=float(np.median(Hh[m])),H_max=float(Hh[m].max()),
        A_med=float(np.median(At[m])) if At is not None else np.nan, A_basin_med=float(np.median(At[land])) if At is not None else np.nan))
pd.DataFrame(pf).to_csv('pft7_cells_holocene.csv',index=False)
# 비우점 식생 비율(홀로세): 각 시점에서 가장 많은 식생유형이 아닌 격자 비율
for mode in ['model_static','model_dynamic']:
    fr=[]
    for t in hol:
        v=rd(mode,t,'vegetation_code')[land]; vals,cnt=np.unique(v,return_counts=True); fr.append(1-cnt.max()/v.size)
    out[f'holocene_nondominant_share_{mode}']=float(np.mean(fr))
json.dump(out,open('results_facts.json','w'),indent=1,ensure_ascii=False)
print(json.dumps(out,indent=1,ensure_ascii=False)); print(g)
