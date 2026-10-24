from common_e13 import *
import numpy as np,torch,argparse
from model_e3 import build
def main(fold,seed):
 verify_seal();guard(infer=True);torch.set_num_threads(2);torch.use_deterministic_algorithms(True);out=R/'05_training'/(fold+'_s'+str(seed));rec=read(out/'COMPLETED.json');assert sha(rec['checkpoint'])==rec['checkpoint_SHA256'];model=build('S1','cpu');ck=torch.load(rec['checkpoint'],map_location='cpu',weights_only=False);assert ck['fold']==fold and ck['seed']==seed;model.load_state_dict(ck['state_dict']);model.eval();rr=[]
 for sid in rec['heldout_sources']:
  assert sid not in rec['train_sources'];g=dict(np.load(R/'02_geometry'/(sid+'.npz')));n=len(g['features']);pred=np.empty(n);counts=np.zeros(n,dtype='i4')
  with torch.inference_mode():
   for j in range(0,n,512):
    q=np.arange(j,min(j+512,n));pred[q]=model(g,q).numpy()*100;counts[q]+=1
  assert np.isfinite(pred).all() and (counts==1).all();p=R/'06_predictions'/('N1_POINT_TRANSFORMER_'+fold+'_s'+str(seed)+'_'+sid+'.npz');np.savez(p,source_ids=g['source_ids'],xyz=g['xyz'],area=g['area'],pred_MPa=pred,valid=np.ones(n,dtype=bool),tile_count=counts)
  rr.append(dict(model='N1_POINT_TRANSFORMER',fold=fold,seed=seed,source_id=sid,plate=sid[0],path=str(p),SHA256=sha(p),checkpoint=rec['checkpoint'],checkpoint_SHA256=rec['checkpoint_SHA256']));print('FULL_SOURCE_INFERENCE',fold,seed,sid,n,flush=True)
 table(out/'PREDICTION_REGISTRY.csv',rr)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--fold',required=True);p.add_argument('--seed',type=int,required=True);a=p.parse_args();main(a.fold,a.seed)
