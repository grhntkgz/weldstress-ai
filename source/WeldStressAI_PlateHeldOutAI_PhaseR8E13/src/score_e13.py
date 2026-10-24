from common_e13 import *
import numpy as np,math
def quantile(v,w,q=.95):
 i=np.argsort(v,kind='stable');return float(np.interp(q,np.cumsum(w[i])/w.sum(),v[i]))
def metric(y,p,w,xyz):
 e=p-y;s=w.sum();sse=float(w@(e*e));den=float(w@(y*y));ym=float(w@y/s);sst=float(w@((y-ym)**2));qy=quantile(y,w);qp=quantile(p,w);hy=y>=qy;hp=p>=qp;inter=float(w[hy&hp].sum());union=float(w[hy|hp].sum());cy=np.sum(xyz[hy]*w[hy,None],0)/w[hy].sum();cp=np.sum(xyz[hp]*w[hp,None],0)/w[hp].sum()
 return dict(MAE_MPa=float(w@abs(e)/s),RMSE_MPa=math.sqrt(sse/s),bias_MPa=float(w@e/s),L2=math.sqrt(sse/den),R2=1-sse/sst if sst>1e-12*s else None,pred_mean_MPa=float(w@p/s),ref_mean_MPa=ym,pred_max_MPa=float(p.max()),ref_max_MPa=float(y.max()),max_ratio_error=float(p.max()/y.max()-1),Q95_error_MPa=qp-qy,ref_Q95_MPa=qy,pred_Q95_MPa=qp,high95_IoU=inter/union,high95_precision=inter/float(w[hp].sum()),high95_recall=inter/float(w[hy].sum()),high95_centroid_distance_mm=float(np.linalg.norm(cy-cp)),area_mm2=float(s),SSE=sse,ref_square_sum=den)
def main():
 verify_seal();registry=rows(R/'04_baselines/PREDICTION_REGISTRY.csv')
 for p in sorted((R/'05_training').glob('F*_s*/PREDICTION_REGISTRY.csv')):registry+=rows(p)
 table(R/'PREDICTION_REGISTRY.csv',registry);scored=[];regional=[]
 for rec in registry:
  sid=rec['source_id'];d=dict(np.load(R/'01_dataset/targets'/(sid+'.npz')));p=dict(np.load(rec['path']));assert sha(rec['path'])==rec['SHA256'];assert all(np.array_equal(d[k],p[k]) for k in ['source_ids','xyz','area']);m=d['core']&d['valid'];assert p['valid'][m].all() and (p['tile_count'][m]==1).all();base={k:rec[k] for k in ['model','fold','seed','source_id','plate']};mtr=metric(d['T2_MPa'][m],p['pred_MPa'][m],d['area'][m],d['xyz'][m]);regionals=[]
  for region in np.unique(d['region'][m]):
   z=m&(d['region']==region);r=metric(d['T2_MPa'][z],p['pred_MPa'][z],d['area'][z],d['xyz'][z]);regional.append(dict(**base,region=int(region),**r));regionals.append(r['L2'])
  scored.append(dict(**base,**mtr,worst_regional_L2=max(regionals),coverage=1.,core_points=int(m.sum())))
 table(R/'SOURCE_LEVEL_METRICS.csv',scored);table(R/'HIGH95_METRICS.csv',[{k:a[k] for k in ['model','fold','seed','source_id','high95_IoU','high95_precision','high95_recall','high95_centroid_distance_mm','ref_Q95_MPa','pred_Q95_MPa']} for a in scored]);table(R/'REGIONAL_PREDICTION_METRICS.csv',regional)
 numeric=['MAE_MPa','RMSE_MPa','bias_MPa','L2','high95_IoU','high95_precision','high95_recall','worst_regional_L2'];plates=[];study=[]
 for model,seed in sorted({(a['model'],str(a['seed'])) for a in scored}):
  ss=[a for a in scored if a['model']==model and str(a['seed'])==seed];pp=[]
  for plate in 'CEGHX':
   s=[a for a in ss if a['plate']==plate]
   if not s:continue
   rec=dict(model=model,seed=seed,plate=plate,sources=len(s),**{k:float(np.mean([a[k] for a in s])) for k in numeric});plates.append(rec);pp.append(rec)
  rec=dict(model=model,seed=seed,plates=len(pp),sources=len(ss),**{'equal_plate_'+k:float(np.mean([a[k] for a in pp])) for k in numeric},equal_source_L2=float(np.mean([a['L2'] for a in ss])),point_area_L2=math.sqrt(sum(a['SSE'] for a in ss)/sum(a['ref_square_sum'] for a in ss)),worst_plate_L2=max(a['L2'] for a in pp),worst_source_L2=max(a['L2'] for a in ss),median_plate_L2=float(np.median([a['L2'] for a in pp])),min_plate_L2=min(a['L2'] for a in pp));study.append(rec)
 table(R/'PLATE_LEVEL_METRICS.csv',plates);table(R/'SEED_LEVEL_METRICS.csv',study);table(R/'MODEL_COMPARISON_METRICS.csv',study);write(R/'07_metrics/SCORING_COMPLETE.json',dict(UTC=now(),sources_scored=len(scored),prediction_files=len(registry)))
 print(json.dumps(study,indent=2),flush=True)
if __name__=='__main__':main()
