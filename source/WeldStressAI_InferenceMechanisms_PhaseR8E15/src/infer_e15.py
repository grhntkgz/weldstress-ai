from common_e15 import *
import numpy as np,torch,argparse
from functools import lru_cache
from model_e3 import build
GLOBAL_COLUMNS=[0,1,2,6,7,8,16,17,18]

@lru_cache(maxsize=6)
def geometry(sid,condition,tile,variant):
 if condition=='FULL':p=H/'02_geometry'/(sid+'.npz')
 elif variant=='SHIFT':p=R/'02_source_geometry'/sid/(condition+'_SHIFT_'+str(tile)+'.npz')
 else:p=J/'07_context_geometry'/sid/(condition+'_'+str(tile)+'.npz')
 a=dict(np.load(p));keys=['features','neighbors','neighbors_1mm','neighbors_3mm','context','source_ids','xyz'];g={k:a[k] for k in keys}
 if variant=='SHIFT' and condition=='FULL':g['context']=np.load(R/'02_source_geometry'/sid/'FULL_SHIFT_CONTEXT.npy')
 if variant=='ORACLE':
  full=dict(np.load(H/'02_geometry'/(sid+'.npz')));ii=np.searchsorted(full['source_ids'],g['source_ids']);assert np.array_equal(full['source_ids'][ii],g['source_ids']);g['features']=g['features'].copy();g['features'][:,GLOBAL_COLUMNS]=full['features'][ii][:,GLOBAL_COLUMNS]
 return g,str(p)

def forbidden(*args,**kwargs):raise RuntimeError('R8E15_OPTIMIZATION_FORBIDDEN')
def statehash(model):
 h=hashlib.sha256()
 for k,v in model.state_dict().items():h.update(k.encode());h.update(v.detach().cpu().numpy().tobytes())
 return h.hexdigest()

def main(modelname,fold,seed,stage):
 verify_protocol();assert read(R/'00_historical_integrity/INTEGRITY_PASS.json')['passed'];gate();torch.set_num_threads(2);torch.use_deterministic_algorithms(True);torch.optim.Optimizer.__init__=forbidden;torch.Tensor.backward=forbidden;torch.autograd.backward=forbidden;guard(inference=True)
 rec=next(a for a in rows(R/'N1_N2_CHECKPOINT_HASHES.csv') if a['model']==modelname and a['fold']==fold and int(a['seed'])==seed);assert sha(rec['checkpoint'])==rec['actual_SHA256'];ck=torch.load(rec['checkpoint'],map_location='cpu',weights_only=False);assert ck['fold']==fold and int(ck['seed'])==seed;assert set(ck['heldout_sources'])==set(rec['heldout_sources'].split(';'));assert not {s[0] for s in ck['train_sources']}&{s[0] for s in ck['heldout_sources']}
 net=build('S1','cpu');net.load_state_dict(ck['state_dict'],strict=True);net.eval();assert sum(v.numel() for v in net.parameters())==7228;before=statehash(net);registry=[];replay=[];batches=[];start=time.monotonic();root=R/('05_original_prediction_replay' if stage=='REPLAY' else '11_raw_tile_predictions');tag=modelname+'_'+fold+'_s'+str(seed)
 if stage!='REPLAY':assert read(R/'05_original_prediction_replay/ALL_REPLAY_PASS.json')['passed']
 for sid in ck['heldout_sources']:
  core=dict(np.load(R/'02_source_geometry'/sid/'CORE.npz'));n=len(core['source_ids']);top=[a for a in rows(R/'ORIGINAL_TILE_TOPOLOGY.csv') if a['source_id']==sid]
  todo=[('S0',c) for c in ['FULL','X50','X43']] if stage=='REPLAY' else [('SHIFT',c) for c in ['FULL','X50','X43']]+[('OVERLAP',c) for c in ['FULL','X50','X43']]+[('ORACLE',c) for c in ['X50','X43']]
  for variant,condition in todo:
   field=tag+'_'+condition+'_'+variant+'_'+sid;outpath=root/(field+'.npz');assert not outpath.exists();preds=[];positions=[];tileout=[];weight=[];contextrecords=[]
   tiles=[0] if condition=='FULL' and variant!='OVERLAP' else sorted(map(int,np.unique(core['tile_id'])))
   for tile in tiles:
    t=next(a for a in top if int(a['tile'])==tile)
    if variant=='OVERLAP':loc=np.flatnonzero((core['xyz'][:,0]>=float(t['overlap_query_min_mm'])-1e-8)&(core['xyz'][:,0]<=float(t['overlap_query_max_mm'])+1e-8))
    elif condition=='FULL':loc=np.arange(n)
    else:loc=np.flatnonzero(core['tile_id']==tile)
    g,gpath=geometry(sid,condition,tile,variant);mapped=np.searchsorted(g['source_ids'],core['source_ids'][loc]);assert np.array_equal(g['source_ids'][mapped],core['source_ids'][loc]);assert np.array_equal(g['xyz'][mapped],core['xyz'][loc]);assert np.isfinite(g['features']).all();contextids=g['source_ids'][g['context']];assert len(contextids)==4096 and len(set(contextids))==4096
    ctxpath=root/(field+'_T'+str(tile)+'_CONTEXT.npy');np.save(ctxpath,contextids);contextsha=hashlib.sha256(contextids.tobytes()).hexdigest();fhash=hashlib.sha256(g['features'].tobytes()).hexdigest();p=np.empty(len(loc));offset=sum(len(a) for a in positions)
    with torch.inference_mode():
     assert not torch.is_grad_enabled()
     for j in range(0,len(loc),512):
      ids=core['source_ids'][loc[j:j+512]];v=net(g,mapped[j:j+512]);assert not v.requires_grad;p[j:j+512]=v.numpy()*100
      batches.append(dict(field=field,model=modelname,fold=fold,heldout_plate=sid[0],seed=seed,source_id=sid,checkpoint_SHA256=rec['actual_SHA256'],condition=condition,feature_policy='ORACLE_FULL_GEOMETRY_DIAGNOSTIC' if variant=='ORACLE' else 'NORM-V',experiment=variant,tile=tile,query_offset=offset+j,query_count=len(ids),query_ID_SHA256=hashlib.sha256(ids.tobytes()).hexdigest(),context_ID_path=str(ctxpath),context_ID_SHA256=contextsha,feature_SHA256=fhash,geometry_path=gpath,grad_enabled=False,optimizer_exists=False))
    assert np.isfinite(p).all();preds.append(p);positions.append(loc);tileout.append(np.full(len(loc),tile,dtype='i1'));radius=(float(t['query_X_max_mm'])-float(t['query_X_min_mm']))/2+1;ww=np.maximum(1e-6,1-abs(core['xyz'][loc,0]-float(t['center_X_mm']))/radius);weight.append(ww)
    contextrecords.append(dict(tile=tile,context_path=str(ctxpath),context_SHA256=sha(ctxpath),geometry_path=gpath,geometry_SHA256=sha(gpath),feature_SHA256=fhash,visible_points=len(g['source_ids']),context_points=len(contextids)))
   pp=np.concatenate(preds);ll=np.concatenate(positions);tt=np.concatenate(tileout);ww=np.concatenate(weight);assert (np.bincount(ll,minlength=n)>0).all();np.savez_compressed(outpath,core_position=ll,source_ids=core['source_ids'][ll],xyz=core['xyz'][ll],pred_MPa=pp,tile_id=tt,tent_weight=ww);write(outpath.with_suffix('.json'),dict(model=modelname,fold=fold,seed=seed,source_id=sid,condition=condition,variant=variant,checkpoint=rec['checkpoint'],checkpoint_SHA256=rec['actual_SHA256'],contexts=contextrecords,raw_predictions=len(pp),core_points=n,coverage=1,oracle=variant=='ORACLE',no_grad=True))
   registry.append(dict(model=modelname,fold=fold,seed=seed,source_id=sid,plate=sid[0],condition=condition,variant=variant,path=str(outpath),SHA256=sha(outpath),raw_predictions=len(pp),core_points=n,coverage=1))
   if stage=='REPLAY':
    oldrec=next(a for a in rows(R/'00_historical_integrity/HISTORICAL_PREDICTION_REGISTRY.csv') if a['model']==modelname and a['fold']==fold and int(a['seed'])==seed and a['source_id']==sid and a['condition']==condition);old=dict(np.load(oldrec['path']));order=np.argsort(ll);assert np.array_equal(core['source_ids'],np.concatenate([core['source_ids'][a] for a in positions])[order]);err=abs(pp[order]-old['pred_MPa']);row=dict(model=modelname,fold=fold,seed=seed,source_id=sid,plate=sid[0],condition=condition,checkpoint_SHA256=rec['actual_SHA256'],original_prediction=oldrec['path'],original_SHA256=oldrec['SHA256'],replayed_prediction=str(outpath),replayed_SHA256=sha(outpath),core_points=n,coverage=1.,maximum_absolute_difference_MPa=float(err.max()),mean_absolute_difference_MPa=float(err.mean()),tolerance_MPa=1e-4,passed=bool(err.max()<=1e-4));replay.append(row);assert row['passed'],row
   print('INFERENCE',field,len(pp),flush=True)
 assert statehash(net)==before and sha(rec['checkpoint'])==rec['actual_SHA256'];table(root/(tag+'_REGISTRY.csv'),registry);table(root/(tag+'_RUNTIME.csv'),batches)
 if replay:table(root/(tag+'_REPLAY.csv'),replay)
 write(root/(tag+'_COMPLETED.json'),dict(UTC=now(),model=modelname,fold=fold,seed=seed,stage=stage,fields=len(registry),forward_batches=len(batches),parameter_state_before=before,parameter_state_after=statehash(net),checkpoint_SHA256=sha(rec['checkpoint']),elapsed_s=time.monotonic()-start,resource=gate(),training_fits=0,optimizer_steps=0,backpropagation=0));print('WORKER_COMPLETE',tag,stage,len(batches),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--fold',required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--stage',required=True);a=p.parse_args();main(a.model,a.fold,a.seed,a.stage)
