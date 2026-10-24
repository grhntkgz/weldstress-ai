from pathlib import Path
import json,hashlib,shutil,datetime,csv
import numpy as np,pandas as pd
from scipy.spatial import cKDTree
from geometry_rule import transition_segments,distance_to_segments
from metric_contract import quantile
D=Path(__file__).resolve().parents[1];O=D.parent;R=O/'WeldStressAI_FinalResearch_PhaseR8E16';P=O/'WeldStressAI_ManuscriptRevision_R2';H=O/'WeldStressAI_PlateHeldOutAI_PhaseR8E13';J=O/'WeldStressAI_ContextRobustness_PhaseR8E14';K=O/'WeldStressAI_InferenceMechanisms_PhaseR8E15'
assert not (D/'R2_1_PROTOCOL_SEAL.json').exists(),'Already sealed; do not silently overwrite protocol'
for n in ['qa','source_snapshot','geometry_only','figures/main','figures/supplementary','tmp']:(D/n).mkdir(parents=True,exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
inputs={};indices={}
def verify(p,root=None,expected=None):
 p=Path(p)
 if expected is None:
  root=Path(root)
  if str(root) not in indices:
   mf=root/'REPRODUCIBILITY_MANIFEST.json';mf=mf if mf.exists() else root/'REVISION_REPRODUCIBILITY_MANIFEST.json';data=json.loads(mf.read_text(encoding='utf-8-sig'));indices[str(root)]={a['path'].replace('\\','/'):a.get('SHA256',a.get('sha256')) for a in data['files']}
  expected=indices[str(root)].get(p.relative_to(root).as_posix())
 assert expected is not None,('Missing source hash',str(p));actual=sha(p);assert actual==expected,('Hash mismatch',str(p));inputs[str(p)]=dict(path=str(p),SHA256=actual,status='PASS');return p
release=[]
for root,mf in [(R,'REPRODUCIBILITY_MANIFEST.json'),(O/'WeldStressAI_ManuscriptRevision_R1','REVISION_REPRODUCIBILITY_MANIFEST.json'),(P,'REPRODUCIBILITY_MANIFEST.json')]:
 data=json.loads((root/mf).read_text());rows=[]
 for a in data['files']:
  p=root/a['path'];actual=sha(p);assert actual==a['SHA256'];rows.append(dict(path=str(p),SHA256=actual,status='PASS'))
 pd.DataFrame(rows).to_csv(D/'qa'/(root.name+'_FULL_INTEGRITY.csv'),index=False);release.append(dict(workspace=str(root),files=len(rows),manifest_SHA256=sha(root/mf),status='PASS'));print('HISTORICAL_RELEASE_VERIFIED',root.name,len(rows),flush=True)
for name in ['MANUSCRIPT_REVISION_R2.md','R2_ENGINEERING_REVIEW_REPORT.md','R2_BOUNDARY_CONDITION_INTERPRETATION.md','R2_WELD_TOE_EVIDENCE_CLASSIFICATION.md','R2_GEOMETRY_STRESS_SPATIAL_AUDIT.csv','ACTUAL_NATIVE_MESH_BOUNDARIES.csv','NATIVE_BOUNDARY_SPATIAL_REGISTRY.csv','R2_PLATE_HIGH95_COMPARISON.csv','SPATIAL_LABEL_EVIDENCE_REGISTRY.csv']:
 p=verify(P/name,P);shutil.copy2(p,D/'source_snapshot'/name)
shutil.copy2(Path(r'C:\Users\grhnt.DESKTOP-KRBB26F\.codex\attachments\d20bee3b-7c07-429d-83cc-917e7f520be5\Pasted text.txt'),D/'source_snapshot'/'R2_1_USER_SPECIFICATION.txt')
for name in ['SOURCE_LEVEL_METRICS.csv','PLATE_LEVEL_METRICS.csv','MODEL_PREDICTION_REGISTRY.csv','QUALIFIED13_SOURCE_REGISTRY.csv','METRIC_DEFINITIONS.json','DOCUMENTED_PLATE_GROUPS.csv','FROZEN_LOPO_SPLITS.csv']:
 p=verify(R/name,R);shutil.copy2(p,D/'source_snapshot'/name)
reg=pd.read_csv(R/'QUALIFIED13_SOURCE_REGISTRY.csv');pred=pd.read_csv(R/'MODEL_PREDICTION_REGISTRY.csv',keep_default_na=False);old=pd.read_csv(R/'SOURCE_LEVEL_METRICS.csv',keep_default_na=False)
assert len(reg)==13 and set(reg.source_id.str[0])==set('CEGHX');assert len(pred)==299
windows=pd.read_csv(verify(J/'OBSERVATION_WINDOW_COORDINATES.csv',J));shutil.copy2(J/'OBSERVATION_WINDOW_COORDINATES.csv',D/'source_snapshot'/'OBSERVATION_WINDOW_COORDINATES.csv')
verify(J/'src'/'seal_protocol_e14.py',J);verify(J/'src'/'context_e14.py',J);verify(R/'src'/'features_e16.py',R)
source_records=[];baseline_audit=[];historical=[];ownership=[]
for _,r in reg.iterrows():
 sid=r.source_id;gp=verify(H/'02_geometry'/(sid+'.npz'),H);tp=verify(H/'01_dataset/targets'/(sid+'.npz'),H);verify(Path(r.qualified_M2_target_path),expected=r.qualified_M2_target_SHA256)
 g=dict(np.load(gp));t=dict(np.load(tp));fine=dict(np.load(r.qualified_M2_target_path));mask=t['core']&t['valid'];q=np.flatnonzero(mask);ids=g['source_ids'][mask];x=g['xyz'];w=t['area'][mask];y=t['T2_MPa'][mask]
 assert len(q)==34200
 for key in ['source_ids','xyz','area']:assert np.array_equal(g[key],t[key]) and np.array_equal(t[key],fine[key])
 assert np.array_equal(t['T2_MPa'],fine['T2_MPa'],equal_nan=True)
 tri=g['triangles'];xx=x[tri];ta=np.linalg.norm(np.cross(xx[:,1]-xx[:,0],xx[:,2]-xx[:,0]),axis=1)/2;areas=np.bincount(tri.ravel(),weights=np.repeat(ta/3,3),minlength=len(x));assert abs(areas-g['area']).max()<1e-10
 datum=json.loads(r.parent_datum);height=(x[:,2]-datum['intercept_Z_mm']-datum['slope_X']*(x[:,0]-datum['origin_X_mm'])-datum['slope_Y']*(x[:,1]-datum['origin_Y_mm']))/np.sqrt(1+datum['slope_X']**2+datum['slope_Y']**2)
 heightmask=height>=.5;distance=cKDTree(x[heightmask,:2]).query(x[:,:2])[0];labels=np.where(heightmask,1,np.where(distance<=2,2,0));assert np.array_equal(labels,t['region'])
 seg,diagnostic=transition_segments(x,tri,height)
 if seg is not None:
  score=-distance_to_segments(x[:,:2],seg);np.savez_compressed(D/'geometry_only'/(sid+'.npz'),source_ids=g['source_ids'],score=score,segments_XY=seg)
 baseline_audit.append(dict(source_id=sid,**diagnostic,score_inputs='original XYZ, triangles and frozen parent-plane relief only',FE_stress_used=False,predictions_used=False))
 supportp=verify(J/'03_source_geometry'/(sid+'_SUPPORT.npz'),J);ksupport=verify(K/'02_source_geometry'/sid/'CORE.npz',K);sup=dict(np.load(supportp));ks=dict(np.load(ksupport));assert np.array_equal(sup['source_ids'],g['source_ids']);assert np.array_equal(ks['query_original_rows'],q);assert np.array_equal(ks['tile_id'],sup['tile_id'][q]);assert np.array_equal(ks['source_ids'],ids)
 for cond in ['X50','X43']:
  for tile in np.unique(ks['tile_id']):
   wr=windows[(windows.source_id==sid)&(windows.condition==cond)&(windows.tile==tile)].iloc[0];idf=verify(J/'07_context_geometry'/sid/(cond+'_'+str(tile)+'_IDS.npy'),J);cidf=verify(J/'07_context_geometry'/sid/(cond+'_'+str(tile)+'_CONTEXT_IDS.npy'),J);visible=np.load(idf);context=np.load(cidf);v=(x[:,0]>=wr.declared_X_min-1e-8)&(x[:,0]<=wr.declared_X_max+1e-8);assert np.array_equal(visible,g['source_ids'][v]);assert np.isin(ids[ks['tile_id']==tile],visible).all();assert len(np.unique(context))==4096 and np.isin(context,visible).all();ownership.append(dict(source_id=sid,condition=cond,tile=tile,queries=int((ks['tile_id']==tile).sum()),exact_visible_IDS=True,core_ownership_unchanged=True,context_unique=4096))
 for _,pr in pred[pred.source_id==sid].iterrows():
  pp=verify(Path(pr.path),expected=pr.SHA256);a=dict(np.load(pp));take=q if len(a['source_ids'])==len(x) else np.arange(len(q));assert np.array_equal(a['source_ids'][take],ids)
  for k in ['xyz','area']:assert np.array_equal(a[k][take],t[k][mask])
  if 'query_original_rows' in a:assert np.array_equal(a['query_original_rows'],q)
  if 'valid' in a:assert a['valid'][take].all()
  if 'tile_count' in a:assert np.all(a['tile_count'][take]==1)
  p=a['pred_MPa'][take];assert np.isfinite(p).all();hy=y>=quantile(y,w,.95);hp=p>=quantile(p,w,.95);iou=float(w[hy&hp].sum()/w[hy|hp].sum());o=old[(old.source_id==sid)&(old.model==pr.model)&(old.condition==pr.condition)]
  if len(o)>1:o=o[o.seed.astype(str)==str(pr.seed)]
  assert len(o)==1;err=abs(iou-float(o.iloc[0].high95_IoU));assert err<1e-12
  historical.append(dict(source_id=sid,model=pr.model,condition=pr.condition,seed=str(pr.seed),IoU_error=err,status='PASS'))
 source_records.append(dict(source_id=sid,plate=sid[0],geometry_path=str(gp),target_path=str(tp),qualified_target_path=r.qualified_M2_target_path,query_points=len(q),original_points=len(x),triangles=len(tri),datum_json=r.parent_datum,region_rule_verified=True,geometry_boundary_status=diagnostic['status'],E14_support_path=str(supportp),E15_core_path=str(ksupport),source_X_min=float(x[:,0].min()),source_X_max=float(x[:,0].max())))
 print('SOURCE_AND_HISTORICAL_FIELDS_VERIFIED',sid,'geometry boundary',diagnostic,flush=True)
pd.DataFrame(source_records).to_csv(D/'R2_1_SOURCE_REGISTRY.csv',index=False);pd.DataFrame(historical).to_csv(D/'qa'/'HISTORICAL_HIGH95_RECOVERY.csv',index=False);pd.DataFrame(ownership).to_csv(D/'qa'/'ORIGINAL_OBSERVATION_OWNERSHIP_AUDIT.csv',index=False);pd.DataFrame(baseline_audit).to_csv(D/'qa'/'GEOMETRY_BOUNDARY_FEASIBILITY.csv',index=False)
contracts={
'R2_1_THRESHOLD_CONTRACT.json':dict(budgets=[.01,.05,.10],rank='Descending value, original int64 point ID ascending at exact ties; choose closest cumulative-area prefix to requested quota, include crossing point if equally close; whole vertices only',area_weights='original T0',historical_control='stable ascending value sort, np.interp(q,cumsum(w)/sum(w),values), own-field >=; only q=.95, unchanged historical metric',common_reference_threshold='same interpolated FE threshold q=.99/.95/.90 applied >= to reference and saved prediction; REFERENCE_THRESHOLD_DIAGNOSTIC_ONLY',no_fixed_MPa_threshold=True,constant_score='rank budget uses arbitrary original-ID tie priority; report as uninformative constant ranking; historical constant all-high unchanged',empty_prediction='precision and centroid undefined (NaN), IoU=0 and recall=0 when reference nonempty',tie_sensitivity='report achieved area, cut score, tie population/split; compare primary rank at 5% to unchanged historical High95; no performance-selected thresholds'),
'R2_1_GEOMETRY_BASELINE_CONTRACT.json':dict(G0='Original region code 2, broad collar, unequal area budget; report core fraction, capture, enrichment, IoU/precision/recall/FN/FP',G1='negative exact minimum XY point-to-segment distance to piecewise-linear parent-normal relief=0.5 mm contour on original triangles; score construction has no stress/prediction input',segments='All mixed-height triangles; linearly interpolate crossed edges, deduplicate intersections <=1e-10 mm; segments length>1e-10 mm; all connected/disconnected components retained; no domain-edge closure, smoothing or component tuning',missing='NOT_EVALUABLE if no contour, nonfinite segments or ambiguous coplanar triangles; no substitute scoring rule',rank='same sealed 1/5/10% area quota rule as neural fields',direct_comparison='FULL only, geometry support FULL, model seed metrics retained then averaged',restricted='NOT_EVALUABLE as a fair operational comparator. Frozen parent plane and original region labels were estimated from full source; no previously qualified strictly visible parent-plane/label rule exists. Do not introduce a replacement fit or reveal full-source labels as restricted inputs. All 34200 restricted queries are unqualified for this comparator, not asserted geometrically absent. No restricted score/result is substituted.',no_stress_amplitude=True,no_L2_for_geometry_masks=True),
'R2_1_REGIONAL_METRIC_CONTRACT.json':dict(regions={'PARENT':0,'HEIGHT_REGION':1,'COLLAR':2},metrics=['MAE_MPa','RMSE_MPa','bias_MPa','absolute_error_Q95_MPa','area_mm2','area_fraction','reference_mean_MPa','reference_Q95_MPa','L2','SSE_share','SAE_share','globally_normalized_SSE_contribution'],unstable_norm='regional reference RMS <=1e-6 MPa gives L2 undefined; empty region undefined errors',boundary_strata='nonexclusive within 1 mm of core X edge, core Y edge, native loaded X cap, native gauge in 3D, or actual owning observation-window X edge; each retains independent label; no causal attribution',aggregation='source first; arithmetic sources within documentary plate; equal five plates; mean separately scored neural seeds. B0/B1/B2 single fixed fit evaluated once; no seed replication.',nulls='NaN means undefined/not available, never zero; report valid group count',no_population_CI=True),
}
for name,value in contracts.items():(D/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
protocol='''# R2.1 retrospective analysis protocol

The three JSON contracts define all algorithms, thresholds, geometry rules, empty-set conventions and weighting. All thirteen accepted sources, five documentary plates and both neural seeds remain fixed. N1/N2/N3 and available B0/B1/B2 saved fields are read without model execution. Original point arrays, T0 weights, labels and ownership remain unchanged. Every R2.1 finding is retrospective exploratory, not independent external validation or original-phase preregistration.

Geometry baseline comparison is deliberately limited to FULL: its full-source fitted parent plane is not an established visible-only input contract. Restricted-view comparator rows must be marked NOT_EVALUABLE, with the information restriction explicit. No alternative plane fit, scoring formula, distance bandwidth or component selection is authorized after seeing metrics. Geometry baselines produce localization scores/masks only, never MPa or L2.

Interpretation is descriptive. Any positive N3−N2 IoU contrast is favorable for that cell; any negative contrast is unfavorable. A claim of uniform robustness requires favorable mean contrasts at all three budgets/contexts and all five plates; mixed plate/budget signs require a mixed conclusion, with both seeds shown. Neural value over G1 requires matched FULL area budgets, and must be qualified by every plate and threshold. No significance threshold or selection is added. Original METHOD_IMPROVEMENT_MIXED is preserved independently of new results.

Plots A show all neural models, budgets, contexts, plates and seed values; B uses FULL masks on actual G07/X10/X23 coordinates; C shows all plates and three frozen regions; D retains actual critical-source FE/N2/N3 fields, centered errors, geometry proxies and separate core/observation/native boundaries. Common within-comparison stress limits are mandatory. No physical toe or crack label is introduced. Detailed source figures are supplementary, and main figures are chosen for explanation without dropping unfavorable cases.

Execution after seal: resource gate; rank budgets and historical control; common FE-threshold diagnostics; G0 and fixed G1; region/boundary errors; independent checking implementation; plots; manuscript revision from immutable R2; complete DOCX render/visual QA; hash/package closeout. No ANSYS, mesh, target, fitting, training, inference, new context, seed, source or model selection is authorized. The program closes after this bounded assessment.
'''
(D/'R2_1_ANALYSIS_PROTOCOL.md').write_text(protocol,encoding='utf-8');(D/'R2_1_INPUT_HASHES.json').write_text(json.dumps(dict(files=list(inputs.values()),original_releases=release),indent=2),encoding='utf-8')
sealed=[D/n for n in contracts]+[D/'R2_1_ANALYSIS_PROTOCOL.md',D/'R2_1_SOURCE_REGISTRY.csv',D/'R2_1_INPUT_HASHES.json',D/'src'/'geometry_rule.py',D/'src'/'metric_contract.py']+list((D/'geometry_only').glob('*.npz'))
seal=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='SEALED_BEFORE_R2_1_METRICS',historical_fields_verified=len(historical),historical_high95_max_error=max(a['IoU_error'] for a in historical),new_results_inspected=False,files=[dict(path=p.relative_to(D).as_posix(),SHA256=sha(p)) for p in sealed]);(D/'R2_1_PROTOCOL_SEAL.json').write_text(json.dumps(seal,indent=2))
print('PROTOCOL_SEALED',seal['UTC'],'inputs',len(inputs),'historical fields',len(historical),flush=True)
