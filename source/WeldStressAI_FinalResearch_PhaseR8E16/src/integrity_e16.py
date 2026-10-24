from common_e16 import *
import numpy as np,pandas as pd
from metric_e14 import metric

def main():
 gate();manifests={};audit=[]
 for root,sealname in [(H,'21_reproducibility/RELEASE_SEAL.json'),(J,'20_reproducibility/RELEASE_SEAL.json'),(K,'21_reproducibility/RELEASE_SEAL.json')]:
  assert sha(root/'REPRODUCIBILITY_MANIFEST.json')==read(root/sealname)['manifest_SHA256'];m=read(root/'REPRODUCIBILITY_MANIFEST.json');manifests[root]={a['path']:a for a in m['files']}
 def bound(p):
  p=Path(p)
  for root,m in manifests.items():
   if p.is_relative_to(root):
    rec=m[p.relative_to(root).as_posix()];expected=rec.get('SHA256',rec.get('sha256'));assert sha(p)==expected,str(p);audit.append(dict(path=str(p),SHA256=sha(p),bytes=p.stat().st_size,passed=True));return
  raise AssertionError(str(p))
 for root,names in [(H,['QUALIFIED13_SOURCE_REGISTRY.csv','DOCUMENTARY_PLATE_GROUPS.csv','OUTER_LOPO_FOLDS.csv','PREDICTION_REGISTRY.csv','MODEL_COMPARISON_METRICS.csv','INDEPENDENT_LEAKAGE_CHECKS.csv']),(J,['N2_TRAINING_RUN_REGISTRY.csv','R8E13_CHECKPOINT_HASHES.csv','SEED_CONTEXT_METRICS.csv','20_reproducibility/PREDICTION_REGISTRY.csv','20_reproducibility/DELIVERY_VERIFICATION.json']),(K,['SOURCE_LEVEL_FIELD_METRICS.csv','MODEL_DEPENDENCE_ALGEBRA.md','MECHANISM_EVIDENCE_MATRIX.csv','FROZEN_DIAGNOSTIC_PARAMETERS.json','PREREGISTRATION_SEAL.json','21_reproducibility/DELIVERY_VERIFICATION.json','18_independent_verification/INDEPENDENT_PASS.json'])]:
  for name in names:bound(root/name)
 for root in [H,J,K]:
  for name in ['model_e3.py','base_arch.py','geometry_e13.py']:bound(root/'src'/name)
 for name in ['context_e14.py','infer_e14.py','train_e14.py']:bound(J/'src'/name)
 registry=rows(H/'QUALIFIED13_SOURCE_REGISTRY.csv');targets=[];geometry=[]
 for a in registry:
  sid=a['source_id'];assert sha(a['qualified_M2_target_path'])==a['qualified_M2_target_SHA256'];t=dict(np.load(a['qualified_M2_target_path']));gpath=H/'02_geometry'/(sid+'.npz');bound(gpath);g=dict(np.load(gpath));s=dict(np.load(K/'02_source_geometry'/sid/'CORE.npz'));q=np.flatnonzero(t['core']&t['valid']);assert len(q)==34200
  for key in ['source_ids','xyz','area']:assert np.array_equal(t[key],g[key]);assert np.array_equal(t[key][q],s[key])
  assert len(g['context'])==4096 and len(set(g['context']))==4096 and g['features'].shape[1]==19
  targets.append(dict(source_id=sid,target_path=a['qualified_M2_target_path'],SHA256=sha(a['qualified_M2_target_path']),core_points=len(q),passed=True));geometry.append(dict(source_id=sid,plate=sid[0],geometry_path=str(gpath),geometry_SHA256=sha(gpath),target_path=a['qualified_M2_target_path'],target_SHA256=sha(a['qualified_M2_target_path']),core_path=str(K/'02_source_geometry'/sid/'CORE.npz'),core_SHA256=sha(K/'02_source_geometry'/sid/'CORE.npz'),points=len(g['xyz']),triangles=len(g['triangles']),core_points=len(q)))
  for condition in ['X50','X43']:
   for tile in range(5):bound(J/'07_context_geometry'/sid/(condition+'_'+str(tile)+'.npz'))
  print('SOURCE_VERIFIED',sid,flush=True)
 ck=rows(K/'N1_N2_CHECKPOINT_HASHES.csv');assert len(ck)==20
 for a in ck:
  bound(a['checkpoint']);assert sha(a['checkpoint'])==a['actual_SHA256'];p=Path(a['checkpoint']);receipt=read(p.parent/'COMPLETED.json');assert not {s[0] for s in receipt['train_sources']}&{s[0] for s in receipt['heldout_sources']};bound(p.parent/'runtime_membership.csv');members=rows(p.parent/'runtime_membership.csv');assert all(b['source_id'] in receipt['train_sources'] for b in members)
 historical=[]
 for a in rows(J/'20_reproducibility/PREDICTION_REGISTRY.csv'):
  if a['condition'] not in ['FULL','X50','X43']:continue
  bound(a['path']);historical.append(a)
 for a in rows(K/'SOURCE_LEVEL_FIELD_METRICS.csv'):
  if a['policy'] in ['S0','ORACLE']:bound(a['path'])
 baseline=[a for a in rows(H/'PREDICTION_REGISTRY.csv') if a['model'] in ['B0_CONSTANT','B1_GEOMETRY_RIDGE']]
 for a in baseline:bound(a['path'])
 recompute=[]
 for a in historical+baseline:
  sid=a['source_id'];p=dict(np.load(a['path']));t=dict(np.load(H/'01_dataset/targets'/(sid+'.npz')));q=np.flatnonzero(t['core']&t['valid']);pred=p['pred_MPa'] if len(p['pred_MPa'])==len(q) else p['pred_MPa'][q];recompute.append(dict(model=a['model'],seed=a['seed'],condition=a.get('condition','FULL'),source_id=sid,plate=sid[0],**metric(t['T2_MPa'][q],pred,t['area'][q],t['xyz'][q])))
 table(R/'00_integrity/HISTORICAL_RECOMPUTED_METRICS.csv',recompute)
 old=pd.read_csv(J/'SEED_CONTEXT_METRICS.csv');df=pd.DataFrame(recompute);comparisons=[]
 for (model,seed,c),ss in df[df.model.isin(['N1','N2'])].groupby(['model','seed','condition']):
  row=old[(old.model==model)&(old.seed==int(seed))&(old.condition==c)].iloc[0]
  for key in ['L2','MAE_MPa','high95_IoU']:
   value=float(ss.groupby('plate')[key].mean().mean());expected=float(row['equal_plate_'+key]);assert abs(value-expected)<1e-12;comparisons.append(dict(model=model,seed=seed,condition=c,metric=key,recomputed=value,historical=expected,passed=True))
 table(R/'00_integrity/HISTORICAL_NUMERICAL_REPLAY.csv',comparisons)
 r6=O/'WeldStressAI_GroupedML_PhaseR6';spl=rows(r6/'FROZEN_GROUPED_SPLITS.csv');test=[a['specimen_id'] for a in spl if a['split']=='test'];dev=[a['specimen_id'] for a in spl if a['split']!='test'];assert len(test)==12 and len(dev)==47;assert not set(test)&{a['source_id'] for a in registry};assert len({a['source_id'][0] for a in registry})==5;table(R/'03_plate_grouping/QUARANTINED_IDENTITIES.csv',[dict(source_id=s,role='historical exposed test; no labels read') for s in test]);table(R/'03_plate_grouping/HISTORICAL_DEVELOPMENT_IDENTITIES.csv',[dict(source_id=s,role='historical development') for s in dev]);table(R/'00_integrity/VERIFIED_HISTORICAL_ARTIFACTS.csv',audit);table(R/'FROZEN_NUMERICAL_TARGET_HASHES.csv',targets);table(R/'HISTORICAL_MODEL_HASHES.csv',ck);table(R/'01_frozen_dataset/GEOMETRY_REGISTRY.csv',geometry)
 for original,dest in [(H/'QUALIFIED13_SOURCE_REGISTRY.csv','QUALIFIED13_SOURCE_REGISTRY.csv'),(H/'DOCUMENTARY_PLATE_GROUPS.csv','DOCUMENTED_PLATE_GROUPS.csv'),(H/'OUTER_LOPO_FOLDS.csv','FROZEN_LOPO_SPLITS.csv'),(K/'ORIGINAL_TILE_TOPOLOGY.csv','01_frozen_dataset/ORIGINAL_TILE_TOPOLOGY.csv')]:shutil.copyfile(original,R/dest)
 table(R/'00_integrity/HISTORICAL_PREDICTION_REGISTRY.csv',historical);table(R/'00_integrity/HISTORICAL_BASELINE_REGISTRY.csv',baseline);write(R/'00_integrity/INTEGRITY_PASS.json',dict(UTC=now(),passed=True,verified_critical_artifacts=len(audit),scope='Fresh SHA of all consumed historical target/geometry/model/prediction/code/metric artifacts; release manifests bound by their stored seals; unconsumed bulk CSVs not redundantly rehashed',targets=13,checkpoints=20,quarantined_test=12,development=47,Aalborg_excluded=True,resource=gate()));print('INTEGRITY_PASS',len(audit),flush=True)
if __name__=='__main__':main()
