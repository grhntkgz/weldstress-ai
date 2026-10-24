from setup_e11r1 import *
def main():
 assert read(R/'HISTORICAL_RELEASE_HASHES.json')['status']=='PASS'
 e3=B/'WeldStressAI_SingleSurface_Transfer_PhaseR8E3';h1=B/'WeldStressAI_V1_Expansion_PhaseR8E11R1';q=read(e3/'00_protocol/QUARANTINE.json');elig=rows(E9/'SOURCE_ELIGIBILITY.csv');reg=rows(h1/'CUMULATIVE_QUALIFIED_V1_TARGET_REGISTRY.csv');assert len(reg)==8
 hashes=[]
 for a in reg:
  p=Path(a['qualified_M2_target_path']);actual=sha(p);assert actual==a['qualified_M2_target_SHA256'];hashes.append(dict(source_id=a['source_id'],target_path=str(p),target_hash=actual))
 ids={a['source_id'] for a in reg};allowed={a['specimen_id'] for a in elig if a['source_geometry_screen_pass']=='True'};assert len(elig)==47 and {a['specimen_id'] for a in elig}==set(q['development_IDs']);assert not set(q['development_IDs'])&set(q['historical_test_IDs']);assert len(allowed)==42 and ids<=allowed and len(allowed-ids)==34
 t=(R/'00_integrity/E9_46_TESTS.log').read_text();assert 'Ran 46 tests' in t and t.rstrip().endswith('OK')
 kernels=[]
 for n in ['quality_r1.py','acceptance_r1.py','fidelity_math_r1.py','reference_r1.py','bernstein_r1.py','recover_r2.py','t2_r2.py','pair_native_r3.py','schema_check_r3.py','mesh_r3.py','protocol_core.py','gate_r2.py','preflight_r2.py']:
  a=sha(H3/'src'/n);b=sha(R/'src'/n);assert a==b;kernels.append(dict(module=n,historical_SHA256=a,new_SHA256=b,byte_identical=True))
 write(R/'00_integrity/SCIENTIFIC_KERNEL_REUSE.json',dict(UTC=now(),modules=kernels,scientific_parameter_changes=0));table(R/'HISTORICAL_V1_TARGET_HASHES.csv',hashes);table(R/'VERIFIED_V1_SOURCE_REGISTRY.csv',reg)
 write(R/'00_integrity/PRE_PROVENANCE_RECONCILIATION.json',dict(UTC=now(),status='PASS',development=47,eligible=42,excluded=5,remaining=34,historical_targets=8,tests=46,quarantine=q['historical_test_IDs'],remaining_IDs=sorted(allowed-ids)))
 print('RECONCILED47_42_5_8_34',flush=True)
if __name__=='__main__':main()
