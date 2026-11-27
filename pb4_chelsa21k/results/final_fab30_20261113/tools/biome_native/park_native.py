"""Park et al.(2021) 검증을 원래 BIOME4 출력으로 다시 확인.
A: 본 검증 (우점 PFT, 상록 침엽수는 BIOME4 present)
B: 생물군계를 정의하는 PFT (냉량 혼효림 = PFT4+PFT6, 온대 낙엽활엽림(optpft 7, subpft 4) = PFT7+PFT4,
   사막(optpft 10) = PFT10, 냉량 침엽수림 = PFT6 ...)
C: BIOME4 present() 전부 (기후 한계와 NPP>0)
화분 쪽은 park_reference_scheme_obs_pct.csv (0.5%).
"""
import numpy as np, pandas as pd, math
obs=pd.read_csv('palaeo_validation/park_reference_scheme_obs_pct.csv',encoding='utf-8-sig').set_index('ka')
D=pd.read_csv('tools/biome_native/cells_biome_pft_veg.csv.gz')
G=['TBD','BDE','CON','TBE','GRS','DWD']; N=656; need=math.ceil(0.01*N)
DEF={7:{'TBD','CON'},9:{'TBD','CON'},6:{'TBE','TBD'},5:{'CON'},8:{'CON'},10:{'CON'},11:{'BDE'},21:{'DWD'}}
def biome_groups(b,o):
    if b==4: return {'BDE','TBD'} if o==7 else {'TBD'}
    if b==9 and o==7: return {'BDE','CON'}
    return DEF.get(b,set())
def score(model_presence):
    tot=dict(TP=0,FP=0,FN=0,TN=0); per={}
    for g in G:
        o=(obs[g]>=0.5).values; mo=np.array([model_presence[(t,g)] for t in obs.index])
        k=dict(TP=int((o&mo).sum()),FP=int((~o&mo).sum()),FN=int((o&~mo).sum()),TN=int((~o&~mo).sum()))
        per[g]='{TP}/{FP}/{FN}/{TN}'.format(**k); [tot.__setitem__(a,tot[a]+k[a]) for a in tot]
    se=tot['TP']/(tot['TP']+tot['FN']); sp=tot['TN']/(tot['TN']+tot['FP'])
    return dict(accuracy=round((tot['TP']+tot['TN'])/168,3),TSS=round(se+sp-1,3),**per)
rows=[]
for m in ['static','dynamic']:
    pc=pd.read_csv(f'reference_run/model_{m}/pft_model_cells_per_output_time.csv',encoding='utf-8-sig').set_index('ka_bp')
    pmap={'TBD':[4],'BDE':[7],'CON':[5,6],'TBE':[3],'GRS':[8],'DWD':[10]}
    A={};B={};C={}
    for t in obs.index:
        s=D[(D.model==m)&np.isclose(D.ka,t)]
        cnt={g:0 for g in G}
        for b,o in zip(s.biome,s.optpft):
            for g in biome_groups(b,o): cnt[g]+=1
        for g in G:
            row=pc.loc[round(t,1)]
            A[(t,g)]=(max(row[f'potential_p{p:02d}'] for p in pmap[g]) if g=='CON' else max(row[f'optpft_p{p:02d}'] for p in pmap[g]))>=need
            B[(t,g)]=cnt[g]>=need
            C[(t,g)]=max(row[f'potential_p{p:02d}'] for p in pmap[g])>=need
    for name,mp in [('A 본 검증',A),('B 생물군계 정의 PFT',B),('C BIOME4 present 전부',C)]:
        rows.append(dict(case=name,model=m,**score(mp)))
R=pd.DataFrame(rows).sort_values(['case','model']); R.to_csv('tools/biome_native/park_native.csv',index=False,encoding='utf-8-sig'); print(R.to_string(index=False))
