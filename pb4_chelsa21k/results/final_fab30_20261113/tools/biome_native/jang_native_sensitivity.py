"""Jang et al.(2011) 검증, 원래 생물군계 기준 (혼효림 생물군계 6, 7, 9 = 혼효림, 1-4 = 활엽수림).
해석 민감도, 화분대 경계 제외, 출현 기준(격자 수와 비율)."""
import numpy as np, pandas as pd, math
D=pd.read_csv('cells_biome_pft_veg.csv.gz')
def native(b,o):
    if b in (5,8,10,11): return 0
    if b in (1,2,3,4): return 1
    if b in (6,7,9): return 2
    if b==21: return 3 if o>0 else 4
    if b in (27,28) or b<0: return 4
    return 3
D['vn']=[native(b,o) for b,o in zip(D.biome,D.optpft)]
cnt={}
for (m,t),s in D.groupby(['model','ka']):
    t=round(t,1)+0.0; valid=int((s.vn!=4).sum())
    cnt[(m,t)]={"valid":valid,**{k:int((s.vn==k).sum()) for k in range(4)}}
def times(a,b): return [round(x,1) for x in np.arange(b,a+1e-9,0.1)]
BASE=[(5.9,4.8,[1]),(4.8,3.4,[2]),(3.4,0.4,[1]),(0.3,0.0,[2])]
def evaluate(zones,rule,excl=0.0):
    out={}
    bounds=[5.9,4.8,3.4,0.39]
    for m in ['static','dynamic']:
        ok=n=0
        for a,b,exp in zones:
            for t in times(a,b):
                if excl>0 and min(abs(t-x) for x in bounds)<=excl+1e-9: continue
                c=cnt[(m,t)]; need=rule(c['valid'])
                n+=1; ok+=int(any(c[e]>=need for e in exp))
        out[m]=(ok,n)
    return out
pct=lambda f:(lambda v:max(1,math.ceil(f*v)))
rows=[]
def add(name,res):
    rows.append(dict(scenario=name,static=f'{res["static"][0]}/{res["static"][1]}',dynamic=f'{res["dynamic"][0]}/{res["dynamic"][1]}'))
add('3대 활엽수림 (본 검증)',evaluate(BASE,pct(0.01)))
add('3,400-1,300 혼효림, 이후 활엽수림 (Jang 고찰)',evaluate([(5.9,4.8,[1]),(4.8,3.4,[2]),(3.4,1.3,[2]),(1.2,0.4,[1]),(0.3,0,[2])],pct(0.01)))
add('3대 혼효림',evaluate([(5.9,4.8,[1]),(4.8,3.4,[2]),(3.4,0.4,[2]),(0.3,0,[2])],pct(0.01)))
add('3대 활엽수림 또는 혼효림',evaluate([(5.9,4.8,[1]),(4.8,3.4,[2]),(3.4,0.4,[1,2]),(0.3,0,[2])],pct(0.01)))
for e in (0.1,0.2,0.3): add(f'경계 ±{e} kyr 제외',evaluate(BASE,pct(0.01),e))
for k in (1,3,5,7,10,15,20,21,22): add(f'출현 기준 {k}개 격자',evaluate(BASE,lambda v,k=k:k))
for f in (0.01,0.02,0.03,0.04,0.05): add(f'출현 기준 {int(f*100)}%',evaluate(BASE,pct(f)))
R=pd.DataFrame(rows); R.to_csv('jang_native_sensitivity.csv',index=False,encoding='utf-8-sig'); print(R.to_string(index=False))
# 3대 동적 활엽수림(온대 낙엽활엽림) 격자 수
z=[cnt[('dynamic',t)][1] for t in times(3.4,0.4)]; print('3대 동적 활엽수림 격자',min(z),max(z))
z=[cnt[('dynamic',t)][1] for t in times(5.9,4.8)]; print('1대 동적 활엽수림 격자',min(z),max(z))
