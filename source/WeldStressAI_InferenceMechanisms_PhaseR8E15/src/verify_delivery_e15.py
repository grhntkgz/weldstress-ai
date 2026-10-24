from common_e15 import *
import numpy as np,pandas as pd,re,math
from PIL import Image

def main():
 verify_protocol();assert read(R/'18_independent_verification/INDEPENDENT_PASS.json')['passed'];assert read(R/'19_figures/FIGURES_COMPLETE.json')['pairs']==38;spec=(R/'00_historical_integrity/USER_SPECIFICATION.txt').read_text(encoding='utf-8-sig')
 for start,end in [('# 29. REQUIRED REPORTS','# 30.'),('# 30. MACHINE-READABLE DELIVERABLES','# 31.')]:
  for name in re.findall(r'`([^`]+)`',spec.split(start)[1].split(end)[0]):
   if name=='REPRODUCIBILITY_MANIFEST.json':continue
   assert (R/name).is_file(),name
 assert len(re.findall(r'^### \d+\.',(R/'R8E15_MASTER_REPORT.md').read_text(encoding='utf8'),re.M))==60
 raw=rows(R/'21_reproducibility/REPLAY_REGISTRY.csv')+rows(R/'21_reproducibility/INTERVENTION_REGISTRY.csv');outputs=rows(R/'SOURCE_LEVEL_FIELD_METRICS.csv');index={}
 for a in raw:
  assert sha(a['path'])==a['SHA256'];key=(a['source_id'],a['model']+'_'+a['fold']+'_s'+a['seed'],a['condition'],a['variant']);index[key]=a
 for a in outputs:assert sha(a['path'])==a['SHA256']
 receipts=[]
 for filename,kind in [('RAW_CONTEXT_PREDICTIONS.csv','raw'),('RAW_OVERLAP_PREDICTIONS.csv','raw'),('STITCHED_SOURCE_PREDICTIONS.csv','stitched'),('STITCHING_WEIGHTS.csv','weight')]:
  seen={};cache={};count=0
  for frame in pd.read_csv(R/filename,chunksize=200000,float_precision='round_trip',keep_default_na=False):
   columns=['source_id','checkpoint_id','condition','variant' if kind=='raw' else 'policy']
   for key,ss in frame.groupby(columns,sort=False):
    if cache.get('key')!=key:
     sid,checkpoint,condition,policy=key
     if kind=='raw':d=dict(np.load(index[key]['path']))
     elif kind=='stitched':
      a=next(a for a in outputs if a['source_id']==sid and a['model']+'_'+a['fold']+'_s'+a['seed']==checkpoint and a['condition']==condition and a['policy']==policy);d=dict(np.load(a['path']))
     else:
      a=index[(sid,checkpoint,condition,'OVERLAP')];d=dict(np.load(R/'13_stitching_interventions'/(Path(a['path']).stem+'_'+policy+'_WEIGHTS.npz')))
     cache={'key':key,'data':d}
    d=cache['data'];offset=seen.get(key,0);end=offset+len(ss);assert np.array_equal(ss.source_point_id.to_numpy(),d['source_ids'][offset:end]),key
    if kind=='weight':assert np.array_equal(ss.weight.to_numpy(),d['weight'][offset:end]) and np.array_equal(ss.tile_id.to_numpy(),d['tile_id'][offset:end]),key
    else:
     assert np.array_equal(ss.prediction_MPa.to_numpy(),d['pred_MPa'][offset:end]),key
     if kind=='raw':assert np.array_equal(ss.tile_id.to_numpy(),d['tile_id'][offset:end]),key
    seen[key]=end;count+=len(ss)
  expected=read(R/'21_reproducibility/CSV_EXPORT_COUNTS.json')[filename];assert count==expected
  if kind=='raw':assert all(seen[k]==int(index[k]['raw_predictions']) for k in seen)
  elif kind=='stitched':assert all(n==34200 for n in seen.values())
  else:assert all(n==int(index[(k[0],k[1],k[2],'OVERLAP')]['raw_predictions']) for k,n in seen.items())
  receipts.append(dict(file=filename,rows=count,fields=len(seen),exact_ID_prediction_or_weight_roundtrip=True,passed=True));print('CSV_ROUNDTRIP_PASS',filename,count,flush=True);gate()
 for a in rows(R/'19_figures/FIGURE_REGISTRY.csv'):
  with Image.open(a['PNG']) as im:im.verify()
  assert Path(a['PDF']).read_bytes().startswith(b'%PDF')
 # Independently confirm both-seed arithmetic means and continuity macros, with no pooled point weighting.
 seedrows=rows(R/'15_plate_level_metrics/SEED_MACRO_METRICS.csv')
 for a in rows(R/'15_plate_level_metrics/ARITHMETIC_SEED_METRIC_MEANS.csv'):
  ss=[b for b in seedrows if all(a[k]==b[k] for k in ['model','condition','policy'])];assert len(ss)==2
  for k in ['L2','MAE_MPa','high95_IoU']:assert abs(float(a[k])-math.fsum(float(b[k]) for b in ss)/2)<1e-12
 pairrows=rows(R/'BOUNDARY_INTERIOR_MATCHED_COMPARISONS.csv')
 for a in rows(R/'15_plate_level_metrics/ARITHMETIC_SEED_CONTINUITY_MEANS.csv'):
  ss=[b for b in pairrows if all(a[k]==b[k] for k in ['model','condition','policy'])]
  for k in ['mean_boundary_jump_error_MPa','mean_matched_interior_jump_error_MPa','boundary_minus_matched_error_MPa']:
   value=math.fsum(math.fsum(math.fsum(float(b[k]) for b in ss if b['seed']==seed and b['plate']==plate)/len([b for b in ss if b['seed']==seed and b['plate']==plate]) for plate in 'CEGHX')/5 for seed in ['20261021','20261022'])/2;assert abs(value-float(a[k]))<1e-12
 hist=[]
 for a in rows(R/'00_historical_integrity/ALL_RELEASE_HASHES.csv'):
  assert sha(a['path'])==a['SHA256'];hist.append(a)
 table(R/'18_independent_verification/FINAL_HISTORICAL_RELEASE_HASHES.csv',hist)
 result=dict(UTC=now(),passed=True,historical_release_files=len(hist),raw_fields=len(raw),evaluated_fields=len(outputs),exact_CSV_roundtrip_rows=sum(a['rows'] for a in receipts),CSV_checks=receipts,scientific_figure_pairs=38,explicit_final_answers=60,resource=gate(),manifest_not_yet_sealed=True);write(R/'21_reproducibility/DELIVERY_VERIFICATION.json',result);print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
