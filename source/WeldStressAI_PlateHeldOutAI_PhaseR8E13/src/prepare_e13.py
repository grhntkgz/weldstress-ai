from common_e13 import *
import numpy as np,ast,platform,subprocess,importlib
def main():
 assert not (R/'PREREGISTRATION_SEAL.json').exists(),'ALREADY_SEALED'
 reg=rows(E12/'CUMULATIVE_QUALIFIED_V1_TARGET_REGISTRY.csv');assert len(reg)==13
 required='C02 C05 C16 E21 G04 G07 G08 G16 G25 H12 H19 X10 X23'.split();assert {x['source_id'] for x in reg}=={s+'-V1-S355-AW' for s in required}
 seal=read(E12/'25_reproducibility/RELEASE_SEAL.json');assert sha(E12/'REPRODUCIBILITY_MANIFEST.json')==seal['manifest_SHA256']
 manifest=read(E12/'REPRODUCIBILITY_MANIFEST.json');checked=[]
 if '--resume-after-hash' in sys.argv:
  checked=rows(R/'00_integrity/E12_RELEASE_HASH_CHECKS.csv');assert len(checked)==len(manifest['files'])
  for a,b in zip(manifest['files'],checked):assert str(E12/a['path'])==b['path'] and a['sha256']==b['sha256'] and (E12/a['path']).stat().st_size==a['bytes']
  print('REUSE_COMPLETED_FIRST_HASH_PASS',len(checked),flush=True)
 else:
  for i,a in enumerate(manifest['files']):
   p=E12/a['path'];assert p.stat().st_size==a['bytes'] and sha(p)==a['sha256'],str(p)
   checked.append(dict(path=str(p),sha256=a['sha256'],bytes=a['bytes']))
   if i%100==0:print('E12_HASH',i,len(manifest['files']),flush=True)
  table(R/'00_integrity/E12_RELEASE_HASH_CHECKS.csv',checked)
 historical=rows(E3/'REPRODUCIBILITY_MANIFEST.csv');lookup={a['path']:a for a in historical}
 for name in ['model_e3.py','base_arch.py','geometry_e3.py','train_e3.py']:
  p=E3/'src'/name;assert sha(p)==lookup['src/'+name]['sha256'];shutil.copyfile(p,R/'00_integrity'/name)
 for name in ['model_e3.py','base_arch.py']:shutil.copyfile(E3/'src'/name,R/'src'/name)
 source=(E3/'src/geometry_e3.py').read_text();node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='single_geometry')
 (R/'src/geometry_e13.py').write_text('import numpy as np\nfrom scipy.spatial import cKDTree\n'+ast.get_source_segment(source,node)+'\n',encoding='utf8')
 importlib.invalidate_caches()
 from geometry_e13 import single_geometry
 schema=read(E3/'SINGLE_SURFACE_FEATURE_SCHEMA.json');assert sha(E3/'SINGLE_SURFACE_FEATURE_SCHEMA.json')==lookup['SINGLE_SURFACE_FEATURE_SCHEMA.json']['sha256'];write(R/'03_protocol/FEATURE_SCHEMA.json',schema)
 q=read(E3/'00_protocol/QUARANTINE.json');assert not set(x['source_id'] for x in reg)&set(q['historical_test_IDs'])
 support=[];hashes=[];splits=[];groups=[]
 for a in reg:
  sid=a['source_id'];plate=sid[0];assert a['confirmed_parent_plate']=='ORIGINAL_S355MLO_PLATE_'+plate
  path=Path(a['qualified_M2_target_path']);assert sha(path)==a['qualified_M2_target_SHA256'];d=dict(np.load(path));gdir=E3/'02_geometry/single'/sid
  raw={n:np.load(gdir/(n+'.npy')) for n in ['xyz','triangles','source_ids','area','normal']}
  for n in raw:
   rel=(gdir/(n+'.npy')).relative_to(E3).as_posix();assert sha(gdir/(n+'.npy'))==lookup[rel]['sha256']
  assert np.array_equal(d['source_ids'],raw['source_ids']) and np.array_equal(d['xyz'],raw['xyz']) and np.array_equal(d['area'],raw['area'])
  m=d['core']&d['valid'];assert m.sum()>0 and np.isfinite(d['T2_MPa'][m]).all() and len(np.unique(d['source_ids']))==len(d['source_ids'])
  g=single_geometry(raw['xyz'],raw['triangles'],raw['source_ids'])
  for n in ['features','context','neighbors','neighbors_1mm','neighbors_3mm','area','normal']:assert np.array_equal(g[n],np.load(gdir/(n+'.npy'))),(sid,n)
  np.savez(R/'02_geometry'/(sid+'.npz'),**g)
  td=R/'01_dataset/targets';td.mkdir(exist_ok=True);np.savez(td/(sid+'.npz'),**d)
  hashes.append(dict(source_id=sid,target_path=str(path),expected_SHA256=a['qualified_M2_target_SHA256'],actual_SHA256=sha(path),passed=True))
  support.append(dict(source_id=sid,plate=plate,n_points=len(m),core_points=int(m.sum()),core_area_mm2=float(d['area'][m].sum()),source_ID_XYZ_area_exact=True,features_exact=True,coverage=1.))
  groups.append(dict(source_id=sid,plate=plate,documentary_parent_plate=a['confirmed_parent_plate'],batch='UNKNOWN',scan_session='UNKNOWN'))
  print('SOURCE_VERIFIED',sid,m.sum(),flush=True)
 for i,plate in enumerate('CEGHX',1):
  for a in reg:splits.append(dict(fold='F'+str(i),heldout_plate=plate,source_id=a['source_id'],plate=a['source_id'][0],role='heldout' if a['source_id'][0]==plate else 'train'))
 table(R/'QUALIFIED13_SOURCE_REGISTRY.csv',reg);table(R/'DOCUMENTARY_PLATE_GROUPS.csv',groups);table(R/'V1_TARGET_SUPPORT_AUDIT.csv',support);table(R/'HISTORICAL_V1_TARGET_HASHES.csv',hashes);table(R/'OUTER_LOPO_FOLDS.csv',splits)
 table(R/'TRAIN_SOURCE_ASSIGNMENTS.csv',[a for a in splits if a['role']=='train']);table(R/'HELDOUT_SOURCE_ASSIGNMENTS.csv',[a for a in splits if a['role']=='heldout'])
 write(R/'00_integrity/PREPARATION_COMPLETE.json',dict(UTC=now(),passed=True,E12_files=len(checked),sources=13,quarantine_overlap=0,historical_weights_loaded=0,features_recomputed_exact=True))
 print('PREPARATION_COMPLETE',flush=True)
if __name__=='__main__':main()
