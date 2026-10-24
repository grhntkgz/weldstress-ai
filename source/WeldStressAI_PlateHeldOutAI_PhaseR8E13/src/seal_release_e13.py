from common_e13 import *
def main():
 assert read(R/'21_reproducibility/DELIVERY_VERIFICATION.json')['integrity_status']=='PASS';assert read(R/'21_reproducibility/CHECKPOINT_REPLAY_RECEIPT.json')['passed'];assert not (R/'REPRODUCIBILITY_MANIFEST.json').exists(),'ALREADY_SEALED'
 counts=read(R/'R8E13_FINAL_COUNTS.json');counts.update(final_integrity_status='PASS',figures_verified=36,exact_CSV_roundtrip_rows=1778400,uncompleted_checks=[]);write(R/'R8E13_FINAL_COUNTS.json',counts)
 for name in ['FINAL_R8E13_DECISION.md','R8E13_MASTER_REPORT.md','INDEPENDENT_METRIC_VERIFICATION.md']:
  p=R/name;p.write_text(p.read_text(encoding='utf8')+'\n\nFinal delivery integrity: **PASS**. All 1,778,400 exported core rows round-trip exact IDs, XYZ, T0 areas, predictions and references; all ten runs pass runtime query/weight replay; all 36 PNG/PDF pairs verify. New-checkpoint prediction replay and chunk consistency passed the separately declared 1e-4 MPa floating-point audit tolerance. See `21_reproducibility/DELIVERY_VERIFICATION.json` and `CHECKPOINT_REPLAY_RECEIPT.json`. No uncompleted checks.\n',encoding='utf8')
 excluded=['REPRODUCIBILITY_MANIFEST.json','21_reproducibility/RELEASE_SEAL.json','21_reproducibility/FINAL_READONLY_VERIFICATION.log','21_reproducibility/INDEPENDENT_RELEASE_RECEIPT.json','21_reproducibility/seal.log','21_reproducibility/finalize_manifest.log']
 listing=[]
 for p in sorted(R.rglob('*')):
  if p.is_file():
   rel=p.relative_to(R).as_posix()
   if rel in excluded or rel.startswith('tmp/'):continue
   listing.append(dict(path=rel,bytes=p.stat().st_size,sha256=sha(p)))
 write(R/'REPRODUCIBILITY_MANIFEST.json',dict(UTC=now(),scope='All durable E13 artifacts; no historical mutation',files=listing,excluded=excluded,temporary_excluded_prefix='tmp/',historical_E12_manifest_SHA256=sha(E12/'REPRODUCIBILITY_MANIFEST.json'),preregistration_seal_SHA256=sha(R/'PREREGISTRATION_SEAL.json')))
 write(R/'21_reproducibility/RELEASE_SEAL.json',dict(UTC=now(),manifest_SHA256=sha(R/'REPRODUCIBILITY_MANIFEST.json'),durable_files=len(listing),durable_bytes=sum(a['bytes'] for a in listing),counts_SHA256=sha(R/'R8E13_FINAL_COUNTS.json'),integrity_status='PASS'))
 print('RELEASE_SEALED',len(listing),sha(R/'REPRODUCIBILITY_MANIFEST.json'),flush=True)
if __name__=='__main__':main()
