from common_e15 import *
import numpy as np,math

def q95(v,w):
 order=sorted(range(len(v)),key=lambda i:float(v[i]));v=v[order];w=w[order];total=math.fsum(map(float,w));c=np.cumsum(w)/total;k=int(np.searchsorted(c,.95));
 if k==0:return float(v[0])
 if k>=len(v):return float(v[-1])
 return float(v[k-1]+(v[k]-v[k-1])*(.95-c[k-1])/(c[k]-c[k-1]))

def main():
 assert read(R/'21_reproducibility/EVALUATION_COMPLETE.json')['passed'];verify_protocol();checks=[];leak=[];fields=rows(R/'SOURCE_LEVEL_FIELD_METRICS.csv');rawregs=rows(R/'21_reproducibility/REPLAY_REGISTRY.csv')+rows(R/'21_reproducibility/INTERVENTION_REGISTRY.csv');runtime=0;cache={};maxerror=0.
 for folder in ['05_original_prediction_replay','11_raw_tile_predictions']:
  for file in sorted((R/folder).glob('*_RUNTIME.csv')):
   for b in rows(file):
    path=R/folder/(b['field']+'.npz')
    if cache.get('field')!=b['field']:cache={'field':b['field'],'raw':dict(np.load(path))}
    raw=cache['raw'];start=int(b['query_offset']);n=int(b['query_count']);ids=raw['source_ids'][start:start+n];assert hashlib.sha256(ids.tobytes()).hexdigest()==b['query_ID_SHA256'];assert np.all(raw['tile_id'][start:start+n]==int(b['tile']));assert b['source_id'][0]==b['heldout_plate'];ck=next(a for a in rows(R/'N1_N2_CHECKPOINT_HASHES.csv') if all(a[k]==b[k] for k in ['model','fold','seed']));assert b['source_id'] in ck['heldout_sources'].split(';') and ck['actual_SHA256']==b['checkpoint_SHA256'];ctx=np.load(b['context_ID_path']);assert len(ctx)==len(set(ctx))==4096 and hashlib.sha256(ctx.tobytes()).hexdigest()==b['context_ID_SHA256'];assert b['grad_enabled']=='False' and b['optimizer_exists']=='False'
    gp=b['geometry_path'];key=(gp,b['feature_policy'],b['experiment'])
    if cache.get('geometry_key')!=key:
     g=dict(np.load(gp));expected=g['features'].copy()
     if b['feature_policy']=='ORACLE_FULL_GEOMETRY_DIAGNOSTIC':
      full=dict(np.load(H/'02_geometry'/(b['source_id']+'.npz')));jj=np.searchsorted(full['source_ids'],g['source_ids']);columns=read(R/'FROZEN_DIAGNOSTIC_PARAMETERS.json')['oracle_columns'];expected[:,columns]=full['features'][jj][:,columns]
     assert hashlib.sha256(expected.tobytes()).hexdigest()==b['feature_SHA256'];cache.update(geometry_key=key,g=g)
    g=cache['g'];assert np.isin(ids,g['source_ids']).all() and np.isin(ctx,g['source_ids']).all();expected_ctx=g['source_ids'][g['context']]
    if b['condition']=='FULL' and b['experiment']=='SHIFT':expected_ctx=g['source_ids'][np.load(R/'02_source_geometry'/b['source_id']/'FULL_SHIFT_CONTEXT.npy')]
    assert np.array_equal(ctx,expected_ctx);runtime+=1
   leak.append(dict(runtime_file=str(file),forward_batches=len(rows(file)),source_membership=True,checkpoint_assignment=True,visible_context_membership=True,query_hashes=True,feature_hashes=True,no_grad=True,optimizer_absent=True,passed=True));print('RUNTIME_AUDIT',file.name,runtime,flush=True)
 assert runtime==read(R/'INFERENCE_EXECUTION_BUDGET.json')['forward_batches_exact']
 def verify(name,value,expected,base,tol=1e-9):
  nonlocal maxerror
  err=abs(float(value)-float(expected));maxerror=max(maxerror,err);assert err<=tol,(name,err,base);checks.append(dict(**base,check=name,reported=float(expected),independent=float(value),absolute_difference=err,passed=True))
 for a in fields:
  sid=a['source_id'];base={k:a[k] for k in ['model','seed','source_id','condition','policy']};p=dict(np.load(a['path']));sr=next(t for t in rows(R/'SOURCE_CORE_REGISTRY.csv') if t['source_id']==sid);d=dict(np.load(sr['target_path']));q=np.flatnonzero(d['core']&d['valid']);assert np.array_equal(p['source_ids'],d['source_ids'][q]) and np.array_equal(p['xyz'],d['xyz'][q]) and np.array_equal(p['area'],d['area'][q]);assert np.array_equal(p['reference_MPa'],d['T2_MPa'][q]);y=d['T2_MPa'][q];v=p['pred_MPa'];w=d['area'][q];delta=v-y;total=math.fsum(map(float,w));sse=math.fsum(map(float,w*delta*delta));sq=math.fsum(map(float,w*y*y));qy=q95(y,w);qp=q95(v,w);hy=y>=qy;hp=v>=qp;inter=math.fsum(map(float,w[hy&hp]));union=math.fsum(map(float,w[hy|hp]));tr=math.fsum(map(float,w[hy]));pr=math.fsum(map(float,w[hp]));cy=np.array([math.fsum(map(float,p['xyz'][hy,k]*w[hy]))/tr for k in range(3)]);cp=np.array([math.fsum(map(float,p['xyz'][hp,k]*w[hp]))/pr for k in range(3)])
  computed=dict(L2=math.sqrt(sse/sq),MAE_MPa=math.fsum(map(float,w*abs(delta)))/total,RMSE_MPa=math.sqrt(sse/total),bias_MPa=math.fsum(map(float,w*delta))/total,high95_IoU=inter/union,high95_precision=inter/pr,high95_recall=inter/tr,high95_centroid_distance_mm=float(np.linalg.norm(cp-cy)),Q95_error_MPa=qp-qy,Kmax_error=(max(v)-max(y))/100,high95_FN_area_mm2=math.fsum(map(float,w[hy&~hp])),high95_FP_area_mm2=math.fsum(map(float,w[hp&~hy])))
  meanp=math.fsum(map(float,w*v))/total;meany=math.fsum(map(float,w*y))/total;computed['pred_std_MPa']=math.sqrt(math.fsum(map(float,w*(v-meanp)**2))/total);computed['ref_std_MPa']=math.sqrt(math.fsum(map(float,w*(y-meany)**2))/total);regional=[]
  for region in np.unique(d['region'][q]):
   mask=d['region'][q]==region;regional.append(math.sqrt(math.fsum(map(float,w[mask]*delta[mask]**2))/math.fsum(map(float,w[mask]*y[mask]**2))))
  computed['worst_regional_L2']=max(regional)
  for k,value in computed.items():verify(k,value,a[k],base)
  raw=dict(np.load(a['raw_path']));ll=raw['core_position']
  if a['policy'] in ['S1','S2']:
   ww=np.ones(len(ll)) if a['policy']=='S1' else raw['tent_weight'];numer=np.zeros(len(v));den=np.zeros(len(v));np.add.at(numer,ll,ww*raw['pred_MPa']);np.add.at(den,ll,ww);assert np.max(abs(numer/den-v))<1e-10
  if a['policy'] in ['SHIFT','ORACLE']:
   baseline=next(t for t in fields if t['policy']=='S0' and all(t[k]==a[k] for k in ['model','seed','source_id','condition']));ov=np.load(baseline['path'])['pred_MPa'];diff=v-ov;b=next(t for t in rows(R/'CONTEXT_PREDICTION_VARIATION.csv') if all(t[k]==a[k] for k in ['model','seed','source_id','condition','policy']));verify('paired_RMS',math.sqrt(math.fsum(map(float,w*diff*diff))/total),b['RMS_difference_MPa'],base);verify('paired_Q95',q95(abs(diff),w),b['Q95_absolute_difference_MPa'],base)
  adj=dict(np.load(R/'02_source_geometry'/sid/'ADJACENCY.npz'));ij=adj['pairs'];cross=(adj['tile_id'][ij[:,0]]!=adj['tile_id'][ij[:,1]])&adj['x_axis_edge'];actual=cross if a['condition']!='FULL' else np.zeros(len(cross),bool);r=next(t for t in rows(R/'BOUNDARY_JUMP_METRICS.csv') if all(t[k]==a[k] for k in ['model','seed','source_id','condition','policy']));assert int(r['pair_count'])==int(actual.sum())
  if actual.any():
   ids=ij[actual];pe=v[ids[:,1]]-v[ids[:,0]];ye=y[ids[:,1]]-y[ids[:,0]];verify('boundary_jump_error',float(np.mean(abs(pe-ye))),r['mean_jump_error_MPa'],base);verify('signed_excess_jump',float(np.mean(abs(pe)-abs(ye))),r['signed_excess_MPa'],base)
  if len(checks)%200<15:print('METRIC_AUDIT',len(checks),flush=True)
 for a in rows(R/'15_plate_level_metrics/SEED_MACRO_METRICS.csv'):
  ss=[b for b in fields if all(a[k]==b[k] for k in ['model','seed','condition','policy'])]
  for k in ['L2','MAE_MPa','high95_IoU']:
   independent=math.fsum(math.fsum(float(b[k]) for b in ss if b['plate']==plate)/len([b for b in ss if b['plate']==plate]) for plate in 'CEGHX')/5;verify('equal_plate_'+k,independent,a[k],{key:a[key] for key in ['model','seed','condition','policy']})
 table(R/'INDEPENDENT_METRIC_AUDIT.csv',checks);table(R/'INDEPENDENT_LEAKAGE_AUDIT.csv',leak)
 historical=[]
 for file in ['HISTORICAL_V1_TARGET_HASHES.csv','N1_N2_CHECKPOINT_HASHES.csv']:
  for a in rows(R/file):
   p=a.get('path',a.get('checkpoint'));assert sha(p)==a['actual_SHA256'];historical.append(dict(path=p,SHA256=sha(p),passed=True))
 for a in rows(R/'SOURCE_CORE_REGISTRY.csv'):assert sha(a['source_geometry_path'])==a['source_geometry_SHA256']
 for folder in ['05_original_prediction_replay','11_raw_tile_predictions']:
  for p in (R/folder).glob('*_COMPLETED.json'):
   receipt=read(p);assert receipt['parameter_state_before']==receipt['parameter_state_after'];assert receipt['training_fits']==receipt['optimizer_steps']==receipt['backpropagation']==0 if 'backpropagation' in receipt else receipt['training_fits']==receipt['optimizer_steps']==0
 table(R/'18_independent_verification/POSTEXECUTION_TARGET_CHECKPOINT_HASHES.csv',historical);write(R/'18_independent_verification/INDEPENDENT_PASS.json',dict(UTC=now(),passed=True,metric_checks=len(checks),runtime_forward_batches=runtime,maximum_metric_difference=maxerror,source_fields=len(fields),postexecution_target_checkpoint_hashes=len(historical),postexecution_source_geometry_hashes=13,training_fits=0,optimizer_steps=0,new_FE=0,external_predictions=0));print('INDEPENDENT_PASS',len(checks),maxerror,flush=True)
if __name__=='__main__':main()
