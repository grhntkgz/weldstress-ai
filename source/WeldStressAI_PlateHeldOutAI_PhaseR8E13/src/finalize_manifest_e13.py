"""Close the explicit active-log self-reference; preserve the initial candidate seal."""
from common_e13 import *
def main():
 verify_seal();assert read(R/'21_reproducibility/DELIVERY_VERIFICATION.json')['integrity_status']=='PASS';archive=R/'21_reproducibility/initial_manifest_candidate';assert not archive.exists();archive.mkdir()
 for p in [R/'REPRODUCIBILITY_MANIFEST.json',R/'21_reproducibility/RELEASE_SEAL.json',R/'21_reproducibility/seal.log']:shutil.copyfile(p,archive/p.name)
 write(R/'21_reproducibility/MANIFEST_ADMIN_AMENDMENT.json',dict(UTC=now(),reason='The active sealing stdout log was initially listed at zero bytes before final stdout was flushed; explicitly exclude this self-referential log and retain the candidate manifest',initial_candidate_archive=str(archive),training_changes=0,prediction_changes=0,metric_changes=0))
 exclusions=['REPRODUCIBILITY_MANIFEST.json','21_reproducibility/RELEASE_SEAL.json','21_reproducibility/FINAL_READONLY_VERIFICATION.log','21_reproducibility/INDEPENDENT_RELEASE_RECEIPT.json','21_reproducibility/seal.log','21_reproducibility/finalize_manifest.log'];files=[]
 for p in sorted(R.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(R).as_posix()
  if rel in exclusions or rel.startswith('tmp/'):continue
  files.append(dict(path=rel,bytes=p.stat().st_size,sha256=sha(p)))
 write(R/'REPRODUCIBILITY_MANIFEST.json',dict(UTC=now(),scope='All durable E13 artifacts; historical work read-only',files=files,excluded=exclusions,temporary_excluded_prefix='tmp/',historical_E12_manifest_SHA256=sha(E12/'REPRODUCIBILITY_MANIFEST.json'),preregistration_seal_SHA256=sha(R/'PREREGISTRATION_SEAL.json')))
 write(R/'21_reproducibility/RELEASE_SEAL.json',dict(UTC=now(),manifest_SHA256=sha(R/'REPRODUCIBILITY_MANIFEST.json'),durable_files=len(files),durable_bytes=sum(a['bytes'] for a in files),counts_SHA256=sha(R/'R8E13_FINAL_COUNTS.json'),integrity_status='PASS'))
 print('FINAL_MANIFEST_SEALED',len(files),sha(R/'REPRODUCIBILITY_MANIFEST.json'),flush=True)
if __name__=='__main__':main()
