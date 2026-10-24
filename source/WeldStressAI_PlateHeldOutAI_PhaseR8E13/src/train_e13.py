from common_e13 import *
import numpy as np,torch,random,argparse,threading
from model_e3 import build
def loadgeom(sid):
 with np.load(R/'02_geometry'/(sid+'.npz')) as d:return dict(d)
def main(fold,seed,dry=False):
 verify_seal();torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
 rr=[a for a in rows(R/'OUTER_LOPO_FOLDS.csv') if a['fold']==fold];tr=[a['source_id'] for a in rr if a['role']=='train'];held=[a['source_id'] for a in rr if a['role']=='heldout'];assert not {s[0] for s in tr}&{s[0] for s in held}
 guard(tr);config=read(R/'MODEL_AND_TRAINING_SEAL.json');run=('DRY_' if dry else '')+fold+'_s'+str(seed);out=R/'05_training'/run;out.mkdir(exist_ok=True);assert not (out/'STARTED.json').exists(),'NO_REPLACEMENT_RUN'
 gate();torch.manual_seed(seed);np.random.seed(seed);random.seed(seed);rng=np.random.default_rng(seed);model=build('S1','cpu');opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001);scheduler=torch.optim.lr_scheduler.CosineAnnealingLR(opt,80,eta_min=1e-5)
 initial={k:v.detach().clone() for k,v in model.state_dict().items()};g={s:loadgeom(s) for s in tr};labels={s:dict(np.load(R/'01_dataset/targets'/(s+'.npz'))) for s in tr};history=[];membership=[];res=[];start=time.monotonic();steps=0;monitor_stop=threading.Event()
 def monitor():
  while not monitor_stop.is_set():res.append(resources());monitor_stop.wait(.5)
 monitor_thread=threading.Thread(target=monitor,daemon=True);monitor_thread.start()
 write(out/'STARTED.json',dict(UTC=now(),fold=fold,seed=seed,train_sources=tr,heldout_sources=held,parameters=sum(x.numel() for x in model.parameters()),fresh_random_initialization=True,recipe_SHA256=sha(R/'MODEL_AND_TRAINING_SEAL.json'),architecture_SHA256=sha(R/'src/model_e3.py'),feature_SHA256=sha(R/'03_protocol/FEATURE_SCHEMA.json'),split_SHA256=sha(R/'DATASET_AND_SPLIT_SEAL.json'),initial_state_digest=hashlib.sha256(b''.join(v.numpy().tobytes() for v in initial.values())).hexdigest(),dryrun=dry))
 try:
  for epoch in range(1 if dry else 80):
   assert time.monotonic()-start<36000,'RUN_WALL_LIMIT'
   res.append(gate());model.train();losses=[]
   for idx in rng.permutation(len(tr)):
    sid=tr[idx];assert sid not in held and sid[0] not in {s[0] for s in held};d=labels[sid];m=d['core']&d['valid'];ix=np.flatnonzero(m);a=d['area'][ix];salt=int(hashlib.sha256(sid.encode()).hexdigest()[:8],16);qrng=np.random.default_rng(np.random.SeedSequence([seed,salt,epoch]));q=qrng.choice(ix,512,replace=True,p=a/a.sum());assert np.array_equal(d['source_ids'][q],g[sid]['source_ids'][q]);weight=len(tr)/(4*sum(s[0]==sid[0] for s in tr));opt.zero_grad(set_to_none=True);pred=model(g[sid],q);assert pred.shape==(512,) and torch.isfinite(pred).all();target=torch.as_tensor(d['T2_MPa'][q]/100,dtype=torch.float32);raw=((pred-target)**2).mean();loss=raw*weight;assert torch.isfinite(loss);loss.backward();assert all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters());grad=torch.nn.utils.clip_grad_norm_(model.parameters(),1);assert torch.isfinite(grad);opt.step();steps+=1;losses.append(float(loss.detach()));membership.append(dict(epoch=epoch,source_id=sid,plate=sid[0],heldout_plate=held[0][0],queries=512,source_step_weight=weight,source_ID_hash=hashlib.sha256(d['source_ids'][q].tobytes()).hexdigest(),heldout_overlap=0))
    if dry:break
   scheduler.step();history.append(dict(run=run,fold=fold,seed=seed,epoch=epoch+1,weighted_MSE_K=float(np.mean(losses)),steps=steps,elapsed_s=time.monotonic()-start));table(out/'history.csv',history);table(out/'runtime_membership.csv',membership);table(out/'resources.csv',res)
   if epoch%10==0 or epoch==79:print(run,'EPOCH',epoch+1,'LOSS',history[-1]['weighted_MSE_K'],'SECONDS',round(time.monotonic()-start,1),flush=True)
   if not dry and (epoch%10==0 or epoch==79):
    p=out/('epoch_'+str(epoch+1)+'.pt');torch.save(dict(state_dict=model.state_dict(),optimizer=opt.state_dict(),scheduler=scheduler.state_dict(),rng=rng.bit_generator.state,torch_rng=torch.get_rng_state(),epoch=epoch+1,fold=fold,seed=seed,train_sources=tr,heldout_sources=held,recipe_SHA256=sha(R/'MODEL_AND_TRAINING_SEAL.json')),p);write(out/'RECOVERY_POINTER.json',dict(path=str(p),sha256=sha(p),epoch=epoch+1,steps=steps))
  monitor_stop.set();monitor_thread.join();table(out/'resources.csv',res);result=dict(UTC=now(),status='COMPLETE',fold=fold,seed=seed,epochs=1 if dry else 80,steps=steps,training_s=time.monotonic()-start,parameters=sum(x.numel() for x in model.parameters()),train_sources=tr,heldout_sources=held,runtime_membership_SHA256=sha(out/'runtime_membership.csv'),resources=res[-1],peak_RSS_bytes=max(a['RSS_bytes'] for a in res),peak_GPU_allocated_bytes=0,dryrun=dry)
  if dry:
   result.update(passed=True,finite_gradients=True,context_points=4096,query_points=512,loss_weight_verified=True,source_ID_alignment=True,heldout_overlap=0,optimization_steps=1);write(R/'TRAINING_DRY_RUN.json',result)
  else:result.update(checkpoint=str(p),checkpoint_SHA256=sha(p))
  write(out/'COMPLETED.json',result)
 except Exception as e:monitor_stop.set();monitor_thread.join();write(out/'FAILED.json',dict(UTC=now(),error=str(e),steps=steps,elapsed_s=time.monotonic()-start));raise
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--fold',default='F1');p.add_argument('--seed',type=int,default=20261021);p.add_argument('--dry',action='store_true');a=p.parse_args();main(a.fold,a.seed,a.dry)
