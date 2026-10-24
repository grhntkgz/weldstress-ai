from pathlib import Path
import pandas as pd,numpy as np,json,math,hashlib
from scipy.spatial import cKDTree
D=Path(__file__).resolve().parents[1];R2=D.parent/'WeldStressAI_ManuscriptRevision_R2';reg=pd.read_csv(D/'R2_1_SOURCE_REGISTRY.csv');fr=pd.read_csv(D/'FROZEN_FIELD_ANALYSIS_REGISTRY.csv');bw=pd.read_csv(D/'BOUNDARY_ERROR_STRATA_SOURCE.csv');win=pd.read_csv(D/'source_snapshot'/'OBSERVATION_WINDOW_COORDINATES.csv');native=pd.read_csv(R2/'NATIVE_BOUNDARY_SPATIAL_REGISTRY.csv');errors=[]
def ck(a,b):
 if pd.isna(a) and pd.isna(b):return
 error=abs(float(a)-float(b));assert error<1e-7+abs(float(b))*1e-10,(a,b);errors.append(error)
for _,sr in reg.iterrows():
 t=dict(np.load(sr.target_path));g=dict(np.load(sr.geometry_path));m=t['core']&t['valid'];x=t['xyz'][m];w=t['area'][m];y=t['T2_MPa'][m];tiles=np.load(sr.E15_core_path)['tile_id'];n=native[native.source_id==sr.source_id].iloc[0];gg=np.array([[a['X'],a['Y'],a['Z']] for a in json.loads(n.gauges)]);ds=np.sqrt(((x[:,None,:]-gg[None,:,:])**2).sum(2)).min(1)
 fixed={'CORE_X_EDGE_1MM':np.minimum(x[:,0]-x[:,0].min(),x[:,0].max()-x[:,0]),'CORE_Y_EDGE_1MM':np.minimum(x[:,1]-x[:,1].min(),x[:,1].max()-x[:,1]),'NATIVE_LOADING_CAP_1MM':np.minimum(abs(x[:,0]-n.left_port_X_mm),abs(x[:,0]-n.right_port_X_mm)),'NATIVE_GAUGE_3D_1MM':ds}
 for _,f in fr[fr.source_id==sr.source_id].iterrows():
  v=np.load(f.path)['pred_MPa'];v=v[m] if len(v)==len(m) else v;e=v-y;S=float(w@(e*e));dist={k:v.copy() for k,v in fixed.items()};obs=np.empty(len(x))
  if f.condition=='FULL':obs=np.minimum(x[:,0]-g['xyz'][:,0].min(),g['xyz'][:,0].max()-x[:,0])
  else:
   for k in set(tiles):
    a=win[(win.source_id==sr.source_id)&(win.condition==f.condition)&(win.tile==k)].iloc[0];z=tiles==k;obs[z]=np.minimum(x[z,0]-a.actual_X_min,a.actual_X_max-x[z,0])
  dist['OWNING_OBSERVATION_X_EDGE_1MM']=obs
  for name,v in dist.items():
   row=bw[(bw.field_id==f.field_id)&(bw.stratum==name)].iloc[0];z=(v<=1+1e-7).astype(float);a=float(w@z);ck(a,row.area_mm2);ck(a/w.sum(),row.area_fraction);ck(v.min(),row.minimum_distance_mm);ck(float((w*z)@(e*e))/S,row.SSE_share)
   if a:ck(float((w*z)@abs(e))/a,row.MAE_MPa);ck(float((w*z)@e)/a,row.bias_MPa)
# Independently verify geometry baseline aggregations, both with one deterministic geometry seed.
for prefix,sourcefile in [('G0_COLLAR','G0_COLLAR_BASELINE_RESULTS.csv'),('G1_GEOMETRY','G1_GEOMETRY_RANKING_RESULTS.csv')]:
 src=pd.read_csv(D/sourcefile);plate=pd.read_csv(D/(prefix+'_PLATE.csv'));macro=pd.read_csv(D/(prefix+'_MACRO.csv'))
 for _,r in plate.iterrows():
  a=src[(src.plate==r.plate)&(src.budget==r.budget)]
  for col in ['IoU','precision','recall','FN_mm2','FP_mm2','predicted_fraction']:ck(math.fsum(a[col])/len(a),r[col])
 for _,r in macro.iterrows():
  a=plate[plate.budget==r.budget]
  for col in ['IoU','precision','recall','FN_mm2','FP_mm2','predicted_fraction']:ck(math.fsum(a[col])/5,r[col])
for _,row in pd.read_csv(D/'NEURAL_VERSUS_GEOMETRY_BASELINES.csv').iterrows():ck(row.neural_or_regression_IoU-row.geometry_IoU,row.delta_IoU)
result=dict(status='PASS',boundary_geometry_and_grouping_cells=len(errors),maximum_absolute_error=max(errors),nonexclusive_boundary_masks_independently_reconstructed=True,geometry_baseline_plate_macro_and_paired_difference_checks=True)
(D/'qa'/'ADDITIONAL_INDEPENDENT_CHECKS.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
