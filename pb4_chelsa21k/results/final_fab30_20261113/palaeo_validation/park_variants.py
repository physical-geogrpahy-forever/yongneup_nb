"""Park et al. (2021) 검증의 처리 선택별 정확도(버드나무속 포함 여부, 화분 기준값).
사용법: python park_variants.py <패키지 embedded_data 폴더>
V0 현행: 그룹 기준(TBD 2, BDE 2, CON 1, TBE 5, GRS 2, DWD 5), BDE = 자작나무속 + 버드나무속
V3: 버드나무속 제외, 현지 분류군 그룹(TBD, BDE, CON, GRS) 0.5%(Prentice et al., 1996), TBE와 DWD 5%
"""
import sys
from pathlib import Path
import pandas as pd,numpy as np,math
E=sys.argv[1].rstrip('/')+'/'
HERE=Path(__file__).resolve().parent
R=str(HERE.parent/'reference_run')+'/'
c=pd.read_csv(E+'yongneup_park2021_ync_pollen_counts.csv',encoding='utf-8-sig').merge(pd.read_csv(E+'pft_taxon_map_yongneup.csv',encoding='utf-8-sig')[['taxon_code','pft_group']],on='taxon_code')
c=c[c.park2021_group.isin(['A','B'])&~c.pft_group.isin(['EXCLUDE_LOCAL','EXCLUDE_NONTERRESTRIAL'])].copy()
c['ka']=c.age_cal_bp/1000
T=np.round(np.arange(0.5,3.21,0.1),1)
G=['TBD','BDE','CON','TBE','GRS','DWD']
model={m:pd.read_csv(R+f'model_{m}/pft_validation_per_output_time.csv',encoding='utf-8-sig').set_index(['ka_bp','pft_group']).model_cells for m in ('static','dynamic')}
def obs_pct(salix_in_bde):
    rows=[]
    for t in T:
        w=c[(c.ka>=t-0.05)&(c.ka<t+0.05)]; s=w['count'].sum()
        g=w.groupby('pft_group')['count'].sum()
        if not salix_in_bde: g['BDE']=w[w.taxon_code=='Bet']['count'].sum()
        rows.append({'ka':t,**{k:100*g.get(k,0)/s for k in G}})
    return pd.DataFrame(rows).set_index('ka')
def score(p,thr):
    out={}
    for m in model:
        tp=fp=fn=tn=0; per={}
        for g in G:
            o=p[g]>=thr[g]; mo=np.array([model[m][(t,g)]>=7 for t in p.index])
            a,b,cc,d=(o&mo).sum(),(~o&mo).sum(),(o&~mo).sum(),(~o&~mo).sum()
            tp+=a;fp+=b;fn+=cc;tn+=d; per[g]=f'{a}/{b}/{cc}/{d}'
        se=tp/(tp+fn); sp=tn/(tn+fp)
        out[m]=dict(acc=(tp+tn)/168,TSS=se+sp-1,TP=tp,FP=fp,FN=fn,TN=tn,**per)
    return out
cur={'TBD':2,'BDE':2,'CON':1,'TBE':5,'GRS':2,'DWD':5}
loc={'TBD':0.5,'BDE':0.5,'CON':0.5,'TBE':5,'GRS':0.5,'DWD':5}
V={'V0 현행':(True,cur),'V1 버드나무 제외':(False,cur),'V2 버드나무 포함, 0.5%':(True,loc),'V3 버드나무 제외, 0.5%':(False,loc)}
rows=[]
for k,(sal,thr) in V.items():
    s=score(obs_pct(sal),thr)
    for m,v in s.items(): rows.append({'variant':k,'model':m,**v})
r=pd.DataFrame(rows); pd.set_option('display.width',250); print(r.round(3).to_string(index=False))
r.round(3).to_csv(HERE/'park_variants.csv',index=False,encoding='utf-8-sig')
p=obs_pct(False); print('Betula-only % min/max',p.BDE.min().round(2),p.BDE.max().round(2)); print('GRS min',p.GRS.min().round(2),'CON min',p.CON.min().round(2),'TBE max',p.TBE.max().round(2),'DWD max',p.DWD.max().round(2))
print('windows CON<1:',list(p.index[p.CON<1]),'CON<0.5:',list(p.index[p.CON<0.5]),'GRS<2:',list(p.index[p.GRS<2]),'GRS<0.5:',list(p.index[p.GRS<0.5]))
