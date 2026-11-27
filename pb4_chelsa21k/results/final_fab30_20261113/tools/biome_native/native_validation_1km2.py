"""유역 1 km² 실행: 원래 생물군계 출력 재실행의 동일성 확인과 Jang, Park 검증.
사용: python native_validation_1km2.py <재실행 outputs_CHELSA21K> <이전 1 km² outputs_CHELSA21K>
"""
import sys, math, json
import numpy as np, pandas as pd, rasterio
from pathlib import Path
P=Path(sys.argv[1]); Q=Path(sys.argv[2]); HERE=Path(__file__).resolve().parent
times=np.round(np.arange(21.0,-0.001,-0.1),1)
def rd(root,mode,t,name):
    lab=('%g'%t) if t>1e-9 else '0'
    a=rasterio.open(root/mode/f'snapshot_{lab}ka'/f'{name}.tif').read(1).astype(float); a[a<-1e3]=np.nan; return a
land=np.isfinite(rd(P,'model_dynamic',21.0,'elevation_m')); N=int(land.sum())
# 동일성
chk={}
for m in ['model_static','model_dynamic']:
    d={}
    for f in ['soil_depth_m','optpft','vegetation_code','npp','eemt']:
        d[f]=max(float(np.nanmax(np.abs(rd(P,m,t,f)[land]-rd(Q,m,t,f)[land]))) for t in times)
    chk[m]=d
print('cells',N,json.dumps(chk))
def native(b,o):
    if b in (5,8,10,11): return 0
    if b in (1,2,3,4): return 1
    if b in (6,7,9): return 2
    if b==21: return 3 if o>0 else 4
    if b in (27,28) or b<0 or not np.isfinite(b): return 4
    return 3
DEF={7:{'TBD','CON'},9:{'TBD','CON'},6:{'TBE','TBD'},5:{'CON'},8:{'CON'},10:{'CON'},11:{'BDE'},21:{'DWD'}}
def groups(b,o):
    if b==4: return {'BDE','TBD'} if o==7 else {'TBD'}
    if b==9 and o==7: return {'BDE','CON'}
    return DEF.get(b,set())
cnt={}; grp={}; share=[]
for m in ['static','dynamic']:
    for t in times:
        b=rd(P,'model_'+m,t,'biome4_native')[land]; o=rd(P,'model_'+m,t,'optpft')[land]
        bb=rd(P,'model_'+m,t,'bare_bedrock')[land]>0.5; b=np.where(bb,-1,np.nan_to_num(b,nan=-1))
        vn=np.array([native(x,y) for x,y in zip(b,o)])
        cnt[(m,t)]={'valid':int((vn!=4).sum()),**{k:int((vn==k).sum()) for k in range(4)}}
        g={k:0 for k in ['TBD','BDE','CON','TBE','GRS','DWD']}
        for x,y in zip(b,o):
            for k in groups(int(x),int(y)): g[k]+=1
        grp[(m,t)]=g
        vals,c=np.unique(b,return_counts=True); share.append(dict(model=m,ka=t,**{str(int(v)):int(k) for v,k in zip(vals,c)}))
pd.DataFrame(share).fillna(0).to_csv(HERE/'biome_native_cells_1km2.csv',index=False)
# Jang
def tl(a,b): return [round(x,1) for x in np.arange(b,a+1e-9,0.1)]
BASE=[(5.9,4.8,[1]),(4.8,3.4,[2]),(3.4,0.4,[1]),(0.3,0.0,[2])]
def ev(zones,rule,excl=0):
    r={}
    for m in ['static','dynamic']:
        ok=n=0
        for a,b,exp in zones:
            for t in tl(a,b):
                if excl and min(abs(t-x) for x in [5.9,4.8,3.4,0.39])<=excl+1e-9: continue
                c=cnt[(m,t)]; need=rule(c['valid']); n+=1; ok+=int(any(c[e]>=need for e in exp))
        r[m]=f'{ok}/{n}'
    return r
pct=lambda f:(lambda v:max(1,math.ceil(f*v)))
rows=[]
add=lambda s,r: rows.append(dict(scenario=s,**r))
add('3대 활엽수림 (본 검증)',ev(BASE,pct(0.01)))
add('3,400-1,300 혼효림, 이후 활엽수림',ev([(5.9,4.8,[1]),(4.8,3.4,[2]),(3.4,1.3,[2]),(1.2,0.4,[1]),(0.3,0,[2])],pct(0.01)))
add('3대 혼효림',ev([(5.9,4.8,[1]),(4.8,3.4,[2]),(3.4,0.4,[2]),(0.3,0,[2])],pct(0.01)))
for e in (0.1,0.2,0.3): add(f'경계 ±{e} kyr 제외',ev(BASE,pct(0.01),e))
add('출현 기준 1개 격자',ev(BASE,lambda v:1))
for f in (0.01,0.02,0.03,0.04,0.05): add(f'출현 기준 {int(f*100)}%',ev(BASE,pct(f)))
J=pd.DataFrame(rows); J.to_csv(HERE/'jang_native_sensitivity_1km2.csv',index=False,encoding='utf-8-sig'); print(J.to_string(index=False))
# Park (생물군계를 정의하는 PFT)
obs=pd.read_csv(HERE.parents[1]/'palaeo_validation'/'park_reference_scheme_obs_pct.csv',encoding='utf-8-sig').set_index('ka')
G=['TBD','BDE','CON','TBE','GRS','DWD']
pr=[]
for f in (1,0.01,0.02,0.03,0.04,0.05):
    for m in ['static','dynamic']:
        tot=dict(TP=0,FP=0,FN=0,TN=0); per={}
        for g in G:
            o=(obs[g]>=0.5).values
            mo=np.array([grp[(m,round(t,1))][g]>=(1 if f==1 else math.ceil(f*N)) for t in obs.index])
            k=dict(TP=int((o&mo).sum()),FP=int((~o&mo).sum()),FN=int((o&~mo).sum()),TN=int((~o&~mo).sum()))
            per[g]='{TP}/{FP}/{FN}/{TN}'.format(**k); [tot.__setitem__(a,tot[a]+k[a]) for a in tot]
        se=tot['TP']/(tot['TP']+tot['FN']); sp=tot['TN']/(tot['TN']+tot['FP'])
        pr.append(dict(model_rule='1개 격자' if f==1 else f'{int(f*100)}%',model=m,accuracy=round((tot['TP']+tot['TN'])/168,3),TSS=round(se+sp-1,3),**per))
PR=pd.DataFrame(pr); PR.to_csv(HERE/'park_native_1km2.csv',index=False,encoding='utf-8-sig'); print(PR.to_string(index=False))
z=[cnt[('dynamic',t)][1] for t in tl(3.4,0.4)]; print('3대 동적 활엽수림 격자',min(z),max(z),'유효 격자',cnt[('dynamic',1.0)]['valid'])
