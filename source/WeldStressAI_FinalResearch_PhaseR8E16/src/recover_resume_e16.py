from common_e16 import *
import numpy as np
def main():
 verify_protocol();gate();verified=[];replay=[];fields=0
 for p in sorted((R/'05_blockwise_interventions').glob('*_COMPLETED.json')):
  r=read(p);assert r['passed'] and r['optimizer_steps']==0 and r['parameter_state_before']==r['parameter_state_after'];prefix=p.name.removesuffix('_COMPLETED.json');registry=rows(p.parent/(prefix+'_REGISTRY.csv'));assert len(registry)==r['fields']
  for a in registry:
   assert sha(a['path'])==a['SHA256'];s=dict(np.load(K/'02_source_geometry'/a['source_id']/'CORE.npz'));d=dict(np.load(a['path']));assert all(np.array_equal(d[k],s[k]) for k in ['source_ids','xyz','area','query_original_rows']);assert len(d['pred_MPa'])==34200 and np.isfinite(d['pred_MPa']).all()
   if a['cell'] in ['F000','F111']:
    policy='S0' if a['cell']=='F000' else 'ORACLE';b=next(b for b in rows(K/'SOURCE_LEVEL_FIELD_METRICS.csv') if all(b[k]==a[k] for k in ['model','seed','source_id','condition']) and b['policy']==policy);error=float(abs(d['pred_MPa']-np.load(b['path'])['pred_MPa']).max());assert error<=1e-4;replay.append(dict(field=Path(a['path']).stem,maximum_difference_MPa=error,passed=True))
  fields+=len(registry);verified.append(dict(job=prefix,fields=len(registry),passed=True))
 assert len(verified)==20 and fields==832
 for a in rows(R/'FROZEN_NUMERICAL_TARGET_HASHES.csv'):assert sha(a['target_path'])==a['SHA256']
 for a in rows(R/'HISTORICAL_MODEL_HASHES.csv'):assert sha(a['checkpoint'])==a['actual_SHA256']
 for a in rows(R/'07_feature_implementation/FEATURE_REGISTRY.csv'):assert sha(a['base_features_path'])==a['SHA256']
 assert read(R/'10_training_validation/FEATURE_CONTRACT_PASS.json')['passed'];dry=read(R/'10_training_validation/TRAINING_DRY_RUN.json');assert dry['passed'] and dry['steps']==0 and dry['finite_gradients']
 completed=[]
 for p in sorted((R/'11_N3_training').glob('F*_s*/COMPLETED.json')):
  a=read(p);assert a['epochs']==80 and sha(a['checkpoint'])==a['checkpoint_SHA256'];assert sha(p.parent/'runtime_membership.csv')==a['runtime_membership_SHA256'];assert sha(p.parent/'QUERY_SOURCE_IDS.npy')==a['query_ID_file_SHA256'];completed.append(p.parent.name)
 infer=[]
 for p in sorted((R/'13_full_core_predictions').glob('*_COMPLETED.json')):
  prefix=p.name.removesuffix('_COMPLETED.json');reg=rows(p.parent/(prefix+'_REGISTRY.csv'));assert len(reg)==read(p)['fields']
  for a in reg:assert sha(a['path'])==a['SHA256']
  infer.append(prefix)
 table(R/'00_integrity/RESUME_FACTORIAL_JOB_AUDIT.csv',verified);table(R/'00_integrity/RESUME_F000_F111_REPLAY.csv',replay);result=dict(UTC=now(),passed=True,seal_SHA256=sha(R/'PREREGISTRATION_SEAL.json'),factorial_workers_complete=20,factorial_fields_complete=832,replay_fields=len(replay),maximum_replay_difference_MPa=max(a['maximum_difference_MPa'] for a in replay),N3_completed=completed,N3_inference_completed=infer,N3_remaining=10-len(completed),XGB_completed=len(list((R/'12_XGBoost_baseline').glob('F*/COMPLETED.json'))),running_workers=0,previous_controller_block='Receipt filename mismatch only: existing valid F1_s20261021 inference complete; current unsealed orchestration path corrected; sealed scientific workers unchanged',resource=gate());write(R/'00_integrity/RESUME_RECOVERY_VERIFIED.json',result)
 text='# R8-E16 verified recovery\n\n'+json.dumps(result,indent=2)+'\n\nAll existing verified jobs will be skipped. Previous CAMPAIGN_BLOCKED.json is retained as historical evidence of an orchestration receipt-name mismatch, not a failed fit. No production model, feature formula, protocol or experimental configuration changed.\n';(R/'R8E16_RECOVERY_REPORT_2026-10-23.md').write_text(text,encoding='utf8');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
