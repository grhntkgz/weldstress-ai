"""Seal actual durable artifacts and run the independent scalar release verifier once."""
from setup_e11r1 import *
import importlib.util,sys,psutil
def main():
 assert not any((p.info['name'] or '').lower()=='ansys231.exe' for p in psutil.process_iter(['name']))
 from prepare_verifier_e12 import main as prepare
 prepare();spec=importlib.util.spec_from_file_location('final_independent_e12',R/'src/verify_release_e12.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
 required=[];text=(R/'R8E12_USER_SPECIFICATION.txt').read_text(encoding='utf-8-sig');import re
 required=re.findall(r'\x60([^\x60]+\.(?:md|json|csv))\x60',text.split('# 27. REQUIRED REPORTS')[1].split('# 29.')[0]);assert all((R/n).exists() for n in required if n!='REPRODUCIBILITY_MANIFEST.json')
 after=[]
 for a in rows(R/'00_integrity/HISTORICAL_HASHES.csv'):
  actual=v.sha(a['path']);assert actual==a['sha256'];after.append(dict(path=a['path'],expected_sha256=a['sha256'],actual_sha256=actual,passed=True))
 for a in rows(R/'00_integrity/HISTORICAL_SEAL_RECEIPT_SNAPSHOT.csv'):
  actual=v.sha(a['path']);assert actual==a['sha256'];after.append(dict(path=a['path'],expected_sha256=a['sha256'],actual_sha256=actual,passed=True))
 table(R/'25_reproducibility/HISTORICAL_AFTER_CHECK.csv',after)
 for a in read(R/'00_integrity/SCIENTIFIC_KERNEL_REUSE.json')['modules']:assert v.sha(R/'src'/a['module'])==a['new_SHA256']==a['historical_SHA256']
 from audit_lineage_e12 import audit_lineage
 write(R/'25_reproducibility/INDEPENDENT_LINEAGE_VERIFICATION.json',dict(UTC=now(),**audit_lineage()))
 first=rows(R/'FROZEN_SELECTED_FIVE_SOURCES.csv')[0];original=read(Path(first['package_path'])/'geometry_provenance.json');archive=R.parent.parent/'WeldScan-FEA/data/raw/scan_geometry.zip';actual_archive=v.sha(archive);assert actual_archive==original['source_archive_sha256']
 archive_checks=[]
 for a in read(R.parent.parent/'WeldScan-FEA/data/metadata/manifest.json'):
  path=archive.parent/a['name'];actual=v.sha(path);assert actual==a['sha256'];archive_checks.append(dict(path=str(path),expected_SHA256=a['sha256'],actual_SHA256=actual,passed=True,scope='Wholeoriginalsourcefilebytehash;noexperimentalFEorAIperformancevaluesusedforselection'))
 table(R/'25_reproducibility/ORIGINAL_ARCHIVE_SHA256_VERIFICATION.csv',archive_checks)
 protocol=read(R/'R8E12_PROTOCOL_HASHES.json');baseline=read(R.parent/'WeldStressAI_V1_Expansion_PhaseR8E11R1/R8E10R3_PROTOCOL_HASHES.json')
 for k in ['UTC','source_order','source_hashes','selection_queue_SHA256','selection_declaration_SHA256']:protocol.pop(k,None);baseline.pop(k,None)
 assert protocol==baseline,'Scientific protocol must remain identical after explicit source/selection administrative fields'
 import common_r3
 common_r3.SID='PHASE_CLOSEOUT'
 from common_r3 import resource_gate
 m=resource_gate();write(R/'25_reproducibility/FINAL_RESOURCE_SNAPSHOT.json',dict(UTC=now(),system=m,C_free_bytes=shutil.disk_usage('C:/').free,remaining_eligible=read(R/'R8E12_FINAL_COUNTS.json')['remaining_eligible'],historical_files_deleted=False,temporary_IO_scope='ControlledTEMP/TMPunderE12;noexternalattributablescratchconfigured;notasystemwideIOtrace'))
 excluded=['REPRODUCIBILITY_MANIFEST.json','REPRODUCIBILITY_MANIFEST.csv','25_reproducibility/RELEASE_SEAL.json','25_reproducibility/INDEPENDENT_RELEASE_VERIFICATION.json'];files=[]
 for p in sorted(R.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(R).as_posix()
  if rel in excluded or rel.startswith('tmp/'):continue
  files.append(dict(path=rel,bytes=p.stat().st_size,sha256=v.sha(p)))
 table(R/'REPRODUCIBILITY_MANIFEST.csv',files);write(R/'REPRODUCIBILITY_MANIFEST.json',dict(UTC=now(),scope='All durable new E12 artifacts;historyread-only',excluded=excluded,temporary_excluded_prefix='tmp/',files=files));write(R/'25_reproducibility/RELEASE_SEAL.json',dict(UTC=now(),manifest_SHA256=v.sha(R/'REPRODUCIBILITY_MANIFEST.json'),CSV_SHA256=v.sha(R/'REPRODUCIBILITY_MANIFEST.csv'),durable_files=len(files),required_names=len(required)))
 sys.argv=['verify_release_e12.py','--write-receipt'];v.main();receipt=read(R/'25_reproducibility/INDEPENDENT_RELEASE_VERIFICATION.json');receipt.update(fresh_unique_SHA256_file_reads=len(v._hash_cache),cache_policy='Within this single release verification pass only; fresh SHA256 per unique unchanged path/size/mtime, stat before/after; expected hashes never substituted for reads',physical_lineage_status=read(R/'R8E12_FINAL_COUNTS.json')['physical_lineage'],physical_independence='PHYSICAL_INDEPENDENCE_NOT_ESTABLISHED',overall_status='R8E12_PARTIAL');write(R/'25_reproducibility/INDEPENDENT_RELEASE_VERIFICATION.json',receipt);print('E12_RELEASE_SEALED_AND_VERIFIED',len(files),flush=True)
if __name__=='__main__':main()
