from common_e14 import *
import numpy as np
from functools import lru_cache
@lru_cache(maxsize=13)
def label_free_support(sid):return dict(np.load(R/'03_source_geometry'/(sid+'_SUPPORT.npz')))
@lru_cache(maxsize=80)
def view(sid,condition,tile):
 path=H/'02_geometry'/(sid+'.npz') if condition in ['FULL','D0'] else R/'07_context_geometry'/sid/(condition+'_'+str(tile)+'.npz')
 with np.load(path) as f:g={k:f[k] for k in ['features','neighbors','neighbors_1mm','neighbors_3mm','context','source_ids']}
 if condition=='D0':g['context']=np.load(R/'15_context_density_controls'/sid/(str(tile)+'.npy'))
 return g
def parts(sid,q,condition):
 if condition=='FULL':return [(np.arange(len(q)),view(sid,'FULL',0),np.asarray(q))]
 support=label_free_support(sid);labels=support['tile_id'][q];out=[]
 for tile in np.unique(labels):
  loc=np.flatnonzero(labels==tile);g=view(sid,condition,int(tile));original=support['source_ids'][q[loc]];mapped=np.searchsorted(g['source_ids'],original);assert np.array_equal(g['source_ids'][mapped],original);out.append((loc,g,mapped))
 return out
def predict(model,sid,q,condition):
 import torch
 output=None
 for loc,g,indices in parts(sid,q,condition):
  value=model(g,indices)
  if output is None:output=torch.zeros(len(q),dtype=value.dtype,device=value.device)
  output=output.index_copy(0,torch.as_tensor(loc,dtype=torch.int64),value)
 return output
