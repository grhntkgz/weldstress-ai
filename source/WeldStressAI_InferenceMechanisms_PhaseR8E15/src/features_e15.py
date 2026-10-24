from common_e15 import *
import numpy as np,pandas as pd

def main():
 verify_protocol();summary=[];visibility=[];detailpath=R/'FEATURE_NORMALIZATION_VALUES.csv';columns=[0,1,2,6,7,8,16,17,18]
 def detailed():
  for rr in rows(R/'SOURCE_CORE_REGISTRY.csv'):
   sid=rr['source_id'];full=dict(np.load(rr['source_geometry_path']));core=dict(np.load(R/'02_source_geometry'/sid/'CORE.npz'));q=core['query_original_rows'];tileids=core['tile_id'];x=full['xyz']
   for tile in np.unique(tileids):
    orig=q[tileids==tile];sample=orig[np.unique(np.linspace(0,len(orig)-1,min(128,len(orig))).astype(int))]
    for condition in ['X50','X43']:
     p=J/'07_context_geometry'/sid/(condition+'_'+str(tile)+'.npz');g=dict(np.load(p));idx=np.searchsorted(g['source_ids'],full['source_ids'][orig]);small=np.searchsorted(g['source_ids'],full['source_ids'][sample]);assert np.array_equal(g['xyz'][idx],x[orig]);fv=full['features'][orig].astype('f8');vv=g['features'][idx].astype('f8');delta=vv-fv;w=core['area'][tileids==tile]
     center=np.average(g['xyz'],weights=g['area'],axis=0);expected=np.c_[(g['xyz'][small]-center)/60,g['normal'][small],np.tile(np.ptp(g['xyz'],axis=0)/60,(len(small),1)),np.tile([1.,0,0],(len(small),1)),np.zeros(len(small)),g['xyz'][small,2]-g['xyz'][g['neighbors'][small],2].mean(1),np.linalg.norm(g['normal'][small]-g['normal'][g['neighbors'][small]].mean(1),axis=1),np.log1p(g['area'][small]),np.tile([np.std(g['normal'][:,0]),np.std(g['normal'][:,1]),np.ptp(g['xyz'][:,2])/60],(len(small),1))].astype('f4');err=float(np.max(abs(expected-g['features'][small])));assert err<=2e-7
     visibility.append(dict(source_id=sid,plate=sid[0],condition=condition,tile=int(tile),sampled_points=len(small),channels=19,maximum_reconstruction_difference=err,only_visible_geometry=True,oracle_excluded_from_operational=True,passed=True))
     for k in range(19):summary.append(dict(source_id=sid,plate=sid[0],condition=condition,tile=int(tile),channel=k,query_points=len(orig),full_mean=float(w@fv[:,k]/w.sum()),visible_mean=float(w@vv[:,k]/w.sum()),mean_absolute_change=float(w@abs(delta[:,k])/w.sum()),RMS_change=float(np.sqrt(w@(delta[:,k]**2)/w.sum())),maximum_change=float(abs(delta[:,k]).max()),affected_points=int(np.sum(abs(delta[:,k])>1e-7)),normalization_alone=k in [0,1,2],oracle_replaced=k in columns,observed_area_mm2=float(g['area'].sum()),full_area_mm2=float(full['area'].sum())))
     for j,original in enumerate(sample):
      for k in range(19):
       a=float(full['features'][original,k]);b=float(g['features'][small[j],k]);factor=60 if k in [0,1,2,6,7,8,18] else 1
       yield dict(source_id=sid,plate=sid[0],source_point_id=int(full['source_ids'][original]),tile=int(tile),condition=condition,channel=k,full_normalized=a,visible_normalized=b,full_raw_before_fixed_scaling=a*factor,visible_raw_before_fixed_scaling=b*factor,absolute_change=abs(b-a),relative_change=(b-a)/a if abs(a)>1e-12 else None,oracle_normalized=a if k in columns else b,physical_X_mm=x[original,0],physical_Y_mm=x[original,1],physical_Z_mm=x[original,2])
 table(detailpath,detailed());table(R/'FEATURE_NORMALIZATION_DIFFERENCES.csv',summary);table(R/'FEATURE_VISIBILITY_AUDIT.csv',visibility);df=pd.DataFrame(summary);table(R/'08_feature_normalization/PLATE_FEATURE_DIFFERENCES.csv',df.groupby(['plate','condition','channel'])[['mean_absolute_change','RMS_change','maximum_change']].mean().reset_index().to_dict('records'));write(R/'03_feature_contract/FEATURE_AUDIT_PASS.json',dict(UTC=now(),passed=True,windows=len(visibility),sampled_point_channels=sum(a['sampled_points']*19 for a in visibility),maximum_difference=max(a['maximum_reconstruction_difference'] for a in visibility),NORM_P='INFEASIBLE',oracle_separate=True));print('FEATURE_AUDIT_PASS',len(visibility),flush=True)
if __name__=='__main__':main()
