from common_e14 import *
import numpy as np,ast,importlib
def main():
 gate();bound=[]
 for root,seal_path in [(E12,'25_reproducibility/RELEASE_SEAL.json'),(H,'21_reproducibility/RELEASE_SEAL.json')]:
  seal=read(root/seal_path);assert sha(root/'REPRODUCIBILITY_MANIFEST.json')==seal['manifest_SHA256'];manifest=read(root/'REPRODUCIBILITY_MANIFEST.json')
  for i,a in enumerate(manifest['files']):
   p=root/a['path'];assert p.stat().st_size==a['bytes'] and sha(p)==a['sha256'],str(p);bound.append(dict(path=str(p),SHA256=a['sha256'],bytes=a['bytes'],passed=True))
   if i%100==0:print('RELEASE_HASH',root.name,i,len(manifest['files']),flush=True)
 table(R/'00_integrity/HISTORICAL_RELEASE_HASHES.csv',bound)
 registry=rows(H/'QUALIFIED13_SOURCE_REGISTRY.csv');assert len(registry)==13;targets=[]
 for a in registry:
  sid=a['source_id'];assert sha(a['qualified_M2_target_path'])==a['qualified_M2_target_SHA256'];d=dict(np.load(a['qualified_M2_target_path']));cached=dict(np.load(H/'01_dataset/targets'/(sid+'.npz')));g=dict(np.load(H/'02_geometry'/(sid+'.npz')))
  for key in ['source_ids','xyz','area','valid','core','region']:assert np.array_equal(d[key],cached[key])
  assert np.array_equal(d['T2_MPa'],cached['T2_MPa'],equal_nan=True);assert all(np.array_equal(d[k],g[k]) for k in ['source_ids','xyz','area']);assert d['valid'][d['core']].all()
  targets.append(dict(source_id=sid,path=a['qualified_M2_target_path'],expected_SHA256=a['qualified_M2_target_SHA256'],actual_SHA256=sha(a['qualified_M2_target_path']),core_points=int(d['core'].sum()),passed=True))
 table(R/'HISTORICAL_V1_TARGET_HASHES.csv',targets);table(R/'SOURCE_TARGET_HASH_AUDIT.csv',targets)
 for name in ['DOCUMENTARY_PLATE_GROUPS.csv','OUTER_LOPO_FOLDS.csv','QUALIFIED13_SOURCE_REGISTRY.csv','METRIC_SPECIFICATION.json','MODEL_AND_TRAINING_SEAL.json']:
  dest='FROZEN_OUTER_FOLDS.csv' if name=='OUTER_LOPO_FOLDS.csv' else name;shutil.copyfile(H/name,R/dest)
 for name in ['model_e3.py','base_arch.py','geometry_e13.py']:shutil.copyfile(H/'src'/name,R/'src'/name)
 code=(H/'src/score_e13.py').read_text(encoding='utf8');tree=ast.parse(code);functions=[ast.get_source_segment(code,n) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['quantile','metric']];(R/'src/metric_e14.py').write_text('import numpy as np,math\n'+'\n\n'.join(functions)+'\n',encoding='utf8');importlib.invalidate_caches();from metric_e14 import metric
 scored=[];checkpoints=[]
 for p in sorted((H/'05_training').glob('F*_s*/COMPLETED.json')):
  rec=read(p);assert sha(rec['checkpoint'])==rec['checkpoint_SHA256'];started=read(p.parent/'STARTED.json');assert started['parameters']==7228;assert rec['epochs']==80;assert not {s[0] for s in rec['train_sources']}&{s[0] for s in rec['heldout_sources']};members=rows(p.parent/'runtime_membership.csv');assert sha(p.parent/'runtime_membership.csv')==rec['runtime_membership_SHA256'];assert len(members)==80*len(rec['train_sources']);assert all(a['source_id'] in rec['train_sources'] and a['plate']!=rec['heldout_sources'][0][0] for a in members);checkpoints.append(dict(fold=rec['fold'],seed=rec['seed'],checkpoint=rec['checkpoint'],expected_SHA256=rec['checkpoint_SHA256'],actual_SHA256=sha(rec['checkpoint']),parameters=7228,epochs=80,runtime_records=len(members),passed=True))
 for a in rows(H/'PREDICTION_REGISTRY.csv'):
  if a['model']!='N1_POINT_TRANSFORMER':continue
  assert sha(a['path'])==a['SHA256'];sid=a['source_id'];d=dict(np.load(H/'01_dataset/targets'/(sid+'.npz')));p=dict(np.load(a['path']));assert all(np.array_equal(d[k],p[k]) for k in ['source_ids','xyz','area']);m=d['core']&d['valid'];scored.append(dict(fold=a['fold'],seed=a['seed'],source_id=sid,plate=sid[0],**metric(d['T2_MPa'][m],p['pred_MPa'][m],d['area'][m],d['xyz'][m])))
 table(R/'05_spatial_error_baseline/RECOMPUTED_R8E13_METRICS.csv',scored);aggregates=[]
 for seed in ['20261021','20261022']:
  ss=[a for a in scored if a['seed']==seed];value={key:float(np.mean([np.mean([a[key] for a in ss if a['plate']==p]) for p in 'CEGHX'])) for key in ['L2','MAE_MPa','high95_IoU']};old=next(a for a in rows(H/'MODEL_COMPARISON_METRICS.csv') if a['model']=='N1_POINT_TRANSFORMER' and a['seed']==seed)
  for key in value:assert abs(value[key]-float(old['equal_plate_'+key]))<1e-12
  aggregates.append(dict(seed=seed,**value))
 table(R/'R8E13_CHECKPOINT_HASHES.csv',checkpoints);table(R/'R8E13_CHECKPOINT_VERIFICATION.csv',checkpoints);write(R/'00_integrity/G0_INTEGRITY_PASS.json',dict(UTC=now(),passed=True,release_files=len(bound),targets=13,checkpoints=10,recomputed_source_metrics=26,aggregate_from_arrays=aggregates));print('G0_INTEGRITY_PASS',flush=True)
if __name__=='__main__':main()
