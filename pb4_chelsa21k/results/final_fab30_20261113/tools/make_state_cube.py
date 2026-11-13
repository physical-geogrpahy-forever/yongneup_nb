import numpy as np, rasterio, json, sys, os
out=sys.argv[1]; P=sys.argv[2]   # outputs_CHELSA21K dir
times=np.round(np.arange(21.0,-0.001,-0.1),1)
cube={'times_ka':times}
for mode,sub in [('static','model_static'),('dynamic','model_dynamic')]:
    arrs={k:[] for k in ['firedays_node','optpft_node','soil_depth_m','vegetation_code','npp_node','eemt_node']}
    land=None
    for t in times:
        lab=('%g'%abs(t)) if abs(t)>1e-9 else '0'
        d=os.path.join(P,sub,f'snapshot_{lab}ka')
        for k,f in [('firedays_node','firedays'),('optpft_node','optpft'),('soil_depth_m','soil_depth_m'),('vegetation_code','vegetation_code'),('npp_node','npp'),('eemt_node','eemt')]:
            with rasterio.open(os.path.join(d,f+'.tif')) as s:
                a=s.read(1).astype('float32'); a[a<-1e3]=np.nan; arrs[k].append(a)
        if land is None:
            with rasterio.open(os.path.join(d,'soil_depth_m.tif')) as s: hh=s.read(1)
            land=np.isfinite(hh)&(hh>-1e3)
    cube[f'{mode}__land']=np.repeat(land[None],len(times),0)
    for k,v in arrs.items(): cube[f'{mode}__{k}']=np.stack(v)
np.savez_compressed(out,**cube); print('saved',out,{k:v.shape for k,v in cube.items() if k.endswith('firedays_node')})
