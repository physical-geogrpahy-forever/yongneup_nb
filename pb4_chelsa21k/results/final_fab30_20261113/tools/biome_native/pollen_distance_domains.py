"""화분 공급원 거리 기준으로 비교 범위를 정한 검증 (원래 생물군계 기준).
두 유역(59 ha, 1 km²) 각각에 대해
 1) 코어(Jang et al., 2011)로부터의 격자 거리 분포, 용늪 자체의 상류 기여면적
 2) 코어 반경 R(100-1000 m) 안의 격자만으로 판정한 Jang, Park 결과
 3) 거리 가중(1/d, 1/d², d 최소 50 m) 판정
사용: python pollen_distance_domains.py <59ha outputs> <1km2 outputs>
"""
import sys, math, heapq
import numpy as np, pandas as pd, rasterio
from pathlib import Path
HERE=Path(__file__).resolve().parent
from pyproj import Transformer
_tr=Transformer.from_crs(4326,5187,always_xy=True)
# 코어 좌표: Jang et al.(2011) 38°12′57.4″N, 128°7′30.2″E(원문 경도 120°는 오기); Park et al.(2021) YN-C 38°12′54.40″N, 128°7′25.1″E, 1,189 m
JANG=_tr.transform(128+7/60+30.2/3600,38+12/60+57.4/3600)
YNC=_tr.transform(128+7/60+25.1/3600,38+12/60+54.40/3600)
OLD=(123245.19,624269.79)  # 이전 기준점(검증 자료의 용늪 지점)
CORE_SET={'old':(OLD,OLD),'cores':(JANG,YNC)}
CX,CY=OLD
obs=pd.read_csv(HERE.parents[1]/'palaeo_validation'/'park_reference_scheme_obs_pct.csv',encoding='utf-8-sig').set_index('ka')
G=['TBD','BDE','CON','TBE','GRS','DWD']
DEF={7:{'TBD','CON'},9:{'TBD','CON'},6:{'TBE','TBD'},5:{'CON'},8:{'CON'},10:{'CON'},11:{'BDE'},21:{'DWD'}}
def groups(b,o):
    if b==4: return {'BDE','TBD'} if o==7 else {'TBD'}
    if b==9 and o==7: return {'BDE','CON'}
    return DEF.get(b,set())
def native(b,o):
    if b in (5,8,10,11): return 0
    if b in (1,2,3,4): return 1
    if b in (6,7,9): return 2
    if b==21: return 3 if o>0 else 4
    if b in (27,28) or b<0: return 4
    return 3
N8=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
def upstream_area(z,ci,cj):
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
    d={}
    for i in range(ny):
        for j in range(nx):
            if not np.isfinite(F[i,j]): continue
            bs=0; best=None
            for a,b in N8:
                p,q=i+a,j+b
                if 0<=p<ny and 0<=q<nx and np.isfinite(F[p,q]):
                    s=(F[i,j]-F[p,q])/math.hypot(a,b)
                    if s>bs: bs,best=s,(p,q)
            d[(i,j)]=best
    up={(ci,cj)}; changed=True
    while changed:
        changed=False
        for k,v in d.items():
            if v in up and k not in up: up.add(k); changed=True
    return len(up)
def load(P):
    P=Path(P); times=np.round(np.arange(21.0,-0.001,-0.1),1)
    def rd(mode,t,name):
        lab=('%g'%t) if t>1e-9 else '0'
        s=rasterio.open(P/mode/f'snapshot_{lab}ka'/f'{name}.tif'); a=s.read(1).astype(float); a[a<-1e3]=np.nan; return a,s.transform
    z,T=rd('model_dynamic',21.0,'elevation_m'); land=np.isfinite(z)
    rr,cc=np.nonzero(land); xs,ys=rasterio.transform.xy(T,rr,cc); xs=np.array(xs); ys=np.array(ys)
    dist=np.hypot(xs-CX,ys-CY)
    dJ=np.hypot(xs-JANG[0],ys-JANG[1]); dP=np.hypot(xs-YNC[0],ys-YNC[1])
    ci,cj=rasterio.transform.rowcol(T,CX,CY)
    inside={}
    for nm,(x0,y0) in [('Jang',JANG),('YN-C',YNC)]:
        i,j=rasterio.transform.rowcol(T,x0,y0); inside[nm]=(bool(0<=i<z.shape[0] and 0<=j<z.shape[1] and land[i,j]), float(z[i,j]) if 0<=i<z.shape[0] and 0<=j<z.shape[1] else float('nan'))
    data={}
    for m in ['static','dynamic']:
        for t in times:
            if not (t<=5.9): continue
            b=np.nan_to_num(rd('model_'+m,t,'biome4_native')[0][land],nan=-1); o=rd('model_'+m,t,'optpft')[0][land]
            bb=rd('model_'+m,t,'bare_bedrock')[0][land]>0.5; b=np.where(bb,-1,b).astype(int); o=np.nan_to_num(o,nan=0).astype(int)
            data[(m,t)]=(b,o)
    return dict(z=z[land],dist=dist,dJ=dJ,dP=dP,inside=inside,data=data,up=upstream_area(z,ci,cj),core_rc=(ci,cj))
def tl(a,b): return [round(x,1) for x in np.arange(b,a+1e-9,0.1)]
ZONES=[(5.9,4.8,1),(4.8,3.4,2),(3.4,0.4,1),(0.3,0.0,2)]
def evaluate(B,w,thr,wP=None):
    """w: 격자 가중치(0이면 제외). thr: 가중 비율 기준(%). 반환 Jang 맞은 수, Park 정확도와 TSS"""
    res={}
    for m in ['static','dynamic']:
        ok=0
        for a,b,exp in ZONES:
            for t in tl(a,b):
                bb,oo=B['data'][(m,t)]; vn=np.array([native(x,y) for x,y in zip(bb,oo)]); veg=(vn!=4)&(w>0)
                share=100*w[veg&(vn==exp)].sum()/w[veg].sum()
                ok+=int(share>=thr)
        tot=dict(TP=0,FP=0,FN=0,TN=0)
        wp=w if wP is None else wP
        for t in obs.index:
            bb,oo=B['data'][(m,round(t,1))]; vn=np.array([native(x,y) for x,y in zip(bb,oo)]); veg=(vn!=4)&(wp>0)
            gs=[groups(x,y) for x,y in zip(bb,oo)]
            for g in G:
                mask=np.array([g in s for s in gs])
                mp=100*wp[veg&mask].sum()/wp[veg].sum()>=thr; op=obs.loc[t,g]>=0.5
                tot['TP' if (mp and op) else 'FP' if mp else 'FN' if op else 'TN']+=1
        se=tot['TP']/(tot['TP']+tot['FN']); sp=tot['TN']/(tot['TN']+tot['FP'])
        res[m]=(ok,round((tot['TP']+tot['TN'])/168,3),round(se+sp-1,3))
    return res
P59,P1k=sys.argv[1],sys.argv[2]
geo=[];rows=[]
for name,P in [('59 ha',P59),('1 km²',P1k)]:
    B=load(P); n=len(B['dist'])
    for core,dj,dp in [('Jang 코어 / YN-C 코어',B['dJ'],B['dP']),('이전 기준점',B['dist'],B['dist'])]:
        geo.append(dict(basin=name,reference=core,cells=n,
            Jang_inside=B['inside']['Jang'],YNC_inside=B['inside']['YN-C'],
            dJ_median=round(float(np.median(dj))),dJ_max=round(float(dj.max())),dP_median=round(float(np.median(dp))),dP_max=round(float(dp.max())),
            Jwithin300=int((dj<=300).sum()),Jwithin400=int((dj<=400).sum()),Pwithin300=int((dp<=300).sum()),Pwithin400=int((dp<=400).sum())))
        for R in (100,200,300,400,500,700,1000,99999):
            wj=(dj<=R).astype(float); wp=(dp<=R).astype(float)
            for thr in (1,2):
                r=evaluate(B,wj,thr,wp); rows.append(dict(basin=name,reference=core,domain=('유역 전체' if R==99999 else f'코어 {R} m 이내'),cells_J=int(wj.sum()),cells_P=int(wp.sum()),threshold=f'{thr}%',
                    static_jang=r['static'][0],dynamic_jang=r['dynamic'][0],static_park=r['static'][1],dynamic_park=r['dynamic'][1],static_TSS=r['static'][2],dynamic_TSS=r['dynamic'][2]))
        for pw in (1,2):
            wj=np.maximum(dj,50.0)**-pw; wp=np.maximum(dp,50.0)**-pw
            for thr in (1,2):
                r=evaluate(B,wj,thr,wp); rows.append(dict(basin=name,reference=core,domain=f'거리 가중 1/d^{pw}',cells_J=n,cells_P=n,threshold=f'{thr}%',
                    static_jang=r['static'][0],dynamic_jang=r['dynamic'][0],static_park=r['static'][1],dynamic_park=r['dynamic'][1],static_TSS=r['static'][2],dynamic_TSS=r['dynamic'][2]))
GE=pd.DataFrame(geo); GE.to_csv(HERE/'basin_geometry_vs_core.csv',index=False,encoding='utf-8-sig'); print(GE.T.to_string())
R=pd.DataFrame(rows); R.to_csv(HERE/'pollen_distance_domains.csv',index=False,encoding='utf-8-sig')
print(R[R.reference!='이전 기준점'].to_string(index=False))
print('JANG',JANG,'YNC',YNC)
