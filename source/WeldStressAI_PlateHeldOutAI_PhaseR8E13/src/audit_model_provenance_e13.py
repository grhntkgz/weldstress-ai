from common_e13 import *
import numpy as np,torch
from model_e3 import build
def main():
 verify_seal();guard(infer=True);torch.set_num_threads(2);torch.use_deterministic_algorithms(True);records=[]
 for p in sorted((R/'05_training').glob('F*_s*/COMPLETED.json')):
  rec=read(p);ck=torch.load(rec['checkpoint'],map_location='cpu',weights_only=False);assert ck['epoch']==80 and ck['recipe_SHA256']==sha(R/'MODEL_AND_TRAINING_SEAL.json');assert ck['train_sources']==rec['train_sources'] and ck['heldout_sources']==rec['heldout_sources'];model=build('S1','cpu');model.load_state_dict(ck['state_dict']);model.eval();assert sum(x.numel() for x in model.parameters())==7228
  for sid in rec['heldout_sources']:
   g=dict(np.load(R/'02_geometry'/(sid+'.npz')));n=len(g['source_ids']);q=np.linspace(0,n-1,256,dtype=int);path=R/'06_predictions'/('N1_POINT_TRANSFORMER_'+rec['fold']+'_s'+str(rec['seed'])+'_'+sid+'.npz');saved=dict(np.load(path))
   with torch.inference_mode():
    a=model(g,q).numpy()*100;b=np.concatenate([model(g,q[i:i+64]).numpy()*100 for i in range(0,256,64)])
   delta_saved=float(np.max(abs(a-saved['pred_MPa'][q])));delta_chunk=float(np.max(abs(a-b)));assert delta_saved<=1e-4 and delta_chunk<=1e-4,(sid,delta_saved,delta_chunk);records.append(dict(fold=rec['fold'],seed=rec['seed'],source_id=sid,checkpoints_epoch=80,queries=256,maximum_saved_replay_error_MPa=delta_saved,maximum_chunk_replay_error_MPa=delta_chunk,passed=True));print('CHECKPOINT_REPLAY',rec['fold'],rec['seed'],sid,delta_saved,delta_chunk,flush=True)
 table(R/'21_reproducibility/CHECKPOINT_PREDICTION_REPLAY.csv',records);write(R/'21_reproducibility/CHECKPOINT_REPLAY_RECEIPT.json',dict(UTC=now(),passed=True,heldout_source_seed_pairs=len(records),sample_queries=sum(x['queries'] for x in records),tolerance_MPa=1e-4,weights_from_new_models_only=True,original_predictions_unchanged=True))
if __name__=='__main__':main()
