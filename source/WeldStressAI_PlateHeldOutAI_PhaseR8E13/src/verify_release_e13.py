"""Read-only release verifier. --preseal writes only new-phase audit receipts before manifest sealing."""
from common_e13 import *
import numpy as np,pandas as pd,math,argparse
def audit():
 verify_seal();assert read(R/'00_integrity/INPUT_AUDIT_COMPLETE.json')['passed'];counts=read(R/'R8E13_FINAL_COUNTS.json');assert counts['completed_fits']==counts['attempted_fits']==10 and counts['new_ANSYS_solves']==0 and counts['external_predictions']==0
 sources=rows(R/'QUALIFIED13_SOURCE_REGISTRY.csv');splits=rows(R/'OUTER_LOPO_FOLDS.csv');checks=[];t={a['source_id']:dict(np.load(R/'01_dataset/targets'/(a['source_id']+'.npz'))) for a in sources};g={a['source_id']:dict(np.load(R/'02_geometry'/(a['source_id']+'.npz'))) for a in sources}
 for a in sources:assert sha(a['qualified_M2_target_path'])==a['qualified_M2_target_SHA256']
 seal_time=datetime.datetime.fromisoformat(read(R/'PREREGISTRATION_SEAL.json')['UTC'])
 for p in sorted((R/'05_training').glob('F*_s*/STARTED.json')):
  rec=read(p);assert datetime.datetime.fromisoformat(rec['UTC'])>seal_time;assert rec['fresh_random_initialization'];tr=rec['train_sources'];held=rec['heldout_sources'];rr=rows(p.parent/'runtime_membership.csv');assert len(rr)==len(tr)*80
  for b in rr:
   sid=b['source_id'];epoch=int(b['epoch']);assert sid in tr and sid not in held and sid[0]!=held[0][0];w=len(tr)/(4*sum(s[0]==sid[0] for s in tr));assert abs(float(b['source_step_weight'])-w)<1e-14
   # Independently reproduce actual query memberships, not just the static split.
   d=t[sid];ix=np.flatnonzero(d['core']&d['valid']);area=d['area'][ix];salt=int(hashlib.sha256(sid.encode()).hexdigest()[:8],16);rng=np.random.default_rng(np.random.SeedSequence([rec['seed'],salt,epoch]));q=rng.choice(ix,512,replace=True,p=area/area.sum());assert hashlib.sha256(d['source_ids'][q].tobytes()).hexdigest()==b['source_ID_hash']
  for epoch in range(80):
   er=[a for a in rr if int(a['epoch'])==epoch];assert {a['source_id'] for a in er}==set(tr)
   for plate in {s[0] for s in tr}:assert abs(sum(float(a['source_step_weight']) for a in er if a['plate']==plate)/len(tr)-.25)<1e-14
  complete=read(p.parent/'COMPLETED.json');assert complete['steps']==80*len(tr) and complete['epochs']==80;assert sha(complete['checkpoint'])==complete['checkpoint_SHA256'];checks.append(dict(check='all_actual_query_memberships_and_plate_weights',run=p.parent.name,records=len(rr),passed=True))
  print('QUERY_AND_WEIGHT_VERIFIED',p.parent.name,len(rr),flush=True)
 for fold in ['F1','F2','F3','F4','F5']:
  fit=read(R/'04_baselines'/(fold+'_FIT.json'));tr=fit['train_sources'];sums=[];matrix=np.zeros((19,19));rhs=np.zeros(19);model=dict(np.load(R/'04_baselines'/(fold+'.npz')));mean=np.zeros(19);second=np.zeros(19)
  for sid in tr:
   d=t[sid];m=d['core']&d['valid'];area=d['area'][m];area=area/area.sum()/(4*sum(s[0]==sid[0] for s in tr));x=g[sid]['features'][m].astype('f8');y=d['T2_MPa'][m]/100;mean+=np.sum(area[:,None]*x,0);second+=np.sum(area[:,None]*x*x,0);sums.append(float(area@y))
  constant=math.fsum(sums);assert abs(constant-model['intercept'])<1e-12 and np.max(abs(mean-model['mean']))<1e-12;std=np.sqrt(np.maximum(second-mean*mean,0));std[std<1e-7]=1
  # Independently check nonconstant standard deviations; exact zero channels are fixed to one.
  zmask=model['std']!=1.;assert np.max(abs(std[zmask]-model['std'][zmask]))<1e-9
  for sid in tr:
   d=t[sid];m=d['core']&d['valid'];area=d['area'][m];area=area/area.sum()/(4*sum(s[0]==sid[0] for s in tr));z=(g[sid]['features'][m]-model['mean'])/model['std'];y=d['T2_MPa'][m]/100;matrix+=z.T@(area[:,None]*z);rhs+=z.T@(area*(y-constant))
  assert np.max(abs((matrix+np.eye(19))@model['beta']-rhs))<1e-9;checks.append(dict(check='training_only_scaler_constant_and_ridge_normal_equations',run=fold,records=len(tr),passed=True))
 predreg=rows(R/'PREDICTION_REGISTRY.csv');assert len(predreg)==52;predcache={};csv_rows=0
 for filename in ['CONSTANT_BASELINE_PREDICTIONS.csv','RIDGE_BASELINE_PREDICTIONS.csv','POINT_TRANSFORMER_OOF_PREDICTIONS.csv']:
  seen={}
  for chunk in pd.read_csv(R/filename,chunksize=100000,float_precision='round_trip',keep_default_na=False,dtype={'seed':str}):
   for key,frame in chunk.groupby(['model','seed','source_id'],sort=False):
    model,seed,sid=key;pr=next(a for a in predreg if a['model']==model and a['seed']==seed and a['source_id']==sid);d=t[sid]
    if key not in predcache:predcache={key:dict(np.load(pr['path']))}
    pp=predcache[key];ids=frame.point_id.to_numpy(dtype='i8');m=d['core']&d['valid'];assert np.all(m[ids]);assert np.array_equal(ids,d['source_ids'][ids]);assert np.array_equal(frame[['X_mm','Y_mm','Z_mm']].to_numpy(),d['xyz'][ids]);assert np.array_equal(frame.T0_area_mm2.to_numpy(),d['area'][ids]);assert np.array_equal(frame.pred_T2_MPa.to_numpy(),pp['pred_MPa'][ids]);assert np.array_equal(frame.reference_T2_MPa.to_numpy(),d['T2_MPa'][ids]);expected=next(a['qualified_M2_target_SHA256'] for a in sources if a['source_id']==sid);assert set(frame.reference_SHA256)=={expected} and set(frame.checkpoint_SHA256)=={pr['checkpoint_SHA256']};seen.setdefault(key,[]).extend(ids.tolist());csv_rows+=len(ids)
  for key,ids in seen.items():assert np.array_equal(np.array(ids),np.flatnonzero(t[key[2]]['core']&t[key[2]]['valid'])),key
  checks.append(dict(check='exact_CSV_source_XYZ_area_predictions_roundtrip',run=filename,records=sum(len(v) for v in seen.values()),passed=True));print('CSV_ROUNDTRIP_EXACT',filename,flush=True)
 assert csv_rows==1778400
 aggregate=read(R/'07_metrics/SEED_AGGREGATE.json')['metrics'];study=pd.read_csv(R/'MODEL_COMPARISON_METRICS.csv',keep_default_na=False);neural=study[study.model=='N1_POINT_TRANSFORMER']
 for name,value in aggregate.items():assert math.isclose(float(value),math.fsum(map(float,neural[name]))/2,rel_tol=1e-12,abs_tol=1e-12),(name,value)
 source_scores=rows(R/'SOURCE_LEVEL_METRICS.csv');plate_scores=rows(R/'PLATE_LEVEL_METRICS.csv')
 for a in plate_scores:
  ss=[b for b in source_scores if b['model']==a['model'] and b['seed']==a['seed'] and b['plate']==a['plate']]
  for name in ['L2','MAE_MPa','RMSE_MPa','bias_MPa','high95_IoU','high95_precision','high95_recall','worst_regional_L2']:assert math.isclose(float(a[name]),math.fsum(float(b[name]) for b in ss)/len(ss),rel_tol=1e-12,abs_tol=1e-12)
 for a in study.to_dict('records'):
  pp=[b for b in plate_scores if b['model']==a['model'] and b['seed']==str(a['seed'])]
  for name in ['L2','MAE_MPa','RMSE_MPa','bias_MPa','high95_IoU','high95_precision','high95_recall','worst_regional_L2']:assert math.isclose(float(a['equal_plate_'+name]),math.fsum(float(b[name]) for b in pp)/5,rel_tol=1e-12,abs_tol=1e-12)
 provenance=rows(R/'21_reproducibility/PREDICTION_PROVENANCE_REGISTRY.csv');assert len(provenance)==52
 for a in provenance:
  side=read(a['provenance_path']);assert sha(a['provenance_path'])==a['provenance_SHA256'];assert sha(a['path'])==side['prediction_SHA256']==a['SHA256'];assert sha(a['support_path'])==a['support_SHA256']==side['original_support_SHA256'];d=t[a['source_id']];support=dict(np.load(a['support_path']));assert np.array_equal(support['original_core'],d['core']) and np.array_equal(support['reference_valid'],d['valid']);assert np.array_equal(support['source_ids'],d['source_ids']) and np.array_equal(support['area'],d['area']);assert side['checkpoint_SHA256']==a['checkpoint_SHA256'] and side['actual_reference_V1_SHA256']==a['reference_SHA256']
 from PIL import Image
 figs=sorted((R/'14_figures').glob('*.png'));assert len(figs)==36
 for p in figs:
  with Image.open(p) as im:im.verify()
  assert p.with_suffix('.pdf').read_bytes().startswith(b'%PDF')
 spec=(R/'00_integrity/USER_SPECIFICATION.txt').read_text(encoding='utf-8-sig');reports=spec.split('# 32. REQUIRED REPORTS')[1].split('# 33.')[0];import re
 for name in re.findall(r'`([^`]+)`',reports):
  if name=='REPRODUCIBILITY_MANIFEST.json' and '--preseal' in sys.argv:continue
  assert (R/name).is_file(),name
 required=spec.split('# 33. REQUIRED MACHINE-READABLE OUTPUTS')[1].split('# 34.')[0]
 for name in re.findall(r'`([^`]+)`',required):assert (R/name).is_file(),name
 report=(R/'R8E13_MASTER_REPORT.md').read_text(encoding='utf8');assert len(re.findall(r'^### \d+\.',report,flags=re.M))==53
 independent=read(R/'07_metrics/INDEPENDENT_VERIFICATION.json');assert independent['passed'];result=dict(UTC=now(),integrity_status='PASS',scheduled_fits=10,qualified_sources=13,documentary_plates=5,actual_query_records=sum(a['records'] for a in checks if a['check']=='all_actual_query_memberships_and_plate_weights'),exact_CSV_rows=csv_rows,figures=36,question_answers=53,new_ANSYS_solves=0,metric_checks=independent['metric_checks'],checks=checks,seal_verified=True)
 if '--preseal' in sys.argv:write(R/'21_reproducibility/DELIVERY_VERIFICATION.json',result)
 if (R/'REPRODUCIBILITY_MANIFEST.json').exists():
  manifest=read(R/'REPRODUCIBILITY_MANIFEST.json');release=read(R/'21_reproducibility/RELEASE_SEAL.json');assert sha(R/'REPRODUCIBILITY_MANIFEST.json')==release['manifest_SHA256'];listed=set()
  for a in manifest['files']:
   p=R/a['path'];assert p.stat().st_size==a['bytes'] and sha(p)==a['sha256'],str(p);listed.add(a['path'])
  for p in R.rglob('*'):
   if p.is_file():
    name=p.relative_to(R).as_posix();assert name in listed or name in manifest['excluded'] or name.startswith('tmp/'),name
  result['durable_files_verified']=len(listed)
 print(json.dumps(result,indent=2),flush=True);return result
if __name__=='__main__':audit()
