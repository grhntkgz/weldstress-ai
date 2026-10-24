from common_e13 import *
import numpy as np,math
def q95(values,weights):
 order=sorted(range(len(values)),key=lambda i:float(values[i]));total=math.fsum(map(float,weights));running=0.;previous_cdf=0.;previous_value=float(values[order[0]])
 for i in order:
  running+=float(weights[i]);cdf=running/total;value=float(values[i])
  if cdf>=.95:return previous_value+(value-previous_value)*(.95-previous_cdf)/(cdf-previous_cdf)
  previous_cdf=cdf;previous_value=value
 return value
def main():
 verify_seal();reported=rows(R/'SOURCE_LEVEL_METRICS.csv');registry=rows(R/'PREDICTION_REGISTRY.csv');checks=[];leak=[]
 for rec in registry:
  sid=rec['source_id'];d=dict(np.load(R/'01_dataset/targets'/(sid+'.npz')));p=dict(np.load(rec['path']));assert all(np.array_equal(p[k],d[k]) for k in ['source_ids','xyz','area']);ix=np.nonzero(d['valid']&d['core'])[0];y=d['T2_MPa'][ix];pred=p['pred_MPa'][ix];w=d['area'][ix];S=math.fsum(map(float,w));sse=math.fsum(float(a)*(float(b)-float(c))**2 for a,b,c in zip(w,pred,y));yy=math.fsum(float(a)*float(b)**2 for a,b in zip(w,y));mae=math.fsum(float(a)*abs(float(b)-float(c)) for a,b,c in zip(w,pred,y))/S;qy=q95(y,w);qp=q95(pred,w);hy=y>=qy;hp=pred>=qp;intersection=math.fsum(float(w[i]) for i in range(len(w)) if hy[i] and hp[i]);union=math.fsum(float(w[i]) for i in range(len(w)) if hy[i] or hp[i]);values=dict(MAE_MPa=mae,RMSE_MPa=math.sqrt(sse/S),L2=math.sqrt(sse/yy),ref_Q95_MPa=qy,pred_Q95_MPa=qp,high95_IoU=intersection/union)
  r=next(a for a in reported if all(str(a[k])==str(rec[k]) for k in ['model','fold','seed','source_id']))
  for key,v in values.items():
   err=abs(v-float(r[key]));passed=math.isclose(v,float(r[key]),rel_tol=1e-10,abs_tol=1e-8);assert passed,(sid,key,v,r[key]);checks.append(dict(model=rec['model'],fold=rec['fold'],seed=rec['seed'],source_id=sid,check=key,error=err,passed=passed))
  for region in np.unique(d['region'][ix]):
   ii=[int(i) for i in ix if d['region'][i]==region];num=math.fsum(float(d['area'][i])*(float(p['pred_MPa'][i])-float(d['T2_MPa'][i]))**2 for i in ii);den=math.fsum(float(d['area'][i])*float(d['T2_MPa'][i])**2 for i in ii);v=math.sqrt(num/den);r2=next(a for a in rows(R/'REGIONAL_PREDICTION_METRICS.csv') if all(str(a[k])==str(rec[k]) for k in ['model','fold','seed','source_id']) and int(a['region'])==region);err=abs(v-float(r2['L2']));assert err<=1e-8;checks.append(dict(model=rec['model'],fold=rec['fold'],seed=rec['seed'],source_id=sid,check='region_'+str(region)+'_L2',error=err,passed=True))
  assert p['valid'][ix].all() and np.all(p['tile_count'][ix]==1);print('INDEPENDENT_METRICS',rec['model'],rec['seed'],sid,flush=True)
 for study in rows(R/'MODEL_COMPARISON_METRICS.csv'):
  ss=[a for a in reported if a['model']==study['model'] and a['seed']==study['seed']];pm=[]
  for plate in 'CEGHX':
   s=[a for a in ss if a['plate']==plate];pm.append(math.fsum(float(a['L2']) for a in s)/len(s))
  v=math.fsum(pm)/5;assert abs(v-float(study['equal_plate_L2']))<1e-10;checks.append(dict(model=study['model'],fold='ALL',seed=study['seed'],source_id='ALL',check='equal_plate_L2',error=abs(v-float(study['equal_plate_L2'])),passed=True))
 for p in sorted((R/'05_training').glob('F*_s*/STARTED.json')):
  a=read(p);assert not set(a['train_sources'])&set(a['heldout_sources']);assert not {s[0] for s in a['train_sources']}&{s[0] for s in a['heldout_sources']};observed=rows(p.parent/'runtime_membership.csv');assert all(x['source_id'] in a['train_sources'] and x['plate']!=a['heldout_sources'][0][0] and int(x['heldout_overlap'])==0 for x in observed);assert len(observed)==80*len(a['train_sources']);assert a['fresh_random_initialization'];assert read(p.parent/'COMPLETED.json')['runtime_membership_SHA256']==sha(p.parent/'runtime_membership.csv');leak.append(dict(run=p.parent.name,source_overlap=0,plate_overlap=0,actual_batches_checked=len(observed),passed=True))
 assert len(leak)==10;assert len({read(p)['initial_state_digest'] for p in (R/'05_training').glob('F*_s*/STARTED.json')})==2,'same seed intentionally same fresh initialization, no weight transfer'
 table(R/'INDEPENDENT_METRIC_CHECKS.csv',checks);table(R/'INDEPENDENT_LEAKAGE_CHECKS.csv',leak);write(R/'07_metrics/INDEPENDENT_VERIFICATION.json',dict(UTC=now(),passed=True,metric_checks=len(checks),runtime_runs=len(leak),prediction_files=len(registry),max_abs_metric_error=max(a['error'] for a in checks),separate_scalar_implementation=True))
if __name__=='__main__':main()
