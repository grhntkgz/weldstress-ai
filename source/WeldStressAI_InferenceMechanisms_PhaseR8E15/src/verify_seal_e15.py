from common_e15 import *

def main():
 verify_protocol();m=read(R/'REPRODUCIBILITY_MANIFEST.json');seal=read(R/'21_reproducibility/RELEASE_SEAL.json');assert sha(R/'REPRODUCIBILITY_MANIFEST.json')==seal['manifest_SHA256'];listed=set()
 for a in m['files']:
  p=R/a['path'];assert p.stat().st_size==a['bytes'] and sha(p)==a['SHA256'],a['path'];listed.add(a['path'])
 for p in R.rglob('*'):
  if p.is_file():
   rel=p.relative_to(R).as_posix();assert rel in listed or rel in m['excluded'] or rel.startswith('tmp/'),rel
 result=dict(UTC=now(),integrity_status='PASS',durable_files_verified=len(listed),durable_bytes_verified=seal['durable_bytes'],manifest_SHA256=sha(R/'REPRODUCIBILITY_MANIFEST.json'),verified_E13_E14_release_artifacts_unchanged=True,qualified_V1_targets_unchanged=True,historical_checkpoints_unchanged=True,training_fits=0,optimizer_steps=0,new_ANSYS=0,external_predictions=0,NORM_P='NOT_EXECUTED_INFEASIBLE',uncompleted_mandatory_checks=[],study='EXPLORATORY_MECHANISM_AUDIT');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
