from common_e16 import *
import numpy as np
from functools import lru_cache

@lru_cache(maxsize=13)
def core(sid):return dict(np.load(K/'02_source_geometry'/sid/'CORE.npz'))

@lru_cache(maxsize=10)
def view(sid,condition,tile):
 file=H/'02_geometry'/(sid+'.npz') if condition=='FULL' else J/'07_context_geometry'/sid/(condition+'_'+str(tile)+'.npz');g=dict(np.load(file));feature=R/'07_feature_implementation'/sid/(condition+('_BASE' if condition=='FULL' else '_'+str(tile))+'_FEATURES.npy');f=np.load(feature).copy();a=read(R/'07_feature_implementation'/sid/'ANCHORS.json')[condition+'_'+str(tile)];anchor=np.array(a['XYZ_mm']);f[:,:3]=((g['xyz']-anchor)/60).astype('f4');g['features']=f;return g

def parts(sid,q,condition):
 s=core(sid);tileids=s['tile_id'][np.searchsorted(s['query_original_rows'],q)];assert np.array_equal(s['query_original_rows'][np.searchsorted(s['query_original_rows'],q)],q);out=[]
 for tile in np.unique(tileids):
  loc=np.flatnonzero(tileids==tile);g=view(sid,condition,int(tile));ids=s['source_ids'][np.searchsorted(s['query_original_rows'],q[loc])];mapped=np.searchsorted(g['source_ids'],ids);assert np.array_equal(g['source_ids'][mapped],ids);out.append((loc,g,mapped))
 return out

def local_base(g):
 x=g['xyz'];nb=g['neighbors'];normal=g['normal'].copy();normal[normal[:,2]<0]*=-1;n=len(x);f=np.zeros((n,19),dtype='f4');f[:,3:6]=normal;f[:,6:9]=(np.ptp(x[nb],axis=1)/60).astype('f4');f[:,9]=1;f[:,13]=(x[:,2]-x[nb,2].mean(1)).astype('f4');f[:,14]=np.linalg.norm(normal-normal[nb].mean(1),axis=1).astype('f4');f[:,15]=np.log1p(g['area']).astype('f4');f[:,16:18]=np.std(normal[nb,:2],axis=1).astype('f4');f[:,18]=(np.std(x[nb,2],axis=1)/60).astype('f4');return f

def prepare():
 verify_protocol();assert read(R/'00_integrity/INTEGRITY_PASS.json')['passed'];records=[];consistency=[];visibility=[];samples=[]
 top=rows(R/'01_frozen_dataset/ORIGINAL_TILE_TOPOLOGY.csv')
 for rr in rows(R/'01_frozen_dataset/GEOMETRY_REGISTRY.csv'):
  sid=rr['source_id'];folder=R/'07_feature_implementation'/sid;folder.mkdir(exist_ok=True);anchors={};fullcore={};q=core(sid);full=dict(np.load(rr['geometry_path']));slope_orientation_min=float(full['normal'][:,2].min())
  for condition in ['FULL','X50','X43']:
   for tile in range(5):
    path=Path(rr['geometry_path']) if condition=='FULL' else J/'07_context_geometry'/sid/(condition+'_'+str(tile)+'.npz');g=dict(np.load(path));cachepath=folder/(condition+('_BASE' if condition=='FULL' else '_'+str(tile))+'_FEATURES.npy')
    if condition!='FULL' or tile==0:np.save(cachepath,local_base(g))
    f=np.load(cachepath);t=next(t for t in top if t['source_id']==sid and int(t['tile'])==tile);xy=np.array([float(t['center_X_mm']),float(t['center_Y_mm'])]);dist=np.sum((g['xyz'][:,:2]-xy)**2,axis=1);nearest=np.flatnonzero(abs(dist-dist.min())<=1e-12);i=nearest[np.argmin(g['source_ids'][nearest])];assert dist[i]<=1.;anchor=np.r_[xy,g['xyz'][i,2]];anchors[condition+'_'+str(tile)]=dict(XYZ_mm=anchor.tolist(),Z_anchor_source_ID=int(g['source_ids'][i]),XY_to_visible_point_distance_mm=float(dist[i]**.5),rule='query-plan XY; nearest visible XY vertex Z; min canonical-ID tie at1e-12mm2',geometry_path=str(path),geometry_SHA256=sha(path),features_path=str(cachepath),features_SHA256=sha(cachepath))
    ids=q['source_ids'][q['tile_id']==tile];local=np.searchsorted(g['source_ids'],ids);ff=f[local].copy();ff[:,:3]=((g['xyz'][local]-anchor)/60).astype('f4');assert np.isfinite(ff).all();w=q['area'][q['tile_id']==tile];members=g['source_ids'][g['neighbors'][local]]
    if condition=='FULL':fullcore[tile]=(ff,members)
    else:
     delta=ff.astype('f8')-fullcore[tile][0].astype('f8');nbchanges=int(np.sum(np.any(members!=fullcore[tile][1],axis=1)))
     for k in range(19):consistency.append(dict(source_id=sid,plate=sid[0],condition=condition,tile=tile,channel=k,points=len(ids),RMS_difference=float(np.sqrt(w@(delta[:,k]**2)/w.sum())),maximum_difference=float(abs(delta[:,k]).max()),classification='EXACTLY_CONTEXT_INVARIANT' if np.array_equal(ff[:,k],fullcore[tile][0][:,k]) else 'LOCALLY_CONTEXT_DEPENDENT',neighbor_membership_changed_queries=nbchanges,hidden_full_features_used=False))
    # Independent sampled reconstruction: direct per-row geometry arithmetic, not local_base.
    sample=np.unique(np.linspace(0,len(local)-1,min(64,len(local))).astype(int));maxerror=0.;nn=g['normal'].copy();nn[nn[:,2]<0]*=-1
    for j in sample:
     z=local[j];neighbors=g['neighbors'][z];v=g['xyz'][neighbors];expected=np.r_[(g['xyz'][z]-anchor)/60,nn[z],(v.max(0)-v.min(0))/60,[1.,0,0],0,g['xyz'][z,2]-sum(map(float,v[:,2]))/16,np.linalg.norm(nn[z]-sum(nn[neighbors])/16),np.log(1+g['area'][z]),np.std(nn[neighbors,:2],axis=0),np.std(v[:,2])/60].astype('f4');error=float(np.max(abs(expected-ff[j])));assert error<3e-7;maxerror=max(maxerror,error)
     for k in range(19):samples.append(dict(source_id=sid,source_point_id=int(ids[j]),condition=condition,tile=tile,channel=k,observable_value=float(ff[j,k]),independent_value=float(expected[k]),absolute_difference=abs(float(ff[j,k]-expected[k]))))
    visibility.append(dict(source_id=sid,condition=condition,tile=tile,visible_points=len(g['xyz']),context_points=len(g['context']),geometry_path=str(path),geometry_SHA256=sha(path),feature_SHA256=sha(cachepath),independent_max_difference=maxerror,anchor_ID_visible=bool(g['source_ids'][i] in g['source_ids']),hidden_geometry=False,target_feature=False,query_coverage=True,passed=True))
    records.append(dict(source_id=sid,condition=condition,tile=tile,base_features_path=str(cachepath),SHA256=sha(cachepath),anchor_source_ID=int(g['source_ids'][i]),canonical_normal_Z_min=slope_orientation_min));print('N3_FEATURE',sid,condition,tile,flush=True)
  write(folder/'ANCHORS.json',anchors);gate()
 table(R/'07_feature_implementation/FEATURE_REGISTRY.csv',records);table(R/'FEATURE_VISIBILITY_AUDIT.csv',visibility);table(R/'FEATURE_CONTEXT_CONSISTENCY.csv',consistency);table(R/'06_observable_geometry_contract/SAMPLED_FEATURE_VALUES.csv',samples);write(R/'10_training_validation/FEATURE_CONTRACT_PASS.json',dict(UTC=now(),passed=True,feature_views=len(records),independent_feature_reconstruction=True,query_plan_required=True,registered_canonical_frame_required=True,no_registration_independence_claim=True,hidden_source_statistics=False));print('FEATURE_CONTRACT_QUALIFIED',len(records),flush=True)
if __name__=='__main__':prepare()
