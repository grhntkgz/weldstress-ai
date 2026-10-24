from common_e14 import *
import numpy as np,torch,argparse
from model_e3 import build
from context_e14 import parts,label_free_support
def main(which,fold,seed):
 verify_protocol();assert read(R/'00_integrity/G2_G3_G4_CONTEXT_PASS.json')['passed'];torch.set_num_threads(2);torch.use_deterministic_algorithms(True);guard(inference=True)
 if which=='N1':rec=next(a for a in rows(R/'R8E13_CHECKPOINT_HASHES.csv') if a['fold']==fold and int(a['seed'])==seed);checkpoint=rec['checkpoint'];expected=rec['actual_SHA256']
 else:rec=read(R/'11_context_robust_training'/(fold+'_s'+str(seed))/'COMPLETED.json');checkpoint=rec['checkpoint'];expected=rec['checkpoint_SHA256']
 assert sha(checkpoint)==expected;ck=torch.load(checkpoint,map_location='cpu',weights_only=False);assert ck['fold']==fold and int(ck['seed'])==seed;model=build('S1','cpu');model.load_state_dict(ck['state_dict']);model.eval();records=[];replays=[];start=time.monotonic()
 for condition in (['FULL','X50','X43','D0'] if which=='N1' else ['FULL','X50','X43']):
  for sid in ck['heldout_sources']:
   s=label_free_support(sid);q=np.flatnonzero(s['core']&s['valid']);output=np.empty(len(q));count=np.zeros(len(q),dtype='i1')
   # FULL uses the historical model directly; cropped views partition only by geometric tiles.
   with torch.inference_mode():
    for loc,g,mapped in parts(sid,q,condition):
     for j in range(0,len(loc),512):
      positions=loc[j:j+512];output[positions]=model(g,mapped[j:j+512]).numpy()*100;count[positions]+=1
   assert np.isfinite(output).all() and (count==1).all();folder=R/('08_frozen_checkpoint_inference' if which=='N1' else '12_new_model_predictions');p=folder/(which+'_'+fold+'_s'+str(seed)+'_'+condition+'_'+sid+'.npz');np.savez_compressed(p,source_ids=s['source_ids'][q],xyz=s['xyz'][q],area=s['area'][q],pred_MPa=output,valid=np.ones(len(q),bool),tile_count=count,query_original_rows=q,core=np.ones(len(q),bool))
   records.append(dict(model=which,fold=fold,seed=seed,condition=condition,source_id=sid,plate=sid[0],path=str(p),SHA256=sha(p),checkpoint=checkpoint,checkpoint_SHA256=expected,core_points=len(q),coverage=1.,elapsed_s=time.monotonic()-start))
   if which=='N1' and condition=='FULL':
    old=dict(np.load(H/'06_predictions'/('N1_POINT_TRANSFORMER_'+fold+'_s'+str(seed)+'_'+sid+'.npz')));err=float(np.max(abs(output-old['pred_MPa'][q])));assert err<=1e-4,(sid,err);replays.append(dict(fold=fold,seed=seed,source_id=sid,full_core_points=len(q),max_replay_error_MPa=err,tolerance_MPa=1e-4,passed=True))
   print('PREDICTED',which,fold,seed,condition,sid,len(q),flush=True)
 table(folder/(which+'_'+fold+'_s'+str(seed)+'_REGISTRY.csv'),records)
 if replays:table(folder/(which+'_'+fold+'_s'+str(seed)+'_FULL_REPLAY.csv'),replays)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--model',choices=['N1','N2'],required=True);p.add_argument('--fold',required=True);p.add_argument('--seed',type=int,required=True);a=p.parse_args();main(a.model,a.fold,a.seed)
