from common_e13 import *
import subprocess,traceback
def worker(name,args,log):
 start=time.monotonic()
 with (R/'05_training'/log).open('x',encoding='utf8') as f:r=subprocess.run([sys.executable,'-B','-u',str(R/'src'/name),*args],stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 ledger=read(R/'21_reproducibility/WORKERS.json') if (R/'21_reproducibility/WORKERS.json').exists() else []
 ledger.append(dict(module=name,args=args,log=log,exit_code=r.returncode,elapsed_s=time.monotonic()-start,UTC=now()));write(R/'21_reproducibility/WORKERS.json',ledger)
 assert r.returncode==0,('WORKER_FAILED',name,log)
def run():
 verify_seal();worker('train_e13.py',['--dry'],'dryrun.log');assert read(R/'TRAINING_DRY_RUN.json')['passed'];worker('baselines_e13.py',[],'baselines.log')
 for i,plate in enumerate('CEGHX',1):
  fold='F'+str(i)
  for seed in [20261021,20261022]:
   ledger=read(R/'21_reproducibility/WORKERS.json');assert sum(a['elapsed_s'] for a in ledger if a['module']=='train_e13.py')<36000,'GLOBAL_TRAINING_PROCESS_BUDGET'
   fits=list((R/'05_training').glob('F*_s*/STARTED.json'));assert len(fits)<10;gate();write(R/'21_reproducibility/PIPELINE_STATE.json',dict(stage='TRAIN',fold=fold,plate=plate,seed=seed,completed=len(list((R/'05_training').glob('F*_s*/COMPLETED.json'))),UTC=now()));worker('train_e13.py',['--fold',fold,'--seed',str(seed)],fold+'_s'+str(seed)+'_train.log')
  for seed in [20261021,20261022]:worker('infer_e13.py',['--fold',fold,'--seed',str(seed)],fold+'_s'+str(seed)+'_infer.log')
  print('FOLD_COMPLETE',fold,plate,flush=True)
 worker('score_e13.py',[],'score.log');write(R/'21_reproducibility/PIPELINE_STATE.json',dict(stage='ALL_FITS_PREDICTIONS_SCORED',completed=10,UTC=now()));print('CAMPAIGN_COMPLETE',flush=True)
if __name__=='__main__':
 try:run()
 except Exception as e:write(R/'21_reproducibility/CAMPAIGN_STOP.json',dict(UTC=now(),error=str(e),traceback=traceback.format_exc()));raise
