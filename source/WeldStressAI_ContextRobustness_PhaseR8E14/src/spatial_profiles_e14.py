from common_e14 import *
import numpy as np,pandas as pd
def main():
 registry=rows(R/'20_reproducibility/PREDICTION_REGISTRY.csv');profiles=[];jumps=[];admissibility=[]
 for a in registry:
  sid=a['source_id'];d=dict(np.load(H/'01_dataset/targets'/(sid+'.npz')));p=dict(np.load(a['path']));q=p['query_original_rows'];x=p['xyz'];v=p['pred_MPa'];y=d['T2_MPa'][q];w=p['area'];base={k:a[k] for k in ['model','seed','condition','source_id','plate']};middle=(d['xyz'][:,1].min()+d['xyz'][:,1].max())/2
  admissibility.append(dict(**base,prediction_min_MPa=float(v.min()),prediction_max_MPa=float(v.max()),negative_prediction_area_mm2=float(w[v<0].sum()),negative_prediction_area_fraction=float(w[v<0].sum()/w.sum()),prediction_clipped=False,physical_validation=False))
  for name,axis,mask in [('longitudinal_Y_area_mean',1,np.ones(len(x),bool)),('transverse_X_central_Y_plusminus_0p5mm',0,abs(x[:,1]-middle)<=.5)]:
   values,group=np.unique(x[mask,axis],return_inverse=True);ww=w[mask];den=np.bincount(group,weights=ww);count=np.bincount(group);ref=np.bincount(group,weights=ww*y[mask])/den;prediction=np.bincount(group,weights=ww*v[mask])/den;bias=np.bincount(group,weights=ww*(v[mask]-y[mask]))/den;mae=np.bincount(group,weights=ww*abs(v[mask]-y[mask]))/den
   for j,value in enumerate(values):profiles.append(dict(**base,profile=name,coordinate_mm=float(value),points=int(count[j]),area_mm2=float(den[j]),reference_mean_MPa=float(ref[j]),prediction_mean_MPa=float(prediction[j]),signed_bias_MPa=float(bias[j]),MAE_MPa=float(mae[j])))
  ux,xi=np.unique(x[:,0],return_inverse=True);uy,yi=np.unique(x[:,1],return_inverse=True);support=dict(np.load(R/'03_source_geometry'/(sid+'_SUPPORT.npz')))
  if len(ux)*len(uy)==len(x):
   mat=np.full((len(uy),len(ux)),-1,dtype='i8');mat[yi,xi]=np.arange(len(x));tile=support['tile_id'][q];line=tile[mat[0]]
   for j in np.flatnonzero(line[:-1]!=line[1:]):
    left=mat[:,j];right=mat[:,j+1];pj=abs(v[right]-v[left]);rj=abs(y[right]-y[left]);jumps.append(dict(**base,boundary_X_mm=float((ux[j]+ux[j+1])/2),physical_X_step_mm=float(ux[j+1]-ux[j]),matched_Y_pairs=len(left),mean_absolute_prediction_jump_MPa=float(pj.mean()),maximum_prediction_jump_MPa=float(pj.max()),mean_absolute_reference_jump_MPa=float(rj.mean()),excess_mean_absolute_jump_MPa=float(pj.mean()-rj.mean()),finding='STITCH_REPRESENTATION_DIAGNOSTIC; not a physical surface discontinuity'))
 table(R/'05_spatial_error_baseline/ALL_CONTEXT_PROFILE_ERRORS.csv',profiles);table(R/'09_context_sensitivity/TILE_STITCH_JUMP_DIAGNOSTICS.csv',jumps);table(R/'09_context_sensitivity/UNCONSTRAINED_OUTPUT_DIAGNOSTICS.csv',admissibility)
 from deliver_e14 import mdtable
 summary=pd.DataFrame(jumps).groupby(['model','condition'])[['mean_absolute_prediction_jump_MPa','mean_absolute_reference_jump_MPa','excess_mean_absolute_jump_MPa']].mean().reset_index();text='\n\n## Geometric query-tile stitching diagnostic\n\nThe following are descriptive source/seed/boundary means of adjacent original X samples at matched Y rows. An excess predicted jump over the unchanged reference jump identifies a representation/stitching effect; it is not a new physical edge or a proof of a stress singularity. Primary field scores remain unchanged. All longitudinal Y means and central-Y transverse profiles are exported for every source/seed/context.\n\n'+mdtable(summary)
 for name in ['R8E14_MASTER_REPORT.md','SPATIAL_STRESS_ERROR_PATTERNS.md','CONTEXT_ROBUSTNESS_METRICS.md']:
  p=R/name;p.write_text(p.read_text(encoding='utf8')+text,encoding='utf8')
 print('SPATIAL_PROFILES_AND_STITCH_DIAGNOSTICS_COMPLETE',len(profiles),len(jumps),flush=True)
if __name__=='__main__':main()
