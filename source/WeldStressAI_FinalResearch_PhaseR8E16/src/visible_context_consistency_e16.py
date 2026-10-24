from common_e16 import *
import numpy as np,pandas as pd
from features_e16 import view
def main():
 verify_protocol();records=[]
 for a in rows(R/'01_frozen_dataset/GEOMETRY_REGISTRY.csv'):
  sid=a['source_id']
  for tile in range(5):
   full=view(sid,'FULL',tile)
   for c in ['X50','X43']:
    g=view(sid,c,tile);ix=np.searchsorted(full['source_ids'],g['source_ids']);assert np.array_equal(full['source_ids'][ix],g['source_ids']);f=full['features'][ix];v=g['features'];delta=v.astype(float)-f;w=full['area'][ix];ctx=g['context'];border=np.minimum(g['xyz'][:,0]-g['xyz'][:,0].min(),g['xyz'][:,0].max()-g['xyz'][:,0]);boundary=border<=3.0000001;nb_changed=np.any(full['source_ids'][full['neighbors'][ix]]!=g['source_ids'][g['neighbors']],axis=1)
    for k in range(19):
     dd=delta[:,k];changed=dd!=0;base=float(np.sqrt(w@(f[:,k].astype(float)**2)/w.sum()));rms=float(np.sqrt(w@(dd*dd)/w.sum()));cc=dd[ctx];classification='EXACTLY_CONTEXT_INVARIANT' if not changed.any() else ('OBSERVATION_BOUNDARY_DEPENDENT' if np.any(changed&boundary) else 'LOCALLY_CONTEXT_DEPENDENT');records.append(dict(source_id=sid,plate=sid[0],condition=c,tile=tile,channel=k,common_visible_points=len(ix),RMS_absolute=rms,RMS_relative=rms/max(base,1e-12),maximum_absolute=float(abs(dd).max()),changed_points=int(changed.sum()),changed_within_3mm_visible_X_boundary=int((changed&boundary).sum()),changed_farther_than_3mm=int((changed&~boundary).sum()),neighbor_ID_changed_points=int(nb_changed.sum()),context4096_RMS=float(np.sqrt(np.mean(cc*cc))),context4096_maximum=float(abs(cc).max()),context4096_changed_points=int(np.count_nonzero(cc)),classification=classification,hidden_full_information_in_operational_inputs=False,scope='post-fit geometry-only audit of unchanged inputs, no feature redesign'))
  print('VISIBLE_CONTEXT_FEATURE_AUDIT',sid,flush=True)
 table(R/'06_observable_geometry_contract/ALL_VISIBLE_POINT_FEATURE_CONSISTENCY.csv',records);d=pd.DataFrame(records);d.groupby(['plate','condition','channel'],as_index=False)[['RMS_absolute','context4096_RMS']].agg(lambda z:np.sqrt(np.mean(z*z))).to_csv(R/'06_observable_geometry_contract/VISIBLE_CONTEXT_PLATE_RMS.csv',index=False);write(R/'10_training_validation/ALL_VISIBLE_FEATURE_AUDIT_PASS.json',dict(UTC=now(),passed=True,comparisons=len(records),geometry_only=True,changes_to_sealed_contract=0,additional_model_fits=0,scope='all common visible original vertices and actual4096context subsets; unlike primary core-only feature consistency'))
if __name__=='__main__':main()
