from common_e16 import *
import numpy as np,torch,argparse
from model_e3 import build
from functools import lru_cache
BLOCKS=[[0,1,2],[6,7,8,18],[16,17]]
@lru_cache(maxsize=6)
def load(sid,condition,tile):return dict(np.load(J/'07_context_geometry'/sid/(condition+'_'+str(tile)+'.npz')))

def main(modelname,fold,seed):
 verify_protocol();gate();torch.set_num_threads(2);torch.use_deterministic_algorithms(True);guard(inference=True);rec=next(a for a in rows(R/'HISTORICAL_MODEL_HASHES.csv') if a['model']==modelname and a['fold']==fold and int(a['seed'])==seed);assert sha(rec['checkpoint'])==rec['actual_SHA256'];ck=torch.load(rec['checkpoint'],map_location='cpu',weights_only=False);net=build('S1','cpu');net.load_state_dict(ck['state_dict'],strict=True);net.eval();assert sum(p.numel() for p in net.parameters())==7228;state_before=hashlib.sha256(b''.join(v.numpy().tobytes() for v in net.state_dict().values())).hexdigest();results=[];runtime=[];replays=[];start=time.monotonic()
 for sid in ck['heldout_sources']:
  full=dict(np.load(H/'02_geometry'/(sid+'.npz')));core=dict(np.load(K/'02_source_geometry'/sid/'CORE.npz'));q=core['query_original_rows'];n=len(q)
  for condition in ['X50','X43']:
   for cell in ['F000','F100','F010','F001','F110','F101','F011','F111']:
    cols=[i for bit,block in zip(cell[1:],BLOCKS) if bit=='1' for i in block];output=np.empty(n);field=modelname+'_'+fold+'_s'+str(seed)+'_'+sid+'_'+condition+'_'+cell
    for tile in range(5):
     g=load(sid,condition,tile).copy();f=g['features'].copy();idx=np.searchsorted(full['source_ids'],g['source_ids']);assert np.array_equal(full['source_ids'][idx],g['source_ids']);f[:,cols]=full['features'][idx][:,cols];g['features']=f;assert np.isfinite(f).all();loc=np.flatnonzero(core['tile_id']==tile);mapped=np.searchsorted(g['source_ids'],core['source_ids'][loc]);assert np.array_equal(g['source_ids'][mapped],core['source_ids'][loc]);ctx=g['source_ids'][g['context']];fh=hashlib.sha256(f.tobytes()).hexdigest()
     with torch.inference_mode():
      for k in range(0,len(loc),512):
       ll=loc[k:k+512];output[ll]=net(g,mapped[k:k+512]).numpy()*100;runtime.append(dict(field=field,model=modelname,fold=fold,seed=seed,source_id=sid,plate=sid[0],condition=condition,cell=cell,tile=tile,query_start=k,query_count=len(ll),query_ID_SHA256=hashlib.sha256(core['source_ids'][ll].tobytes()).hexdigest(),context_ID_SHA256=hashlib.sha256(ctx.tobytes()).hexdigest(),feature_SHA256=fh,visible_geometry_path=str(J/'07_context_geometry'/sid/(condition+'_'+str(tile)+'.npz')),checkpoint_SHA256=rec['actual_SHA256'],grad_enabled=False))
    assert np.isfinite(output).all();baseline=next(a for a in rows(K/'SOURCE_LEVEL_FIELD_METRICS.csv') if a['model']==modelname and a['seed']==str(seed) and a['source_id']==sid and a['condition']==condition and a['policy']=='S0');base=np.load(baseline['path'])['pred_MPa'];path=R/'05_blockwise_interventions'/(field+'.npz');np.savez_compressed(path,source_ids=core['source_ids'],xyz=core['xyz'],area=core['area'],pred_MPa=output,delta_F000_MPa=output-base,query_original_rows=q);results.append(dict(model=modelname,fold=fold,seed=seed,source_id=sid,plate=sid[0],condition=condition,cell=cell,path=str(path),SHA256=sha(path),checkpoint_SHA256=rec['actual_SHA256'],core_points=n,coverage=1.))
    if cell in ['F000','F111']:
     policy='S0' if cell=='F000' else 'ORACLE';old=next(a for a in rows(K/'SOURCE_LEVEL_FIELD_METRICS.csv') if a['model']==modelname and a['seed']==str(seed) and a['source_id']==sid and a['condition']==condition and a['policy']==policy);reference=np.load(old['path'])['pred_MPa'];err=float(np.max(abs(output-reference)));assert err<=1e-4;replays.append(dict(model=modelname,seed=seed,source_id=sid,condition=condition,cell=cell,historical_path=old['path'],maximum_difference_MPa=err,tolerance_MPa=1e-4,passed=True))
    print('FACTORIAL',field,flush=True)
  gate()
 tag=modelname+'_'+fold+'_s'+str(seed);folder=R/'05_blockwise_interventions';table(folder/(tag+'_REGISTRY.csv'),results);table(folder/(tag+'_RUNTIME.csv'),runtime);table(folder/(tag+'_REPLAY.csv'),replays);after=hashlib.sha256(b''.join(v.numpy().tobytes() for v in net.state_dict().values())).hexdigest();assert after==state_before and sha(rec['checkpoint'])==rec['actual_SHA256'];write(folder/(tag+'_COMPLETED.json'),dict(UTC=now(),passed=True,fields=len(results),forward_batches=len(runtime),elapsed_s=time.monotonic()-start,parameter_state_before=state_before,parameter_state_after=after,optimizer_steps=0,checkpoint_SHA256=sha(rec['checkpoint']),resource=gate()));print('FACTORIAL_WORKER_COMPLETE',tag,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--fold',required=True);p.add_argument('--seed',type=int,required=True);a=p.parse_args();main(a.model,a.fold,a.seed)
