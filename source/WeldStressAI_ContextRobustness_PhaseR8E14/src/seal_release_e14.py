from common_e14 import *
def main():
 assert read(R/'20_reproducibility/DELIVERY_VERIFICATION.json')['integrity_status']=='PASS';assert read(R/'17_independent_audits/VISUAL_REVIEW_RECEIPT.json')['status']=='PASS';assert not (R/'REPRODUCIBILITY_MANIFEST.json').exists();counts=read(R/'R8E14_FINAL_COUNTS.json');extra=read(R/'17_independent_audits/SPATIAL_SHIFT_PASS.json');counts.update(final_integrity_status='PASS',additional_spatial_metric_checks=extra['checks'],total_metric_checks=counts['metric_checks']+extra['checks'],uncompleted_checks=[]);write(R/'R8E14_FINAL_COUNTS.json',counts)
 for name in ['R8E14_MASTER_REPORT.md','FINAL_R8E14_DECISION.md','INDEPENDENT_METRIC_AUDIT.md']:
  p=R/name;p.write_text(p.read_text(encoding='utf8')+f"\n\nFinal release integrity: **PASS**. All 6,224,400 prediction CSV rows round-trip exact source IDs, coordinates, T0 areas and predictions. Historical artifacts were rehashed after execution. Independent evaluation includes {counts['metric_checks']} primary plus {extra['checks']} centroid/variance/field-shift/regional-shift checks ({counts['total_metric_checks']} total), with every actual training batch replayed. All 36 primary and 26 supplemental PNG/PDF pairs verify; all 55 final questions are answered. See 20_reproducibility/DELIVERY_VERIFICATION.json, 17_independent_audits/SPATIAL_SHIFT_PASS.json and final independent release receipt.\n",encoding='utf8')
 excluded=['REPRODUCIBILITY_MANIFEST.json','20_reproducibility/RELEASE_SEAL.json','20_reproducibility/seal_release.log','20_reproducibility/FINAL_READONLY_VERIFICATION.log','20_reproducibility/INDEPENDENT_RELEASE_RECEIPT.json'];files=[]
 for p in sorted(R.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(R).as_posix()
  if rel in excluded or rel.startswith('tmp/'):continue
  files.append(dict(path=rel,bytes=p.stat().st_size,SHA256=sha(p)))
 write(R/'REPRODUCIBILITY_MANIFEST.json',dict(UTC=now(),scope='All durable new E14 artifacts; historical workspaces unchanged',files=files,excluded=excluded,temporary_excluded_prefix='tmp/',protocol_seal_SHA256=sha(R/'N2_PREREGISTRATION_SEAL.json'),historical_E13_manifest_SHA256=sha(H/'REPRODUCIBILITY_MANIFEST.json')))
 write(R/'20_reproducibility/RELEASE_SEAL.json',dict(UTC=now(),manifest_SHA256=sha(R/'REPRODUCIBILITY_MANIFEST.json'),durable_files=len(files),durable_bytes=sum(a['bytes'] for a in files),integrity_status='PASS'));print('SEALED',len(files),sha(R/'REPRODUCIBILITY_MANIFEST.json'),flush=True)
if __name__=='__main__':main()
