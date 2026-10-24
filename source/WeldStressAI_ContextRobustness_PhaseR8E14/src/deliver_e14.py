from common_e14 import *
import numpy as np,pandas as pd,math
from metric_e14 import metric,quantile
def mdtable(frame,columns=None):
 f=frame[columns] if columns else frame
 return '| '+' | '.join(map(str,f.columns))+' |\n|'+'|'.join(['---']*len(f.columns))+'|\n'+'\n'.join('| '+' | '.join(f'{v:.7g}' if isinstance(v,(float,np.floating)) else str(v) for v in r)+' |' for r in f.itertuples(index=False,name=None))+'\n'
def main():
 verify_protocol();assert read(R/'17_independent_audits/INDEPENDENT_PASS.json')['passed'];registry=rows(R/'20_reproducibility/PREDICTION_REGISTRY.csv');sources=sorted({a['source_id'] for a in registry});data={s:dict(np.load(H/'01_dataset/targets'/(s+'.npz'))) for s in sources};original=[];geo=[];feature=[];source_registry={a['source_id']:a for a in rows(R/'QUALIFIED13_SOURCE_REGISTRY.csv')};support={s:dict(np.load(R/'03_source_geometry'/(s+'_SUPPORT.npz'))) for s in sources}
 for sid in sources:
  d=data[sid];m=d['core']&d['valid'];g=dict(np.load(H/'02_geometry'/(sid+'.npz')));x=g['xyz'];datum=json.loads(source_registry[sid]['parent_datum']);h=x[:,2]-(datum['intercept_Z_mm']+datum['slope_X']*(x[:,0]-datum['origin_X_mm'])+datum['slope_Y']*(x[:,1]-datum['origin_Y_mm']));normal=g['normal'];slope=np.linalg.norm(normal[:,:2],axis=1)/np.maximum(abs(normal[:,2]),1e-12)
  geo.append(dict(source_id=sid,plate=sid[0],X_extent_mm=float(np.ptp(x[:,0])),Y_extent_mm=float(np.ptp(x[:,1])),height_Q05_mm=float(np.quantile(h,.05)),height_Q95_mm=float(np.quantile(h,.95)),height_span_mm=float(np.ptp(h)),normal_variation_mean=float(g['features'][:,14].mean()),curvature_proxy_Z_K16_std_mm=float(g['features'][:,13].std()),slope_Q95=float(np.quantile(slope,.95)),original_source_points=len(x),original_triangles=len(g['triangles']),original_area_mm2=float(g['area'].sum()),source_vertex_density_per_mm2=len(x)/float(g['area'].sum()),historical_M1_M2_L2=float(source_registry[sid]['T2_L2']),historical_M1_M2_high95_IoU=float(source_registry[sid]['T2_high95_IoU']),interpretation='DESCRIPTIVE_ASSOCIATION; not causally tested'))
  for seed in ['20261021','20261022']:
   fold='F'+str('CEGHX'.index(sid[0])+1);old=dict(np.load(H/'06_predictions'/('N1_POINT_TRANSFORMER_'+fold+'_s'+seed+'_'+sid+'.npz')));y=d['T2_MPa'][m];p=old['pred_MPa'][m];w=d['area'][m];r=metric(y,p,w,d['xyz'][m]);hp=p>=quantile(p,w);hy=y>=quantile(y,w);crit=np.flatnonzero(m)[np.argmax(abs(p-y))];original.append(dict(source_id=sid,plate=sid[0],seed=seed,**r,false_positive_area_mm2=float(w[hp&~hy].sum()),false_negative_area_mm2=float(w[hy&~hp].sum()),maximum_error_source_point_ID=int(d['source_ids'][crit]),X_mm=x[crit,0],Y_mm=x[crit,1],Z_mm=x[crit,2],original_prediction_SHA256=sha(H/'06_predictions'/('N1_POINT_TRANSFORMER_'+fold+'_s'+seed+'_'+sid+'.npz')),relative_error_denominator_MPa=100.))
  for a in [z for z in rows(R/'OBSERVATION_WINDOW_COORDINATES.csv') if z['source_id']==sid]:
   v=dict(np.load(a['geometry_path']));q=np.flatnonzero(support[sid]['core']&(support[sid]['tile_id']==int(a['tile'])));local=np.searchsorted(v['source_ids'],q);delta=v['features'][local].astype('f8')-g['features'][q]
   for channel in range(19):feature.append(dict(source_id=sid,condition=a['condition'],tile=a['tile'],channel=channel,mean_signed_change=float(np.average(delta[:,channel],weights=d['area'][q])),mean_absolute_change=float(np.average(abs(delta[:,channel]),weights=d['area'][q])),maximum_absolute_change=float(abs(delta[:,channel]).max()),finding='CONTROLLED_INPUT_INTERVENTION_EFFECT_ON_FEATURES'))
 table(R/'GEOMETRY_DOMAIN_SHIFT.csv',geo);table(R/'05_spatial_error_baseline/ORIGINAL_OOF_SPATIAL_DIAGNOSTICS.csv',original);table(R/'04_feature_contract/FEATURE_CHANGES_BY_CHANNEL.csv',feature)
 runs=[read(p) for p in sorted((R/'11_context_robust_training').glob('F*_s*/COMPLETED.json'))];table(R/'N2_TRAINING_RUN_REGISTRY.csv',[{k:a[k] for k in ['fold','seed','epochs','steps','training_s','parameters','checkpoint','checkpoint_SHA256','runtime_membership_SHA256','peak_RSS_bytes','status']} for a in runs]);table(R/'N2_CHECKPOINT_REGISTRY.csv',[dict(fold=a['fold'],seed=a['seed'],path=a['checkpoint'],SHA256=a['checkpoint_SHA256'],architecture_SHA256=sha(R/'src/model_e3.py'),base_architecture_SHA256=sha(R/'src/base_arch.py'),protocol_SHA256=sha(R/'N2_PREREGISTRATION_SEAL.json'),epoch=80) for a in runs]);history=pd.concat([pd.read_csv(Path(a['checkpoint']).parent/'history.csv') for a in runs]);history.to_csv(R/'N2_TRAINING_LOSS_HISTORY.csv',index=False);freq=[]
 for a in runs:
  for c,n in a['context_counts'].items():freq.append(dict(fold=a['fold'],seed=a['seed'],context=c,steps=n,fraction=n/a['steps'],expected_probability=1/3))
 table(R/'N2_CONTEXT_FREQUENCIES.csv',freq)
 # Stream exact source-core rows. Per-file provenance is bound by the prediction registry, not copied as long hashes into every row.
 for filename,which,condition_scope in [('FROZEN_N1_PREDICTIONS.csv','N1','ALL'),('N2_FULL_CONTEXT_PREDICTIONS.csv','N2','FULL'),('N2_RESTRICTED_CONTEXT_PREDICTIONS.csv','N2','RESTRICTED')]:
  def records():
   for a in registry:
    if a['model']!=which:continue
    if condition_scope=='FULL' and a['condition']!='FULL':continue
    if condition_scope=='RESTRICTED' and a['condition']=='FULL':continue
    p=dict(np.load(a['path']));sid=a['source_id']
    for i in range(len(p['pred_MPa'])):yield dict(source_id=sid,point_id=int(p['source_ids'][i]),model=which,seed=a['seed'],fold=a['fold'],condition=a['condition'],X_mm=float(p['xyz'][i,0]),Y_mm=float(p['xyz'][i,1]),Z_mm=float(p['xyz'][i,2]),T0_area_mm2=float(p['area'][i]),pred_T2_MPa=float(p['pred_MPa'][i]))
  table(R/filename,records());print('EXPORTED',filename,flush=True)
 provenance=[]
 for a in registry:
  sid=a['source_id'];side=Path(a['path']).with_suffix('.provenance.json');record=dict(**a,original_source_support_path=str(R/'03_source_geometry'/(sid+'_SUPPORT.npz')),original_source_support_SHA256=sha(R/'03_source_geometry'/(sid+'_SUPPORT.npz')),original_reference_path=source_registry[sid]['qualified_M2_target_path'],original_reference_SHA256=source_registry[sid]['qualified_M2_target_SHA256'],metric_version=read(R/'METRIC_SPECIFICATION.json')['version'],observation_protocol_SHA256=sha(R/'N2_PREREGISTRATION_SEAL.json'),stitching='Each original frozen core row exactly once; geometry-only X tiles; no label-driven placement',target_units='MPa',full_view_global_features_used_only_if_observable=a['condition'] in ['FULL','D0']);write(side,record);provenance.append(dict(**a,reference_SHA256=record['original_reference_SHA256'],source_support_SHA256=record['original_source_support_SHA256'],sidecar=str(side),sidecar_SHA256=sha(side)))
 table(R/'20_reproducibility/PREDICTION_PROVENANCE_REGISTRY.csv',provenance)
 from figures_e14 import figures
 figures()
 from reports_e14 import reports
 reports()
 from spatial_profiles_e14 import main as spatial_profiles
 spatial_profiles()
 write(R/'20_reproducibility/DELIVERY_GENERATED.json',dict(UTC=now(),passed=True,prediction_fields=182,core_rows=6224400,figures=36));print('DELIVERY_GENERATED',flush=True)
if __name__=='__main__':main()
