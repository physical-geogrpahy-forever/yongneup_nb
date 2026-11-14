"""H2: 얇은 토양 패치가 습지 화분에 줄 수 있는 최대 신호와 계수 오차 비교."""
import pandas as pd,numpy as np,math
from scipy.stats import beta
S='/home/claude/sc07/PB4Studio_v6.6.3_CHELSA21K/outputs_CHELSA21K/'
CX,CY=123245.19,624269.79; RB=math.sqrt(7490/math.pi); n,Cz,g=0.25,0.12,0.125
bco=lambda vg,u:4*vg/(n*u*math.sqrt(math.pi)*Cz)
sub=np.linspace(-15+1.5,15-1.5,10); SX,SY=np.meshgrid(sub,sub); SX,SY=SX.ravel(),SY.ravel()
def cellw(x,y,bb):  # integrate Prentice density over 3 m subcells
    d=np.hypot(x[:,None]+SX-CX,y[:,None]+SY-CY)
    dens=np.where(d>RB,bb*g*d**(g-1)*np.exp(-bb*d**g)/(2*np.pi*d),0.0)
    return (dens*9.0).sum(1)
def total(bb): return math.exp(-bb*RB**g)
o=pd.read_csv(S+'model_dynamic/pft_validation_per_output_time.csv',encoding='utf-8-sig')
o['k']=np.rint(o.obs_pct*o.terrestrial_sum/100).astype(int)
Bk=o[o.pft_group=='BDE'].set_index('ka_bp')
# upper bound: patch fully Betula with highest RPP (12.5, vg 0.024); rest of landscape lowest-RPP tree (Carpinus 2.106, vg 0.042); slowest wind 2 m/s
cases={'upper':(12.5,0.024,2.106,0.042,2.0),'central':(2.42,0.024,5.83,0.035,3.0)}
rows=[]
for ka in sorted(Bk.index):
    st=pd.read_csv(S+f'model_static/snapshot_{ka:g}ka/cell_values.csv',encoding='utf-8-sig')
    dy=pd.read_csv(S+f'model_dynamic/snapshot_{ka:g}ka/cell_values.csv',encoding='utf-8-sig')
    patch=((dy.optpft.round()==7)&(st.optpft.round()!=7)).values
    x,y=dy.x.values[patch],dy.y.values[patch]
    k,N=int(Bk.loc[ka,'k']),int(Bk.loc[ka,'terrestrial_sum'])
    lo,hi=beta.ppf(.025,k,N-k+1),beta.ppf(.975,k+1,N-k)
    r=dict(ka=ka,patch_cells=int(patch.sum()),betula_obs_pct=100*k/N,ci_lo=100*lo,ci_hi=100*hi,ci_halfwidth=50*(hi-lo),n_sum=N)
    for lab,(rB,vB,rT,vT,u) in cases.items():
        bB,bT=bco(vB,u),bco(vT,u)
        wB=cellw(x,y,bB).sum(); wTp=cellw(x,y,bT).sum()
        pb=rB*wB; pt=rT*(total(bT)-wTp)
        r[f'delta_pct_{lab}']=100*pb/(pb+pt)
        r[f'patch_share_of_betula_loading_{lab}']=wB/total(bB)
    rows.append(r)
d=pd.DataFrame(rows); d.to_csv('h2_patch_signal.csv',index=False)
print(d.round(3).to_string(index=False))
kB,NB=int(Bk.k.sum()),int(Bk.terrestrial_sum.sum())
lo,hi=beta.ppf(.025,kB,NB-kB+1),beta.ppf(.975,kB+1,NB-kB)
print('pooled Betula %.2f%% CI %.2f-%.2f halfwidth %.2f'%(100*kB/NB,100*lo,100*hi,50*(hi-lo)))
print('delta upper mean %.3f max %.3f | central mean %.3f'%(d.delta_pct_upper.mean(),d.delta_pct_upper.max(),d.delta_pct_central.mean()))
print('windows with delta_upper > CI halfwidth:',(d.delta_pct_upper>d.ci_halfwidth).sum(),'/',len(d))
print('windows with delta_central > CI halfwidth:',(d.delta_pct_central>d.ci_halfwidth).sum())
