from common_e16 import *
import subprocess
PT=O/'WeldScan_VisualAI_Segmentation_Phase5D/.venv/Scripts/python.exe'
ENG=O/'WeldScan_MechanicalBenchmark_Phase5E/.venv/Scripts/python.exe'
def job(py,script,args,tag,receipt):
 if Path(receipt).exists():print('RECEIPT_EXISTS',tag,flush=True);return
 verify_protocol();gate();log=R/'22_reproducibility'/(tag+'.log');print('START',tag,now(),flush=True)
 with log.open('w',encoding='utf8',buffering=8*1024**2) as f:
  p=subprocess.Popen([str(py),'-B','-u',str(R/'src'/script)]+args,stdout=f,stderr=subprocess.STDOUT,cwd=str(R))
  write(R/'22_reproducibility/ACTIVE_JOB.json',dict(tag=tag,PID=p.pid,UTC=now(),log=str(log)))
  rc=p.wait()
 assert rc==0,tag+' FAILED: '+str(log)
 assert Path(receipt).exists(),tag+' missing receipt'
 print('COMPLETE',tag,now(),flush=True)
def main():
 for a in rows(R/'HISTORICAL_MODEL_HASHES.csv'):
  tag=a['model']+'_'+a['fold']+'_s'+a['seed'];job(PT,'factorial_e16.py',['--model',a['model'],'--fold',a['fold'],'--seed',a['seed']],'factorial_'+tag,R/'05_blockwise_interventions'/(tag+'_COMPLETED.json'))
 receipts=list((R/'05_blockwise_interventions').glob('*_COMPLETED.json'));assert len(receipts)==20 and sum(read(p)['fields'] for p in receipts)==832
 write(R/'04_feature_mechanisms/FACTORIAL_COMPLETE.json',dict(UTC=now(),passed=True,workers=20,fields=832,forward_batches=sum(read(p)['forward_batches'] for p in receipts)))
 job(ENG,'features_e16.py',[],'feature_qualification',R/'10_training_validation/FEATURE_CONTRACT_PASS.json')
 job(PT,'train_e16.py',['--dry'],'dry_run',R/'10_training_validation/TRAINING_DRY_RUN.json')
 assert read(R/'10_training_validation/TRAINING_DRY_RUN.json')['steps']==0
 for fold in ['F1','F2','F3','F4','F5']:
  for seed in ['20261021','20261022']:
   tag=fold+'_s'+seed;job(PT,'train_e16.py',['--fold',fold,'--seed',seed],'train_'+tag,R/'11_N3_training'/tag/'COMPLETED.json');job(PT,'infer_n3_e16.py',['--fold',fold,'--seed',seed],'infer_'+tag,R/'13_full_core_predictions'/(tag+'_COMPLETED.json'))
 for fold in ['F1','F2','F3','F4','F5']:job(ENG,'xgb_e16.py',['--fold',fold],'xgb_'+fold,R/'12_XGBoost_baseline'/fold/'COMPLETED.json')
 write(R/'22_reproducibility/EXPERIMENT_MATRIX_COMPLETE.json',dict(UTC=now(),passed=True,factorial_fields=832,N3_fits=10,XGB_fits=5,resource=gate()))
if __name__=='__main__':
 try:main()
 except Exception as e:write(R/'22_reproducibility/CAMPAIGN_BLOCKED.json',dict(UTC=now(),error=str(e),resource=resources()));raise
