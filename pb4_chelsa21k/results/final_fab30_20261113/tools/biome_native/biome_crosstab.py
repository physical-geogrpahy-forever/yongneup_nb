"""생물군계 x 우점 PFT x 검증 식생유형 교차표와 혼효림 51% 규칙의 활엽수 비율."""
import sys, numpy as np, pandas as pd, rasterio
from pathlib import Path
P=Path(sys.argv[1]); cube=np.load(sys.argv[2]); times=np.round(cube['times_ka'],1); land=cube['dynamic__land'][0]
def rd(mode,t,name):
    lab=('%g'%t) if t>1e-9 else '0'
    a=rasterio.open(P/mode/f'snapshot_{lab}ka'/f'{name}.tif').read(1).astype(float); a[a<-1e3]=np.nan; return a
rows=[]
for mode in ['static','dynamic']:
    for t in times:
        b=rd('model_'+mode,t,'biome4_native')[land]; o=rd('model_'+mode,t,'optpft')[land]; v=rd('model_'+mode,t,'vegetation_code')[land]
        br=np.nanmax(np.stack([rd('model_'+mode,t,f'pft0{p}_npp')[land] for p in (2,3,4)]),0)
        co=np.nanmax(np.stack([rd('model_'+mode,t,f'pft0{p}_npp')[land] for p in (5,6,7)]),0)
        share=br/(br+co)
        H=rd('model_'+mode,t,'soil_depth_m')[land]
        for i in range(land.sum()):
            rows.append((mode,t,int(b[i]) if np.isfinite(b[i]) else -1,int(o[i]),int(v[i]),share[i],H[i]))
D=pd.DataFrame(rows,columns=['model','ka','biome','optpft','veg','broad_share','H'])
D.to_csv('cells_biome_pft_veg.csv.gz',index=False,compression='gzip')
hol=D[D.ka<=11.7]
print(pd.crosstab([hol.model,hol.biome,hol.optpft],hol.veg))
z3=D[(D.ka<=3.4)&(D.ka>=0.4)]
print('zone3 broadleaf cells by biome/pft:'); print(pd.crosstab([z3.model,z3.biome,z3.optpft],z3.veg))
print('zone3 cool mixed broad_share:'); print(z3[z3.biome==7].groupby('model').broad_share.describe())
z1=D[(D.ka<=5.9)&(D.ka>=4.8)]; print('zone1 cool mixed broad_share'); print(z1[z1.biome==7].groupby('model').broad_share.describe())
z2=D[(D.ka<4.8)&(D.ka>3.4)]; print('zone2 cool mixed broad_share'); print(z2[z2.biome==7].groupby('model').broad_share.describe())
b4=D[(D.biome==4)&(D.ka<=11.7)]; print('temperate deciduous biome cells H', b4.groupby('model').H.describe())
