import numpy as np, subprocess, pandas as pd, json
DIM=np.array([31,28,31,30,31,30,31,31,30,31,30,31]); E=np.cumsum(np.r_[0,DIM])
def run(cases):
    inp='\n'.join(' '.join(f'{x:.6f}' for x in list(T)+list(P)) for T,P in cases)+'\n'
    out=subprocess.run(['./drv'],input=inp,capture_output=True,text=True).stdout.split('\n')
    assert not any('MISMATCH' in l for l in out)
    res=[]; k=0
    for _ in cases:
        pk=[float(x) for x in out[k].split()]; arr=[np.array(out[k+j].split(),float) for j in range(1,5)]; k+=5
        dt,dpin,dp,dm=arr
        drain=dpin/(365/12)
        Lm=np.array([ (dp[E[i]:E[i+1]]+dm[E[i]:E[i+1]]).sum() for i in range(12)])
        Rm=np.array([dp[E[i]:E[i+1]].sum() for i in range(12)]); Mm=np.array([dm[E[i]:E[i+1]].sum() for i in range(12)])
        Pm_int=np.array([drain[E[i]:E[i+1]].sum() for i in range(12)])
        Tmin_d=np.array([dt[E[i]:E[i+1]].min() for i in range(12)])
        res.append(dict(pack1=pk[0],pack2=pk[1],dt=dt,drain=drain,dp=dp,dm=dm,L=Lm,R=Rm,M=Mm,Pint=Pm_int))
    return res
