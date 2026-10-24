from common_e14 import *
import subprocess,traceback
def main():
 while True:
  if (R/'20_reproducibility/CAMPAIGN_STOP.json').exists() or (R/'20_reproducibility/LAUNCHER_STOP.json').exists():raise RuntimeError('EXECUTION_STOP_REQUIRES_AUDIT')
  p=R/'20_reproducibility/PIPELINE_STATE.json'
  if p.exists() and read(p)['stage']=='ALL_SCHEDULED_EXECUTIONS_COMPLETE':break
  time.sleep(10)
 for module in ['evaluate_e14.py','independent_e14.py','deliver_e14.py']:
  write(R/'20_reproducibility/CLOSEOUT_STATE.json',dict(UTC=now(),stage=module,status='RUNNING'));log=R/'20_reproducibility'/(module+'.log');assert not log.exists()
  with log.open('x',encoding='utf8') as f:result=subprocess.run([sys.executable,'-B','-u',str(R/'src'/module)],stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  assert result.returncode==0,('POSTPROCESSING_FAILED',module)
 write(R/'20_reproducibility/CLOSEOUT_STATE.json',dict(UTC=now(),stage='READY_FOR_VISUAL_QA_AND_RELEASE',status='READY'));print('READY_FOR_VISUAL_QA_AND_RELEASE',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:write(R/'20_reproducibility/CLOSEOUT_STOP.json',dict(UTC=now(),error=str(e),traceback=traceback.format_exc()));raise
