"""Jang et al.(2011) 검증: 51% 규칙 적용(본 검증)과 원래 생물군계 그대로(혼효림 생물군계 = 혼효림) 비교."""
import numpy as np, pandas as pd
D=pd.read_csv('cells_biome_pft_veg.csv.gz')
def native(b,o):
    if b in (5,8,10,11): return 0
    if b in (1,2,3,4): return 1
    if b in (6,7,9): return 2
    if b==21: return 3 if o>0 else 4
    if b in (27,28) or b<0: return 4
    return 3
D['veg_native']=[native(b,o) for b,o in zip(D.biome,D.optpft)]
zones=[('1대',5.9,4.8,1,12),('2대',4.8,3.4,2,15),('3대',3.4,0.4,1,31),('4대',0.3,0.0,2,4)]
rows=[]
for col in ['veg','veg_native']:
  for frac in [0.01,0.02,0.03,0.05]:
    for m in ['static','dynamic']:
        tot=0; det={}
        for z,a,b,exp,n in zones:
            ok=0
            for t in np.round(np.arange(b,a+1e-9,0.1),1):
                s=D[(D.model==m)&(np.isclose(D.ka,t))]
                valid=(s[col]!=4).sum(); need=int(np.ceil(frac*valid))
                ok+= int(((s[col]==exp).sum())>=max(need,1))
            det[z]=f'{ok}/{n}'; tot+=ok
        rows.append(dict(classes='51% 규칙' if col=='veg' else '원래 생물군계',threshold=frac,model=m,total=tot,**det))
R=pd.DataFrame(rows); R.to_csv('jang_native_vs_rule.csv',index=False,encoding='utf-8-sig'); print(R.to_string(index=False))
