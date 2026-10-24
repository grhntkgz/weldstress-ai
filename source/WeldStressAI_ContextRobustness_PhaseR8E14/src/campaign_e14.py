from common_e14 import *
import subprocess,traceback
def worker(module,args,name):
 start=time.monotonic();log=R/'20_reproducibility'/(name+'.log');assert not log.exists()
 with log.open('x',encoding='utf8') as f:r=subprocess.run([sys.executable,'-B','-u',str(R/'src'/module),*args],stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 ledger=rows(R/'EXECUTION_BUDGET_LEDGER.csv') if (R/'EXECUTION_BUDGET_LEDGER.csv').exists() else [];ledger.append(dict(UTC=now(),module=module,args=json.dumps(args),name=name,exit_code=r.returncode,elapsed_s=time.monotonic()-start,new_scheduled_fit=int(module=='train_e14.py' and '--dry' not in args),dryrun_optimizer_steps=int('--dry' in args),native_FE_jobs=0,external_jobs=0,log=str(log)));table(R/'EXECUTION_BUDGET_LEDGER.csv',ledger);assert r.returncode==0,('WORKER_FAILED',name,str(log))
def main():
 verify_protocol();assert read(R/'00_integrity/G2_G3_G4_CONTEXT_PASS.json')['passed']
 for i in range(1,6):
  for seed in [20261021,20261022]:
   write(R/'20_reproducibility/PIPELINE_STATE.json',dict(UTC=now(),stage='FROZEN_N1_INFERENCE',fold='F'+str(i),seed=seed));worker('infer_e14.py',['--model','N1','--fold','F'+str(i),'--seed',str(seed)],'N1_F'+str(i)+'_s'+str(seed))
 write(R/'00_integrity/G5_N1_COMPLETE.json',dict(UTC=now(),passed=True,checkpoint_condition_executions=40,source_seed_condition_predictions=104,new_training_runs=0))
 worker('train_e14.py',['--dry'],'N2_dryrun');assert read(R/'17_independent_audits/TRAINING_DRY_RUN.json')['passed']
 for i in range(1,6):
  fold='F'+str(i)
  for seed in [20261021,20261022]:
   assert len(list((R/'11_context_robust_training').glob('F*_s*/STARTED.json')))<10;gate();write(R/'20_reproducibility/PIPELINE_STATE.json',dict(UTC=now(),stage='N2_TRAINING',fold=fold,seed=seed,completed=len(list((R/'11_context_robust_training').glob('F*_s*/COMPLETED.json')))));worker('train_e14.py',['--fold',fold,'--seed',str(seed)],'N2_'+fold+'_s'+str(seed)+'_train')
  for seed in [20261021,20261022]:worker('infer_e14.py',['--model','N2','--fold',fold,'--seed',str(seed)],'N2_'+fold+'_s'+str(seed)+'_infer')
 write(R/'20_reproducibility/PIPELINE_STATE.json',dict(UTC=now(),stage='ALL_SCHEDULED_EXECUTIONS_COMPLETE',new_fits=10,new_FE=0,external=0));print('ALL_SCHEDULED_EXECUTIONS_COMPLETE',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:write(R/'20_reproducibility/CAMPAIGN_STOP.json',dict(UTC=now(),error=str(e),traceback=traceback.format_exc()));raise
