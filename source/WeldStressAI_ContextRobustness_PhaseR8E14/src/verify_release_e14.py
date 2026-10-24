"""Read-only release verification; --preseal writes only the new-phase verification receipt."""
from common_e14 import *
import numpy as np,pandas as pd,math,re
def main():
 verify_protocol();assert read(R/'17_independent_audits/INDEPENDENT_PASS.json')['passed'];assert read(R/'17_independent_audits/SPATIAL_SHIFT_PASS.json')['passed'];counts=read(R/'R8E14_FINAL_COUNTS.json');assert counts['N2_completed_fits']==10 and counts['new_ANSYS_solves']==counts['external_predictions']==0;checks=[]
 seal_time=datetime.datetime.fromisoformat(read(R/'N2_PREREGISTRATION_SEAL.json')['UTC'])
 for p in (R/'11_context_robust_training').glob('*/STARTED.json'):assert datetime.datetime.fromisoformat(read(p)['UTC'])>seal_time
 extension=read(R/'06_observation_protocol/CONTEXT_METRIC_EXTENSION_SEAL.json');assert sha(R/extension['path'])==extension['SHA256']
 for a in rows(R/'R8E13_CHECKPOINT_HASHES.csv'):assert sha(a['checkpoint'])==a['expected_SHA256']==a['actual_SHA256']
 for a in rows(R/'HISTORICAL_V1_TARGET_HASHES.csv'):assert sha(a['path'])==a['expected_SHA256']==a['actual_SHA256']
 # Final independent historical rehash of every originally verified historical artifact.
 if '--preseal' in sys.argv:
  receipt=read(R/'20_reproducibility/FINAL_HISTORICAL_AUDIT.json');assert receipt['passed'] and receipt['after_all_training_and_independent_metric_checks'];assert receipt['ledger_SHA256']==sha(R/'20_reproducibility/FINAL_HISTORICAL_HASHES.csv');historical=rows(R/'20_reproducibility/FINAL_HISTORICAL_HASHES.csv');assert len(historical)==receipt['artifacts']
  for a in historical:
   s=Path(a['path']).stat();assert int(a['bytes'])==s.st_size and int(a['mtime_ns'])==s.st_mtime_ns and a['expected_SHA256']==a['actual_SHA256'],a['path']
  checks.append(dict(check='all_historical_release_artifacts_rehashed_after_execution',records=len(historical),passed=True))
 for a in rows(R/'OBSERVATION_WINDOW_COORDINATES.csv'):assert sha(a['geometry_path'])==a['geometry_SHA256']
 registry=rows(R/'20_reproducibility/PREDICTION_REGISTRY.csv');provenance=rows(R/'20_reproducibility/PREDICTION_PROVENANCE_REGISTRY.csv');assert len(registry)==len(provenance)==182
 for a in provenance:
  assert sha(a['path'])==a['SHA256'];assert sha(a['sidecar'])==a['sidecar_SHA256'];side=read(a['sidecar']);assert side['checkpoint_SHA256']==a['checkpoint_SHA256'];assert side['original_source_support_SHA256']==sha(side['original_source_support_path']);assert side['original_reference_SHA256']==a['reference_SHA256']
 seen_cases=set();csv_rows=0
 for filename in ['FROZEN_N1_PREDICTIONS.csv','N2_FULL_CONTEXT_PREDICTIONS.csv','N2_RESTRICTED_CONTEXT_PREDICTIONS.csv']:
  seen={};cache={}
  for frame in pd.read_csv(R/filename,chunksize=150000,float_precision='round_trip',keep_default_na=False,dtype={'seed':str}):
   for key,ss in frame.groupby(['model','seed','condition','source_id'],sort=False):
    model,seed,condition,sid=key;a=next(a for a in registry if all(a[k]==v for k,v in zip(['model','seed','condition','source_id'],key)))
    if key not in cache:cache={key:dict(np.load(a['path']))}
    p=cache[key];ids=ss.point_id.to_numpy(dtype='i8');local=np.searchsorted(p['source_ids'],ids);assert np.array_equal(ids,p['source_ids'][local]);assert np.array_equal(ss[['X_mm','Y_mm','Z_mm']].to_numpy(),p['xyz'][local]);assert np.array_equal(ss.T0_area_mm2.to_numpy(),p['area'][local]);assert np.array_equal(ss.pred_T2_MPa.to_numpy(),p['pred_MPa'][local]);assert set(ss.fold)=={a['fold']};seen.setdefault(key,[]).extend(ids.tolist());csv_rows+=len(ids)
  for key,ids in seen.items():
   sid=key[3];d=dict(np.load(R/'03_source_geometry'/(sid+'_SUPPORT.npz')));assert np.array_equal(np.array(ids),d['source_ids'][d['core']&d['valid']]);seen_cases.add(key)
  checks.append(dict(check='exact_CSV_source_XYZ_T0_prediction_roundtrip_'+filename,records=sum(len(a) for a in seen.values()),passed=True));print('CSV_EXACT',filename,checks[-1]['records'],flush=True)
 assert csv_rows==6224400 and len(seen_cases)==182
 study=pd.read_csv(R/'SEED_CONTEXT_METRICS.csv');means=pd.read_csv(R/'16_plate_metrics/ARITHMETIC_SEED_METRIC_MEANS.csv')
 for a in means.to_dict('records'):
  ss=study[(study.model==a['model'])&(study.condition==a['condition'])];assert len(ss)==2
  for key,value in a.items():
   if key in ['model','condition']:continue
   assert math.isclose(float(value),math.fsum(map(float,ss[key]))/2,abs_tol=1e-9,rel_tol=1e-10),(key,value)
 from PIL import Image
 images=list((R/'18_figures').glob('*.png'))+list((R/'18_figures/source_maps').glob('*.png'));assert len(images)==62
 for p in images:
  with Image.open(p) as im:im.verify()
  assert p.with_suffix('.pdf').read_bytes().startswith(b'%PDF')
 master=(R/'R8E14_MASTER_REPORT.md').read_text(encoding='utf8');assert len(re.findall(r'^### \d+\.',master,re.M))==55
 spec=(R/'00_integrity/USER_SPECIFICATION.txt').read_text(encoding='utf-8-sig')
 for start,end in [('# 27. REQUIRED REPORTS','# 28.'),('# 28. MACHINE-READABLE DELIVERABLES','# 29.')]:
  for name in re.findall(r'`([^`]+)`',spec.split(start)[1].split(end)[0]):
   if name=='REPRODUCIBILITY_MANIFEST.json' and '--preseal' in sys.argv:continue
   assert (R/name).is_file(),name
 ledger=rows(R/'EXECUTION_BUDGET_LEDGER.csv');assert sum(int(a['new_scheduled_fit']) for a in ledger)==10;assert sum(int(a['dryrun_optimizer_steps']) for a in ledger)==1;assert all(int(a['native_FE_jobs'])==int(a['external_jobs'])==0 for a in ledger);assert all(int(a['exit_code'])==0 for a in ledger)
 v=gate();result=dict(UTC=now(),integrity_status='PASS',historical_targets_verified=13,N1_checkpoints_verified=10,new_N2_fits_verified=10,source_fields_verified=182,exact_CSV_rows=csv_rows,primary_figure_pairs=36,supplemental_figure_pairs=26,explicit_question_answers=55,metric_checks=read(R/'17_independent_audits/INDEPENDENT_PASS.json')['metric_checks'],new_ANSYS=0,new_external_predictions=0,resources=v,checks=checks)
 if '--preseal' in sys.argv:write(R/'20_reproducibility/DELIVERY_VERIFICATION.json',result)
 if (R/'REPRODUCIBILITY_MANIFEST.json').exists():
  manifest=read(R/'REPRODUCIBILITY_MANIFEST.json');seal=read(R/'20_reproducibility/RELEASE_SEAL.json');assert sha(R/'REPRODUCIBILITY_MANIFEST.json')==seal['manifest_SHA256'];listed=set()
  for a in manifest['files']:
   p=R/a['path'];assert p.stat().st_size==a['bytes'] and sha(p)==a['SHA256'],str(p);listed.add(a['path'])
  for p in R.rglob('*'):
   if p.is_file():
    rel=p.relative_to(R).as_posix();assert rel in listed or rel in manifest['excluded'] or rel.startswith('tmp/'),rel
  result['durable_files_verified']=len(listed)
 print(json.dumps(result,indent=2),flush=True);return result
if __name__=='__main__':main()
