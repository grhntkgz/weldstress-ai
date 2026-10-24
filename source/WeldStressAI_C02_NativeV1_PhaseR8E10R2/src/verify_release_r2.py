"""Independent read-only release verifier. --write-receipt writes only its excluded receipt."""
from pathlib import Path
import json,hashlib,csv,sys,datetime
import numpy as np
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
 return h.hexdigest()
def rows(p):
 with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def main():
 errors=[];seal=read(R/'17_reproducibility/RELEASE_SEAL.json');manifest=read(R/'REPRODUCIBILITY_MANIFEST.json');assert sha(R/'REPRODUCIBILITY_MANIFEST.json')==seal['manifest_SHA256'];assert sha(R/'REPRODUCIBILITY_MANIFEST.csv')==seal['manifest_CSV_SHA256']
 for a in manifest['files']:
  p=R/a['path']
  if not p.exists() or p.stat().st_size!=a['bytes'] or sha(p)!=a['sha256']:errors.append('release:'+a['path'])
 excluded=manifest['excluded'];listed={a['path'] for a in manifest['files']};unexpected=[]
 for p in R.rglob('*'):
  if p.is_file():
   rel=p.relative_to(R).as_posix()
   if rel not in listed and rel not in excluded and not rel.startswith('tmp/'):unexpected.append(rel)
 errors+=['unmanifested:'+s for s in unexpected]
 hist=rows(R/'HISTORICAL_INTEGRITY_EXTENDED_AUDIT.csv')
 for a in hist:
  if sha(a['path'])!=a['expected_sha256']:errors.append('history:'+a['path'])
 gate=read(R/'05_mechanical_preflight/PRE_SOLVE_GATE_SEALED.json')
 assert sha(R/'05_mechanical_preflight/PRE_SOLVE_GATE_SEALED.json')==seal['pre_solve_gate_SHA256']
 for a in gate['files']:
  if sha(R/a['path'])!=a['sha256']:errors.append('presolve:'+a['path'])
 ledger=read(R/'17_reproducibility/NATIVE_INVOCATION_LEDGER.json');solves=[a for a in ledger if a['kind']=='SOLVE'];prep=[a for a in ledger if a['kind'].startswith('PREPROCESS') and a['status']!='LAUNCH_NOT_EXECUTED'];assert [a['level'] for a in solves]==['M1','M2'] and len(prep)==3 and all(a['status']=='PASS' for a in solves)
 for l,folder in [('M1','06_native_M1'),('M2','07_native_M2')]:
  s=read(R/folder/'SOLVE_COMPLETE.json');assert s['completed'] and s['equilibrium_passed'] and s['native_errors']==0
  for name,digest in s['files'].items():assert sha(R/folder/name)==digest
  t=np.load(R/('11_T2_M1' if l=='M1' else '12_T2_M2')/'SOURCE_T2.npz');c=np.load(R/'01_protocol_freeze/TARGET_GEOMETRY_SUPPORT.npz');assert np.array_equal(t['source_ids'],c['source_ids']) and np.array_equal(t['xyz'],c['xyz']) and np.array_equal(t['area'],c['area']) and np.array_equal(t['valid'],c['core']);assert np.isfinite(t['T2_MPa'][t['valid']]).all()
  # CSV round-trip retains original identities, coordinates, weights and numerical T2.
  rr=rows(R/f'SOURCE_T2_{l}.csv');assert len(rr)==len(t['source_ids']);assert np.array_equal(np.array([int(a['source_id']) for a in rr]),t['source_ids']);assert np.array_equal(np.array([[float(a[k]) for k in ['X','Y','Z']] for a in rr]),t['xyz']);assert np.array_equal(np.array([float(a['T0_area_mm2']) for a in rr]),t['area']);assert np.array_equal(np.array([float(a['T2_MPa']) for a in rr if a['valid_T2']=='True']),t['T2_MPa'][t['valid']])
 q=read(R/'13_numerical_qualification/QUALIFICATION_DECISION.json');assert q['qualified'] and all(q['checks'].values());reg=rows(R/'QUALIFIED_V1_TARGET_REGISTRY.csv');assert len(reg)==1 and reg[0]['mesh']=='M2' and sha(reg[0]['target_path'])==reg[0]['target_hash']==seal['qualified_target_SHA256']
 figs=rows(R/'SCIENTIFIC_FIGURES.csv');assert len(figs)==34
 from PIL import Image
 for f in figs:
  with Image.open(R/f['PNG']) as im:im.verify()
  assert (R/f['PDF']).read_bytes().startswith(b'%PDF')
 report=(R/'R8E10R2_MASTER_REPORT.md').read_text(encoding='utf8');assert sum(1 for a in report.splitlines() if a.startswith('### '))==45
 result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='PASS' if not errors else 'FAIL',durable_artifacts_verified=len(manifest['files']),historical_bindings_rehashed=len(hist),pre_solve_artifacts_verified=len(gate['files']),native_preprocessing_invocations=len(prep),actual_SOLVE_invocations=len(solves),successful_solutions=2,qualified_V1_targets=1,figures_PNG_PDF_pairs_verified=34,scientific_questions=45,CSV_T2_roundtrip='EXACT',qualified_target_SHA256=seal['qualified_target_SHA256'],errors=errors,manifest_SHA256=seal['manifest_SHA256'],historical_files_modified=False,new_solutions_by_verifier=0)
 if '--write-receipt' in sys.argv:(R/'17_reproducibility/INDEPENDENT_RELEASE_VERIFICATION.json').write_text(json.dumps(result,indent=2),encoding='utf8')
 print(json.dumps(result,indent=2));assert not errors
if __name__=='__main__':main()
