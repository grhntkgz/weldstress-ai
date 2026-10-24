from pathlib import Path
import json,hashlib,datetime,shutil
import numpy as np,pandas as pd,psutil
from scipy.spatial import cKDTree
from metric_contract import budget,quantile,localization,regional
D=Path(__file__).resolve().parents[1];O=D.parent;R=O/'WeldStressAI_FinalResearch_PhaseR8E16';P=O/'WeldStressAI_ManuscriptRevision_R2'
seal=json.loads((D/'R2_1_PROTOCOL_SEAL.json').read_text())
for a in seal['files']:assert hashlib.sha256((D/a['path']).read_bytes()).hexdigest()==a['SHA256'],a['path']
assert not (D/'qa'/'ASSESSMENT_COMPLETE.json').exists(),'Do not rerun a completed assessment'
resource=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),free_RAM_GiB=psutil.virtual_memory().available/1024**3,E_free_GiB=shutil.disk_usage('E:/').free/1024**3,C_free_GiB=shutil.disk_usage('C:/').free/1024**3,estimated_peak_RAM_GiB=.7,estimated_workspace_GiB=2.,minimum_RAM_GiB=1.,minimum_E_free_GiB=3.,minimum_C_free_GiB=.5)
assert resource['free_RAM_GiB']>=1 and resource['E_free_GiB']>=3 and resource['C_free_GiB']>=.5
resource['status']='PASS';(D/'qa'/'RESOURCE_PREFLIGHT.json').write_text(json.dumps(resource,indent=2));(D/'qa'/'masks').mkdir(exist_ok=True)
reg=pd.read_csv(D/'R2_1_SOURCE_REGISTRY.csv');pr=pd.read_csv(R/'MODEL_PREDICTION_REGISTRY.csv',keep_default_na=False);windows=pd.read_csv(D/'source_snapshot'/'OBSERVATION_WINDOW_COORDINATES.csv');bvp=pd.read_csv(P/'NATIVE_BOUNDARY_SPATIAL_REGISTRY.csv');rankrows=[];commonrows=[];ties=[];regionrows=[];brows=[];g0rows=[];g1rows=[];observable=[];critical=[];fregistry=[]
def save(name,rows):pd.DataFrame(rows).to_csv(D/name,index=False)
for _,sr in reg.iterrows():
 sid=sr.source_id;g=dict(np.load(sr.geometry_path));t=dict(np.load(sr.target_path));core=t['core']&t['valid'];q=np.flatnonzero(core);x=t['xyz'][core];ids=t['source_ids'][core];w=t['area'][core];y=t['T2_MPa'][core];labels=t['region'][core];ks=dict(np.load(sr.E15_core_path));geo=dict(np.load(D/'geometry_only'/(sid+'.npz')));score=geo['score'][core]
 refs={};historical_ref=y>=quantile(y,w,.95);rm={};reference_thresholds={};basemasks={}
 for frac in [.01,.05,.10]:
  code=f'{int(frac*100):02d}';refs[code],meta=budget(y,w,ids,frac);reference_thresholds[code]=quantile(y,w,1-frac);basemasks[code],bmeta=budget(score,w,ids,frac)
  ties.append(dict(field_id='GEOMETRY_'+sid,source_id=sid,model='G1_GEOMETRY_TRANSITION_RANKING',condition='FULL',seed='GEOMETRY',scheme='RANK_BUDGET',field='predicted',budget=frac,**bmeta))
  for model in ['G0_EXISTING_COLLAR_MASK','G1_GEOMETRY_TRANSITION_RANKING']:
   mm=labels==2 if model.startswith('G0') else basemasks[code];met=localization(refs[code],mm,w,x);row=dict(source_id=sid,plate=sr.plate,model=model,condition='FULL',seed='GEOMETRY',budget=frac,scheme='RANK_BUDGET_REFERENCE',information='FULL processed geometry and original full-source parent-plane rule',status='EVALUABLE',area_budget_matched=model.startswith('G1'),**met,retrospective=True)
   if model.startswith('G0'):row.update(collar_core_fraction=float(w[labels==2].sum()/w.sum()),hotspot_capture_fraction=met['recall'],enrichment=met['recall']/met['predicted_fraction']);g0rows.append(row)
   else:g1rows.append(row)
 for cond in ['FULL','X50','X43']:
  for model in ['G0_EXISTING_COLLAR_MASK','G1_GEOMETRY_TRANSITION_RANKING']:
   observable.append(dict(source_id=sid,condition=cond,model=model,status='EVALUABLE' if cond=='FULL' else 'NOT_EVALUABLE',scoring_core_points=34200,unqualified_for_partial_comparator=0 if cond=='FULL' else 34200,geometrically_absent_query_points='NOT_ASSERTED',full_source_plane_required=True,reason='Original FULL geometry-only benchmark' if cond=='FULL' else 'Original parent-plane estimate and region labels depend on FULL source. No qualified visible-only replacement plane rule; no partial score is substituted.',retrospective=True))
 native=bvp[bvp.source_id==sid].iloc[0];gauges=pd.DataFrame(json.loads(native.gauges))[['X','Y','Z']].drop_duplicates().to_numpy();gdist=cKDTree(gauges).query(x)[0];capdist=np.minimum(abs(x[:,0]-native.left_port_X_mm),abs(x[:,0]-native.right_port_X_mm));corexdist=np.minimum(x[:,0]-x[:,0].min(),x[:,0].max()-x[:,0]);coreydist=np.minimum(x[:,1]-x[:,1].min(),x[:,1].max()-x[:,1])
 for i,rr in pr[pr.source_id==sid].iterrows():
  fieldid=f'F{i:03d}';a=dict(np.load(rr.path));take=q if len(a['source_ids'])==len(g['xyz']) else np.arange(len(q));p=a['pred_MPa'][take];sd=str(rr.seed) if str(rr.seed).isdigit() else 'FIXED';key=dict(field_id=fieldid,source_id=sid,plate=sr.plate,model=rr.model,condition=rr.condition,seed=sd,retrospective=True);fregistry.append(dict(**key,path=rr.path,SHA256=rr.SHA256));masks={}
  for frac in [.01,.05,.10]:
   code=f'{int(frac*100):02d}';hy=refs[code];hp,meta=budget(p,w,ids,frac);masks['ref_rank_'+code]=hy;masks['pred_rank_'+code]=hp
   rankrows.append(dict(**key,scheme='RANK_BUDGET',budget=frac,**localization(hy,hp,w,x)))
   _,ymeta=budget(y,w,ids,frac)
   for which,mm in [('reference',ymeta),('predicted',meta)]:ties.append(dict(**key,scheme='RANK_BUDGET',field=which,budget=frac,**mm))
   threshold=reference_thresholds[code];hyc=y>=threshold;hpc=p>=threshold;masks['ref_common_'+code]=hyc;masks['pred_common_'+code]=hpc
   commonrows.append(dict(**key,scheme='REFERENCE_THRESHOLD_DIAGNOSTIC_ONLY',budget=frac,FE_threshold_MPa=threshold,**localization(hyc,hpc,w,x)))
   for which,v,mm in [('reference',y,hyc),('predicted',p,hpc)]:ties.append(dict(**key,scheme='REFERENCE_THRESHOLD_DIAGNOSTIC_ONLY',field=which,budget=frac,requested_fraction=frac,achieved_fraction=float(w[mm].sum()/w.sum()),quota_error_mm2=float(w[mm].sum()-frac*w.sum()),selected_points=int(mm.sum()),cut_score=threshold,tie_points=int((v==threshold).sum()),tie_selected_points=int(((v==threshold)&mm).sum()),tie_split=False,constant_score=bool(np.ptp(v)==0)))
  hp=p>=quantile(p,w,.95);masks['ref_historical']=historical_ref;masks['pred_historical']=hp;rankrows.append(dict(**key,scheme='HISTORICAL_HIGH95',budget=.05,**localization(historical_ref,hp,w,x)))
  for which,v,mm in [('reference',y,historical_ref),('predicted',p,hp)]:ties.append(dict(**key,scheme='HISTORICAL_HIGH95',field=which,budget=.05,requested_fraction=.05,achieved_fraction=float(w[mm].sum()/w.sum()),quota_error_mm2=float(w[mm].sum()-.05*w.sum()),selected_points=int(mm.sum()),cut_score=quantile(v,w,.95),tie_points=int((v==quantile(v,w,.95)).sum()),tie_selected_points=int(((v==quantile(v,w,.95))&mm).sum()),tie_split=False,constant_score=bool(np.ptp(v)==0)))
  np.savez_compressed(D/'qa'/'masks'/(fieldid+'.npz'),**masks)
  e=p-y
  for code,name in [(0,'PARENT'),(1,'HEIGHT_REGION'),(2,'COLLAR')]:
   z=labels==code;met=regional(y,p,w,z);regionrows.append(dict(**key,region=name,region_code=code,**met))
  if rr.condition=='FULL':obsdist=np.minimum(x[:,0]-g['xyz'][:,0].min(),g['xyz'][:,0].max()-x[:,0])
  else:
   obsdist=np.empty(len(x))
   for tile in np.unique(ks['tile_id']):
    z=ks['tile_id']==tile;row=windows[(windows.source_id==sid)&(windows.condition==rr.condition)&(windows.tile==tile)].iloc[0];obsdist[z]=np.minimum(x[z,0]-row.actual_X_min,row.actual_X_max-x[z,0])
  for name,dist in [('CORE_X_EDGE_1MM',corexdist),('CORE_Y_EDGE_1MM',coreydist),('NATIVE_LOADING_CAP_1MM',capdist),('NATIVE_GAUGE_3D_1MM',gdist),('OWNING_OBSERVATION_X_EDGE_1MM',obsdist)]:
   brows.append(dict(**key,stratum=name,minimum_distance_mm=float(dist.min()),nonexclusive=True,**regional(y,p,w,dist<=1+1e-7)))
  if sid[:3] in ['G07','X10','X23'] and rr.model in ['N2','N3']:
   for code,name in [(0,'PARENT'),(1,'HEIGHT_REGION'),(2,'COLLAR')]:
    z=labels==code;ww=w[z];ee=e[z];signedsq=ww*ee**2;critical.append(dict(**key,region=name,underprediction_area_fraction=float(ww[ee<0].sum()/ww.sum()),overprediction_area_fraction=float(ww[ee>0].sum()/ww.sum()),underprediction_SSE_fraction=float(signedsq[ee<0].sum()/signedsq.sum()),overprediction_SSE_fraction=float(signedsq[ee>0].sum()/signedsq.sum()),mean_underprediction_MPa=float(np.average(ee[ee<0],weights=ww[ee<0])) if (ee<0).any() else np.nan,mean_overprediction_MPa=float(np.average(ee[ee>0],weights=ww[ee>0])) if (ee>0).any() else np.nan))
 print('BOUNDED_ASSESSMENT_SOURCE_COMPLETE',sid,flush=True)
save('THRESHOLD_ROBUSTNESS_SOURCE.csv',rankrows);save('REFERENCE_THRESHOLD_DIAGNOSTICS.csv',commonrows);save('THRESHOLD_TIE_AND_AREA_AUDIT.csv',ties);save('G0_COLLAR_BASELINE_RESULTS.csv',g0rows);save('G1_GEOMETRY_RANKING_RESULTS.csv',g1rows);save('GEOMETRY_BASELINE_OBSERVABILITY_AUDIT.csv',observable);save('REGIONAL_ERROR_SOURCE.csv',regionrows);save('BOUNDARY_ERROR_STRATA_SOURCE.csv',brows);save('CRITICAL_SOURCE_SIGNED_ERROR_REGIONS.csv',critical);save('FROZEN_FIELD_ANALYSIS_REGISTRY.csv',fregistry)
regions=pd.DataFrame(regionrows);regions[['field_id','source_id','plate','model','condition','seed','region','area_mm2','area_fraction','SSE_share','SAE_share','globally_normalized_SSE_contribution','SSE_MPa2_mm2','SAE_MPa_mm2','retrospective']].to_csv(D/'REGIONAL_ERROR_CONTRIBUTIONS.csv',index=False)
def aggregate(frame,dimensions,prefix):
 keys=['model','condition','seed']+dimensions;exclude=set(keys+['field_id','source_id','region_code','retrospective','area_budget_matched']);metrics=[c for c in frame.select_dtypes(include=np.number) if c not in exclude]
 # Every metric remains a source metric, including error shares; no pooled surface sums.
 ps=frame.groupby(keys+['plate'],dropna=False)[metrics].mean().reset_index();ps['source_count']=frame.groupby(keys+['plate'],dropna=False).size().to_numpy()
 for c in ['precision','centroid_separation_mm','L2']:
  if c in metrics:ps[c+'_valid_source_count']=frame.groupby(keys+['plate'],dropna=False)[c].count().to_numpy()
 pm=ps.groupby(['model','condition','plate']+dimensions,dropna=False)[metrics].mean().reset_index();macro_seed=ps.groupby(keys,dropna=False)[metrics].mean().reset_index();macro=macro_seed.groupby(['model','condition']+dimensions,dropna=False)[metrics].mean().reset_index()
 for c in ['precision','centroid_separation_mm','L2']:
  if c in metrics:macro_seed[c+'_valid_plate_count']=ps.groupby(keys,dropna=False)[c].count().to_numpy()
 ps.to_csv(D/(prefix+'_PLATE_SEED.csv'),index=False);pm.to_csv(D/(prefix+'_PLATE.csv'),index=False);macro_seed.to_csv(D/(prefix+'_MACRO_SEED.csv'),index=False);macro.to_csv(D/(prefix+'_MACRO.csv'),index=False)
 return ps,pm,macro_seed,macro
aggregate(pd.DataFrame(rankrows),['scheme','budget'],'THRESHOLD_ROBUSTNESS');aggregate(pd.DataFrame(commonrows),['scheme','budget'],'REFERENCE_THRESHOLD');aggregate(regions,['region'],'REGIONAL_ERROR');aggregate(pd.DataFrame(brows),['stratum'],'BOUNDARY_ERROR_STRATA');aggregate(pd.DataFrame(g0rows),['budget'],'G0_COLLAR');aggregate(pd.DataFrame(g1rows),['budget'],'G1_GEOMETRY')
full=pd.DataFrame(rankrows);full=full[(full.scheme=='RANK_BUDGET')&(full.condition=='FULL')]
comparison=[]
for _,nr in full.iterrows():
 for z in [pd.DataFrame(g0rows),pd.DataFrame(g1rows)]:
  gr=z[(z.source_id==nr.source_id)&(z.budget==nr.budget)].iloc[0];comparison.append(dict(source_id=nr.source_id,plate=nr.plate,condition='FULL',seed=nr.seed,model=nr.model,geometry_model=gr.model,budget=nr.budget,neural_or_regression_IoU=nr.IoU,geometry_IoU=gr.IoU,delta_IoU=nr.IoU-gr.IoU,geometry_budget_matched=gr.area_budget_matched,predicted_fraction=nr.predicted_fraction,geometry_fraction=gr.predicted_fraction,retrospective=True))
save('NEURAL_VERSUS_GEOMETRY_BASELINES.csv',comparison)
df=pd.DataFrame(comparison);cols=['neural_or_regression_IoU','geometry_IoU','delta_IoU','predicted_fraction','geometry_fraction'];ps=df.groupby(['model','seed','condition','geometry_model','budget','plate'])[cols].mean().reset_index();pm=ps.groupby(['model','condition','geometry_model','budget','plate'])[cols].mean().reset_index();ps.to_csv(D/'NEURAL_VERSUS_GEOMETRY_PLATE_SEED.csv',index=False);pm.to_csv(D/'NEURAL_VERSUS_GEOMETRY_PLATE.csv',index=False);ps.groupby(['model','seed','condition','geometry_model','budget'])[cols].mean().reset_index().groupby(['model','condition','geometry_model','budget'])[cols].mean().reset_index().to_csv(D/'NEURAL_VERSUS_GEOMETRY_MACRO.csv',index=False)
(D/'qa'/'ASSESSMENT_COMPLETE.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),historical_fields=299,rank_and_historical_rows=len(rankrows),common_threshold_rows=len(commonrows),geometry_G0_rows=len(g0rows),geometry_G1_rows=len(g1rows),regional_rows=len(regionrows),boundary_rows=len(brows),new_FE=0,new_training=0,new_inference=0,new_fitting=0),indent=2));print('ASSESSMENT_COMPLETE',flush=True)
