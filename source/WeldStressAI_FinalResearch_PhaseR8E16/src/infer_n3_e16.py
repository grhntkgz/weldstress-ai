from common_e16 import *
import numpy as np,torch,argparse
from model_e3 import build
from features_e16 import parts,core

def main(fold,seed):
 verify_protocol();torch.set_num_threads(2);torch.use_deterministic_algorithms(True);guard(inference=True);receipt=read(R/'11_N3_training'/(fold+'_s'+str(seed))/'COMPLETED.json');assert sha(receipt['checkpoint'])==receipt['checkpoint_SHA256'];ck=torch.load(receipt['checkpoint'],map_location='cpu',weights_only=False);net=build('S1','cpu');net.load_state_dict(ck['state_dict']);net.eval();registry=[];runtime=[];start=time.monotonic()
 for sid in ck['heldout_sources']:
  s=core(sid);q=s['query_original_rows']
  for c in ['FULL','X50','X43']:
   prediction=np.empty(len(q));seen=np.zeros(len(q),int)
   with torch.inference_mode():
    for loc,g,idx in parts(sid,q,c):
     ctx=g['source_ids'][g['context']];tile=int(s['tile_id'][loc[0]]);fh=hashlib.sha256(g['features'].tobytes()).hexdigest()
     for j in range(0,len(loc),512):
      ll=loc[j:j+512];prediction[ll]=net(g,idx[j:j+512]).numpy()*100;seen[ll]+=1;runtime.append(dict(model='N3',fold=fold,seed=seed,source_id=sid,plate=sid[0],condition=c,tile=tile,query_start=j,query_count=len(ll),query_ID_SHA256=hashlib.sha256(s['source_ids'][ll].tobytes()).hexdigest(),context_ID_SHA256=hashlib.sha256(ctx.tobytes()).hexdigest(),feature_SHA256=fh,checkpoint_SHA256=receipt['checkpoint_SHA256'],grad_enabled=False))
   assert (seen==1).all() and np.isfinite(prediction).all();path=R/'13_full_core_predictions'/('N3_'+fold+'_s'+str(seed)+'_'+sid+'_'+c+'.npz');np.savez_compressed(path,source_ids=s['source_ids'],xyz=s['xyz'],area=s['area'],pred_MPa=prediction,query_original_rows=q);registry.append(dict(model='N3',fold=fold,seed=seed,source_id=sid,plate=sid[0],condition=c,policy='S0',path=str(path),SHA256=sha(path),checkpoint=receipt['checkpoint'],checkpoint_SHA256=receipt['checkpoint_SHA256'],core_points=len(q),coverage=1.,inference_s=time.monotonic()-start));print('N3_PREDICT',sid,seed,c,flush=True)
 tag=fold+'_s'+str(seed);table(R/'13_full_core_predictions'/(tag+'_REGISTRY.csv'),registry);table(R/'13_full_core_predictions'/(tag+'_RUNTIME.csv'),runtime);write(R/'13_full_core_predictions'/(tag+'_COMPLETED.json'),dict(UTC=now(),passed=True,fields=len(registry),batches=len(runtime),elapsed_s=time.monotonic()-start,resource=gate()))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--fold',required=True);p.add_argument('--seed',required=True,type=int);a=p.parse_args();main(a.fold,a.seed)
