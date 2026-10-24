from pathlib import Path
import json,hashlib,csv,datetime
import pandas as pd
D=Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRevision_R1');R=D.parent/'WeldStressAI_FinalResearch_PhaseR8E16';S=D/'source_snapshot'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
manifest=R/'REPRODUCIBILITY_MANIFEST.json';assert sha(manifest)=='b3e10116f7a149bd003f86343059984f259135d7a68c34d7cfa7d085f905cd50';m=json.loads(manifest.read_text());results=[]
for r in m['files']:
 p=R/r['path'];h=sha(p);results.append(dict(path=str(p),expected_SHA256=r['SHA256'],actual_SHA256=h,status='PASS' if h==r['SHA256'] else 'FAIL'))
pd.DataFrame(results).to_csv(D/'qa'/'R8E16_FULL_RELEASE_HASH_AUDIT.csv',index=False);assert all(r['status']=='PASS' for r in results)
print('R8E16_HASH_PASS',len(results),flush=True)
h=pd.read_csv(S/'00_integrity/TERMINAL_HISTORICAL_HASH_AUDIT.csv');historical=[]
for _,r in h.iterrows():
 actual=sha(Path(r.path));historical.append(dict(path=r.path,expected_SHA256=r.SHA256,actual_SHA256=actual,status='PASS' if actual==r.SHA256 else 'FAIL'))
pd.DataFrame(historical).to_csv(D/'qa'/'FRESH_CONSUMED_HISTORICAL_HASH_AUDIT.csv',index=False);assert all(r['status']=='PASS' for r in historical)
print('HISTORICAL_HASH_PASS',len(historical),flush=True)
lookup={r['path']:r['expected_SHA256'] for r in results+historical}
e15=R.parent/'WeldStressAI_InferenceMechanisms_PhaseR8E15';e15ix={str(e15/r['path']):r['SHA256'] for r in json.loads((e15/'REPRODUCIBILITY_MANIFEST.json').read_text())['files']};lookup.update(e15ix)
inputs=pd.read_csv(D/'qa'/'SPATIAL_FIGURE_INPUT_HASHES.csv');extra=[]
for _,r in inputs.iterrows():
 expected=lookup.get(r.path);assert expected is not None,r.path;actual=sha(Path(r.path));assert actual==expected;extra.append(dict(path=r.path,expected_SHA256=expected,observed_SHA256=actual,status='PASS'))
pd.DataFrame(extra).to_csv(D/'qa'/'SPATIAL_FIGURE_INPUT_VERIFICATION.csv',index=False)
snap=pd.read_csv(D/'SOURCE_INTEGRITY_AUDIT.csv')
for _,r in snap.iterrows():assert sha(S/r.relative_path)==r.copy_SHA256
receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),passed=True,original_R8E16_manifest_SHA256=sha(manifest),R8E16_files_freshly_verified=len(results),consumed_historical_files_freshly_verified=len(historical),snapshot_files_verified=len(snap),spatial_figure_inputs_verified=len(extra),historical_scope='consumed historical subset inherited from the sealed E16 audit, not every historical bulk export',new_FE_solves=0,new_training=0,new_inference=0)
(D/'qa'/'INTEGRITY_CLOSEOUT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8');print(json.dumps(receipt))
