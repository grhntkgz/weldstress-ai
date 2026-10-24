from common_e14 import *
import subprocess,traceback
def main():
 while not (R/'20_reproducibility/DELIVERY_GENERATED.json').exists():
  if (R/'20_reproducibility/CLOSEOUT_STOP.json').exists():raise RuntimeError('DELIVERY_FAILED')
  time.sleep(10)
 assert read(R/'17_independent_audits/SPATIAL_SHIFT_PASS.json')['passed'];assert read(R/'20_reproducibility/FINAL_HISTORICAL_AUDIT.json')['passed']
 for module,args,log in [('visual_qa_e14.py',[],'visual_qa.log'),('verify_release_e14.py',['--preseal'],'preseal_verification.log')]:
  with (R/'20_reproducibility'/log).open('x',encoding='utf8') as f:r=subprocess.run([sys.executable,'-B','-u',str(R/'src'/module),*args],stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  assert r.returncode==0,(module,log)
 print('PRESEAL_VERIFICATION_COMPLETE',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:write(R/'20_reproducibility/PRESEAL_STOP.json',dict(UTC=now(),error=str(e),traceback=traceback.format_exc()));raise
