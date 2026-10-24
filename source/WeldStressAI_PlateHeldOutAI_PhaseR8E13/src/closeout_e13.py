from common_e13 import *
import subprocess,traceback
def main():
 while True:
  if (R/'21_reproducibility/CAMPAIGN_STOP.json').exists():raise RuntimeError('CAMPAIGN_STOP_REQUIRES_AUDIT')
  if (R/'07_metrics/SCORING_COMPLETE.json').exists():break
  time.sleep(10)
 for module,args in [('independent_metrics_e13.py',[]),('deliver_e13.py',[]),('audit_model_provenance_e13.py',[]),('verify_release_e13.py',['--preseal'])]:
  write(R/'21_reproducibility/CLOSEOUT_STATE.json',dict(UTC=now(),stage=module,status='RUNNING'))
  with (R/'21_reproducibility'/(module+'.log')).open('x',encoding='utf8') as f:result=subprocess.run([sys.executable,'-B','-u',str(R/'src'/module),*args],stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  assert result.returncode==0,('POSTPROCESS_FAILED',module)
 write(R/'21_reproducibility/CLOSEOUT_STATE.json',dict(UTC=now(),stage='AWAITING_VISUAL_QA_AND_FINAL_SEAL',status='READY'));print('CLOSEOUT_READY_FOR_VISUAL_QA',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:write(R/'21_reproducibility/CLOSEOUT_STOP.json',dict(UTC=now(),error=str(e),traceback=traceback.format_exc()));raise
