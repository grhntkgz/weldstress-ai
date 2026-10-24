from common_e16 import *
import numpy as np,torch,argparse,threading,random
from model_e3 import build
from features_e16 import parts
def main(fold,seed,dry=False):
 verify_protocol();assert read(R/'10_training_validation/FEATURE_CONTRACT_PASS.json')['passed'];torch.set_num_threads(2);torch.use_deterministic_algorithms(True);rr=[a for a in rows(R/'FROZEN_LOPO_SPLITS.csv') if a['fold']==fold];tr=[a['source_id'] for a in rr if a['role']=='train'];held=[a['source_id'] for a in rr if a['role']=='heldout'];guard(training=tr);run=('DRY_' if dry else '')+fold+'_s'+str(seed);out=R/'11_N3_training'/run;out.mkdir(exist_ok=True);assert not (out/'STARTED.json').exists(),'NO_REPLACEMENT_FIT';gate();torch.manual_seed(seed);np.random.seed(seed);random.seed(seed);rng=np.random.default_rng(seed);model=build('S1','cpu');assert sum(p.numel() for p in model.parameters())==7228;opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001);scheduler=torch.optim.lr_scheduler.CosineAnnealingLR(opt,80,eta_min=1e-5);labels={s:dict(np.load(H/'01_dataset/targets'/(s+'.npz'))) for s in tr};initial=hashlib.sha256(b''.join(p.detach().numpy().tobytes() for p in model.state_dict().values())).hexdigest();start=time.monotonic();history=[];members=[];queryrows=[];samples=[];steps=0;stop=threading.Event()
 def monitor():
  while not stop.is_set():samples.append(resources());stop.wait(1)
 thread=threading.Thread(target=monitor,daemon=True);thread.start();write(out/'STARTED.json',dict(UTC=now(),fold=fold,seed=seed,train_sources=tr,heldout_sources=held,architecture_SHA256=sha(R/'src/model_e3.py'),base_architecture_SHA256=sha(R/'src/base_arch.py'),protocol_SHA256=sha(R/'PREREGISTRATION_SEAL.json'),initial_state_SHA256=initial,fresh_random_initialization=True,dryrun=dry))
 try:
  for epoch in range(1 if dry else 80):
   gate();assert time.monotonic()-start<36000;losses=[]
   for si in rng.permutation(len(tr)):
    sid=tr[si];assert sid not in held and sid[0]!=held[0][0];d=labels[sid];m=d['core']&d['valid'];ix=np.flatnonzero(m);a=d['area'][ix];salt=int(hashlib.sha256(sid.encode()).hexdigest()[:8],16);q=np.random.default_rng(np.random.SeedSequence([seed,salt,epoch])).choice(ix,512,replace=True,p=a/a.sum());ctype=['FULL','X50','X43'][int(np.random.default_rng(np.random.SeedSequence([seed,salt,epoch,140014])).integers(0,3))];opt.zero_grad(set_to_none=True);prediction=torch.zeros(512);contexts=[]
    for loc,g,localq in parts(sid,q,ctype):
     assert np.array_equal(g['source_ids'][localq],d['source_ids'][q[loc]]);p=model(g,localq);prediction=prediction.index_copy(0,torch.as_tensor(loc,dtype=torch.int64),p);context_ids=g['source_ids'][g['context']];assert len(context_ids)==len(np.unique(context_ids))==4096;contexts.append(dict(query_positions=loc.tolist(),context_source_IDs_SHA256=hashlib.sha256(context_ids.tobytes()).hexdigest(),visible_source_IDs_SHA256=hashlib.sha256(g['source_ids'].tobytes()).hexdigest(),query_source_IDs_SHA256=hashlib.sha256(d['source_ids'][q[loc]].tobytes()).hexdigest()))
    target=torch.as_tensor(d['T2_MPa'][q]/100,dtype=torch.float32);weight=len(tr)/(4*sum(s[0]==sid[0] for s in tr));raw=((prediction-target)**2).mean();loss=raw*weight;assert torch.isfinite(loss);loss.backward();assert all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters());grad=torch.nn.utils.clip_grad_norm_(model.parameters(),1);assert torch.isfinite(grad);
    if not dry:opt.step();steps+=1
    losses.append(float(loss.detach()));queryrows.append(d['source_ids'][q]);members.append(dict(epoch=epoch,step=steps,source_id=sid,plate=sid[0],heldout_plate=held[0][0],context_type=ctype,source_step_weight=weight,query_row=len(queryrows)-1,query_source_IDs_SHA256=hashlib.sha256(d['source_ids'][q].tobytes()).hexdigest(),label_source_IDs_SHA256=hashlib.sha256(d['source_ids'][q].tobytes()).hexdigest(),contexts=json.dumps(contexts,separators=(',',':')),heldout_overlap=0))
    if dry:break
   if not dry:scheduler.step()
   history.append(dict(fold=fold,seed=seed,epoch=epoch+1,weighted_MSE_K=float(np.mean(losses)),steps=steps,elapsed_s=time.monotonic()-start));table(out/'history.csv',history);table(out/'runtime_membership.csv',members)
   if epoch%10==0 or epoch==79:
    print(run,'EPOCH',epoch+1,'LOSS',history[-1]['weighted_MSE_K'],'S',round(time.monotonic()-start,2),flush=True)
    if not dry:
     ck=out/('epoch_'+str(epoch+1)+'.pt');torch.save(dict(state_dict=model.state_dict(),optimizer=opt.state_dict(),scheduler=scheduler.state_dict(),rng=rng.bit_generator.state,torch_rng=torch.get_rng_state(),epoch=epoch+1,fold=fold,seed=seed,train_sources=tr,heldout_sources=held,protocol_SHA256=sha(R/'PREREGISTRATION_SEAL.json')),ck);np.save(out/'QUERY_SOURCE_IDS.npy',np.array(queryrows,dtype='i8'));write(out/'RECOVERY_POINTER.json',dict(checkpoint=str(ck),SHA256=sha(ck),epoch=epoch+1,steps=steps))
  stop.set();thread.join();table(out/'resources.csv',samples);np.save(out/'QUERY_SOURCE_IDS.npy',np.array(queryrows,dtype='i8'));result=dict(UTC=now(),status='COMPLETE',fold=fold,seed=seed,epochs=1 if dry else 80,steps=steps,training_s=time.monotonic()-start,train_sources=tr,heldout_sources=held,parameters=7228,runtime_membership_SHA256=sha(out/'runtime_membership.csv'),query_ID_file_SHA256=sha(out/'QUERY_SOURCE_IDS.npy'),peak_RSS_bytes=max(a['RSS_bytes'] for a in samples),peak_GPU_allocated_bytes=0,dryrun=dry,context_counts={c:sum(a['context_type']==c for a in members) for c in ['FULL','X50','X43']})
  if dry:result.update(passed=True,finite_gradients=True,query_points=512,context_points=4096,source_ID_alignment=True,heldout_overlap=0);write(R/'10_training_validation/TRAINING_DRY_RUN.json',result)
  else:result.update(checkpoint=str(ck),checkpoint_SHA256=sha(ck))
  write(out/'COMPLETED.json',result)
 except Exception as e:stop.set();thread.join();write(out/'FAILED.json',dict(UTC=now(),error=str(e),steps=steps));raise
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--fold',default='F1');p.add_argument('--seed',type=int,default=20261021);p.add_argument('--dry',action='store_true');a=p.parse_args();main(a.fold,a.seed,a.dry)
