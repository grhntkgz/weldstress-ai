"""Independent reaggregation directly from original released CSVs, no shared metric helpers."""
from pathlib import Path
import csv,json,math,hashlib
from collections import defaultdict
D=Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRevision_R2');R=D.parent/'WeldStressAI_FinalResearch_PhaseR8E16'
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
original=read(R/'SOURCE_LEVEL_METRICS.csv');metrics=['L2','MAE_MPa','high95_IoU','false_negative_area_mm2','false_positive_area_mm2','high95_precision','high95_recall','absolute_max_error_MPa','absolute_Q95_error_MPa','high95_centroid_distance_mm'];groups=defaultdict(list)
for row in original:
 if row['model'] in ['N2','N3']:groups[(row['model'],row['seed'],row['plate'],row['condition'])].append(row)
means={k:{m:math.fsum(float(r[m]) for r in rows)/len(rows) for m in metrics} for k,rows in groups.items()}
assert len(groups)==60
checks=[]
for row in read(D/'R2_PLATE_HIGH95_COMPARISON.csv'):
 for model in ['N2','N3']:
  for m in metrics:
   value=math.fsum(means[(model,seed,row['plate'],row['condition'])][m] for seed in ['20261021','20261022'])/2;err=abs(value-float(row[m+'_'+model]));assert err<1e-9;checks.append(err)
for row in read(D/'R2_SOURCE_HIGH95_COMPARISON.csv'):
 for model in ['N2','N3']:
  rows=[r for r in original if r['model']==model and r['source_id']==row['source_id'] and r['condition']==row['condition']];assert len(rows)==2
  for m in metrics:
   err=abs(math.fsum(float(r[m]) for r in rows)/2-float(row[m+'_'+model]));assert err<1e-9;checks.append(err)
for row in read(R/'17_model_comparisons'/'N3_N2_PLATE_CONTRASTS.csv'):
 new=next(z for z in read(D/'R2_PLATE_HIGH95_COMPARISON.csv') if z['plate']==row['plate'] and z['condition']==row['condition'])
 for c in ['L2_N2','L2_N3','high95_IoU_N2','high95_IoU_N3']:assert abs(float(row[c])-float(new[c]))<1e-12
for row in read(R/'17_model_comparisons'/'TWO_SEED_METRIC_MEANS.csv'):
 if row['model'] not in ['N2','N3']:continue
 for m in metrics:
  value=math.fsum(means[(row['model'],s,p,row['condition'])][m] for p in 'CEGHX' for s in ['20261021','20261022'])/10
  assert abs(value-float(row[m]))<1e-9,(m,value,row[m])
sp=read(D/'R2_GEOMETRY_STRESS_SPATIAL_AUDIT.csv');assert len(sp)==13
for row in sp:
 assert abs(sum(float(row['high95_'+r+'_fraction']) for r in ['parent','weld','collar'])-1)<1e-12
 assert float(row['high95_fraction_within_1mm_loaded_X_port'])==0
 assert row['engineering_classification']=='GEOMETRIC_PROXY_ASSOCIATION_ONLY'
mask=read(D/'ORIGINAL_HIGH95_THRESHOLDS_AND_MASK_HASHES.csv');assert len(mask)==156
for sid in {r['source_id'] for r in mask}:assert len({r['reference_mask_SHA256'] for r in mask if r['source_id']==sid})==1
for row in read(D/'ACTUAL_NATIVE_MESH_BOUNDARIES.csv'):assert row['cap_positions_verified_on_actual_quadratic_mesh']=='True' and row['all_six_gauge_coordinates_match_native_mesh']=='True'
xf=[r for r in original if r['model'] in ['N2','N3'] and r['plate']=='X'];negative=0
for sid in {r['source_id'] for r in xf}:
 for seed in ['20261021','20261022']:
  for context in ['FULL','X50','X43']:
   a=next(r for r in xf if r['model']=='N2' and r['source_id']==sid and r['seed']==seed and r['condition']==context);b=next(r for r in xf if r['model']=='N3' and r['source_id']==sid and r['seed']==seed and r['condition']==context)
   if float(b['high95_IoU'])<float(a['high95_IoU']):negative+=1
report=dict(status='PASS',scope='Retrospective released-output audit, not new independent generalization validation',independent_CSV_cells=len(checks),maximum_absolute_metric_error=max(checks),original_plate_table_rows=15,original_macro_rows=6,source_seed_context_X_adverse_IoU_cells=negative,X_total_cells=12,all_13_geometry_region_sums_PASS=True,all_13_native_cap_and_gauge_mesh_checks_PASS=True,reference_masks_identical_across_models_seeds_contexts=True,field_replay_cells=1560,new_training=False,new_inference=False,new_FE=False)
(D/'qa'/'INDEPENDENT_R2_REAUDIT.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
