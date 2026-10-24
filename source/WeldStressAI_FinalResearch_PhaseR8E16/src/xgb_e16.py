from common_e16 import *
sys.path.insert(0,str(R/'runtime_site'))
import numpy as np,xgboost as xgb,argparse
from features_e16 import parts,core

def main(fold):
 verify_protocol();gate();assert read(R/'10_training_validation/FEATURE_CONTRACT_PASS.json')['passed'];rr=[a for a in rows(R/'FROZEN_LOPO_SPLITS.csv') if a['fold']==fold];train=[a['source_id'] for a in rr if a['role']=='train'];held=[a['source_id'] for a in rr if a['role']=='heldout'];guard(training=train);folder=R/'12_XGBoost_baseline'/fold;folder.mkdir(exist_ok=True);assert not (folder/'STARTED.json').exists();protocol=read(R/'XGBOOST_BASELINE_PROTOCOL.json');write(folder/'STARTED.json',dict(UTC=now(),fold=fold,train_sources=train,heldout_sources=held,protocol_SHA256=sha(R/'PREREGISTRATION_SEAL.json'),version=xgb.__version__,parameters=protocol['parameters']));features=[];targets=[];weights=[];samples=[];start=time.monotonic()
 for sid in train:
  d=dict(np.load(H/'01_dataset/targets'/(sid+'.npz')));s=core(sid);qq=s['query_original_rows'];area=s['area'];cdf=np.cumsum(area)/sum(area);chosen=np.searchsorted(cdf,(np.arange(1024)+.5)/1024);assert len(np.unique(chosen))==1024;original=qq[chosen];mass=float(sum(area)/1024)
  for c in ['FULL','X50','X43']:
   f=np.empty((1024,19),dtype='f4')
   for loc,g,idx in parts(sid,original,c):f[loc]=g['features'][idx]
   assert np.isfinite(f).all();features.append(f);targets.append((d['T2_MPa'][original]/100).astype('f4'));ww=np.full(1024,1/(4*sum(t[0]==sid[0] for t in train)*3*1024));weights.append(ww)
   for j,i in enumerate(chosen):samples.append(dict(fold=fold,source_id=sid,plate=sid[0],heldout_plate=held[0][0],condition=c,source_point_id=int(s['source_ids'][i]),original_area_mm2=float(area[i]),area_CDF_stratum=j,quadrature_mass_mm2=mass,hierarchical_weight=float(ww[j]),geometry_feature_SHA256=hashlib.sha256(f[j].tobytes()).hexdigest(),target_SHA256=sha(H/'01_dataset/targets'/(sid+'.npz'))))
 X=np.concatenate(features);Y=np.concatenate(targets);W=np.concatenate(weights);W*=len(W)/W.sum();assert abs(W.mean()-1)<1e-12;table(folder/'SAMPLE_IDS.csv',samples);np.savez_compressed(folder/'ACTUAL_TRAINING_ARRAYS.npz',features=X,target_K=Y,sample_weight=W,source_ids=np.array([a['source_id'] for a in samples]),point_ids=np.array([a['source_point_id'] for a in samples]),condition=np.array([a['condition'] for a in samples]));model=xgb.XGBRegressor(**protocol['parameters']);model.fit(X,Y,sample_weight=W,verbose=False);assert model.n_estimators==500;model.save_model(str(folder/'model.ubj'));fit_s=time.monotonic()-start;registry=[]
 for sid in held:
  s=core(sid);q=s['query_original_rows']
  for c in ['FULL','X50','X43']:
   t0=time.monotonic();v=np.empty(len(q));count=np.zeros(len(q),int)
   for loc,g,idx in parts(sid,q,c):v[loc]=model.predict(g['features'][idx])*100;count[loc]+=1
   assert np.isfinite(v).all() and (count==1).all();path=R/'13_full_core_predictions'/('B2_'+fold+'_'+sid+'_'+c+'.npz');np.savez_compressed(path,source_ids=s['source_ids'],xyz=s['xyz'],area=s['area'],pred_MPa=v,query_original_rows=q);registry.append(dict(model='B2_GEOMETRY_XGBOOST',fold=fold,seed='NA',source_id=sid,plate=sid[0],condition=c,policy='S0',path=str(path),SHA256=sha(path),checkpoint=str(folder/'model.ubj'),checkpoint_SHA256=sha(folder/'model.ubj'),core_points=len(q),coverage=1.,inference_s=time.monotonic()-t0))
 table(folder/'PREDICTION_REGISTRY.csv',registry);write(folder/'COMPLETED.json',dict(UTC=now(),passed=True,fold=fold,fit_count=1,boosting_rounds=500,training_rows=len(X),training_s=fit_s,train_sources=train,heldout_sources=held,model=str(folder/'model.ubj'),model_SHA256=sha(folder/'model.ubj'),sample_registry_SHA256=sha(folder/'SAMPLE_IDS.csv'),training_arrays_SHA256=sha(folder/'ACTUAL_TRAINING_ARRAYS.npz'),parameters=protocol['parameters'],resource=gate()));print('XGBOOST_COMPLETE',fold,fit_s,len(X),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--fold',required=True);a=p.parse_args();main(a.fold)
