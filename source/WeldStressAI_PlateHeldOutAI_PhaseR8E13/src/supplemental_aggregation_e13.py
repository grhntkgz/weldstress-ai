"""Additional descriptive aggregates; no training or change to preregistered source metrics."""
from common_e13 import *
import numpy as np,pandas as pd,math
from score_e13 import quantile
from deliver_e13 import mdtable
def main():
 verify_seal();src=pd.read_csv(R/'SOURCE_LEVEL_METRICS.csv',keep_default_na=False);plates=pd.read_csv(R/'PLATE_LEVEL_METRICS.csv',keep_default_na=False);registry=rows(R/'PREDICTION_REGISTRY.csv');agg=[];summary=[]
 for (model,seed),ss in src.groupby(['model','seed']):
  total=float(ss.area_mm2.sum());intersection=union=predarea=refarea=0.
  for rec in registry:
   if rec['model']!=model or str(rec['seed'])!=str(seed):continue
   d=dict(np.load(R/'01_dataset/targets'/(rec['source_id']+'.npz')));p=dict(np.load(rec['path']));m=d['core']&d['valid'];w=d['area'][m];y=d['T2_MPa'][m];v=p['pred_MPa'][m];hy=y>=quantile(y,w);hp=v>=quantile(v,w);intersection+=float(w[hy&hp].sum());union+=float(w[hy|hp].sum());predarea+=float(w[hp].sum());refarea+=float(w[hy].sum())
  agg.append(dict(model=model,seed=seed,point_area_MAE_MPa=float(ss.MAE_MPa@ss.area_mm2/total),point_area_RMSE_MPa=math.sqrt(float(ss.SSE.sum())/total),point_area_bias_MPa=float(ss.bias_MPa@ss.area_mm2/total),point_area_L2=math.sqrt(float(ss.SSE.sum())/float(ss.ref_square_sum.sum())),point_area_high95_IoU=intersection/union,point_area_high95_precision=intersection/predarea,point_area_high95_recall=intersection/refarea,high95_convention='Union of source-specific independently-thresholded masks; descriptive pooled area, no independent-point inference'))
  pp=plates[(plates.model==model)&(plates.seed.astype(str)==str(seed))]
  for metric in ['L2','MAE_MPa','high95_IoU','bias_MPa']:
   v=pp[metric].to_numpy();summary.append(dict(model=model,seed=seed,metric=metric,groups=5,mean=float(v.mean()),median=float(np.median(v)),minimum=float(v.min()),maximum=float(v.max())))
 table(R/'07_metrics/POINT_AREA_AGGREGATES.csv',agg);table(R/'07_metrics/PLATE_STATISTICAL_SUMMARY.csv',summary)
 ns=plates[plates.model=='N1_POINT_TRANSFORMER'];seedmeans=ns.groupby('plate')[['L2','MAE_MPa','high95_IoU','bias_MPa']].mean().reset_index();seedmeans.to_csv(R/'07_metrics/SEED_AGGREGATE_PER_PLATE.csv',index=False)
 text='\n\n## Descriptive aggregation supplement\n\nThese summaries do not alter the preregistered primary equal-plate macro metric or the frozen model comparison. The pooled High95 metric sums intersection/union areas from source-specific thresholds; point areas are not independent experimental replicates.\n\n'+mdtable(pd.DataFrame(agg))+'\n\nAll five plate values support the following mean, median and observed range; no inferential confidence interval is claimed.\n\n'+mdtable(pd.DataFrame(summary))+'\n\nArithmetic mean of independently scored neural seeds by plate:\n\n'+mdtable(seedmeans)
 for name in ['R8E13_MASTER_REPORT.md','PLATE_LEVEL_PREDICTION_METRICS.md','SEED_VARIABILITY.md']:
  p=R/name;p.write_text(p.read_text(encoding='utf8')+text,encoding='utf8')
 print('DESCRIPTIVE_AGGREGATES_COMPLETE',flush=True)
if __name__=='__main__':main()
