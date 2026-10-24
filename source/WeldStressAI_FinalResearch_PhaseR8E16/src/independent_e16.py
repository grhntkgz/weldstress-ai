from common_e16 import *
import numpy as np,math,pandas as pd
from functools import lru_cache
from features_e16 import parts,core

@lru_cache(maxsize=195)
def geometry_membership(sid,condition,tile):
 path=H/'02_geometry'/(sid+'.npz') if condition=='FULL' else J/'07_context_geometry'/sid/(condition+'_'+str(tile)+'.npz');d=np.load(path);ids=d['source_ids'];ctx=ids[d['context']];return ids,hashlib.sha256(ctx.tobytes()).hexdigest(),hashlib.sha256(ids.tobytes()).hexdigest()

def independent_quantile(v,w):
 total=math.fsum(map(float,w));cum=0.;lastcdf=0.;last=float(min(v))
 for i in sorted(range(len(v)),key=lambda i:float(v[i])):
  cum+=float(w[i]);cdf=cum/total;value=float(v[i])
  if cdf>=.95:return last+(value-last)*(.95-lastcdf)/(cdf-lastcdf)
  lastcdf=cdf;last=value
 return value
def independent_values(y,v,w,x,region):
 total=math.fsum(map(float,w));dot=lambda a:math.fsum(float(wi)*float(ai) for wi,ai in zip(w,a));ym=dot(y)/total;vm=dot(v)/total;sse=math.fsum(float(a)*(float(b)-float(c))**2 for a,b,c in zip(w,v,y));den=dot(y*y);refq=independent_quantile(y,w);predq=independent_quantile(v,w);hy=y>=refq;hp=v>=predq;area=lambda z:math.fsum(float(a) for a,b in zip(w,z) if b);inter=area(hy&hp);refarea=area(hy);predarea=area(hp);centroid=lambda z:np.array([math.fsum(float(w[i])*float(x[i,k]) for i in np.flatnonzero(z))/area(z) for k in range(3)]);rr=[]
 for r in sorted(set(map(int,region))):
  ii=np.flatnonzero(region==r);num=math.fsum(float(w[i])*(float(v[i])-float(y[i]))**2 for i in ii);de=math.fsum(float(w[i])*float(y[i])**2 for i in ii);rr.append(math.sqrt(num/de))
 return dict(L2=math.sqrt(sse/den),MAE_MPa=math.fsum(float(a)*abs(float(b)-float(c)) for a,b,c in zip(w,v,y))/total,RMSE_MPa=math.sqrt(sse/total),bias_MPa=math.fsum(float(a)*(float(b)-float(c)) for a,b,c in zip(w,v,y))/total,high95_IoU=inter/area(hy|hp),high95_precision=inter/predarea,high95_recall=inter/refarea,high95_centroid_distance_mm=float(np.linalg.norm(centroid(hy)-centroid(hp))),worst_regional_L2=max(rr),max_error_MPa=float(max(v)-max(y)),Q95_error_MPa=predq-refq,absolute_max_error_MPa=abs(float(max(v)-max(y))),absolute_Q95_error_MPa=abs(predq-refq),pred_variance_MPa2=math.fsum(float(a)*(float(b)-vm)**2 for a,b in zip(w,v))/total,ref_variance_MPa2=math.fsum(float(a)*(float(b)-ym)**2 for a,b in zip(w,y))/total,false_negative_area_mm2=area(hy&~hp),false_positive_area_mm2=area(hp&~hy))
def main():
 verify_protocol();gate();checks=[];leak=[];data={s:dict(np.load(H/'01_dataset/targets'/(s+'.npz'))) for s in {a['source_id'] for a in rows(R/'QUALIFIED13_SOURCE_REGISTRY.csv')}};modelrows=rows(R/'SOURCE_LEVEL_METRICS.csv');factrows=rows(R/'BLOCK_FACTORIAL_RESULTS.csv');lookup={tuple(a[k] for k in ['model','seed','source_id','condition']):a for a in modelrows};fl={tuple(a[k] for k in ['model','seed','source_id','condition','cell']):a for a in factrows}
 for registry,isfactor in [(rows(R/'MODEL_PREDICTION_REGISTRY.csv'),False),(rows(R/'05_blockwise_interventions/ALL_FIELD_REGISTRY.csv'),True)]:
  for rec in registry:
   d=data[rec['source_id']];q=np.flatnonzero(d['core']&d['valid']);p=dict(np.load(rec['path']));assert sha(rec['path'])==rec['SHA256']
   if len(p['source_ids'])!=len(q):
    assert all(np.array_equal(p[k],d[k]) for k in ['source_ids','xyz','area']);p={k:(np.take(v,q,axis=0) if isinstance(v,np.ndarray) and v.ndim and len(v)==len(d['source_ids']) else v) for k,v in p.items()}
   assert all(np.array_equal(p[k],d[k][q]) for k in ['source_ids','xyz','area']);assert 'query_original_rows' not in p or np.array_equal(p['query_original_rows'],q);key=tuple(rec[k] for k in ['model','seed','source_id','condition']+(['cell'] if isfactor else []));row=fl[key] if isfactor else lookup[key];values=independent_values(d['T2_MPa'][q],p['pred_MPa'],d['area'][q],d['xyz'][q],d['region'][q])
   for k,value in values.items():
    error=abs(value-float(row[k]));assert math.isclose(value,float(row[k]),abs_tol=1e-8,rel_tol=1e-10),(key,k,value,row[k]);checks.append(dict(field='|'.join(key),metric=k,absolute_error=error,passed=True))
   print('INDEPENDENT_METRICS','|'.join(key),flush=True)
 table(R/'INDEPENDENT_METRIC_AUDIT.csv',checks)
 # Independent aggregation and factorial Walsh contrasts, using fsum rather than pandas/primary contrast helper.
 agg=[]
 for name,source,groups in [('PLATE_LEVEL_METRICS.csv',modelrows,['model','seed','condition','plate']),('17_model_comparisons/SEED_METRICS.csv',rows(R/'PLATE_LEVEL_METRICS.csv'),['model','seed','condition']),('17_model_comparisons/TWO_SEED_METRIC_MEANS.csv',rows(R/'17_model_comparisons/SEED_METRICS.csv'),['model','condition'])]:
  for a in rows(R/name):
   z=[b for b in source if all(b[k]==a[k] for k in groups)]
   for k in values:
    value=math.fsum(float(b[k]) for b in z)/len(z);err=abs(value-float(a[k]));assert err<1e-8;agg.append(dict(table=name,key='|'.join(a[k] for k in groups),metric=k,absolute_error=err,passed=True))
 for a in rows(R/'BLOCK_MAIN_EFFECTS.csv')+rows(R/'BLOCK_INTERACTIONS.csv'):
  z=[b for b in factrows if all(b[k]==a[k] for k in ['model','seed','source_id','condition'])];bits=['ABC'.index(c)+1 for c in a['effect']]
  for k in values:
   pos=[float(b[k]) for b in z if sum(b['cell'][i]=='0' for i in bits)%2==0];neg=[float(b[k]) for b in z if sum(b['cell'][i]=='0' for i in bits)%2==1];value=(math.fsum(pos)-math.fsum(neg))/4;err=abs(value-float(a[k]));assert err<1e-8;agg.append(dict(table='FACTORIAL_CONTRAST',key='|'.join(a[k] for k in ['model','seed','source_id','condition','effect']),metric=k,absolute_error=err,passed=True))
 table(R/'18_independent_verification/AGGREGATION_AND_CONTRAST_AUDIT.csv',agg)
 for p in sorted((R/'11_N3_training').glob('F*_s*/STARTED.json')):
  start=read(p);done=read(p.parent/'COMPLETED.json');members=rows(p.parent/'runtime_membership.csv');queries=np.load(p.parent/'QUERY_SOURCE_IDS.npy');tr=start['train_sources'];held=start['heldout_sources'];seed=int(start['seed']);assert not set(s[0] for s in tr)&set(s[0] for s in held);assert len(members)==80*len(tr)==done['steps'];assert sha(done['checkpoint'])==done['checkpoint_SHA256'];assert sha(p.parent/'runtime_membership.csv')==done['runtime_membership_SHA256'];assert sha(p.parent/'QUERY_SOURCE_IDS.npy')==done['query_ID_file_SHA256'];oldstart=read(J/'11_context_robust_training'/p.parent.name/'STARTED.json');assert start['initial_state_SHA256']==oldstart['initial_state_SHA256'];assert start['fresh_random_initialization']
  for epoch in range(80):
   ee=[b for b in members if int(b['epoch'])==epoch];assert {b['source_id'] for b in ee}==set(tr)
   for plate in {s[0] for s in tr}:assert abs(math.fsum(float(b['source_step_weight']) for b in ee if b['plate']==plate)/len(ee)-.25)<1e-14
  for b in members:
   sid=b['source_id'];epoch=int(b['epoch']);assert sid in tr and sid[0] not in {s[0] for s in held};d=data[sid];ix=np.flatnonzero(d['core']&d['valid']);a=d['area'][ix];salt=int(hashlib.sha256(sid.encode()).hexdigest()[:8],16);q=np.random.default_rng(np.random.SeedSequence([seed,salt,epoch])).choice(ix,512,replace=True,p=a/a.sum());ids=d['source_ids'][q];assert np.array_equal(ids,queries[int(b['query_row'])]);c=['FULL','X50','X43'][int(np.random.default_rng(np.random.SeedSequence([seed,salt,epoch,140014])).integers(0,3))];assert c==b['context_type'];assert b['query_source_IDs_SHA256']==b['label_source_IDs_SHA256']==hashlib.sha256(ids.tobytes()).hexdigest();assert abs(float(b['source_step_weight'])-len(tr)/(4*sum(t[0]==sid[0] for t in tr)))<1e-14
   sourcecore=core(sid);qpos=np.searchsorted(sourcecore['query_original_rows'],q);assert np.array_equal(sourcecore['query_original_rows'][qpos],q);tiles=sourcecore['tile_id'][qpos];recorded_contexts=json.loads(b['contexts']);assert len(recorded_contexts)==len(np.unique(tiles))
   for recorded,tile in zip(recorded_contexts,np.unique(tiles)):
    loc=np.flatnonzero(tiles==tile);visible,ctxhash,visiblehash=geometry_membership(sid,c,int(tile));mapped=np.searchsorted(visible,ids[loc]);assert recorded['query_positions']==loc.tolist();assert np.array_equal(visible[mapped],ids[loc]);assert recorded['context_source_IDs_SHA256']==ctxhash;assert recorded['visible_source_IDs_SHA256']==visiblehash
  leak.append(dict(model='N3',run=p.parent.name,actual_batches=len(members),train_sources=len(tr),heldout_sources=len(held),plate_overlap=0,source_overlap=0,query_RNG_replayed=True,initial_random_state_matches_frozen_seed=True,passed=True));print('TRAIN_MEMBERSHIP_PASS',p.parent.name,flush=True)
 sys.path.insert(0,str(R/'runtime_site'));import xgboost as xgb
 assert xgb.__version__=='3.0.2'
 for p in sorted((R/'12_XGBoost_baseline').glob('F*/COMPLETED.json')):
  done=read(p);tr=done['train_sources'];held=done['heldout_sources'];assert not {s[0] for s in tr}&{s[0] for s in held};a=dict(np.load(p.parent/'ACTUAL_TRAINING_ARRAYS.npz'));samples=rows(p.parent/'SAMPLE_IDS.csv');assert len(samples)==len(a['features']);assert sha(p.parent/'ACTUAL_TRAINING_ARRAYS.npz')==done['training_arrays_SHA256'];assert sha(p.parent/'model.ubj')==done['model_SHA256'];booster=xgb.Booster();booster.load_model(str(p.parent/'model.ubj'));assert booster.num_boosted_rounds()==500 and booster.num_features()==19;assert done['parameters']==read(R/'XGBOOST_BASELINE_PROTOCOL.json')['parameters'];offset=0;raw=[]
  for sid in tr:
   d=data[sid];s=core(sid);i=np.searchsorted(np.cumsum(s['area'])/sum(s['area']),(np.arange(1024)+.5)/1024);assert len(set(i))==1024;q=s['query_original_rows'][i]
   for c in ['FULL','X50','X43']:
    sl=slice(offset,offset+1024);f=np.empty((1024,19),dtype='f4')
    for loc,g,idx in parts(sid,q,c):f[loc]=g['features'][idx]
    assert np.array_equal(f,a['features'][sl]);assert np.array_equal(a['target_K'][sl],(d['T2_MPa'][q]/100).astype('f4'));assert np.array_equal(a['point_ids'][sl],s['source_ids'][i]);assert all(z==sid for z in a['source_ids'][sl]);assert all(z==c for z in a['condition'][sl]);raw.extend([1/(4*sum(t[0]==sid[0] for t in tr)*3*1024)]*1024);offset+=1024
  weights=np.array(raw);weights*=len(weights)/sum(weights);assert np.allclose(weights,a['sample_weight'],atol=1e-11,rtol=1e-11);leak.append(dict(model='B2_GEOMETRY_XGBOOST',run=p.parent.name,actual_batches=1,train_sources=len(tr),heldout_sources=len(held),plate_overlap=0,source_overlap=0,query_RNG_replayed=True,initial_random_state_matches_frozen_seed='NA tree model',passed=True));print('XGB_MEMBERSHIP_PASS',p.parent.name,flush=True)
 table(R/'INDEPENDENT_LEAKAGE_AUDIT.csv',leak)
 # Fresh terminal historical hashes, no stale hash cache reuse.
 history=rows(R/'00_integrity/VERIFIED_HISTORICAL_ARTIFACTS.csv')+rows(R/'00_integrity/ADDITIONAL_CORE_HASH_AUDIT.csv')+[dict(path=a['target_path'],SHA256=a['SHA256']) for a in rows(R/'FROZEN_NUMERICAL_TARGET_HASHES.csv')]+[dict(path=a['cache_path'],SHA256=a['cache_SHA256']) for a in rows(R/'00_integrity/TRAINING_CACHE_TARGET_EQUIVALENCE.csv')];out=[]
 for a in history:
  p=Path(a['path']);h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
  expected=a.get('SHA256',a.get('actual_SHA256'));assert h.hexdigest()==expected;out.append(dict(path=str(p),SHA256=h.hexdigest(),passed=True))
 table(R/'00_integrity/TERMINAL_HISTORICAL_HASH_AUDIT.csv',out);assert len(leak)==15
 write(R/'18_independent_verification/INDEPENDENT_PASS.json',dict(UTC=now(),passed=True,metric_fields=1131,metric_checks=len(checks),max_metric_abs_error=max(a['absolute_error'] for a in checks),aggregation_and_contrast_checks=len(agg),N3_runs=10,XGB_folds=5,runtime_N3_batches=sum(a['actual_batches'] for a in leak if a['model']=='N3'),terminal_historical_hashes=len(out),resource=gate()))
if __name__=='__main__':main()
