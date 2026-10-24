"""Administrative adapters only; scientific kernels are independently hash-compared."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def main():
 p=R/'src/complete_metrics_r3.py';s=p.read_text();s=s.replace("physical_independence='UNCERTIFIED'","physical_independence='PHYSICAL_INDEPENDENCE_UNRESOLVED'").replace('FrozenR3_isoparametric_V1_reused_E11R1','FrozenR3_isoparametric_V1_reused_E12');p.write_text(s)
 # The inherited helper module only supplies serialization; never run its obsolete amendment main.
 p=R/'src/aggregate_e11r1.py';s=p.read_text().replace("from setup_e11r1 import *","from setup_e11r1 import *\nP=B/'WeldStressAI_V1_Expansion_PhaseR8E11R1'")
 start=s.index(' # Enrich historical rows only');end=s.index(' reg+=new;',start);s=s[:start]+" reg.extend(old)\n"+s[end:];s=s.replace("qualification_status='QUALIFIED_NEW_E11R1'","qualification_status='QUALIFIED_NEW_E12'").replace("physical_independence='UNCERTIFIED'","physical_independence='PHYSICAL_INDEPENDENCE_UNRESOLVED'").replace("R/'R8E11R1_FINAL_COUNTS.json'","R/'R8E12_FINAL_COUNTS.json'")
 p=R/'src/aggregate_e12.py';p.write_text(s)
 # Read-only repair audit also works with empty repair ledgers.
 p=R/'src/repair_audit_e11r1.py';s=p.read_text();(R/'src/repair_audit_e12.py').write_text(s)
 print('E12_ADMINISTRATIVE_ADAPTATION_READY')
if __name__=='__main__':main()
