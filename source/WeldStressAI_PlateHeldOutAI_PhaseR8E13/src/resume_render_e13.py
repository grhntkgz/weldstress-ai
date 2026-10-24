from common_e13 import *
import numpy as np,pandas as pd
def main():
 verify_seal();assert read(R/'07_metrics/INDEPENDENT_VERIFICATION.json')['passed'];reg=rows(R/'PREDICTION_REGISTRY.csv');sources=sorted({a['source_id'] for a in reg});data={s:dict(np.load(R/'01_dataset/targets'/(s+'.npz'))) for s in sources};geom={s:dict(np.load(R/'02_geometry'/(s+'.npz'))) for s in sources};preds={(a['model'],str(a['seed']),a['source_id']):dict(np.load(a['path']))['pred_MPa'] for a in reg};source=pd.read_csv(R/'SOURCE_LEVEL_METRICS.csv',keep_default_na=False);plate=pd.read_csv(R/'PLATE_LEVEL_METRICS.csv',keep_default_na=False);study=pd.read_csv(R/'MODEL_COMPARISON_METRICS.csv',keep_default_na=False);regional=pd.read_csv(R/'REGIONAL_PREDICTION_METRICS.csv',keep_default_na=False);history=pd.read_csv(R/'TRAINING_LOSS_HISTORY.csv');resources=rows(R/'TRAINING_RESOURCE_ACCOUNTING.csv');domains=rows(R/'DOMAIN_SHIFT_DESCRIPTORS.csv');mesh=rows(R/'NUMERICAL_TARGET_COMPARISON.csv');diagnostics=rows(R/'ERROR_DIAGNOSTICS.csv');binned=rows(R/'07_metrics/ERROR_DESCRIPTOR_BINS.csv');counts=read(R/'R8E13_FINAL_COUNTS.json');shifts=[]
 for records,names in [(domains,['geometry_mean_standardized_distance','mean_feature_outside_training_range_fraction']),(mesh,['M1_M2_L2','M1_M2_worst_region_L2','M1_M2_high95_IoU','mapping_coverage']),(binned,['descriptor_mean','MAE_MPa','bias_MPa','area_mm2'])]:
  for rec in records:
   for name in names:rec[name]=float(rec[name])
 for s in sources:
  f='F'+str('CEGHX'.index(s[0])+1);tr=read(R/'04_baselines'/(f+'_FIT.json'))['train_sources'];lo=np.min(np.stack([geom[t]['features'].min(0) for t in tr]),0);hi=np.max(np.stack([geom[t]['features'].max(0) for t in tr]),0);d=data[s];m=d['core']&d['valid'];shifts.append(np.average((geom[s]['features'][m]<lo)|(geom[s]['features'][m]>hi),axis=0,weights=d['area'][m]))
 from figures_render_repair_e13 import figures
 figures(data,geom,preds,source,plate,study,regional,history,resources,domains,shifts,mesh,diagnostics,binned,counts['model_comparison'])
 from reports_e13 import reports
 reports(counts,source,plate,study,regional,domains,diagnostics,mesh,history)
 for name in ['R8E13_MASTER_REPORT.md','README_REPRODUCIBILITY.md']:
  p=R/name;p.write_text(p.read_text(encoding='utf8')+'\n\nRendering provenance: the first render stopped at Figure 12 because RSS CSV strings required numeric conversion. The sealed original renderer remains unchanged; `figures_render_repair_e13.py` changes only this plotting cast. Initial figures and the failure log are retained. Training, predictions, metric calculations and CSV exports were not rerun or changed. See `21_reproducibility/RENDER_ONLY_AMENDMENT.json`.\n',encoding='utf8')
 write(R/'21_reproducibility/RENDER_REPORT_RESUME_COMPLETE.json',dict(UTC=now(),passed=True,render_only=True,figure_pairs=36,training_reruns=0,prediction_changes=0,metric_changes=0))
 print('RENDER_REPORT_RESUME_COMPLETE',flush=True)
if __name__=='__main__':main()
