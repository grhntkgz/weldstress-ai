from common_e3 import *
import numpy as np,pandas as pd,torch,random,psutil,threading,msvcrt,argparse
from model_e3 import build
from geometry_e3 import loadgeom,common_labels,queries,valqueries
def train(exp,fold,seed,epochs=100,final=False,budget_s=36000):
 verify_freeze();dev=rows(R/'00_protocol/DEVELOPMENT_GROUPS.csv');fr=[x for x in rows(R/'GROUPED_DEVELOPMENT_FOLDS.csv') if x['fold']==fold];roles={x['specimen_id']:x['role'] for x in fr}
 if final:roles={x['specimen_id']:'train' for x in dev}
 tr=[x['specimen_id'] for x in dev if roles.get(x['specimen_id'])=='train'];va=[x['specimen_id'] for x in dev if roles.get(x['specimen_id'])=='inner_validation'];outer=[x['specimen_id'] for x in dev if roles.get(x['specimen_id'])=='outer'];assert tr and (va or final) and not set(tr+va)&set(outer)
 guard('train',tr+va,single_observation=exp!='D1');gate();run=f'{exp}_{fold}_s{seed}';folder=R/'04_checkpoints'/run;folder.mkdir(exist_ok=True)
 if (folder/'COMPLETED.json').exists():print('REUSE_COMPLETED',run,flush=True);return
 lock=(R/'16_resources/TRAINING_EXCLUSIVE.lock').open('a+b');lock.write(b'1');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
 torch.set_num_threads(2);torch.use_deterministic_algorithms(True);device='cuda' if torch.cuda.is_available() else 'cpu';torch.manual_seed(seed);np.random.seed(seed);random.seed(seed);rng=np.random.default_rng(seed);model=build(exp,device);opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001);scheduler=torch.optim.lr_scheduler.CosineAnnealingLR(opt,epochs,eta_min=1e-5)
 labels={sid:common_labels(sid) for sid in tr+va};start=time.monotonic();first=0;prior_s=0.;best=float('inf');bestpath=None;history=[];resources=[];running=[True]
 if (folder/'RESUME_POINTER.json').exists():
  rec=read(folder/'RESUME_POINTER.json');assert sha(rec['path'])==rec['sha256'];ck=torch.load(rec['path'],map_location=device,weights_only=False);model.load_state_dict(ck['state_dict']);opt.load_state_dict(ck['optimizer']);scheduler.load_state_dict(ck['scheduler']);rng.bit_generator.state=ck['case_rng'];torch.set_rng_state(ck['torch_rng'].cpu());first=ck['epoch']+1;prior_s=ck['training_elapsed_s'];best=ck['best'];bestpath=Path(ck['bestpath']) if ck['bestpath'] else None;history=pd.read_csv(folder/'history.csv').iloc[:first].to_dict('records')
  if device=='cuda' and ck.get('cuda_rng') is not None:torch.cuda.set_rng_state_all(ck['cuda_rng'])
 else:write(folder/'STARTED.json',dict(run=run,UTC=now(),experiment=exp,fold=fold,seed=seed,training_IDs=tr,inner_validation_IDs=va,outer_IDs=outer,epochs=epochs,query_points=512,source_freeze_sha256=sha(R/'00_protocol/SOURCE_FREEZE.json'),protocol_sha256=sha(R/'00_protocol/EXPERIMENT_PROTOCOL.json'),schema_sha256=sha(R/'SINGLE_SURFACE_FEATURE_SCHEMA.json'),device=device))
 def monitor():
  while running[0]:resources.append(dict(UTC=now(),RSS_bytes=psutil.Process().memory_info().rss,available_RAM_bytes=psutil.virtual_memory().available,VRAM_bytes=torch.cuda.max_memory_allocated() if device=='cuda' else 0,**commit()));time.sleep(1)
 th=threading.Thread(target=monitor,daemon=True);th.start()
 def checkpoint(path,epoch):
  ck=dict(experiment=exp,fold=fold,seed=seed,epoch=epoch,state_dict=model.state_dict(),optimizer=opt.state_dict(),scheduler=scheduler.state_dict(),case_rng=rng.bit_generator.state,torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all() if device=='cuda' else None,best=best,bestpath=str(bestpath) if bestpath else None,training_elapsed_s=prior_s+time.monotonic()-start,training_IDs=tr,inner_validation_IDs=va,outer_IDs=outer,feature_schema_sha256=sha(R/'SINGLE_SURFACE_FEATURE_SCHEMA.json'),protocol_sha256=sha(R/'00_protocol/EXPERIMENT_PROTOCOL.json'),source_freeze_sha256=sha(R/'00_protocol/SOURCE_FREEZE.json'),target='Selected original front-face unchangedT2 K=sigma/100MPa',parameters=sum(x.numel() for x in model.parameters()),physical_validation=False)
  if path.exists():
   old=torch.load(path,map_location=device,weights_only=False);assert old['epoch']==epoch and all(torch.equal(v,old['state_dict'][k]) for k,v in model.state_dict().items()),'CHECKPOINT_REPLAY_MISMATCH';return
  tmp=path.with_suffix('.pt.tmp');torch.save(ck,tmp);tmp.replace(path)
 try:
  for epoch in range(first,epochs):
   assert prior_s+time.monotonic()-start<budget_s,'GLOBAL_TRAINING_WALL_CEILING'
   if epoch%10==0:gate()
   model.train();losses=[]
   for i in rng.permutation(len(tr)):
    sid=tr[i];sg=loadgeom(sid,'S1');g=loadgeom(sid,exp);y,m=labels[sid];qlocal=queries(sg,m,512,seed,sid,epoch);qmodel=sg['global_indices'][qlocal] if exp=='D1' else qlocal;opt.zero_grad(set_to_none=True);pred=model(g,qmodel);target=torch.as_tensor(np.asarray(y[qlocal]),dtype=torch.float32,device=device);loss=((pred-target)**2).mean();assert torch.isfinite(loss);loss.backward();grad=torch.nn.utils.clip_grad_norm_(model.parameters(),1);assert torch.isfinite(grad);opt.step();losses.append(float(loss.detach()))
   scheduler.step();val=None
   if epoch%5==0 or epoch==epochs-1:
    model.eval();vv=[]
    with torch.inference_mode():
     for sid in va:
      sg=loadgeom(sid,'S1');g=loadgeom(sid,exp);y,m=labels[sid];ql=valqueries(sg,m);qm=sg['global_indices'][ql] if exp=='D1' else ql;vv.append(float(((model(g,qm)-torch.as_tensor(np.asarray(y[ql]),dtype=torch.float32,device=device))**2).mean()))
    if va:
     val=float(np.mean(vv));assert np.isfinite(val)
     if val<best:best=val;bestpath=folder/f'best_epoch{epoch:04d}.pt';checkpoint(bestpath,epoch)
    print(run,'epoch',epoch,'train',float(np.mean(losses)),'inner_MSE',val,'training_s',round(prior_s+time.monotonic()-start),flush=True)
   history.append(dict(run=run,experiment=exp,fold=fold,seed=seed,epoch=epoch,training_MSE_K=float(np.mean(losses)),inner_validation_MSE_K=val,optimizer_steps=(epoch+1)*len(tr),query_presentations=(epoch+1)*len(tr)*512,elapsed_s=prior_s+time.monotonic()-start));pd.DataFrame(history).to_csv(folder/'history.csv',index=False)
   if epoch%10==0 or epoch==epochs-1:
    last=folder/f'last_epoch{epoch:04d}.pt';checkpoint(last,epoch);write(folder/'RESUME_POINTER.json',dict(path=str(last),sha256=sha(last),epoch=epoch))
  if final:bestpath=last;best=None
  running[0]=False;th.join();table(folder/'resources.csv',resources);assert bestpath and len(history)==epochs
  result=dict(run=run,status='COMPLETE',experiment=exp,fold=fold,seed=seed,epochs=epochs,checkpoint=str(bestpath),checkpoint_sha256=sha(bestpath),last_checkpoint=str(last),last_sha256=sha(last),best_epoch=int(torch.load(bestpath,map_location='cpu',weights_only=False)['epoch']),best_inner_validation_MSE_K=best,training_IDs=tr,inner_validation_IDs=va,outer_IDs=outer,parameters=sum(x.numel() for x in model.parameters()),training_s=prior_s+time.monotonic()-start,device=device,peak_RSS_bytes=max(x['RSS_bytes'] for x in resources),peak_VRAM_bytes=max(x['VRAM_bytes'] for x in resources),UTC=now(),common_selected_face_only_target=True,source_freeze_sha256=sha(R/'00_protocol/SOURCE_FREEZE.json'))
  write(folder/'COMPLETED.json',result)
 finally:running[0]=False;th.join();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1);lock.close()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--exp',required=True,choices=['S0','S1','D1']);p.add_argument('--fold',required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--epochs',type=int,default=100);p.add_argument('--final',action='store_true');p.add_argument('--budget-s',type=float,default=36000);a=p.parse_args();train(a.exp,a.fold,a.seed,a.epochs,a.final,a.budget_s)

