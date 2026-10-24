from common_e14 import *
import numpy as np,math,pandas as pd
from metric_e14 import metric,quantile
def main():
 verify_protocol();registry=[]
 for folder in ['08_frozen_checkpoint_inference','12_new_model_predictions']:
  for p in sorted((R/folder).glob('*_REGISTRY.csv')):registry+=rows(p)
 assert len(registry)==182;table(R/'20_reproducibility/PREDICTION_REGISTRY.csv',registry);scores=[];regions=[];changes=[];fpfn=[];peak=[];diagnostic=[];domain=[];original=[];bins=[]
 data={sid:dict(np.load(H/'01_dataset/targets'/(sid+'.npz'))) for sid in {a['source_id'] for a in registry}};fullpred={};geometry={sid:dict(np.load(H/'02_geometry'/(sid+'.npz'))) for sid in data};windows=rows(R/'OBSERVATION_CONTEXT_DENSITY.csv');sources={a['source_id']:a for a in rows(R/'QUALIFIED13_SOURCE_REGISTRY.csv')}
 for a in registry:
  if a['condition']=='FULL':fullpred[a['model'],a['seed'],a['source_id']]=dict(np.load(a['path']))['pred_MPa']
 for rec in registry:
  sid=rec['source_id'];d=data[sid];ix=np.flatnonzero(d['core']&d['valid']);p=dict(np.load(rec['path']));assert sha(rec['path'])==rec['SHA256'];assert all(np.array_equal(p[k],d[k][ix]) for k in ['source_ids','xyz','area']);assert p['valid'].all() and (p['tile_count']==1).all();y=d['T2_MPa'][ix];v=p['pred_MPa'];w=d['area'][ix];x=d['xyz'][ix];base={k:rec[k] for k in ['model','fold','seed','condition','source_id','plate']};m=metric(y,v,w,x);region_results=[]
  for code in np.unique(d['region'][ix]):
   z=d['region'][ix]==code;rm=metric(y[z],v[z],w[z],x[z]);regions.append(dict(**base,region=int(code),**rm));region_results.append(rm['L2'])
  wa=[a for a in windows if a['source_id']==sid and a['condition']==rec['condition']];trunc=max(float(a['truncation_ratio']) for a in wa);hy=y>=quantile(y,w);hp=v>=quantile(v,w);fp=float(w[hp&~hy].sum());fn=float(w[hy&~hp].sum());row=dict(**base,**m,worst_regional_L2=max(region_results),coverage=1.,core_points=len(ix),max_error_MPa=float(v.max()-y.max()),pred_Kmax=float(v.max()/100),reference_Kmax=float(y.max()/100),pred_std_MPa=float(np.sqrt(np.average((v-np.average(v,weights=w))**2,weights=w))),reference_std_MPa=float(np.sqrt(np.average((y-np.average(y,weights=w))**2,weights=w))),max_observation_truncation=trunc,feature_visibility_pass=True,false_positive_area_mm2=fp,false_negative_area_mm2=fn);scores.append(row);fpfn.append(dict(**base,false_positive_area_mm2=fp,false_negative_area_mm2=fn,**{k:m[k] for k in ['high95_IoU','high95_precision','high95_recall','high95_centroid_distance_mm']}));peak.append(dict(**base,**{k:row[k] for k in ['pred_max_MPa','ref_max_MPa','max_error_MPa','pred_Kmax','reference_Kmax','Q95_error_MPa','pred_std_MPa','reference_std_MPa']}));e=v-y;crit=int(np.argmax(abs(e)));diagnostic.append(dict(**base,max_absolute_error_MPa=float(abs(e[crit])),max_error_source_point_ID=int(p['source_ids'][crit]),X_mm=x[crit,0],Y_mm=x[crit,1],Z_mm=x[crit,2],signed_error_at_max_MPa=float(e[crit]),relative_error_denominator_MPa=100,mean_absolute_relative_error=float(np.average(abs(e)/100,weights=w)),false_positive_area_mm2=fp,false_negative_area_mm2=fn))
  full=fullpred[rec['model'],rec['seed'],sid];dv=v-full;df=np.sum(w*full**2);changes.append(dict(**base,mean_signed_prediction_shift_MPa=float(np.average(dv,weights=w)),RMS_prediction_shift_MPa=float(np.sqrt(np.average(dv**2,weights=w))),prediction_change_L2=float(np.sqrt(np.sum(w*dv**2)/df)),maximum_absolute_prediction_change_MPa=float(np.max(abs(dv))),predicted_maximum_amplitude_change_MPa=float(v.max()-full.max()),coverage=1.))
  g=geometry[sid];datum=json.loads(sources[sid]['parent_datum']);height=x[:,2]-(datum['intercept_Z_mm']+datum['slope_X']*(x[:,0]-datum['origin_X_mm'])+datum['slope_Y']*(x[:,1]-datum['origin_Y_mm']));normal=g['normal'][ix];slope=np.linalg.norm(normal[:,:2],axis=1)/np.maximum(abs(normal[:,2]),1e-12);support=dict(np.load(R/'03_source_geometry'/(sid+'_SUPPORT.npz')));t=support['tile_id'][ix];boundary=np.empty(len(ix));density=np.empty(len(ix));extent=np.empty(len(ix));featurechange=np.empty(len(ix))
  for tile in np.unique(t):
   a=next(a for a in wa if int(a['tile'])==tile);z=t==tile;boundary[z]=np.minimum(x[z,0]-float(a['actual_X_min']),float(a['actual_X_max'])-x[z,0]);density[z]=float(a['context_density_per_mm2']);extent[z]=float(a['actual_X_mm']);featurechange[z]=float(a['feature_query_RMS_change'])
  descriptors=dict(parent_relative_vertical_height_mm=height,curvature_proxy_K16_Z_residual_mm=g['features'][ix,13],normal_variation_proxy=g['features'][ix,14],slope_magnitude=slope,original_vertex_density_per_mm2=1/w,query_observation_X_boundary_distance_mm=boundary,actual_observation_X_mm=extent,context_density_per_mm2=density,geometry_feature_RMS_change=featurechange,target_T2_MPa_evaluation_only=y)
  for name,values in descriptors.items():
   edges=np.linspace(float(values.min()),float(values.max())+1e-10,13)
   for j in range(12):
    z=(values>=edges[j])&(values<edges[j+1])
    if z.any():bins.append(dict(**base,descriptor=name,bin=j,mean_descriptor=float(np.average(values[z],weights=w[z])),MAE_MPa=float(np.average(abs(e[z]),weights=w[z])),bias_MPa=float(np.average(e[z],weights=w[z])),area_mm2=float(w[z].sum()),finding='DESCRIPTIVE_ASSOCIATION'))
  print('SCORED',rec['model'],rec['seed'],rec['condition'],sid,flush=True)
 table(R/'SOURCE_CONTEXT_METRICS.csv',scores);table(R/'REGIONAL_CONTEXT_ERRORS.csv',regions);table(R/'CONTEXT_PREDICTION_CHANGES.csv',changes);table(R/'HIGH95_PRECISION_RECALL.csv',fpfn);table(R/'HIGH95_FALSE_POSITIVE_NEGATIVE_AREAS.csv',fpfn);table(R/'STRESS_PEAK_AMPLITUDE_ERRORS.csv',peak);table(R/'SPATIAL_ERROR_DIAGNOSTICS.csv',diagnostic);table(R/'05_spatial_error_baseline/ERROR_DESCRIPTOR_BINS.csv',bins)
 metrics=['L2','MAE_MPa','RMSE_MPa','bias_MPa','high95_IoU','high95_precision','high95_recall','high95_centroid_distance_mm','worst_regional_L2','max_error_MPa','Q95_error_MPa','pred_std_MPa','reference_std_MPa','false_positive_area_mm2','false_negative_area_mm2'];pl=[];study=[]
 for model,seed,condition in sorted({(a['model'],a['seed'],a['condition']) for a in scores}):
  ss=[a for a in scores if (a['model'],a['seed'],a['condition'])==(model,seed,condition)];pp=[]
  for plate in 'CEGHX':
   z=[a for a in ss if a['plate']==plate];r=dict(model=model,seed=seed,condition=condition,plate=plate,sources=len(z),**{key:float(np.mean([a[key] for a in z])) for key in metrics});pl.append(r);pp.append(r)
  study.append(dict(model=model,seed=seed,condition=condition,**{'equal_plate_'+key:float(np.mean([a[key] for a in pp])) for key in metrics},equal_source_L2=float(np.mean([a['L2'] for a in ss])),point_area_L2=float(np.sqrt(sum(a['SSE'] for a in ss)/sum(a['ref_square_sum'] for a in ss))),point_area_MAE_MPa=sum(a['MAE_MPa']*a['area_mm2'] for a in ss)/sum(a['area_mm2'] for a in ss),worst_plate_L2=max(a['L2'] for a in pp),worst_source_L2=max(a['L2'] for a in ss),median_plate_L2=float(np.median([a['L2'] for a in pp])),minimum_plate_L2=min(a['L2'] for a in pp)))
 table(R/'PLATE_CONTEXT_METRICS.csv',pl);table(R/'SEED_CONTEXT_METRICS.csv',study)
 sensitivity=[];paired=[]
 for a in scores:
  f=next(z for z in scores if all(z[k]==a[k] for k in ['model','seed','source_id']) and z['condition']=='FULL');sensitivity.append(dict(**{k:a[k] for k in ['model','seed','condition','source_id','plate']},DELTA_L2=a['L2']-f['L2'],DELTA_IOU=a['high95_IoU']-f['high95_IoU'],DELTA_MAE_MPa=a['MAE_MPa']-f['MAE_MPa'],**{k:v for k,v in next(z for z in changes if all(z[k]==a[k] for k in ['model','seed','condition','source_id'])).items() if k not in ['model','seed','condition','source_id','plate','fold']}))
  if a['model']=='N2':
   n1=next(z for z in scores if z['model']=='N1' and all(z[k]==a[k] for k in ['seed','source_id','condition']));paired.append(dict(seed=a['seed'],source_id=a['source_id'],plate=a['plate'],condition=a['condition'],**{'N2_minus_N1_'+key:a[key]-n1[key] for key in metrics}))
 table(R/'N1_CONTEXT_SENSITIVITY.csv',[a for a in sensitivity if a['model']=='N1']);table(R/'09_context_sensitivity/ALL_MODEL_SENSITIVITY.csv',sensitivity);table(R/'N1_HIGH95_METRICS.csv',[a for a in fpfn if a['model']=='N1']);table(R/'N1_N2_PAIRED_COMPARISONS.csv',paired)
 write(R/'20_reproducibility/SCORING_COMPLETE.json',dict(UTC=now(),source_fields=182,passed=True,core_prediction_records=sum(a['core_points'] for a in scores),study_rows=14))
if __name__=='__main__':main()
