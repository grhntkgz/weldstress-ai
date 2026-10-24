from common_e3 import *
import numpy as np
from scipy.spatial import cKDTree
_CACHE={}
def single_geometry(xyz,tri,source_ids=None):
 # All arguments describe the observed face only; the API accepts no hidden face or full-object descriptor.
 x=np.asarray(xyz,dtype='f8');tri=np.asarray(tri,dtype='i8');n=len(x);cross=np.cross(x[tri[:,1]]-x[tri[:,0]],x[tri[:,2]]-x[tri[:,0]]);aa=np.linalg.norm(cross,axis=1)/2;assert (aa>0).all()
 area=np.zeros(n);normal=np.zeros_like(x)
 for j in range(3):np.add.at(area,tri[:,j],aa/3);np.add.at(normal,tri[:,j],cross/2)
 assert (area>0).all();normal/=np.linalg.norm(normal,axis=1)[:,None];center=np.sum(x*area[:,None],axis=0)/sum(area);p=(x-center)/60;dims=np.ptp(x,axis=0)/60
 order=np.lexsort((x[:,2],x[:,1],x[:,0]));tree=cKDTree(x[order]);nb=order[tree.query(x,k=16,workers=2)[1]];smooth=x[:,2]-x[nb,2].mean(1);nvar=np.linalg.norm(normal-normal[nb].mean(1),axis=1)
 features=np.c_[p,normal,np.tile(dims,(n,1)),np.tile([1.,0,0],(n,1)),np.zeros(n),smooth,nvar,np.log1p(area),np.tile([np.std(normal[:,0]),np.std(normal[:,1]),np.ptp(x[:,2])/60],(n,1))].astype('f4');assert features.shape==(n,19)
 cdf=np.cumsum(area[order])/sum(area);context=order[np.searchsorted(cdf,(np.arange(4096)+.5)/4096).clip(0,n-1)]
 g=dict(xyz=x,triangles=tri.astype('i4'),area=area,normal=normal,center=center,features=features,neighbors=nb.astype('i4'),context=context.astype('i4'),source_ids=np.arange(n,dtype='i8') if source_ids is None else np.asarray(source_ids,dtype='i8'))
 for radius in [1,3]:
  theta=2*np.pi*np.arange(16)/16;offset=np.c_[np.cos(theta),np.sin(theta),np.zeros(16)]*radius;out=np.empty((n,16),dtype='i4')
  for j in range(0,n,4096):out[j:j+4096]=order[tree.query((x[j:j+4096,None,:]+offset).reshape(-1,3),k=1,workers=2)[1].reshape(-1,16)]
  g['neighbors_'+str(radius)+'mm']=out
 return g
class DualFeatureView:
 def __init__(self,base,depth):self.base=base;self.depth=depth;self.shape=base.shape
 def __getitem__(self,key):
  rr,cc=(key[0],key[1]) if isinstance(key,tuple) else (key,None);v=np.array(self.base[rr],copy=True);v[...,18]=self.depth[rr]/19;return v if cc is None else v[...,cc]
def loadgeom(sid,exp='S1'):
 assert sid in read(R/'00_protocol/QUARANTINE.json')['development_IDs']
 key=(sid,exp=='D1')
 if key in _CACHE:return _CACHE[key]
 if exp=='D1':
  g={p.stem:np.load(p,mmap_mode='r') for p in (R6/'01_feature_engineering'/sid).glob('*.npy')}
  for name in ['neighbors_1mm','neighbors_3mm']:g[name]=np.load(R7/'02_geometry_resolution_audit'/sid/(name+'.npy'),mmap_mode='r')
  depth=np.load(R7/'02_geometry_resolution_audit'/sid/'paired_surface_separation_mm.npy',mmap_mode='r');g['features']=DualFeatureView(g['features'],depth)
 else:g={p.stem:np.load(p,mmap_mode='r') for p in (R/'02_geometry/single'/sid).glob('*.npy')}
 _CACHE[key]=g;return g
def common_labels(sid):
 p=R/'03_targets'/sid;return np.load(p/'K.npy',mmap_mode='r'),np.load(p/'valid.npy',mmap_mode='r')
def quantile(v,w,q):
 ix=np.argsort(v,kind='stable');return float(v[ix[min(np.searchsorted(np.cumsum(w[ix])/sum(w),q),len(v)-1)]])
def queries(sg,m,n,seed,sid,epoch):
 ix=np.flatnonzero(m);a=sg['area'][ix];salt=int(hashlib.sha256(sid.encode()).hexdigest()[:8],16);rng=np.random.default_rng(np.random.SeedSequence([seed,salt,epoch]));return rng.choice(ix,n,replace=True,p=a/sum(a))
def valqueries(sg,m,n=2048):
 ix=np.flatnonzero(m);cdf=np.cumsum(sg['area'][ix])/sum(sg['area'][ix]);return ix[np.searchsorted(cdf,(np.arange(n)+.5)/n).clip(0,len(ix)-1)]
