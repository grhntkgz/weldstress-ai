"""Retrospective diagnostics of frozen arrays only. No fitting, inference or FE execution."""
from pathlib import Path
import json,hashlib,csv,shutil,zipfile
import numpy as np,pandas as pd
from scipy.spatial import cKDTree
D=Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRevision_R2');O=D.parent;R=O/'WeldStressAI_FinalResearch_PhaseR8E16';H=O/'WeldStressAI_PlateHeldOutAI_PhaseR8E13';P=O/'WeldStressAI_ManuscriptRevision_R1'
reg=pd.read_csv(R/'QUALIFIED13_SOURCE_REGISTRY.csv');predreg=pd.read_csv(R/'MODEL_PREDICTION_REGISTRY.csv',keep_default_na=False);released=pd.read_csv(R/'SOURCE_LEVEL_METRICS.csv',keep_default_na=False)
cache={};consumed={};checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def index(root):
 root=Path(root)
 if str(root) not in cache:
  file=root/'REPRODUCIBILITY_MANIFEST.json'
  if file.exists():entries=json.loads(file.read_text())['files']
  else:entries=pd.read_csv(root/'REPRODUCIBILITY_MANIFEST.csv').to_dict('records')
  cache[str(root)]={r['path'].replace('\\','/'):r.get('SHA256',r.get('sha256',r.get('hash'))) for r in entries}
 return cache[str(root)]
def verify(p,root=None,expected=None,copy=False):
 p=Path(p);h=sha(p)
 if expected is None and root is not None:expected=index(root).get(p.relative_to(root).as_posix())
 assert expected is not None,('Missing original manifest entry',str(p));assert h==expected,('Hash mismatch',str(p))
 consumed[str(p)]=dict(path=str(p),SHA256=h,status='PASS')
 if copy:
  rel=p.relative_to(O) if p.is_relative_to(O) else Path('original_project')/p.name;dest=D/'source_snapshot'/'spatial_records'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 return p
def quant(v,w):
 order=np.argsort(v,kind='stable');return float(np.interp(.95,np.cumsum(w[order])/w.sum(),v[order]))
def metric(y,p,w,x):
 qy=quant(y,w);qp=quant(p,w);hy=y>=qy;hp=p>=qp;inter=w[hy&hp].sum();cp=np.average(x[hp],axis=0,weights=w[hp]);cy=np.average(x[hy],axis=0,weights=w[hy]);e=p-y
 return dict(L2=float(np.sqrt(np.sum(w*e**2)/np.sum(w*y**2))),MAE_MPa=float(w@abs(e)/w.sum()),high95_IoU=float(inter/w[hy|hp].sum()),false_negative_area_mm2=float(w[hy&~hp].sum()),false_positive_area_mm2=float(w[hp&~hy].sum()),high95_precision=float(inter/w[hp].sum()),high95_recall=float(inter/w[hy].sum()),absolute_max_error_MPa=abs(float(p.max()-y.max())),absolute_Q95_error_MPa=abs(qp-qy),max_error_MPa=float(p.max()-y.max()),Q95_error_MPa=qp-qy,pred_max_MPa=float(p.max()),ref_max_MPa=float(y.max()),pred_Q95_MPa=qp,ref_Q95_MPa=qy,reference_high_area_mm2=float(w[hy].sum()),predicted_high_area_mm2=float(w[hp].sum()),high95_centroid_distance_mm=float(np.linalg.norm(cp-cy)),centroid_error_X_mm=float(cp[0]-cy[0]),centroid_error_Y_mm=float(cp[1]-cy[1]),centroid_error_Z_mm=float(cp[2]-cy[2]))
scores=[];spatial=[];regions=[];boundary=[];sourceinfo={};critical=[];masks=[]
for _,r in reg.iterrows():
 sid=r.source_id;gf=verify(H/'02_geometry'/(sid+'.npz'),H);tf=verify(H/'01_dataset/targets'/(sid+'.npz'),H);verify(Path(r.qualified_M2_target_path),expected=r.qualified_M2_target_SHA256)
 g=dict(np.load(gf));t=dict(np.load(tf));fine=dict(np.load(r.qualified_M2_target_path))
 assert all(np.array_equal(g[k],t[k]) and np.array_equal(t[k],fine[k]) for k in ['source_ids','xyz','area'])
 assert np.array_equal(t['T2_MPa'],fine['T2_MPa'],equal_nan=True);assert np.array_equal(t['region'],fine['region']);assert np.array_equal(t['core'],fine['core'])
 core=t['core']&t['valid'];assert core.sum()==34200;assert len(np.unique(g['source_ids']))==len(g['source_ids'])
 x=t['xyz'][core];y=t['T2_MPa'][core];w=t['area'][core];rr=t['region'][core];hy=y>=quant(y,w);xyz=g['xyz'];tri=g['triangles'];assert tri.min()>=0 and tri.max()<len(xyz)
 # Reconstruct original lumped T0 areas without modifying geometry or labels.
 tv=xyz[tri].astype(float);ta=np.linalg.norm(np.cross(tv[:,1]-tv[:,0],tv[:,2]-tv[:,0]),axis=1)/2;areas=np.zeros(len(xyz))
 for j in range(3):np.add.at(areas,tri[:,j],ta/3)
 aerr=float(abs(areas-g['area']).max());assert aerr<1e-10,(sid,aerr)
 datum=json.loads(r.parent_datum);norm=np.sqrt(1+datum['slope_X']**2+datum['slope_Y']**2);height=(xyz[:,2]-datum['intercept_Z_mm']-datum['slope_X']*(xyz[:,0]-datum['origin_X_mm'])-datum['slope_Y']*(xyz[:,1]-datum['origin_Y_mm']))/norm
 weld=height>=.5;distance=cKDTree(xyz[weld,:2]).query(xyz[:,:2])[0];proxy=np.where(weld,1,np.where(distance<=2,2,0)).astype('i1');proxy_mismatch=int(np.count_nonzero(proxy!=t['region']))
 case=Path(r.qualified_M2_target_path).parent.parent;root=Path(r.release_workspace);bvpfile=case/'02_mesh_import'/'M2'/'BVP_ASSEMBLY.json';gaugefile=case/'02_mesh_import'/'M2'/'GAUGE_CONSTRAINT_REGISTRY.csv'
 verify(bvpfile,root,copy=True);verify(gaugefile,root,copy=True);bvp=json.loads(bvpfile.read_text());gauges=pd.read_csv(gaugefile);assert len(gauges)==6;gxyz=gauges[['X','Y','Z']].drop_duplicates().to_numpy();assert len(gxyz)==3
 xmin=float(xyz[:,0].min());xmax=float(xyz[:,0].max());ymin=float(xyz[:,1].min());ymax=float(xyz[:,1].max());ports=np.array([gxyz[:,0].mean(),gxyz[:,0].mean()+60]);portdist=np.minimum(abs(x[:,0]-ports[0]),abs(x[:,0]-ports[1]));coredist=np.minimum(x[:,0]-x[:,0].min(),x[:,0].max()-x[:,0]);gdist=cKDTree(gxyz).query(x)[0];slope=np.linalg.norm(g['normal'][:,:2],axis=1)/np.maximum(abs(g['normal'][:,2]),1e-12)
 # Compare the documented source bounds to actual M2 cap geometry recorded in its port registry.
 portfile=case/'02_mesh_import'/'M2'/'PORT_FACE_REGISTRY.csv';verify(portfile,root,copy=True);pr=pd.read_csv(portfile)
 critical.append(dict(source_id=sid,original_XYZ_ID_area_exact=True,T2_exact_qualified_package=True,triangle_area_max_error_mm2=aerr,region_reconstruction_mismatches=proxy_mismatch,core_points=int(core.sum()),native_BVP_path=str(bvpfile),gauge_path=str(gaugefile),port_registry_path=str(portfile)))
 for code,name in [(0,'parent_proxy'),(1,'weld_relief_proxy'),(2,'collar_proxy')]:
  z=rr==code;regions.append(dict(source_id=sid,plate=sid[0],region=code,region_name=name,region_area_mm2=float(w[z].sum()),reference_high95_area_mm2=float(w[z&hy].sum()),fraction_reference_high95=float(w[z&hy].sum()/w[hy].sum()),definition='EXISTING_GEOMETRY_DERIVED_PROXY',retrospective=True))
 spatial.append(dict(source_id=sid,plate=sid[0],original_points=len(xyz),triangles=len(tri),evaluation_points=len(x),load_axis='canonical X',weld_longitudinal_axis='retained profile Y convention; physical frame calibration unresolved',source_X_min_mm=xmin,source_X_max_mm=xmax,source_Y_min_mm=ymin,source_Y_max_mm=ymax,core_X_min_mm=float(x[:,0].min()),core_X_max_mm=float(x[:,0].max()),core_Y_min_mm=float(x[:,1].min()),core_Y_max_mm=float(x[:,1].max()),high95_X_min_mm=float(x[hy,0].min()),high95_X_max_mm=float(x[hy,0].max()),high95_Y_min_mm=float(x[hy,1].min()),high95_Y_max_mm=float(x[hy,1].max()),High95_threshold_MPa=quant(y,w),High95_area_mm2=float(w[hy].sum()),high95_parent_fraction=float(w[hy&(rr==0)].sum()/w[hy].sum()),high95_weld_fraction=float(w[hy&(rr==1)].sum()/w[hy].sum()),high95_collar_fraction=float(w[hy&(rr==2)].sum()/w[hy].sum()),high95_min_X_port_distance_mm=float(portdist[hy].min()),high95_min_gauge_distance_mm=float(gdist[hy].min()),high95_min_core_X_edge_distance_mm=float(coredist[hy].min()),high95_fraction_within_1mm_core_X_edge=float(w[hy&(coredist<=1+1e-7)].sum()/w[hy].sum()),high95_fraction_within_1mm_loaded_X_port=float(w[hy&(portdist<=1+1e-7)].sum()/w[hy].sum()),high95_mean_parent_normal_height_mm=float(np.average(height[core][hy],weights=w[hy])),high95_mean_surface_slope=float(np.average(slope[core][hy],weights=w[hy])),remainder_mean_surface_slope=float(np.average(slope[core][~hy],weights=w[~hy])),documented_measured_toe_trajectory='NOT_AVAILABLE_FOR_QUALIFIED_FRAME',region_label_class='EXISTING_GEOMETRY_DERIVED_PROXY',engineering_classification='MIXED_OR_UNRESOLVED_ASSOCIATION',retrospective=True))
 boundary.append(dict(source_id=sid,left_port_X_mm=float(ports[0]),right_port_X_mm=float(ports[1]),gauges=json.dumps(gauges[['node','dof','X','Y','Z']].to_dict('records')),force_N=bvp['force_N'],loadline=json.dumps(bvp['loadline_origin']),ports=json.dumps(bvp['ports']),boundary_source=str(bvpfile),direct_High95_overlap_loaded_port=False,retrospective=True))
 sourceinfo[sid]=dict(geometry_path=str(gf),target_path=str(tf),case=str(case),root=str(root),bvp_path=str(bvpfile),gauge_path=str(gaugefile),datum=datum)
 for _,p in predreg[(predreg.source_id==sid)&predreg.model.isin(['N2','N3'])].iterrows():
  verify(Path(p.path),expected=p.SHA256);field=dict(np.load(p.path));assert all(np.array_equal(field[k],t[k][core]) for k in ['source_ids','xyz','area']);v=field['pred_MPa'];met=metric(y,v,w,x);key=dict(model=p.model,source_id=sid,plate=sid[0],seed=int(p.seed),condition=p.condition)
  baseline=released[(released.model==p.model)&(released.source_id==sid)&(released.seed.astype(str)==str(p.seed))&(released.condition==p.condition)];assert len(baseline)==1
  for name in ['L2','MAE_MPa','high95_IoU','false_negative_area_mm2','false_positive_area_mm2','high95_precision','high95_recall','absolute_max_error_MPa','absolute_Q95_error_MPa','high95_centroid_distance_mm']:
   err=abs(met[name]-float(baseline.iloc[0][name]));assert err<1e-9,(sid,name,err);checks.append(dict(**key,metric=name,error=err,status='PASS'))
  scores.append(dict(**key,**met,retrospective=True));hp=v>=met['pred_Q95_MPa'];masks.append(dict(**key,reference_threshold_MPa=met['ref_Q95_MPa'],prediction_threshold_MPa=met['pred_Q95_MPa'],reference_mask_SHA256=hashlib.sha256(hy.tobytes()).hexdigest(),prediction_mask_SHA256=hashlib.sha256(hp.tobytes()).hexdigest(),points=len(hp)))
 print('FROZEN_SOURCE_AUDITED',sid,'high95_region_fractions',[spatial[-1][k] for k in ['high95_parent_fraction','high95_weld_fraction','high95_collar_fraction']],'proxy_mismatch',proxy_mismatch,flush=True)
frame=pd.DataFrame(scores);metrics=[c for c in frame if c not in ['model','source_id','plate','seed','condition','retrospective']]
def paired(data,keys):
 n2=data[data.model=='N2'].drop(columns='model');n3=data[data.model=='N3'].drop(columns='model');z=n2.merge(n3,on=keys,suffixes=('_N2','_N3'),validate='one_to_one')
 for m in metrics:z['delta_'+m]=z[m+'_N3']-z[m+'_N2']
 z['retrospective']=True;return z
frame.to_csv(D/'SEED_SPECIFIC_LOCALIZATION_RESULTS.csv',index=False)
source_mean=frame.groupby(['model','source_id','plate','condition'],as_index=False)[metrics].mean();source_pair=paired(source_mean,['source_id','plate','condition']);source_pair.to_csv(D/'SOURCE_LEVEL_HIGH95_REAUDIT.csv',index=False);source_pair.to_csv(D/'R2_SOURCE_HIGH95_COMPARISON.csv',index=False)
plate_seed=frame.groupby(['model','seed','plate','condition'],as_index=False)[metrics].mean();plate_seed.to_csv(D/'PLATE_SEED_LOCALIZATION_RESULTS.csv',index=False);paired(plate_seed,['seed','plate','condition']).to_csv(D/'PLATE_SEED_PAIRED_CONTRASTS.csv',index=False)
plate_mean=plate_seed.groupby(['model','plate','condition'],as_index=False)[metrics].mean();plate_pair=paired(plate_mean,['plate','condition']);plate_pair.to_csv(D/'PLATE_LEVEL_HIGH95_REAUDIT.csv',index=False);plate_pair.to_csv(D/'R2_PLATE_HIGH95_COMPARISON.csv',index=False)
pd.DataFrame(spatial).to_csv(D/'R2_GEOMETRY_STRESS_SPATIAL_AUDIT.csv',index=False);pd.DataFrame(regions).to_csv(D/'REFERENCE_HIGH95_BY_EXISTING_REGION.csv',index=False);pd.DataFrame(boundary).to_csv(D/'NATIVE_BOUNDARY_SPATIAL_REGISTRY.csv',index=False);pd.DataFrame(critical).to_csv(D/'qa'/'ORIGINAL_SUPPORT_ALIGNMENT.csv',index=False);pd.DataFrame(checks).to_csv(D/'qa'/'FROZEN_FIELD_METRIC_REPLAY.csv',index=False);pd.DataFrame(masks).to_csv(D/'ORIGINAL_HIGH95_THRESHOLDS_AND_MASK_HASHES.csv',index=False);pd.DataFrame(list(consumed.values())).to_csv(D/'qa'/'CONSUMED_SPATIAL_INPUT_HASHES.csv',index=False);(D/'qa'/'SOURCE_SPATIAL_INPUTS.json').write_text(json.dumps(sourceinfo,indent=2))
print('X_PLATE',plate_pair[plate_pair.plate=='X'][['condition','delta_L2','delta_high95_IoU','delta_false_negative_area_mm2','delta_false_positive_area_mm2']].to_json(orient='records'))
