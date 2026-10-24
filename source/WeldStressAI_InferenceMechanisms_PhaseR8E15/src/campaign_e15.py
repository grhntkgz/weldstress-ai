from common_e15 import *
import subprocess
PY=O/'WeldScan_VisualAI_Segmentation_Phase5D/.venv/Scripts/python.exe'

def main():
 verify_protocol();ledger=[]
 for stage in ['REPLAY','INTERVENTION']:
  if stage=='INTERVENTION':
   replay=[a for p in (R/'05_original_prediction_replay').glob('*_REPLAY.csv') for a in rows(p)];assert len(replay)==156 and all(a['passed']=='True' for a in replay);table(R/'ORIGINAL_INFERENCE_REPLAY.csv',replay);write(R/'05_original_prediction_replay/ALL_REPLAY_PASS.json',dict(UTC=now(),passed=True,fields=len(replay),max_difference_MPa=max(float(a['maximum_absolute_difference_MPa']) for a in replay),tolerance_MPa=1e-4));print('ALL_REPLAY_PASS',flush=True)
  for a in rows(R/'N1_N2_CHECKPOINT_HASHES.csv'):
   gate();name=a['model']+'_'+a['fold']+'_s'+a['seed']+'_'+stage;log=R/'21_reproducibility'/(name+'.log');start=time.monotonic()
   with log.open('w',encoding='utf8') as f:p=subprocess.run([str(PY),'-B','-u',str(R/'src/infer_e15.py'),'--model',a['model'],'--fold',a['fold'],'--seed',a['seed'],'--stage',stage],stdout=f,stderr=subprocess.STDOUT)
   ledger.append(dict(worker=name,stage=stage,model=a['model'],fold=a['fold'],seed=a['seed'],exit_code=p.returncode,elapsed_s=time.monotonic()-start,training_fits=0,optimizer_steps=0,ANSYS=0,**gate()));table(R/'RESOURCE_ACCOUNTING.csv',ledger)
   if p.returncode:write(R/'21_reproducibility/CAMPAIGN_STOP.json',dict(UTC=now(),worker=name,log=str(log),reason='worker nonzero exit; no automatic retry'));raise RuntimeError(name)
   print('WORKER_FINISHED',name,round(time.monotonic()-start,2),flush=True)
  folder=R/('05_original_prediction_replay' if stage=='REPLAY' else '11_raw_tile_predictions');registry=[a for p in folder.glob('*_REGISTRY.csv') for a in rows(p)];table(R/'21_reproducibility'/(stage+'_REGISTRY.csv'),registry)
 actual=sum(int(read(p)['forward_batches']) for folder in ['05_original_prediction_replay','11_raw_tile_predictions'] for p in (R/folder).glob('*_COMPLETED.json'));assert actual==read(R/'INFERENCE_EXECUTION_BUDGET.json')['forward_batches_exact'];write(R/'21_reproducibility/INFERENCE_COMPLETE.json',dict(UTC=now(),passed=True,workers=40,forward_batches=actual,training_fits=0,optimizer_steps=0));print('INFERENCE_COMPLETE',actual,flush=True)
if __name__=='__main__':main()
