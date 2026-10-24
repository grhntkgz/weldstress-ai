"""Build an independent E12 release audit from qualified read-only scalar checks."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def main():
 s=(R/'src/verify_release_e11r1.py').read_text();s=s.replace("P=R.parent/'WeldStressAI_V1_Expansion_PhaseR8E11'","P=R.parent/'WeldStressAI_V1_Expansion_PhaseR8E11R1'")
 start=s.index(" parent=read(R/'PARENT_PROTOCOL_HASHES.json')");end=s.index(" final=read(R/'R8E11R1_FINAL_COUNTS.json')",start)
 s=s[:start]+''' for a in read(R/'PREREGISTRATION_SEAL.json')['files']:assert sha(R/a['path'])==a['sha256']
 gate=read(R/'RESOURCE_GATE_DECISION.json');assert gate['decision']=='RESOURCE_PREFLIGHT_PASS' and all(gate['checks'].values())
 queue=rows(R/'FROZEN_SELECTED_FIVE_SOURCES.csv');assert len(queue)==5 and len({a['source_id'] for a in queue})==5
 for a in read(R/'SOURCE_SELECTION_SEAL.json')['files']:assert sha(R/a['path'])==a['sha256']
 from selection_audit_e12 import audit_selection
 audit_selection()
 from audit_lineage_e12 import audit_lineage
 assert audit_lineage()['status']=='PASS'
 for a in rows(R/'25_reproducibility/ORIGINAL_ARCHIVE_SHA256_VERIFICATION.csv'):assert sha(a['path'])==a['expected_SHA256']==a['actual_SHA256']
 for a in read(R/'00_integrity/SCIENTIFIC_KERNEL_REUSE.json')['modules']:assert sha(R/'src'/a['module'])==a['new_SHA256']==a['historical_SHA256']
'''+s[end:]
 s=s.replace("R/'R8E11R1_FINAL_COUNTS.json'","R/'R8E12_FINAL_COUNTS.json'").replace('len(reg)==3+len(new)','len(reg)==8+len(new)')
 start=s.index(" assert read(P/'R8E11_FINAL_COUNTS.json')");end=s.index(" test=(R/",start);s=s[:start]+s[end:]
 s=s.replace("['R2_READONLY_VERIFICATION.log','R3_READONLY_VERIFICATION.log','E11_READONLY_VERIFICATION.log']","['R2_READONLY_VERIFICATION.log','R3_READONLY_VERIFICATION.log','E11_READONLY_VERIFICATION.log','E11R1_READONLY_VERIFICATION.log']")
 start=s.index(" spec=(R/'01_protocol_freeze/USER_SPECIFICATION.txt')");end=s.index(' from PIL import Image',start)
 s=s[:start]+''' spec=(R/'R8E12_USER_SPECIFICATION.txt').read_text(encoding='utf-8-sig');required=re.findall(r'\\x60([^\\x60]+\\.(?:md|json|csv))\\x60',spec.split('# 27. REQUIRED REPORTS')[1].split('# 29.')[0]);assert all((R/n).exists() for n in required);assert len(re.findall(r'^### \\d+\\.',(R/'R8E12_MASTER_REPORT.md').read_text(),re.M))==56
'''+s[end:]
 s=s.replace("sole_amendment='workspace16to24GiB',selection_copied_exactly=True,amendment_before_production=True","prospective_E12_authorization=True,selection_independently_replayed=True,selection_before_production=True").replace('questions_explicitly_answered=45','questions_explicitly_answered=56')
 s=s.replace("  if sid not in qualified:\n   assert (R/'21_reproducibility/CAMPAIGN_STOP.json').exists();continue",'''  if sid not in qualified:
   assert (R/'21_reproducibility/CAMPAIGN_STOP.json').exists()
   for a in ls:
    if a.get('log_SHA256'):assert sha(c/(a['stage']+'.log'))==a['log_SHA256']
   nl=read(c/'17_reproducibility/NATIVE_INVOCATION_LEDGER.json') if (c/'17_reproducibility/NATIVE_INVOCATION_LEDGER.json').exists() else []
   preprocessing+=sum(a['kind'].startswith('PREPROCESS') for a in nl)
   invoked=[a for a in nl if a['kind']=='SOLVE'];assert len(invoked)<=2 and len({a['level'] for a in invoked})==len(invoked)
   for a in invoked:
    l=a['level'];observed_stage_order.append((sid,l));fol=c/('06_native_M1' if l=='M1' else '07_native_M2');assert sha(fol/'input.dat')==a['input_sha256']
    if (fol/'SOLVE_COMPLETE.json').exists():
     comp=read(fol/'SOLVE_COMPLETE.json');assert comp['completed'] and comp['equilibrium_passed'] and comp['native_errors']==0
     for name,h in comp['files'].items():assert sha(fol/name)==h
     solve_success+=1
   continue''')
 # Fresh SHA reads once per unchanged unique file within this verification pass.
 start=s.index('def sha(p):');end=s.index('def independent_quantile',start)
 s=s[:start]+'''_hash_cache={}
def sha(p):
 p=Path(p).resolve();st=p.stat();key=(str(p),st.st_size,st.st_mtime_ns)
 if key not in _hash_cache:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
  assert p.stat().st_mtime_ns==st.st_mtime_ns and p.stat().st_size==st.st_size
  _hash_cache[key]=h.hexdigest()
 return _hash_cache[key]

'''+s[end:]
 s=s.replace(" if '--write-receipt' in sys.argv:"," out.update(minimum_sampled_available_RAM_bytes=min(int(a['RAM_available_bytes']) for a in samples),minimum_sampled_available_commit_bytes=min(int(a['commit_free_bytes']) for a in samples))\n if '--write-receipt' in sys.argv:")
 (R/'src/verify_release_e12.py').write_text(s)
if __name__=='__main__':main()
