from common_e14 import *
import subprocess,traceback
def main():
 while not (R/'00_integrity/G2_G3_G4_CONTEXT_PASS.json').exists():
  text=(R/'00_integrity/prepare_contexts.log').read_text(encoding='utf-8-sig')
  if 'Traceback' in text:raise RuntimeError('GEOMETRY_PREPARATION_FAILED')
  time.sleep(10)
 for module,log in [('audit_visibility_e14.py','visibility_audit.log'),('campaign_e14.py','campaign.log')]:
  with (R/'20_reproducibility'/log).open('x',encoding='utf8') as f:r=subprocess.run([sys.executable,'-B','-u',str(R/'src'/module)],stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  assert r.returncode==0,(module,log)
 print('PIPELINE_EXECUTIONS_COMPLETE',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:write(R/'20_reproducibility/LAUNCHER_STOP.json',dict(UTC=now(),error=str(e),traceback=traceback.format_exc()));raise
