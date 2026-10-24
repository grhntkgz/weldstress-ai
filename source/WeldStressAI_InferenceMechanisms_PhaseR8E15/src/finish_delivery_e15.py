from common_e15 import *
import subprocess
PY=O/'WeldScan_MechanicalBenchmark_Phase5E/.venv/Scripts/python.exe'

def main():
 assert read(R/'18_independent_verification/INDEPENDENT_PASS.json')['passed'];assert (R/'FINAL_R8E15_DECISION.md').exists()
 for name in ['export_e15.py','figures_e15.py','contact_e15.py','verify_delivery_e15.py']:
  gate();log=R/'21_reproducibility'/(name.replace('.py','')+'_final.log')
  with log.open('w',encoding='utf8') as f:p=subprocess.run([str(PY),'-B','-u',str(R/'src'/name)],stdout=f,stderr=subprocess.STDOUT)
  if p.returncode:write(R/'21_reproducibility/DELIVERY_STOP.json',dict(UTC=now(),script=name,exit_code=p.returncode,log=str(log)));raise RuntimeError(name)
  print('DELIVERY_STAGE_COMPLETE',name,flush=True)
 write(R/'21_reproducibility/CLOSEOUT_READY.json',dict(UTC=now(),passed=True,status='READY_FOR_VISUAL_AND_RELEASE_AUDIT'));print('DELIVERY_READY',flush=True)
if __name__=='__main__':main()
