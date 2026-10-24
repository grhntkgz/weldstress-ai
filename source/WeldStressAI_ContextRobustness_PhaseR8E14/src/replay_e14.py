from common_e14 import *
import numpy as np,torch
from model_e3 import build
def main():
 assert read(R/'00_integrity/G0_INTEGRITY_PASS.json')['passed'];guard(inference=True);torch.set_num_threads(2);records=[]
 for rec in rows(R/'R8E13_CHECKPOINT_HASHES.csv'):
  ck=torch.load(rec['checkpoint'],map_location='cpu',weights_only=False);assert ck['epoch']==80;model=build('S1','cpu');model.load_state_dict(ck['state_dict']);model.eval()
  for sid in ck['heldout_sources']:
   g=dict(np.load(H/'02_geometry'/(sid+'.npz')));q=np.linspace(0,len(g['source_ids'])-1,256,dtype=int);saved=dict(np.load(H/'06_predictions'/('N1_POINT_TRANSFORMER_'+rec['fold']+'_s'+str(rec['seed'])+'_'+sid+'.npz')))
   with torch.inference_mode():p=model(g,q).numpy()*100
   err=float(np.max(abs(p-saved['pred_MPa'][q])));assert err<=1e-4,(sid,err);records.append(dict(fold=rec['fold'],seed=rec['seed'],source_id=sid,queries=256,maximum_error_MPa=err,tolerance_MPa=1e-4,checkpoint_SHA256=sha(rec['checkpoint']),passed=True))
  print('HISTORICAL_REPLAY',rec['fold'],rec['seed'],flush=True)
 table(R/'ORIGINAL_PREDICTION_REPLAY.csv',records);table(R/'R8E13_PREDICTION_REPLAY.csv',records);write(R/'00_integrity/G1_REPLAY_PASS.json',dict(UTC=now(),passed=True,checkpoints=10,source_seed_pairs=26,queries=6656,max_error_MPa=max(a['maximum_error_MPa'] for a in records),tolerance_MPa=1e-4))
if __name__=='__main__':main()
