from common_e14 import *
import numpy as np,math
def q95(v,w):
 total=math.fsum(map(float,w));c=0.;previous_cdf=0.;previous=float(min(v))
 for i in sorted(range(len(v)),key=lambda i:float(v[i])):
  c+=float(w[i]);cdf=c/total;value=float(v[i])
  if cdf>=.95:return previous+(value-previous)*(.95-previous_cdf)/(cdf-previous_cdf)
  previous_cdf=cdf;previous=value
 return value
def main():
 verify_protocol();registry=rows(R/'20_reproducibility/PREDICTION_REGISTRY.csv');reported=rows(R/'SOURCE_CONTEXT_METRICS.csv');regional=rows(R/'REGIONAL_CONTEXT_ERRORS.csv');checks=[];runtime=[]
 for rec in registry:
  sid=rec['source_id'];d=dict(np.load(H/'01_dataset/targets'/(sid+'.npz')));ix=np.nonzero(d['core']&d['valid'])[0];p=dict(np.load(rec['path']));assert sha(rec['path'])==rec['SHA256'];assert np.array_equal(ix,p['query_original_rows']);assert all(np.array_equal(p[k],d[k][ix]) for k in ['source_ids','xyz','area']);assert p['valid'].all() and np.all(p['tile_count']==1);w=d['area'][ix];y=d['T2_MPa'][ix];v=p['pred_MPa'];total=math.fsum(map(float,w));sse=math.fsum(float(a)*(float(b)-float(c))**2 for a,b,c in zip(w,v,y));den=math.fsum(float(a)*float(b)**2 for a,b in zip(w,y));mae=math.fsum(float(a)*abs(float(b)-float(c)) for a,b,c in zip(w,v,y))/total;bias=math.fsum(float(a)*(float(b)-float(c)) for a,b,c in zip(w,v,y))/total;predq=q95(v,w);refq=q95(y,w);hy=y>=refq;hp=v>=predq;inter=math.fsum(float(w[i]) for i in range(len(w)) if hy[i] and hp[i]);union=math.fsum(float(w[i]) for i in range(len(w)) if hy[i] or hp[i]);values=dict(L2=math.sqrt(sse/den),MAE_MPa=mae,RMSE_MPa=math.sqrt(sse/total),bias_MPa=bias,high95_IoU=inter/union,high95_precision=inter/math.fsum(float(w[i]) for i in range(len(w)) if hp[i]),high95_recall=inter/math.fsum(float(w[i]) for i in range(len(w)) if hy[i]),Q95_error_MPa=predq-refq,max_error_MPa=float(max(v)-max(y)),pred_Kmax=float(max(v)/100),reference_Kmax=float(max(y)/100))
  row=next(a for a in reported if all(a[k]==rec[k] for k in ['model','seed','condition','source_id']))
  for key,value in values.items():
   err=abs(value-float(row[key]));assert math.isclose(value,float(row[key]),abs_tol=1e-8,rel_tol=1e-10),(rec,key,value,row[key]);checks.append(dict(model=rec['model'],seed=rec['seed'],condition=rec['condition'],source_id=sid,check=key,absolute_error=err,passed=True))
  for region in set(map(int,d['region'][ix])):
   jj=[i for i in range(len(ix)) if int(d['region'][ix[i]])==region];num=math.fsum(float(w[i])*(float(v[i])-float(y[i]))**2 for i in jj);de=math.fsum(float(w[i])*float(y[i])**2 for i in jj);value=math.sqrt(num/de);row=next(a for a in regional if all(a[k]==rec[k] for k in ['model','seed','condition','source_id']) and int(a['region'])==region);err=abs(value-float(row['L2']));assert err<1e-8;checks.append(dict(model=rec['model'],seed=rec['seed'],condition=rec['condition'],source_id=sid,check='region_'+str(region)+'_L2',absolute_error=err,passed=True))
  print('METRICS_INDEPENDENT',rec['model'],rec['seed'],rec['condition'],sid,flush=True)
 plates=rows(R/'PLATE_CONTEXT_METRICS.csv')
 for a in plates:
  ss=[b for b in reported if all(b[k]==a[k] for k in ['model','seed','condition','plate'])]
  for metric in ['L2','MAE_MPa','RMSE_MPa','bias_MPa','high95_IoU','high95_precision','high95_recall','worst_regional_L2']:
   value=math.fsum(float(b[metric]) for b in ss)/len(ss);assert abs(value-float(a[metric]))<1e-10
 for a in rows(R/'SEED_CONTEXT_METRICS.csv'):
  pp=[b for b in plates if all(b[k]==a[k] for k in ['model','seed','condition'])];assert len(pp)==5
  for metric in ['L2','MAE_MPa','RMSE_MPa','bias_MPa','high95_IoU','high95_precision','high95_recall','worst_regional_L2']:assert abs(math.fsum(float(b[metric]) for b in pp)/5-float(a['equal_plate_'+metric]))<1e-10
 from context_e14 import parts
 for p in sorted((R/'11_context_robust_training').glob('F*_s*/STARTED.json')):
  start=read(p);rec=read(p.parent/'COMPLETED.json');members=rows(p.parent/'runtime_membership.csv');queries=np.load(p.parent/'QUERY_SOURCE_IDS.npy');assert sha(p.parent/'runtime_membership.csv')==rec['runtime_membership_SHA256'];assert sha(p.parent/'QUERY_SOURCE_IDS.npy')==rec['query_ID_file_SHA256'];assert sha(rec['checkpoint'])==rec['checkpoint_SHA256'];assert start['fresh_random_initialization'];assert len(members)==80*len(start['train_sources']);assert not {s[0] for s in start['train_sources']}&{s[0] for s in start['heldout_sources']};data={s:dict(np.load(H/'01_dataset/targets'/(s+'.npz'))) for s in start['train_sources']}
  oldstart=read(H/'05_training'/p.parent.name/'STARTED.json');assert start['initial_state_SHA256']==oldstart['initial_state_digest'];oldmembers={(int(a['epoch']),a['source_id']):a for a in rows(H/'05_training'/p.parent.name/'runtime_membership.csv')}
  for epoch in range(80):
   ee=[a for a in members if int(a['epoch'])==epoch];assert len(ee)==len(start['train_sources']) and {a['source_id'] for a in ee}==set(start['train_sources'])
   for plate in {s[0] for s in start['train_sources']}:assert abs(sum(float(a['source_step_weight']) for a in ee if a['plate']==plate)/len(ee)-.25)<1e-14
  for b in members:
   sid=b['source_id'];epoch=int(b['epoch']);seed=int(start['seed']);assert sid in start['train_sources'] and sid[0]!=start['heldout_sources'][0][0];salt=int(hashlib.sha256(sid.encode()).hexdigest()[:8],16);ctype=['FULL','X50','X43'][int(np.random.default_rng(np.random.SeedSequence([seed,salt,epoch,140014])).integers(0,3))];assert ctype==b['context_type'];d=data[sid];ix=np.flatnonzero(d['core']&d['valid']);a=d['area'][ix];q=np.random.default_rng(np.random.SeedSequence([seed,salt,epoch])).choice(ix,512,replace=True,p=a/a.sum());ids=d['source_ids'][q];assert np.array_equal(queries[int(b['query_row'])],ids);h=hashlib.sha256(ids.tobytes()).hexdigest();assert b['query_source_IDs_SHA256']==b['label_source_IDs_SHA256']==h;weight=len(start['train_sources'])/(4*sum(s[0]==sid[0] for s in start['train_sources']));assert abs(float(b['source_step_weight'])-weight)<1e-14
   assert oldmembers[epoch,sid]['source_ID_hash']==h
   recorded=json.loads(b['contexts']);actual=parts(sid,q,ctype);assert len(recorded)==len(actual)
   for z,(loc,g,mapped) in zip(recorded,actual):
    assert z['query_positions']==loc.tolist();assert np.array_equal(g['source_ids'][mapped],ids[loc]);assert z['context_source_IDs_SHA256']==hashlib.sha256(g['source_ids'][g['context']].tobytes()).hexdigest();assert z['visible_source_IDs_SHA256']==hashlib.sha256(g['source_ids'].tobytes()).hexdigest();assert len(np.unique(g['source_ids'][g['context']]))==4096
  runtime.append(dict(run=p.parent.name,actual_batches=len(members),query_and_label_alignment=True,geometry_only_context_RNG=True,context_membership_replayed=True,source_overlap=0,plate_overlap=0,passed=True));print('RUNTIME_REPLAY_PASS',p.parent.name,len(members),flush=True)
 assert len(runtime)==10;table(R/'INDEPENDENT_METRIC_CHECKS.csv',checks);table(R/'INDEPENDENT_LEAKAGE_CHECKS.csv',runtime);write(R/'17_independent_audits/INDEPENDENT_PASS.json',dict(UTC=now(),passed=True,metric_checks=len(checks),max_abs_error=max(a['absolute_error'] for a in checks),source_fields=182,runs=10,actual_batches=sum(a['actual_batches'] for a in runtime),absolute_tolerance=1e-8,relative_tolerance=1e-10))
if __name__=='__main__':main()
