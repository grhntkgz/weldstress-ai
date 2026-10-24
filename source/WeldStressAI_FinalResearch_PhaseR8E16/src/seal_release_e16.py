from common_e16 import *
def fresh(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for chunk in iter(lambda:f.read(8*1024**2),b''):h.update(chunk)
 return h.hexdigest()
def main():
 verify_protocol();assert read(R/'22_reproducibility/PRESEAL_COMPLETE.json')['passed'];assert read(R/'19_scientific_figures/VISUAL_REVIEW.json')['passed'];assert read(R/'18_independent_verification/INDEPENDENT_PASS.json')['passed'];assert read(R/'18_independent_verification/RUNTIME_PASS.json')['passed'];gate()
 excluded={'REPRODUCIBILITY_MANIFEST.json','22_reproducibility/RELEASE_SEAL.json','22_reproducibility/DELIVERY_VERIFICATION.json'};files=[]
 for p in sorted(R.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(R).as_posix()
  if rel in excluded:continue
  files.append(dict(path=rel,bytes=p.stat().st_size,SHA256=fresh(p)))
 manifest=dict(UTC=now(),root=str(R),scope='all current R16 files including dependencies, logs, failed setup record and retained temporary artifacts, except three explicitly circular release files',excluded=sorted(excluded),historical_scope='consumed critical artifacts freshly verified in00_integrity/TERMINAL_HISTORICAL_HASH_AUDIT.csv; not a new rehash of every unconsumed historical bulk CSV',preregistration_SHA256=fresh(R/'PREREGISTRATION_SEAL.json'),files=files);write(R/'REPRODUCIBILITY_MANIFEST.json',manifest);mh=fresh(R/'REPRODUCIBILITY_MANIFEST.json');write(R/'22_reproducibility/RELEASE_SEAL.json',dict(UTC=now(),manifest_SHA256=mh,files=len(files),bytes=sum(a['bytes'] for a in files)))
 # A second file-stream hashing pass verifies actual delivery bytes independently of the cache helper.
 for a in files:
  p=R/a['path'];assert p.stat().st_size==a['bytes'] and fresh(p)==a['SHA256'],str(p)
 assert fresh(R/'REPRODUCIBILITY_MANIFEST.json')==mh;receipt=dict(UTC=now(),passed=True,manifest_SHA256=mh,verified_files=len(files),verified_bytes=sum(a['bytes'] for a in files),scientific_decision=read(R/'21_reports/SCIENTIFIC_DECISION.json')['scientific_result'],historical_integrity='HISTORICAL_V1_AND_MODELS_VERIFIED',feature_mechanisms='BLOCKWISE_MECHANISM_AUDIT_COMPLETE',feature_contract='OBSERVABLE_GEOMETRY_CONTRACT_QUALIFIED',N3_training='N3_TEN_RUNS_COMPLETE',XGBoost='XGBOOST_FIVE_FOLDS_COMPLETE',manuscript='MANUSCRIPT_DRAFT_COMPLETE',independent_external_validation='NOT_ESTABLISHED',physical_stress_validation='NOT_ESTABLISHED',research_closed=True,uncompleted_mandatory_checks=[],public_deposit='NOT_PERFORMED',human_editorial_and_author_review='REQUIRED_BEFORE_SUBMISSION',resource=gate());write(R/'22_reproducibility/DELIVERY_VERIFICATION.json',receipt);print(json.dumps(receipt,indent=2),flush=True)
if __name__=='__main__':main()
