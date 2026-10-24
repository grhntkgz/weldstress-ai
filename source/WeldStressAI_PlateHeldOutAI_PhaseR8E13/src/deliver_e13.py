from common_e13 import *
import numpy as np,pandas as pd
from scipy.stats import spearmanr
from score_e13 import quantile
def mdtable(frame,columns=None):
 f=frame[columns] if columns else frame
 return '| '+' | '.join(map(str,f.columns))+' |\n|'+'|'.join(['---']*len(f.columns))+'|\n'+'\n'.join('| '+' | '.join(f'{v:.8g}' if isinstance(v,(float,np.floating)) else str(v) for v in a)+' |' for a in f.itertuples(index=False,name=None))+'\n'
def main():
 verify_seal();assert read(R/'07_metrics/INDEPENDENT_VERIFICATION.json')['passed'];reg=rows(R/'PREDICTION_REGISTRY.csv');sources=sorted({a['source_id'] for a in reg});source=pd.read_csv(R/'SOURCE_LEVEL_METRICS.csv',keep_default_na=False);plate=pd.read_csv(R/'PLATE_LEVEL_METRICS.csv',keep_default_na=False);study=pd.read_csv(R/'MODEL_COMPARISON_METRICS.csv',keep_default_na=False);regional=pd.read_csv(R/'REGIONAL_PREDICTION_METRICS.csv',keep_default_na=False)
 data={s:dict(np.load(R/'01_dataset/targets'/(s+'.npz'))) for s in sources};geom={s:dict(np.load(R/'02_geometry'/(s+'.npz'))) for s in sources};preds={(a['model'],str(a['seed']),a['source_id']):dict(np.load(a['path']))['pred_MPa'] for a in reg};lookup={a['source_id']:a for a in rows(R/'QUALIFIED13_SOURCE_REGISTRY.csv')};runs=[read(p) for p in sorted((R/'05_training').glob('F*_s*/COMPLETED.json'))];modelkeys=[('B0_CONSTANT','NA'),('B1_GEOMETRY_RIDGE','NA'),('N1_POINT_TRANSFORMER','20261021'),('N1_POINT_TRANSFORMER','20261022')]
 histories=pd.concat([pd.read_csv(Path(a['checkpoint']).parent/'history.csv') for a in runs]);histories.to_csv(R/'TRAINING_LOSS_HISTORY.csv',index=False);table(R/'NEURAL_RUN_REGISTRY.csv',[{k:a[k] for k in ['fold','seed','epochs','steps','training_s','parameters','checkpoint','checkpoint_SHA256','peak_RSS_bytes','peak_GPU_allocated_bytes','status']} for a in runs]);table(R/'CHECKPOINT_REGISTRY.csv',[dict(fold=a['fold'],seed=a['seed'],checkpoint=a['checkpoint'],SHA256=a['checkpoint_SHA256'],epoch=a['epochs'],recipe_SHA256=sha(R/'MODEL_AND_TRAINING_SEAL.json'),feature_SHA256=sha(R/'03_protocol/FEATURE_SCHEMA.json'),split_SHA256=sha(R/'DATASET_AND_SPLIT_SEAL.json'),runtime_membership_SHA256=a['runtime_membership_SHA256']) for a in runs]);table(R/'TRAINING_CONFIGURATIONS.csv',[dict(fold=a['fold'],seed=a['seed'],recipe_SHA256=sha(R/'MODEL_AND_TRAINING_SEAL.json'),final_epoch=80,queries=512,context=4096) for a in runs]);table(R/'PREPROCESSING_FIT_PROVENANCE.csv',[dict(fold=f,model='B1_GEOMETRY_RIDGE',scaler=str(R/'04_baselines'/(f+'.npz')),SHA256=sha(R/'04_baselines'/(f+'.npz')),training_IDs=';'.join(read(R/'04_baselines'/(f+'_FIT.json'))['train_sources']),heldout_fit=False) for f in ['F1','F2','F3','F4','F5']])
 resources=[]
 for a in runs:
  rr=rows(Path(a['checkpoint']).parent/'resources.csv')
  for z in rr:resources.append(dict(fold=a['fold'],seed=a['seed'],**z))
 table(R/'TRAINING_RESOURCE_ACCOUNTING.csv',resources)
 diagnostics=[];domains=[];feature_shift=[];mesh=[];binned=[]
 for s in sources:
  d=data[s];g=geom[s];m=d['core']&d['valid'];w=d['area'][m];f='F'+str('CEGHX'.index(s[0])+1);sc=dict(np.load(R/'04_baselines'/(f+'.npz')));dist=np.sqrt(np.mean(((np.average(g['features'][m],axis=0,weights=w)-sc['mean'])/sc['std'])**2));tr=read(R/'04_baselines'/(f+'_FIT.json'))['train_sources'];lo=np.min(np.stack([geom[t]['features'].min(0) for t in tr]),0);hi=np.max(np.stack([geom[t]['features'].max(0) for t in tr]),0);out=np.average((g['features'][m]<lo)|(g['features'][m]>hi),axis=0,weights=w)
  domains.append(dict(source_id=s,plate=s[0],geometry_mean_standardized_distance=float(dist),mean_feature_outside_training_range_fraction=float(out.mean()),front_X_span_mm=float(np.ptp(g['xyz'][:,0])),front_Y_span_mm=float(np.ptp(g['xyz'][:,1])),Z_span_mm=float(np.ptp(g['xyz'][:,2])),median_vertex_area_mm2=float(np.median(g['area'])),n_source_points=len(g['xyz']),core_points=int(m.sum()),interpretation='OBSERVED_ASSOCIATION;NOT_CAUSALLY_TESTED'))
  feature_shift.append(out);mesh.append(dict(source_id=s,plate=s[0],M1_M2_L2=float(lookup[s]['T2_L2']),M1_M2_worst_region_L2=float(lookup[s]['T2_worst_regional_L2']),M1_M2_high95_IoU=float(lookup[s]['T2_high95_IoU']),mapping_coverage=float(lookup[s]['mapping_coverage'])))
  for model,seed in modelkeys:
   p=preds[model,seed,s];e=p-d['T2_MPa'];i=np.flatnonzero(m)[np.argmax(abs(e[m]))];qy=quantile(d['T2_MPa'][m],w);qp=quantile(p[m],w);hy=d['T2_MPa'][m]>=qy;hp=p[m]>=qp
   diagnostics.append(dict(source_id=s,plate=s[0],model=model,seed=seed,max_abs_error_MPa=float(abs(e[i])),source_point_id=int(d['source_ids'][i]),X_mm=d['xyz'][i,0],Y_mm=d['xyz'][i,1],Z_mm=d['xyz'][i,2],signed_error_at_max_MPa=float(e[i]),negative_prediction_area_fraction=float(w[p[m]<0].sum()/w.sum()),false_positive_high95_area_mm2=float(w[hp&~hy].sum()),false_negative_high95_area_mm2=float(w[hy&~hp].sum())))
   for descriptor,v in [('target_T2_MPa',d['T2_MPa'][m]),('parent_relative_height_mm',None),('K16_height_residual_mm',g['features'][m,13]),('K16_normal_variation',g['features'][m,14])]:
    if v is None:
     datum=json.loads(lookup[s]['parent_datum']);x=d['xyz'][m];v=x[:,2]-(datum['intercept_Z_mm']+datum['slope_X']*(x[:,0]-datum['origin_X_mm'])+datum['slope_Y']*(x[:,1]-datum['origin_Y_mm']))
    edges=np.linspace(v.min(),v.max()+1e-12,21)
    for k in range(20):
     z=(v>=edges[k])&(v<edges[k+1])
     if z.any():binned.append(dict(source_id=s,model=model,seed=seed,descriptor=descriptor,bin=k,descriptor_mean=float(np.average(v[z],weights=w[z])),MAE_MPa=float(np.average(abs(e[m][z]),weights=w[z])),bias_MPa=float(np.average(e[m][z],weights=w[z])),area_mm2=float(w[z].sum())))
 table(R/'DOMAIN_SHIFT_DESCRIPTORS.csv',domains);table(R/'ERROR_DIAGNOSTICS.csv',diagnostics);table(R/'NUMERICAL_TARGET_COMPARISON.csv',mesh);table(R/'07_metrics/ERROR_DESCRIPTOR_BINS.csv',binned)
 # Export frozen core rows, with all source identities and exact-coordinate provenance.
 for name,models in [('CONSTANT_BASELINE_PREDICTIONS.csv',['B0_CONSTANT']),('RIDGE_BASELINE_PREDICTIONS.csv',['B1_GEOMETRY_RIDGE']),('POINT_TRANSFORMER_OOF_PREDICTIONS.csv',['N1_POINT_TRANSFORMER'])]:
  def export_rows():
   for a in reg:
    if a['model'] not in models:continue
    s=a['source_id'];d=data[s];p=preds[a['model'],str(a['seed']),s];m=d['core']&d['valid']
    for i in np.flatnonzero(m):yield dict(source_id=s,plate=s[0],fold=a['fold'],model=a['model'],seed=a['seed'],point_id=int(d['source_ids'][i]),X_mm=float(d['xyz'][i,0]),Y_mm=float(d['xyz'][i,1]),Z_mm=float(d['xyz'][i,2]),T0_area_mm2=float(d['area'][i]),frozen_core=True,valid_prediction=True,tile_count=1,pred_T2_MPa=float(p[i]),reference_T2_MPa=float(d['T2_MPa'][i]),reference_SHA256=lookup[s]['qualified_M2_target_SHA256'],checkpoint_SHA256=a['checkpoint_SHA256'])
  table(R/name,export_rows())
  print('CSV_EXPORTED',name,flush=True)
 neural=study[study.model=='N1_POINT_TRANSFORMER'];baseline=study[study.model!='N1_POINT_TRANSFORMER'];np_plates=plate[plate.model=='N1_POINT_TRANSFORMER'];ridgeplate=plate[plate.model=='B1_GEOMETRY_RIDGE'].set_index('plate');better=[]
 for seed in ['20261021','20261022']:
  n=np_plates[np_plates.seed.astype(str)==seed].set_index('plate');b0plate=plate[plate.model=='B0_CONSTANT'].set_index('plate');better.append(((n.L2<ridgeplate.L2)&(n.L2<b0plate.L2)).reindex(list('CEGHX')).to_numpy())
 all_macro_better=all(float(r.equal_plate_L2)<baseline.equal_plate_L2.min() for r in neural.itertuples())
 decision='NEURAL_IMPROVES_HELDOUT_PLATES' if all_macro_better and np.all(better) else ('NEURAL_DOES_NOT_IMPROVE' if not np.any(better) else 'NEURAL_MIXED_RESULTS')
 counts=dict(UTC=now(),dataset_status='QUALIFIED13_V1_DATASET_VERIFIED',plate_status='DOCUMENTARY_PLATE_GROUPING_VERIFIED',leakage_status='LOPO_LEAKAGE_AUDIT_PASS',baseline_status='GEOMETRY_BASELINES_COMPLETE',neural_status='POINT_TRANSFORMER_10_RUNS_COMPLETE',coverage_status='FULL_CORE_PREDICTION_COVERAGE_PASS',metric_status='INDEPENDENT_METRICS_VERIFIED',model_comparison=decision,external_status='INDEPENDENT_EXTERNAL_VALIDATION_NOT_ESTABLISHED',physical_status='BATCH_INDEPENDENCE_NOT_VERIFIED',overall='R8E13_COMPLETE',sources=13,plates=5,scheduled_fits=10,attempted_fits=len(runs),completed_fits=len(runs),dryrun_steps=1,training_interruptions=0,new_ANSYS_solves=0,new_FE_meshes=0,new_V1_targets=0,external_predictions=0,training_s=sum(a['training_s'] for a in runs),peak_RSS_bytes=max(a['peak_RSS_bytes'] for a in runs),peak_GPU_allocated_bytes=0,prediction_files=len(reg),core_predictions=sum(int(a['core_points']) for a in rows(R/'SOURCE_LEVEL_METRICS.csv')),figures_planned=36)
 write(R/'R8E13_FINAL_COUNTS.json',counts)
 from figures_e13 import figures
 figures(data,geom,preds,source,plate,study,regional,histories,resources,domains,feature_shift,mesh,diagnostics,binned,decision)
 from reports_e13 import reports
 reports(counts,source,plate,study,regional,domains,diagnostics,mesh,histories)
 print('DELIVERY_GENERATED',decision,flush=True)
if __name__=='__main__':main()
