from common_e15 import *
import subprocess
PY=O/'WeldScan_MechanicalBenchmark_Phase5E/.venv/Scripts/python.exe'

def main():
 # Bounded prerequisite wait; independent authoring can proceed in the main session.
 deadline=time.monotonic()+7200
 while not (R/'21_reproducibility/INFERENCE_COMPLETE.json').exists():
  if (R/'21_reproducibility/CAMPAIGN_STOP.json').exists():raise RuntimeError('inference campaign stopped')
  assert time.monotonic()<deadline;time.sleep(10)
 for name in ['evaluate_e15.py','independent_e15.py','reports_e15.py','export_e15.py','figures_e15.py']:
  gate();log=R/'21_reproducibility'/(name.replace('.py','')+'.log')
  with log.open('w',encoding='utf8') as f:p=subprocess.run([str(PY),'-B','-u',str(R/'src'/name)],stdout=f,stderr=subprocess.STDOUT)
  if p.returncode:write(R/'21_reproducibility/CLOSEOUT_STOP.json',dict(UTC=now(),script=name,exit_code=p.returncode,log=str(log)));raise RuntimeError(name)
  print('CLOSEOUT_STAGE_COMPLETE',name,flush=True)
 write(R/'21_reproducibility/CLOSEOUT_READY.json',dict(UTC=now(),passed=True,status='READY_FOR_VISUAL_AND_RELEASE_AUDIT'));print('CLOSEOUT_READY',flush=True)
if __name__=='__main__':main()
