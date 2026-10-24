"""Record exact reuse of scientific kernels; no scientific execution."""
from setup_e11r1 import *
def main():
 exact=['quality_r1.py','acceptance_r1.py','fidelity_math_r1.py','reference_r1.py','bernstein_r1.py','recover_r2.py','t2_r2.py','pair_native_r3.py','schema_check_r3.py','mesh_r3.py','protocol_core.py','gate_r2.py','preflight_r2.py']
 result=[]
 for n in exact:
  old=sha(H3/'src'/n);new=sha(R/'src'/n);assert old==new,n;result.append(dict(module=n,old_R3_SHA256=old,new_R1_SHA256=new,byte_identical=True,scope='ScientificgeometrymeshBVPtensorT2kernelreusedunchanged'))
 write(R/'25_reproducibility/SCIENTIFIC_KERNEL_REUSE.json',dict(UTC=now(),modules=result,numerical_parameter_changes=0,selection_rerun=False,administrative_adaptations=dict(common_r3='Independentroot,canonicalqueue,prospective24GiBcap,operationresourceledger;scientificlimitsunchanged',solve_r2='ExistingE11authorization10SOLVEs;durablecompletionstatusandgloballedger;decksandphysicsunchanged',geometry_e10='Separateprospectiveconstructionandfidelitytimingonly',complete_metrics_r3='Canonicalper-sourcehistoricalprovenancepathandadditionalpackagemetadataonly'),new_controller='Sequentialstagecheckpointsand2sresourceobservations;neverrepeatscompletednativejobs',unused_copied_reference_modules=['initialize_r3.py','adapt_reference_r3.py','historical_r3.py','evidence_r3.py','reports_r3.py','figures_r3.py','seal_release_r3.py','verify_release_r3.py','repair_diagnosis_r3.py']))
 print('13scientifickernelsbyte-identicaltoqualifiedR3')
if __name__=='__main__':main()
