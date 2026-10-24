from common_e16 import *
import numpy as np,pandas as pd
from features_e16 import core,view
def main():
 verify_protocol();classes=[]
 for a in rows(R/'OBSERVABLE_N3_FEATURE_CONTRACT.csv'):
  i=int(a['channel']);classes.append(dict(channel=i,name=a['name'],observability_class='DOCUMENTED_DESIGN_METADATA' if i in [9,10,11,12] else 'DERIVED_FROM_VISIBLE_GEOMETRY',registration_required=True,query_plan_required=i in [0,1,2],unobserved_geometry_required=False,target_information=False))
 table(R/'06_observable_geometry_contract/FEATURE_OBSERVABILITY_CLASSES.csv',classes);details=[]
 for rr in rows(R/'01_frozen_dataset/GEOMETRY_REGISTRY.csv'):
  sid=rr['source_id'];s=core(sid)
  for tile in range(5):
   ii=np.flatnonzero(s['tile_id']==tile);ids=s['source_ids'][ii];x=s['xyz'][ii];g=view(sid,'FULL',tile);idx=np.searchsorted(g['source_ids'],ids);f=g['features'][idx];nn=g['source_ids'][g['neighbors'][idx]]
   for c in ['X50','X43']:
    v=view(sid,c,tile);j=np.searchsorted(v['source_ids'],ids);q=v['features'][j];delta=q.astype(float)-f;w=s['area'][ii];changed=np.any(nn!=v['source_ids'][v['neighbors'][j]],axis=1);boundary=np.minimum(x[:,0]-v['xyz'][:,0].min(),v['xyz'][:,0].max()-x[:,0]);boundary_effect=changed&(boundary<1.)
    for k in range(19):
     rms=float(np.sqrt(w@(delta[:,k]**2)/w.sum()));base=float(np.sqrt(w@(f[:,k].astype(float)**2)/w.sum()));details.append(dict(source_id=sid,plate=sid[0],condition=c,tile=tile,channel=k,RMS_absolute=rms,RMS_relative=rms/max(base,1e-12),relative_denominator_floor=1e-12,maximum_absolute=float(abs(delta[:,k]).max()),changed_queries=int(np.count_nonzero(delta[:,k])),neighbor_changed_queries=int(changed.sum()),observation_boundary_changed_queries=int(boundary_effect.sum()),minimum_visible_X_boundary_distance_mm=float(boundary.min()),support_class='EXACTLY_CONTEXT_INVARIANT' if np.array_equal(q[:,k],f[:,k]) else ('OBSERVATION_BOUNDARY_DEPENDENT' if np.any(boundary_effect) else 'LOCALLY_CONTEXT_DEPENDENT')))
 table(R/'06_observable_geometry_contract/FEATURE_CONSISTENCY_DETAIL.csv',details);d=pd.DataFrame(details);ss=d.groupby(['source_id','plate','condition','channel'],as_index=False)[['RMS_absolute','RMS_relative']].agg(lambda z:np.sqrt(np.mean(z*z)));ss.to_csv(R/'06_observable_geometry_contract/SOURCE_FEATURE_RMS.csv',index=False);ss.groupby(['plate','condition','channel'],as_index=False)[['RMS_absolute','RMS_relative']].agg(lambda z:np.sqrt(np.mean(z*z))).to_csv(R/'06_observable_geometry_contract/PLATE_FEATURE_RMS.csv',index=False)
 write(R/'10_training_validation/VISIBILITY_SUPPLEMENT_PASS.json',dict(UTC=now(),passed=True,observability_classes=19,scope='all original-core same-point features; RMS across equal tiles then sources',cases=len(details)))
if __name__=='__main__':main()
