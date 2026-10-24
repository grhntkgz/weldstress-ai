from common_e15 import *
import numpy as np

def main():
 gate();checks=[]
 for root,seal in [(H,'21_reproducibility/RELEASE_SEAL.json'),(J,'20_reproducibility/RELEASE_SEAL.json')]:
  assert sha(root/'REPRODUCIBILITY_MANIFEST.json')==read(root/seal)['manifest_SHA256']
  manifest=read(root/'REPRODUCIBILITY_MANIFEST.json')
  for i,a in enumerate(manifest['files']):
   p=root/a['path'];expected=a.get('SHA256',a.get('sha256'));assert p.stat().st_size==a['bytes'] and sha(p)==expected,str(p);checks.append(dict(path=str(p),SHA256=expected,bytes=a['bytes'],passed=True))
   if i%200==0:print('HISTORICAL_HASH',root.name,i,len(manifest['files']),flush=True)
 table(R/'00_historical_integrity/ALL_RELEASE_HASHES.csv',checks)
 targets=[];support=[]
 for a in rows(J/'QUALIFIED13_SOURCE_REGISTRY.csv'):
  sid=a['source_id'];p=Path(a['qualified_M2_target_path']);assert sha(p)==a['qualified_M2_target_SHA256'];d=dict(np.load(p));g=dict(np.load(H/'02_geometry'/(sid+'.npz')));s=dict(np.load(J/'03_source_geometry'/(sid+'_SUPPORT.npz')))
  for key in ['source_ids','xyz','area']:assert np.array_equal(d[key],g[key]) and np.array_equal(d[key],s[key]),(sid,key)
  for key in ['core','valid']:assert np.array_equal(d[key],s[key])
  assert d['valid'][d['core']].all();assert len(g['context'])==4096 and g['features'].shape[1]==19
  targets.append(dict(source_id=sid,path=str(p),expected_SHA256=sha(p),actual_SHA256=sha(p),passed=True))
  support.append(dict(source_id=sid,plate=sid[0],original_points=len(d['xyz']),core_points=int(d['core'].sum()),source_geometry_path=str(H/'02_geometry'/(sid+'.npz')),source_geometry_SHA256=sha(H/'02_geometry'/(sid+'.npz')),target_path=str(p),target_SHA256=sha(p),T0_triangles=len(g['triangles']),T0_area_mm2=float(d['area'][d['core']].sum()),passed=True))
 table(R/'HISTORICAL_V1_TARGET_HASHES.csv',targets);table(R/'SOURCE_CORE_REGISTRY.csv',support)
 ck=[]
 for model,filename in [('N1','R8E13_CHECKPOINT_HASHES.csv'),('N2','N2_TRAINING_RUN_REGISTRY.csv')]:
  for a in rows(J/filename):
   p=Path(a['checkpoint']);expected=a['actual_SHA256'] if model=='N1' else a['checkpoint_SHA256'];assert sha(p)==expected
   fold=a['fold'];seed=int(a['seed']);receipt=read(p.parent/'COMPLETED.json');assert receipt['fold']==fold and int(receipt['seed'])==seed;held=receipt['heldout_sources'];train=receipt['train_sources'];assert len({s[0] for s in held})==1 and not {s[0] for s in held}&{s[0] for s in train}
   ck.append(dict(model=model,fold=fold,seed=seed,heldout_plate=held[0][0],heldout_sources=';'.join(held),checkpoint=str(p),expected_SHA256=expected,actual_SHA256=sha(p),parameters=int(a['parameters']),passed=True))
 assert len(ck)==20;table(R/'N1_N2_CHECKPOINT_HASHES.csv',ck)
 for name in ['DOCUMENTARY_PLATE_GROUPS.csv','FROZEN_OUTER_FOLDS.csv','QUALIFIED13_SOURCE_REGISTRY.csv']:shutil.copyfile(J/name,R/name)
 historical=[]
 for a in rows(J/'20_reproducibility/PREDICTION_REGISTRY.csv'):
  if a['condition'] not in ['FULL','X50','X43']:continue
  assert sha(a['path'])==a['SHA256'];p=dict(np.load(a['path']));d=dict(np.load(next(x['path'] for x in targets if x['source_id']==a['source_id'])));q=np.flatnonzero(d['core']&d['valid']);assert np.array_equal(p['source_ids'],d['source_ids'][q]);assert np.array_equal(p['xyz'],d['xyz'][q]);assert np.array_equal(p['area'],d['area'][q]);historical.append(a)
 assert len(historical)==156;table(R/'00_historical_integrity/HISTORICAL_PREDICTION_REGISTRY.csv',historical)
 write(R/'00_historical_integrity/INTEGRITY_PASS.json',dict(UTC=now(),passed=True,historical_release_files=len(checks),targets=13,checkpoints=20,historical_prediction_fields=156,resource=gate()));print('INTEGRITY_PASS',len(checks),flush=True)
if __name__=='__main__':main()
