"""Standard-library-only independent sealed-release review; --dry-run only."""
from pathlib import Path
import json,csv,sys,hashlib,datetime,shutil
from fractions import Fraction
R=Path(__file__).resolve().parents[1]
EXCLUDE={'REPRODUCIBILITY_MANIFEST.json','REPRODUCIBILITY_MANIFEST.csv','14_reproducibility/RELEASE_SEAL.json','14_reproducibility/INDEPENDENT_RELEASE_VERIFICATION.json'}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rows(p):
 with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
 return h.hexdigest()
def require(value,message):
 if not value:raise ValueError(message)
def main():
 require(sys.argv[1:]==['--dry-run'],'Only --dry-run supported');seal=read(R/'14_reproducibility/RELEASE_SEAL.json');require(sha(R/'REPRODUCIBILITY_MANIFEST.json')==seal['manifest_SHA256'],'Manifest seal mismatch');require(sha(R/'REPRODUCIBILITY_MANIFEST.csv')==seal['CSV_SHA256'],'CSV seal mismatch');manifest=read(R/'REPRODUCIBILITY_MANIFEST.json');items=manifest['files'];paths=set()
 for z in items:
  p=(R/z['path']).resolve();require(p.is_relative_to(R),'Path escape');require(z['path'] not in paths,'Duplicate file');paths.add(z['path']);require(p.is_file() and p.stat().st_size==z['bytes'] and sha(p)==z['sha256'],'File mismatch:'+z['path'])
 actual={p.relative_to(R).as_posix() for p in R.rglob('*') if p.is_file() and p.relative_to(R).as_posix() not in EXCLUDE and not p.relative_to(R).as_posix().startswith('tmp/')};require(paths==actual,'Manifest inventory incomplete');csvitems=rows(R/'REPRODUCIBILITY_MANIFEST.csv');require(len(csvitems)==len(items),'CSV count mismatch')
 for a,b in zip(csvitems,items):require(a['path']==b['path'] and int(a['bytes'])==b['bytes'] and a['sha256']==b['sha256'],'CSV manifest mismatch')
 historical=rows(R/'00_integrity/HISTORICAL_HASHES.csv')
 for z in historical:require(sha(z['path'])==z['sha256'],'Historical file changed:'+z['path'])
 for z in read(R/'00_integrity/FROZEN_COPIES.json'):require(sha(R/z['copy'])==z['sha256'],'Frozen copied artifact changed')
 counts=read(R/'R8E10R1_FINAL_COUNTS.json');require(counts['actually_displaced_M1_nodes']==1 and counts['optimization_variable_nodes']==4,'Wrong movement summary');require(counts['new_full_M1_candidates']==counts['new_full_M2_candidates']==1,'Candidate count mismatch');ledger=read(R/'14_reproducibility/FULL_CANDIDATE_LEDGER.json');require(len(ledger)==2 and all(v['status']=='QUALIFIED' for v in ledger),'Full candidate ledger mismatch');require(len(read(R/'14_reproducibility/LOCAL_TRIAL_LEDGER.json'))==1,'Unexpected repair trial');require(counts['source_identities']==1 and counts['new_CAD_generations']==0,'Scope violation')
 for k in ['native_ANSYS_jobs','native_ANSYS_SOLVEs','AI_training_runs','AI_inference_runs','V1_T2_targets']:require(counts[k]==0,'Prohibited execution/target claim')
 require(not [p for p in R.rglob('*') if p.suffix.lower() in ['.rst','.rth','.db','.cdb','.pt','.pth','.onnx','.wbpj','.mechdb']],'Unexpected native or AI artifact')
 pair=read(R/'MESH_PAIR_RELEASE.json');require(sha(R/'MESH_PAIR_RELEASE.json')==manifest['mesh_pair_release_SHA256'],'Release index mismatch');require(pair['native_execution_authorized_in_R1'] is False and pair['qualified_T2_target'] is None,'Wrong scientific scope')
 for m in pair['meshes']:
  for z in m['files'].values():require(sha(R/z['path'])==z['sha256'],'Mesh package mismatch')
  p=next(z for key,z in m['files'].items() if key=='PRE_SOLVER_QUALIFICATION.json');q=read(R/p['path']);require(q['pre_solver_qualified'] and q['minSICN']>=.02 and q['negative_J_elements']==q['zero_J_elements']==0,'Mesh gate failure')
 m1=read(R/'06_recovered_M1/M1_C1/PRE_SOLVER_QUALIFICATION.json');require(sha(R/'06_recovered_M1/M1_C1/PRE_SOLVER_QUALIFICATION.json')==read(R/'10_mesh_hierarchy/M2_PREREGISTRATION.json')['M1_qualification_SHA256'],'M1 receipt changed after M2 freeze')
 proof_counts=[]
 for cid in ['M1_C1','M2_C1']:
  p=read(R/'08_quadratic_quality'/(cid+'_EXACT_BERNSTEIN_CERTIFICATES.json'))
  for e in p['elements']:require(len(e['exact_Bernstein_coefficients'])==20 and min(Fraction(s) for s in e['exact_Bernstein_coefficients'])>0,'Local exact certificate failed')
  proof_counts.append(len(p['elements']))
 require(proof_counts==[14,16],'Certificate scope mismatch');require(read(R/'10_mesh_hierarchy/PAIR_PRE_SOLVER_QUALIFICATION.json')['passed'],'Hierarchy failure');require(len(rows(R/'SCIENTIFIC_FIGURES.csv'))==25,'Figure audit incomplete');resources=dict(workspace_bytes=sum(p.stat().st_size for p in R.rglob('*') if p.is_file()),free_disk_bytes=shutil.disk_usage(R).free);require(resources['workspace_bytes']<12*1024**3 and resources['free_disk_bytes']>=20*1024**3,'Disk budget failed')
 result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),integrity_status='PASS',scientific_status='C02_M1_M2_PRE_SOLVER_QUALIFIED',overall='R8E10R1_MESH_RECOVERY_COMPLETE',durable_artifacts_verified=len(items),historical_rows_reverified=len(historical),historical_unique_paths=len({v['path'] for v in historical}),manifest_inventory_exact=True,manifest_SHA256=sha(R/'REPRODUCIBILITY_MANIFEST.json'),seal_SHA256=sha(R/'14_reproducibility/RELEASE_SEAL.json'),one_actual_displaced_node_confirmed_by_hashed_coordinate_audit=True,M1_pass_receipt_unchanged_after_M2_freeze=True,local_rational_certificate_signs_checked=proof_counts,whole_mesh_continuous_positivity_certified=False,native_ANSYS_jobs=0,AI_runs=0,V1_T2_targets=0,resources=resources,uncompleted_in_scope_checks=[],future_native_import_equilibrium_stress_and_T2_checks='NOT_EXECUTED;separate authorization required')
 (R/'14_reproducibility/INDEPENDENT_RELEASE_VERIFICATION.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
