from common_e16 import *
import subprocess
PY=O/'WeldScan_MechanicalBenchmark_Phase5E/.venv/Scripts/python.exe'
def main():
 assert read(R/'22_reproducibility/EXPERIMENT_MATRIX_COMPLETE.json')['passed']
 for script,receipt in [('score_e16.py',R/'18_independent_verification/SCORING_COMPLETE.json'),('independent_e16.py',R/'18_independent_verification/INDEPENDENT_PASS.json'),('runtime_audit_e16.py',R/'18_independent_verification/RUNTIME_PASS.json'),('report_e16.py',R/'20_manuscript/DRAFT_GENERATED.json'),('figures_e16.py',R/'19_scientific_figures/FIGURES_COMPLETE.json'),('closeout_e16.py',R/'22_reproducibility/PRESEAL_COMPLETE.json')]:
  if receipt.exists():print('POST_RECEIPT_EXISTS',script,flush=True);continue
  gate();log=R/'22_reproducibility'/('post_'+script.removesuffix('.py')+'.log');print('POST_START',script,now(),flush=True)
  with log.open('w',encoding='utf8',buffering=8*1024**2) as f:rc=subprocess.call([str(PY),'-B','-u',str(R/'src'/script)],stdout=f,stderr=subprocess.STDOUT,cwd=R)
  assert rc==0 and receipt.exists(),str(log);print('POST_COMPLETE',script,now(),flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:write(R/'22_reproducibility/POSTPROCESSING_BLOCKED.json',dict(UTC=now(),error=str(e)));raise
