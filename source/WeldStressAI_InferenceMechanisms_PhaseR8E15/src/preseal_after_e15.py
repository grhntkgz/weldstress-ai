from common_e15 import *
import subprocess
PY=O/'WeldScan_MechanicalBenchmark_Phase5E/.venv/Scripts/python.exe'

def main():
 deadline=time.monotonic()+7200
 while not (R/'21_reproducibility/CLOSEOUT_READY.json').exists():
  if (R/'21_reproducibility/CLOSEOUT_STOP.json').exists():raise RuntimeError('closeout stopped')
  assert time.monotonic()<deadline;time.sleep(10)
 for name in ['contact_e15.py','verify_delivery_e15.py']:
  with (R/'21_reproducibility'/(name.replace('.py','')+'.log')).open('w',encoding='utf8') as f:p=subprocess.run([str(PY),'-B','-u',str(R/'src'/name)],stdout=f,stderr=subprocess.STDOUT)
  if p.returncode:write(R/'21_reproducibility/PRESEAL_STOP.json',dict(UTC=now(),script=name,exit_code=p.returncode));raise RuntimeError(name)
  print('PRESEAL_STAGE_COMPLETE',name,flush=True)
 print('PRESEAL_VERIFICATION_COMPLETE',flush=True)
if __name__=='__main__':main()
