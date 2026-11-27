"""BIOME4 원래 생물군계 코드 집계 (진단 출력만 추가한 재실행).
사용: python biome_native.py <재실행 outputs_CHELSA21K> <FINAL_STATE_CUBE.npz>
1) 재실행 결과가 최종 실행과 같은지 확인 (토심, 우점 PFT, 식생유형, NPP, EEMT)
2) 시점별 생물군계 격자 수와 시기별 비율
"""
import sys, json
import numpy as np, pandas as pd, rasterio
from pathlib import Path
P=Path(sys.argv[1]); cube=np.load(sys.argv[2])
times=np.round(cube['times_ka'],1)
NAME={1:'열대 상록림',2:'열대 반낙엽림',3:'열대 낙엽림 및 소림',4:'온대 낙엽활엽림',5:'온대 침엽수림',6:'난온대 혼효림',7:'냉량 혼효림',8:'냉량 침엽수림',9:'한랭 혼효림',10:'상록 타이가 및 산지림',11:'낙엽 타이가 및 산지림',12:'열대 사바나',13:'열대 건생관목림',14:'온대 건생관목림',15:'온대 경엽수 소림',16:'온대 활엽수 사바나',17:'개방 침엽수 소림',18:'아한대 소림지대',19:'열대 초지',20:'온대 초지',21:'사막',22:'스텝 툰드라',23:'관목 툰드라',24:'왜성관목 툰드라',25:'포복성 관목 툰드라',26:'방석식물 지의류 이끼',27:'나지',28:'빙하'}
def rd(mode,t,name):
    lab=('%g'%t) if t>1e-9 else '0'
    a=rasterio.open(P/mode/f'snapshot_{lab}ka'/f'{name}.tif').read(1).astype(float); a[a<-1e3]=np.nan; return a
land=cube['dynamic__land'][0]
# 1) 동일성
check={}
for mode in ['static','dynamic']:
    mx={}
    for k,f in [('soil_depth_m','soil_depth_m'),('optpft_node','optpft'),('vegetation_code','vegetation_code'),('npp_node','npp'),('eemt_node','eemt')]:
        d=0.0
        for i,t in enumerate(times):
            a=rd('model_'+mode,t,f)[land]; b=cube[f'{mode}__{k}'][i][land]
            d=max(d,float(np.nanmax(np.abs(a-b))))
        mx[k]=d
    check[mode]=mx
print(json.dumps(check,indent=1))
# 2) 생물군계 집계
rows=[]
for mode in ['static','dynamic']:
    for t in times:
        b=rd('model_'+mode,t,'biome4_native')[land]; bb=rd('model_'+mode,t,'bare_bedrock')[land]>0.5
        b=np.where(bb,0,b)  # 0 = 기반암 노출 격자
        vals,cnt=np.unique(b,return_counts=True)
        for v,c in zip(vals,cnt): rows.append(dict(model=mode,ka=t,biome=int(v),name=NAME.get(int(v),'기반암 노출'),cells=int(c)))
B=pd.DataFrame(rows); B.to_csv('biome_native_cells.csv',index=False,encoding='utf-8-sig')
per={'21-19 ka':(19,21),'19-11.7 ka':(11.7,19),'11.7-8.2 ka':(8.2,11.7),'8.2-4.2 ka':(4.2,8.2),'4.2-0 ka':(0,4.2)}
out=[]
for mode in ['static','dynamic']:
    for pn,(a,b) in per.items():
        s=B[(B.model==mode)&(B.ka>=a)&(B.ka<=b)]
        tot=s.cells.sum()
        g=(s.groupby('name').cells.sum()/tot*100).sort_values(ascending=False)
        out.append(dict(model=mode,period=pn,shares='; '.join(f'{k} {v:.1f}' for k,v in g.items() if v>=0.05)))
O=pd.DataFrame(out); O.to_csv('biome_native_period_shares.csv',index=False,encoding='utf-8-sig'); print(O.to_string(index=False))
# 우점 생물군계 전환 시점
for mode in ['static','dynamic']:
    prev=None; print('==',mode)
    for t in times:
        s=B[(B.model==mode)&(B.ka==t)].sort_values('cells',ascending=False)
        top=s.iloc[0]['name']
        if top!=prev: print(t, top, dict(zip(s.name,s.cells)))
        prev=top
