import rasterio, numpy as np, heapq, json, sys
from rasterio.warp import reproject, Resampling
from rasterio.features import shapes
from affine import Affine
name, ox, oy, outdir = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
cur='/home/claude/fin/x/PB4Studio_v6.6.3_CHELSA21K/embedded_inputs/yongneup_exact20m/'
with rasterio.open(cur+'dem_20m_exact.tif') as s: T0=s.transform; crs=s.crs; prof=s.profile
RES=float(sys.argv[6]) if len(sys.argv)>6 else T0.a
dx,dy=RES,-RES
# window 2 km x 2 km around core aligned to current grid
cx,cy=123245.19,624269.79
c0=int(np.floor((cx-1200-T0.c)/dx)); r0=int(np.floor((T0.f-(cy+1200))/(-dy)))
W=int(2400/dx); H=int(2400/(-dy))
T=Affine(dx,0,T0.c+c0*dx,0,dy,T0.f+r0*dy)
z=np.full((H,W),np.nan)
with rasterio.open('/home/claude/dem_yn/dem_yn.tif') as s:
    reproject(rasterio.band(s,1),z,dst_transform=T,dst_crs=crs,resampling=Resampling.bilinear,src_nodata=-9999,dst_nodata=np.nan)
m=np.isfinite(z); ny,nx=z.shape
N8=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
F=np.full(z.shape,np.nan); done=np.zeros(z.shape,bool); pq=[]
for i in range(ny):
    for j in range(nx):
        if m[i,j] and (i in (0,ny-1) or j in (0,nx-1) or any(not m[i+a,j+b] for a,b in N8 if 0<=i+a<ny and 0<=j+b<nx)):
            F[i,j]=z[i,j]; done[i,j]=True; heapq.heappush(pq,(z[i,j],i,j))
while pq:
    e,i,j=heapq.heappop(pq)
    for a,b in N8:
        p,q=i+a,j+b
        if 0<=p<ny and 0<=q<nx and m[p,q] and not done[p,q]:
            done[p,q]=True; F[p,q]=max(z[p,q],e+1e-4); heapq.heappush(pq,(F[p,q],p,q))
rec=-np.ones(z.shape,dtype=int)
for i in range(ny):
    for j in range(nx):
        if not m[i,j]: continue
        best=-1;bs=0
        for a,b in N8:
            p,q=i+a,j+b
            if 0<=p<ny and 0<=q<nx and m[p,q]:
                sl=(F[i,j]-F[p,q])/np.hypot(a,b)
                if sl>bs: bs=sl;best=p*nx+q
        rec[i,j]=best
order=np.argsort(-np.nan_to_num(F,nan=-1e9).ravel()); acc=np.where(m,1.0,0.0).ravel(); rr=rec.ravel()
for k in order:
    if rr[k]>=0: acc[rr[k]]+=acc[k]
acc=acc.reshape(z.shape)
oi=int((T.f-oy)/(-dy)); oj=int((ox-T.c)/dx)
w=int(sys.argv[5]) if len(sys.argv)>5 else 3; sub=acc[oi-w:oi+w+1,oj-w:oj+w+1]; k=np.unravel_index(np.argmax(sub),sub.shape); oi,oj=oi-w+k[0],oj-w+k[1]
# catchment
basin=np.zeros(z.shape,bool); basin[oi,oj]=True
up=[[] for _ in range(ny*nx)]
for k2 in range(ny*nx):
    if rr[k2]>=0: up[rr[k2]].append(k2)
st=[oi*nx+oj]
while st:
    k2=st.pop()
    for u in up[k2]:
        ui,uj=divmod(u,nx)
        if not basin[ui,uj]: basin[ui,uj]=True; st.append(u)
rows=np.where(basin.any(1))[0]; cols=np.where(basin.any(0))[0]
r1,r2,c1,c2=rows.min()-1,rows.max()+2,cols.min()-1,cols.max()+2
zc=z[r1:r2,c1:c2]; bc=basin[r1:r2,c1:c2]; Tc=Affine(dx,0,T.c+c1*dx,0,dy,T.f+r1*dy)
# soil depth: current raster extended by nearest (1 km SoilGrids is near-uniform here)
with rasterio.open(cur+'soil_depth_20m_exact_m.tif') as s:
    hs=np.full(zc.shape,np.nan); reproject(rasterio.band(s,1),hs,dst_transform=Tc,dst_crs=crs,resampling=Resampling.nearest,src_nodata=np.nan,dst_nodata=np.nan)
fillv=1.94
hs=np.where(np.isfinite(hs),hs,fillv)
tex=np.full(zc.shape,2.0)
zc=np.where(np.isfinite(zc),zc,np.nan)
import os; os.makedirs(outdir,exist_ok=True)
p=dict(driver='GTiff',dtype='float32',nodata=np.nan,width=zc.shape[1],height=zc.shape[0],count=1,crs=crs,transform=Tc)
for fn,arr in [('dem_20m_exact.tif',zc),('soil_depth_20m_exact_m.tif',hs),('soil_texture_20m_exact.tif',tex)]:
    with rasterio.open(os.path.join(outdir,fn),'w',**p) as d: d.write(arr.astype('float32'),1)
geoms=[g for g,v in shapes(bc.astype('uint8'),mask=bc,transform=Tc) if v==1]
json.dump({"type":"FeatureCollection","name":name,"crs":{"type":"name","properties":{"name":"EPSG:5187"}},"features":[{"type":"Feature","properties":{},"geometry":g} for g in geoms]},open(os.path.join(outdir,'basin_exact20m.geojson'),'w'))
oi2,oj2=oi-r1,oj-c1; x,y=rasterio.transform.xy(Tc,oi2,oj2)
json.dump({"type":"FeatureCollection","name":name+"_outlet","crs":{"type":"name","properties":{"name":"EPSG:5187"}},"features":[{"type":"Feature","properties":{"boundary":"OPEN_FREE","row":int(oi2),"col":int(oj2)},"geometry":{"type":"Point","coordinates":[x,y]}}]},open(os.path.join(outdir,'outlet_open_free_exact20m.geojson'),'w'))
# pits/peaks inside basin
pits=peaks=0
for i in range(bc.shape[0]):
    for j in range(bc.shape[1]):
        if not bc[i,j]: continue
        nb=[zc[a,b] for a,b in [(i-1,j),(i+1,j),(i,j-1),(i,j+1)] if bc[a,b]]
        if len(nb)==4: pits+=zc[i,j]<min(nb); peaks+=zc[i,j]>max(nb)
print(name,'cells',int(bc.sum()),'area ha %.1f'%(bc.sum()*dx*dx/1e4),'shape',zc.shape,'outlet',(oi2,oj2),'elev %.0f-%.0f'%(np.nanmin(zc[bc]),np.nanmax(zc[bc])),'pits/peaks',pits,peaks)
print(json.dumps({"shape":list(zc.shape),"active_cells":int(bc.sum()),"outlet_row_col":[int(oi2),int(oj2)]}))
