from common_e16 import *
import numpy as np,pandas as pd,math
from metric_e14 import metric,quantile
from functools import lru_cache
@lru_cache(maxsize=13)
def target(sid):
 d=dict(np.load(H/'01_dataset/targets'/(sid+'.npz')));q=np.flatnonzero(d['core']&d['valid']);return {k:d[k][q] for k in ['source_ids','xyz','area','T2_MPa','region']},q
KEYS=['model','fold','seed','source_id','plate','condition']
METRICS=['L2','MAE_MPa','RMSE_MPa','bias_MPa','high95_IoU','high95_precision','high95_recall','high95_centroid_distance_mm','worst_regional_L2','max_error_MPa','Q95_error_MPa','absolute_max_error_MPa','absolute_Q95_error_MPa','pred_variance_MPa2','ref_variance_MPa2','false_negative_area_mm2','false_positive_area_mm2']
def field(rec):
 p=dict(np.load(rec['path']));d,q=target(rec['source_id'])
 if len(p['source_ids'])!=len(q):
  original=np.load(H/'01_dataset/targets'/(rec['source_id']+'.npz'));assert all(np.array_equal(p[k],original[k]) for k in ['source_ids','xyz','area']);p={k:(v[q] if isinstance(v,np.ndarray) and v.ndim and len(v)==len(original['source_ids']) else v) for k,v in p.items()}
 return p
def score(rec):
 d,q=target(rec['source_id']);assert sha(rec['path'])==rec['SHA256'];p=field(rec);assert all(np.array_equal(d[k],p[k]) for k in ['source_ids','xyz','area']);assert 'query_original_rows' not in p or np.array_equal(q,p['query_original_rows']);v=p['pred_MPa'];y=d['T2_MPa'];w=d['area'];x=d['xyz'];assert np.isfinite(v).all() and len(v)==34200;m=metric(y,v,w,x);hy=y>=quantile(y,w);hp=v>=quantile(v,w);regions=[]
 for region in np.unique(d['region']):
  z=d['region']==region;regions.append(dict(region=int(region),L2=float(np.sqrt(w[z]@((v[z]-y[z])**2)/(w[z]@(y[z]**2))))))
 m.update(worst_regional_L2=max(a['L2'] for a in regions),false_negative_area_mm2=float(w[hy&~hp].sum()),false_positive_area_mm2=float(w[hp&~hy].sum()),max_error_MPa=float(v.max()-y.max()),absolute_max_error_MPa=abs(float(v.max()-y.max())),absolute_Q95_error_MPa=abs(m['Q95_error_MPa']),pred_variance_MPa2=float(w@((v-w@v/w.sum())**2)/w.sum()),ref_variance_MPa2=float(w@((y-w@y/w.sum())**2)/w.sum()),coverage=1.,core_points=len(v))
 return dict(**{k:rec[k] for k in KEYS},**m),regions
def aggregate(scores,extra=[]):
 f=pd.DataFrame(scores);by=['model','seed','condition']+extra;plates=f.groupby(by+['plate'],as_index=False)[METRICS].mean();seeds=plates.groupby(by,as_index=False)[METRICS].mean();means=seeds.groupby(['model','condition']+extra,as_index=False)[METRICS].mean();means['seed']='METRIC_MEAN';return plates,seeds,means
def main():
 verify_protocol();assert read(R/'22_reproducibility/EXPERIMENT_MATRIX_COMPLETE.json')['passed'];registry=rows(R/'00_integrity/HISTORICAL_PREDICTION_REGISTRY.csv')
 for a in registry:a.update(policy='S0',inference_s=float(a['elapsed_s']),inference_time_scope='cumulative from worker start, not isolated field time')
 for a in rows(R/'00_integrity/HISTORICAL_BASELINE_REGISTRY.csv'):a.update(condition='FULL',policy='S0',coverage=1.,core_points=34200,inference_s=None,stored_support='68457 full source rows',evaluation_projection='unchanged frozen core&valid original rows; no new inference');registry.append(a)
 for p in sorted((R/'13_full_core_predictions').glob('*_REGISTRY.csv')):
  rr=rows(p)
  for a in rr:a['inference_time_scope']='cumulative from worker start, not isolated field time'
  registry+=rr
 for p in sorted((R/'12_XGBoost_baseline').glob('F*/PREDICTION_REGISTRY.csv')):registry+=rows(p)
 assert len(registry)==299;sources=[a['source_id'] for a in rows(R/'QUALIFIED13_SOURCE_REGISTRY.csv')];expected={(model,str(seed),sid,c) for model in ['N1','N2','N3'] for seed in [20261021,20261022] for sid in sources for c in ['FULL','X50','X43']}|{('B2_GEOMETRY_XGBOOST','NA',sid,c) for sid in sources for c in ['FULL','X50','X43']}|{(model,'NA',sid,'FULL') for model in ['B0_CONSTANT','B1_GEOMETRY_RIDGE'] for sid in sources};assert len({(a['model'],str(a['seed']),a['source_id'],a['condition']) for a in registry})==len(registry);assert {(a['model'],str(a['seed']),a['source_id'],a['condition']) for a in registry}==expected;fields=sorted(set().union(*(a.keys() for a in registry)));table(R/'MODEL_PREDICTION_REGISTRY.csv',registry,fields);scores=[];regions=[];changes=[]
 for a in registry:
  row,rr=score(a);scores.append(row);regions +=[dict(**{k:a[k] for k in KEYS},**z) for z in rr]
 for a in registry:
  full=next(b for b in registry if b['model']==a['model'] and b['seed']==a['seed'] and b['source_id']==a['source_id'] and b['condition']=='FULL');v=field(a)['pred_MPa'];f=field(full)['pred_MPa'];d,_=target(a['source_id']);w=d['area'];changes.append(dict(**{k:a[k] for k in KEYS},prediction_change_L2=float(np.sqrt(w@((v-f)**2)/(w@(f*f)))),RMS_prediction_change_MPa=float(np.sqrt(w@((v-f)**2)/w.sum())),max_prediction_change_MPa=float(abs(v-f).max())))
 table(R/'SOURCE_LEVEL_METRICS.csv',scores);table(R/'14_source_metrics/REGIONAL_METRICS.csv',regions);table(R/'CONTEXT_ROBUSTNESS_METRICS.csv',changes)
 for name,keys in [('HIGH95_LOCALIZATION_METRICS.csv',['high95_IoU','high95_precision','high95_recall','high95_centroid_distance_mm','false_negative_area_mm2','false_positive_area_mm2']),('PEAK_AND_Q95_ERRORS.csv',['pred_max_MPa','ref_max_MPa','max_error_MPa','Q95_error_MPa','pred_variance_MPa2','ref_variance_MPa2'])]:table(R/name,[{k:a[k] for k in KEYS+keys} for a in scores])
 plates,seeds,means=aggregate(scores);plates.to_csv(R/'PLATE_LEVEL_METRICS.csv',index=False);seeds.to_csv(R/'17_model_comparisons/SEED_METRICS.csv',index=False);means.to_csv(R/'17_model_comparisons/TWO_SEED_METRIC_MEANS.csv',index=False)
 paired=[]
 for a in scores:
  if a['model']!='N3':continue
  for other in ['N1','N2','B2_GEOMETRY_XGBOOST']:
   b=next(b for b in scores if b['model']==other and b['source_id']==a['source_id'] and b['condition']==a['condition'] and (b['seed']==a['seed'] or b['seed']=='NA'));paired.append(dict(**{k:a[k] for k in KEYS},comparator=other,**{'N3_minus_'+k:a[k]-b[k] for k in METRICS}))
 table(R/'MODEL_PAIRED_COMPARISONS.csv',paired)
 factorial=[];fr=[]
 for p in sorted((R/'05_blockwise_interventions').glob('*_REGISTRY.csv')):fr+=rows(p)
 assert len(fr)==832;table(R/'05_blockwise_interventions/ALL_FIELD_REGISTRY.csv',fr)
 for a in fr:
  row,_=score(a);row['cell']=a['cell'];factorial.append(row)
 table(R/'BLOCK_FACTORIAL_RESULTS.csv',factorial);fp,fs,fm=aggregate(factorial,['cell']);fp.to_csv(R/'04_feature_mechanisms/FACTORIAL_PLATE_METRICS.csv',index=False);fs.to_csv(R/'04_feature_mechanisms/FACTORIAL_SEED_METRICS.csv',index=False);fm.to_csv(R/'04_feature_mechanisms/FACTORIAL_METRIC_MEANS.csv',index=False)
 effects=[]
 for model,seed,sid,c in sorted({(a['model'],a['seed'],a['source_id'],a['condition']) for a in factorial}):
  z=[a for a in factorial if (a['model'],a['seed'],a['source_id'],a['condition'])==(model,seed,sid,c)];assert len(z)==8
  for subset in ['A','B','C','AB','AC','BC','ABC']:
   signs=lambda a:math.prod(2*int(a['cell'][1+'ABC'.index(k)])-1 for k in subset)
   effects.append(dict(model=model,seed=seed,source_id=sid,plate=sid[0],condition=c,effect=subset,normalization='orthogonal sum(sign*y)/4',**{k:sum(signs(a)*a[k] for a in z)/4 for k in METRICS}))
 table(R/'BLOCK_MAIN_EFFECTS.csv',[a for a in effects if len(a['effect'])==1]);table(R/'BLOCK_INTERACTIONS.csv',[a for a in effects if len(a['effect'])>1]);ep,es,em=aggregate(effects,['effect']);em.to_csv(R/'04_feature_mechanisms/EQUAL_PLATE_EFFECTS.csv',index=False)
 costs=[];train=[];history=[];checkpoints=[];xtrain=[];xsamples=[];xregistry=[]
 for p in sorted((R/'11_N3_training').glob('F*_s*/COMPLETED.json')):
  r=read(p);train.append(r);history+=rows(p.parent/'history.csv');checkpoints.append(dict(run=p.parent.name,fold=r['fold'],seed=r['seed'],path=r['checkpoint'],SHA256=r['checkpoint_SHA256'],epoch=80,selection='fixed final epoch',parameters=7228));inf=read(R/'13_full_core_predictions'/(p.parent.name+'_COMPLETED.json'));costs.append(dict(model='N3',run=p.parent.name,training_s=r['training_s'],inference_s=inf['elapsed_s'],inference_fields=inf['fields'],peak_RSS_bytes=r['peak_RSS_bytes'],timing_scope='worker cumulative all heldout fields; includes save/I/O'))
 for p in sorted((R/'12_XGBoost_baseline').glob('F*/COMPLETED.json')):
  r=read(p);xtrain.append(r);xsamples+=rows(p.parent/'SAMPLE_IDS.csv');reg=rows(p.parent/'PREDICTION_REGISTRY.csv');xregistry+=reg;costs.append(dict(model='B2_GEOMETRY_XGBOOST',run=p.parent.name,training_s=r['training_s'],inference_s=sum(float(a['inference_s']) for a in reg),inference_fields=len(reg),peak_RSS_bytes=None,timing_scope='training includes sample construction; inference per-field includes save/I/O'))
 for model in ['N1','N2']:
  for rec in rows(R/'HISTORICAL_MODEL_HASHES.csv'):
   if rec['model']!=model:continue
   old=read(Path(rec['checkpoint']).parent/'COMPLETED.json');rs=[a for a in registry if a['model']==model and a['fold']==rec['fold'] and a['seed']==rec['seed']];costs.append(dict(model=model,run=rec['fold']+'_s'+rec['seed'],training_s=old.get('training_s',old.get('elapsed_s')),inference_s=max(float(a['inference_s']) for a in rs),inference_fields=len(rs),peak_RSS_bytes=old.get('peak_RSS_bytes'),timing_scope='maximum cumulative historical worker elapsed, different run date; not controlled hardware benchmark'))
 table(R/'N3_TRAINING_REGISTRY.csv',train,sorted(set().union(*(a.keys() for a in train))));table(R/'N3_TRAINING_HISTORIES.csv',history);table(R/'N3_CHECKPOINT_REGISTRY.csv',checkpoints);table(R/'XGBOOST_TRAINING_REGISTRY.csv',xtrain,sorted(set().union(*(a.keys() for a in xtrain))));table(R/'XGBOOST_SAMPLE_IDS.csv',xsamples);table(R/'XGBOOST_PREDICTION_REGISTRY.csv',xregistry);table(R/'COMPUTATIONAL_COST_COMPARISON.csv',costs)
 write(R/'18_independent_verification/SCORING_COMPLETE.json',dict(UTC=now(),passed=True,model_fields=len(scores),factorial_fields=len(factorial),source_point_predictions=(len(scores)+len(factorial))*34200))
 print(means[['model','condition','L2','MAE_MPa','high95_IoU']].to_string(index=False),flush=True)
if __name__=='__main__':main()
