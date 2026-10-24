"""Full historical preservation check and immutable release manifest; no solver invocation."""
from setup_e11r1 import *
def main():
 assert not any((p.name().lower()=='ansys231.exe') for p in __import__('psutil').process_iter()),'Never seal during native job'
 counts=read(R/'R8E11R1_FINAL_COUNTS.json');assert counts['actual_native_SOLVE_invocations']<=10
 checks=[]
 for a in rows(R/'00_integrity/HISTORICAL_HASHES.csv'):
  h=sha(a['path']);assert h==a['sha256'],a['path'];checks.append(dict(path=a['path'],expected_sha256=a['sha256'],actual_sha256=h,passed=True))
 table(R/'25_reproducibility/HISTORICAL_AFTER_CHECK.csv',checks)
 required=re.findall(r'\x60([^\x60]+\.(?:md|json|csv))\x60',(R/'01_protocol_freeze/USER_SPECIFICATION.txt').read_text(encoding='utf-8-sig').split('# 24. REQUIRED REPORTS')[1].split('# 26.')[0]);missing=[n for n in required if not (R/n).exists() and n!='REPRODUCIBILITY_MANIFEST.json'];assert not missing,missing
 # Final resource snapshot includes all figures, reports and retained candidates.
 from common_r3 import resource_gate
 snapshot=resource_gate(ram=int(.25*GiB),commit=int(.25*GiB),disk=int(.1*GiB));write(R/'25_reproducibility/FINAL_RESOURCE_SNAPSHOT.json',dict(UTC=now(),resources=snapshot,native_jobs_active=0,cap_GiB=24,E_reserve_GiB=20,measurement='Directorysumandsystemsnapshot;notcontinuouspeak'))
 from resource_attribution_e11r1 import main as attribute
 attribute()
 excluded=['REPRODUCIBILITY_MANIFEST.json','REPRODUCIBILITY_MANIFEST.csv','25_reproducibility/RELEASE_SEAL.json','25_reproducibility/INDEPENDENT_RELEASE_VERIFICATION.json']
 files=[dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(R.rglob('*')) if p.is_file() and p.relative_to(R).as_posix() not in excluded and not p.relative_to(R).as_posix().startswith('tmp/')]
 table(R/'REPRODUCIBILITY_MANIFEST.csv',files);write(R/'REPRODUCIBILITY_MANIFEST.json',dict(UTC=now(),campaign=counts['campaign_status'],files=files,excluded=excluded,transient_exclusion='tmp/**;declaredlibraries/fontcacheonly;noscientificresultsexcluded',new_qualified_targets=counts['new_qualified_targets'],cumulative_qualified_targets=counts['cumulative_qualified_targets'],historical_workspaces_read_only=True))
 write(R/'25_reproducibility/RELEASE_SEAL.json',dict(UTC=now(),manifest_SHA256=sha(R/'REPRODUCIBILITY_MANIFEST.json'),CSV_SHA256=sha(R/'REPRODUCIBILITY_MANIFEST.csv'),amendment_seal_SHA256=sha(R/'AMENDMENT_PREREGISTRATION_SEAL.json'),files=len(files),actual_SOLVEs=counts['actual_native_SOLVE_invocations'],newtargets=counts['new_qualified_targets'],cumulativetargets=counts['cumulative_qualified_targets']))
 print('RELEASE_SEALED',len(files),'files',len(checks),'historicalbindings',flush=True)
if __name__=='__main__':main()
