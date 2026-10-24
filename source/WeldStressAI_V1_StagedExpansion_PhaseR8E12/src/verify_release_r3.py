"""Independent read-only release audit; --write-receipt writes only its excluded receipt."""
from pathlib import Path
import json,csv,hashlib,datetime,re,sys,math
import numpy as np
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rows(p):
 with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
 return h.hexdigest()
def main():
 seal=read(R/'21_reproducibility/RELEASE_SEAL.json');manifest=read(R/'REPRODUCIBILITY_MANIFEST.json');assert sha(R/'REPRODUCIBILITY_MANIFEST.json')==seal['manifest_SHA256'];assert sha(R/'REPRODUCIBILITY_MANIFEST.csv')==seal['CSV_SHA256'];errors=[]
 for a in manifest['files']:
  p=R/a['path']
  if not p.exists() or p.stat().st_size!=a['bytes'] or sha(p)!=a['sha256']:errors.append('release:'+a['path'])
 listed={a['path'] for a in manifest['files']}
 for p in R.rglob('*'):
  if p.is_file():
   rel=p.relative_to(R).as_posix()
   if rel not in listed and rel not in manifest['excluded'] and not rel.startswith('tmp/'):errors.append('unmanifested:'+rel)
 historical=rows(R/'21_reproducibility/HISTORICAL_AFTER_CHECK.csv')
 for a in historical:
  if sha(a['path'])!=a['expected_sha256']:errors.append('history:'+a['path'])
 assert sha(R/'PREREGISTRATION_SEAL.json')==seal['preregistration_SHA256'];pr=read(R/'PREREGISTRATION_SEAL.json')
 for a in pr['files']:assert sha(R/a['path'])==a['sha256']
 solves=read(R/'21_reproducibility/NATIVE_SOLVE_LEDGER.json');assert [(a['source_id'][:3],a['level']) for a in solves]==[('G08','M1'),('G08','M2'),('X10','M1'),('X10','M2')];assert all(a['final_status']=='NATIVE_COMPLETED_AND_VERIFIED' for a in solves);preprocess=0;package_artifacts=0
 for sid in ['G08-V1-S355-AW','X10-V1-S355-AW']:
  c=R/'cases'/sid;gp=c/'05_mechanical_preflight/PRE_SOLVE_GATE_SEALED.json';assert sha(gp)==seal['source_pre_solve_seals'][sid];gate=read(gp)
  for a in gate['files']:assert sha(c/a['path'])==a['sha256'],a['path']
  sel=read(c/'SELECTED_MESHES.json');support=np.load(c/'01_protocol_freeze/TARGET_GEOMETRY_SUPPORT.npz');source=c/'01_frozen_protocol/source';assert np.array_equal(support['xyz'],np.load(source/'xyz.npy')) and np.array_equal(support['area'],np.load(source/'area.npy'));ledger=read(c/'17_reproducibility/NATIVE_INVOCATION_LEDGER.json');preprocess+=sum(a['kind'].startswith('PREPROCESS') for a in ledger);assert len([a for a in ledger if a['kind']=='SOLVE'])==2
  for level,folder in [('M1','06_native_M1'),('M2','07_native_M2')]:
   s=read(c/folder/'SOLVE_COMPLETE.json');assert s['completed'] and s['equilibrium_passed'] and s['native_errors']==0 and s['native_warnings']==0
   for name,h in s['files'].items():assert sha(c/folder/name)==h
   txt=(c/folder/'solve.out').read_text(errors='replace');assert 'RUN COMPLETED' in txt and re.search(r'LOAD STEP\s+1\s+SUBSTEP\s+1\s+COMPLETED',txt)
   f=Path(sel[level]['folder']);assert sha(f/'mesh.npz')==sel[level]['sha256'];assert read(f/'PRE_SOLVER_QUALIFICATION.json')['pre_solver_qualified'];assert read(f/'SOURCE_FIDELITY.json')['passed'];mesh=np.load(f/'mesh.npz');native=np.load(c/folder/'native_displacements.npz');assert np.array_equal(native['connectivity_native'],mesh['tet10'][:,[0,1,2,3,4,5,6,7,9,8]]);assert np.max(abs(native['xyz']-mesh['xyz']))<1e-12
   tar=np.load(c/('11_T2_M1' if level=='M1' else '12_T2_M2')/'SOURCE_T2.npz');assert np.array_equal(tar['source_ids'],support['source_ids']) and np.array_equal(tar['xyz'],support['xyz']) and np.array_equal(tar['area'],support['area']) and np.array_equal(tar['valid'],support['core']);assert np.isfinite(tar['T2_MPa'][tar['valid']]).all();rr=rows(c/f'SOURCE_T2_{level}.csv');assert len(rr)==68457;assert np.array_equal(np.array([int(a['source_id']) for a in rr]),tar['source_ids']);assert np.array_equal(np.array([[float(a[k]) for k in ['X','Y','Z']] for a in rr]),tar['xyz']);assert np.array_equal(np.array([float(a['T0_area_mm2']) for a in rr]),tar['area']);assert np.array_equal(np.array([float(a['T2_MPa']) for a in rr if a['valid_T2']=='True']),tar['T2_MPa'][tar['valid']])
  q=read(c/'13_numerical_qualification/QUALIFICATION_DECISION.json');assert q['qualified'] and all(q['checks'].values());assert all(z['passed']=='True' for z in rows(c/'T2_COMPLETE_INDEPENDENT_AUDIT.csv'));pkg=c/'QUALIFIED_V1_PACKAGE';pm=read(pkg/'REPRODUCIBILITY_MANIFEST.json')
  for a in pm['files']:assert sha(pkg/a['path'])==a['sha256'];package_artifacts+=1
  meta=read(pkg/'TARGET_PROVENANCE.json');assert meta['source_id']==sid and sha(pkg/'T2_M2.npz')==meta['target_SHA256'];assert np.array_equal(np.load(pkg/'original_T0_triangles.npy'),np.load(source/'triangles.npy'));assert not meta['AI_training'] and not meta['AI_inference']
  assert read(c/'01_frozen_protocol/SCHEMA_AUDIT.json')['target_schema_pass'];assert len(read(c/'17_reproducibility/CAD_ATTEMPTS.json'))==1
  candidates=read(c/'14_reproducibility/FULL_CANDIDATE_LEDGER.json');assert all(sum(a['mesh_level']==l for a in candidates)<=3 for l in ['M1','M2'])
 assert preprocess==6
 x=R/'cases/X10-V1-S355-AW';audit=read(x/'08_quadratic_quality/REPAIR_ROOT_CAUSE_AND_ACTUAL_CHANGE_AUDIT.json');old=np.load(x/'07_refined_M2/M2_C1/mesh.npz');new=np.load(x/'07_refined_M2/M2_C2/mesh.npz');changed=np.flatnonzero(np.any(old['xyz']!=new['xyz'],axis=1));assert len(changed)==audit['actual_changed_node_count']==1 and old['node_tags'][changed][0]==144307;assert np.array_equal(old['xyz'][np.unique(old['tri6'])],new['xyz'][np.unique(new['tri6'])]);assert np.array_equal(old['tet10'],new['tet10']);assert np.array_equal(old['xyz'][np.unique(old['tet10'][:,:4])],new['xyz'][np.unique(new['tet10'][:,:4])])
 registry=rows(R/'QUALIFIED_V1_TARGET_REGISTRY.csv');assert len(registry)==3;assert len([z for z in registry if z['provenance']=='NEW_R3'])==2
 for z in registry:assert sha(z['target_path'])==z['target_hash']
 assert sha(R/'QUALIFIED_V1_TARGET_REGISTRY.csv')==seal['qualified_target_registry_SHA256'];tests=(R/'00_integrity/E9_46_TESTS.log').read_text(encoding='utf-8-sig');assert 'Ran 46 tests' in tests and tests.rstrip().endswith('OK');figs=rows(R/'SCIENTIFIC_FIGURES.csv');assert len(figs)==36
 from PIL import Image
 for z in figs:
  with Image.open(R/z['PNG']) as im:im.verify()
  assert (R/z['PDF']).read_bytes().startswith(b'%PDF')
 spec=(R/'01_protocol_freeze/USER_SPECIFICATION.txt').read_text(encoding='utf-8-sig');required=re.findall(r'`([^`]+\.(?:md|json|csv))`',spec.split('# 24. REQUIRED REPORTS')[1].split('# 25.')[0]);assert all((R/p).exists() for p in required),[p for p in required if not (R/p).exists()];assert sum(z.startswith('### ') for z in (R/'R8E10R3_MASTER_REPORT.md').read_text(encoding='utf8').splitlines())==48
 output=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='PASS' if not errors else 'FAIL',durable_artifacts_verified=len(manifest['files']),historical_bindings_rehashed=len(historical),pre_solve_seals_verified=2,native_preprocessing_jobs=6,actual_new_SOLVE_invocations=4,successful_new_solutions=4,repeated_SOLVEs=0,C02_reexecuted=False,new_qualified_V1_targets=2,pilot_qualified_targets=3,original_protocol_tests_passed=46,source_CSV_roundtrip='EXACT',actual_repair_nodes_moved=1,qualified_package_artifacts_verified=package_artifacts,figures_PNG_PDF_pairs_verified=36,required_scientific_questions=48,required_named_outputs_verified=len(required),manifest_SHA256=seal['manifest_SHA256'],errors=errors,new_execution_by_verifier=0,instrumentation_limitations=['CADconstructionandfidelitytimedjointly','PaircrossprojectionandDBauditnottimedseparately'],physical_validation=False,AI_training=False,AI_inference=False)
 if '--write-receipt' in sys.argv:(R/'21_reproducibility/INDEPENDENT_RELEASE_VERIFICATION.json').write_text(json.dumps(output,indent=2),encoding='utf8')
 print(json.dumps(output,indent=2));assert not errors
if __name__=='__main__':main()
