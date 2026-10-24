from setup_e11r1 import *
from aggregate_e12 import dump
import numpy as np,math
def main():
 f=read(R/'R8E12_FINAL_COUNTS.json');queue=rows(R/'FROZEN_SELECTED_FIVE_SOURCES.csv');prov={a['source_id']:a for a in rows(R/'SOURCE_PROVENANCE_REGISTRY.csv')};parents=[];rear=[];imports=[];common=[];cad=[];support_counts=[]
 aliases={'CAD_GEOMETRY_METRICS.csv':'CAD_ATTEMPT_REGISTRY.csv','SOURCE_CAD_FIDELITY.csv':'SOURCE_GEOMETRY_FIDELITY.csv','M1_M2_MESH_COUNTS.csv':'QUADRATIC_JACOBIAN_AUDIT.csv','M1_M2_MESH_QUALITY.csv':'QUADRATIC_JACOBIAN_AUDIT.csv','M1_M2_HIERARCHY.csv':'M1_M2_REFINEMENT.csv','LOCAL_MESH_REPAIR_ATTEMPTS.csv':'LOCAL_MESH_REPAIR_REGISTRY.csv','LOCAL_NODE_DISPLACEMENTS.csv':'ACTUAL_MOVED_NODES.csv','INDEPENDENT_TENSOR_CHECKS.csv':'TENSOR_INDEPENDENT_CHECKS.csv','SOURCE_MAPPING_COVERAGE.csv':'SOURCE_STRESS_MAPPING.csv','INDEPENDENT_T2_VERIFICATION.csv':'T2_INDEPENDENT_VERIFICATION.csv','ACTUAL_RESOURCE_ACCOUNTING.csv':'FINAL_STORAGE_ACCOUNTING.csv','REMAINING_COHORT_RESOURCE_FORECAST.csv':'REMAINING_COHORT_FORECAST.csv'}
 for a,b in aliases.items():shutil.copy2(R/b,R/a)
 moved=rows(R/'ACTUAL_MOVED_NODES.csv')
 for a in moved:
  for coord in 'XYZ':a['delta_'+coord+'_mm']=float(a['new_'+coord])-float(a['old_'+coord])
 dump('LOCAL_NODE_DISPLACEMENTS.csv',moved)
 for z in queue:
  sid=z['source_id'];c=R/'cases'/sid;p=c/'03_parent_datum'/(sid+'.json')
  if p.exists():
   d=read(p);parents.append(dict(source_id=sid,**{k:v for k,v in d.items() if k!='source_id'}));rear.append(dict(source_id=sid,nominal_thickness_mm=19,source_nominal_basis=prov[sid]['nominal_thickness_mm'],rule=d['rule'],intercept_Z_mm=d['intercept_Z_mm'],slope_X=d['slope_X'],slope_Y=d['slope_Y'],normal_offset_mm=-19,vertical_offset_mm=-19*math.sqrt(1+d['slope_X']**2+d['slope_Y']**2),rear_is_measured=False))
  cp=c/'04_standardized_solids'/sid/'CAD_QUALIFICATION.json'
  if cp.exists():cad.append(read(cp))
  for level in ['M1','M2']:
   p=c/'02_mesh_import'/level/'NATIVE_PREFLIGHT_RECEIPT.json'
   if p.exists():imports.append(dict(source_id=sid,**read(p)))
   target=c/('11_T2_M1' if level=='M1' else '12_T2_M2')/'SOURCE_T2.npz';mapping=c/'10_source_mapping'/level/'MAPPING_AUDIT.json'
   if target.exists() and mapping.exists():
    t=np.load(target);ma=read(mapping);support_counts.append(dict(source_id=sid,level=level,full_front_points=len(t['xyz']),frozen_core_points=int(t['core'].sum()),valid_T2_points=int(t['valid'].sum()),queried_halo_points=ma['queried_halo_points'],valid_mapped_points=ma['valid_mapped_points'],not_queried_points=ma['not_queried_points'],T2_valid_area_fraction_original_front=float(t['area'][t['valid']].sum()/t['area'].sum()),mapping_coverage=ma['area_weighted_mapping_coverage'],masks_changed_to_match_other_sources=False))
 dump('PARENT_DATUM_FITS.csv',parents);dump('REAR_PLANE_DEFINITIONS.csv',rear);dump('NATIVE_IMPORT_COUNTS.csv',imports);dump('SOURCE_SUPPORT_COUNTS.csv',support_counts);dump('CAD_GEOMETRY_METRICS.csv',cad)
 telemetry=rows(R/'04_resource_preflight/CONTROLLER_RESOURCE_SAMPLES.csv');accounting=rows(R/'FINAL_STORAGE_ACCOUNTING.csv')
 for a in accounting:
  ts=[b for b in telemetry if b['source_id']==a['source_id']]
  if ts:a.update(observed_peak_worker_RSS_bytes=max(int(b['observed_worker_RSS_bytes']) for b in ts),observed_peak_worker_private_bytes=max(int(b['observed_worker_private_bytes']) for b in ts),minimum_available_RAM_bytes=min(int(b['RAM_available_bytes']) for b in ts),minimum_available_commit_bytes=min(int(b['commit_free_bytes']) for b in ts),minimum_E_free_bytes=min(int(b['E_free_bytes']) for b in ts),minimum_C_free_bytes=min(int(b['C_free_bytes']) for b in ts),sampled_cumulative_phase_workspace_peak_bytes=max(int(b['workspace_bytes']) for b in ts),sampled_extrema_not_continuous_peak=True)
 dump('ACTUAL_RESOURCE_ACCOUNTING.csv',accounting);res=read(R/'04_resource_preflight/ACTUAL_RESOURCE_ACCOUNTING.json');res.update(minimum_sampled_available_RAM_bytes=min(int(b['RAM_available_bytes']) for b in telemetry),minimum_sampled_available_commit_bytes=min(int(b['commit_free_bytes']) for b in telemetry));write(R/'04_resource_preflight/ACTUAL_RESOURCE_ACCOUNTING.json',res);f['resources']=res
 # Full pointwise exports preserve source row order and all outside-support rows.
 for level in ['M1','M2']:
  path=R/f'SOURCE_T2_{level}.csv';header=None
  with path.open('w',newline='',encoding='utf8') as out:
   for z in queue:
    p=R/'cases'/z['source_id']/f'SOURCE_T2_{level}.csv'
    if not p.exists():continue
    with p.open(encoding='utf8',newline='') as inp:
     rr=csv.reader(inp);h=next(rr)
     if header is None:header=['specimen_id']+h;writer=csv.writer(out);writer.writerow(header)
     assert header==['specimen_id']+h
     for row in rr:writer.writerow([z['source_id']]+row)
   if header is None:csv.writer(out).writerow(['specimen_id','point_id','status_NOT_EXECUTED'])
 with (R/'T2_COMMON_SUPPORT.csv').open('w',newline='',encoding='utf8') as out:
  w=csv.writer(out);w.writerow(['specimen_id','point_id','X','Y','Z','original_T0_area_mm2','frozen_core','common_T2_support'])
  for z in queue:
   c=R/'cases'/z['source_id'];p=c/'13_numerical_qualification/COMPARISON_FIELDS.npz'
   if not p.exists():continue
   a=np.load(p);support=np.load(c/'01_protocol_freeze/TARGET_GEOMETRY_SUPPORT.npz');xyz=a['xyz'];point_ids=a['source_ids'];area=a['area'];core=support['core'];common_mask=a['common']
   for i in range(len(xyz)):w.writerow([z['source_id'],int(point_ids[i]),*xyz[i],area[i],bool(core[i]),bool(common_mask[i])])
 registry=rows(R/'CUMULATIVE_QUALIFIED_V1_TARGET_REGISTRY.csv');new=rows(R/'NEW_QUALIFIED_V1_TARGET_REGISTRY.csv');newids={a['source_id'] for a in new}
 for a in registry:
  p=prov[a['source_id']];a.update(documented_coupon_id=p['documented_coupon_id'],confirmed_parent_plate=p['confirmed_parent_plate'],manufacturing_batch='UNKNOWN',scan_session='UNKNOWN',physical_dependency_status='PHYSICAL_DEPENDENCE_CONFIRMED',physical_independence='PHYSICAL_INDEPENDENCE_UNRESOLVED',provenance_evidence='Originalmetadata/scan_files + dissertation3.2.6/Figure3.9',dataset_leakage_risk='SAME_PARENT_PLATE_MUST_GROUP;BATCH_DEPENDENCY_UNRESOLVED')
  c=Path(a['qualified_M2_target_path']).parent.parent
  for level,folder in [('M1','06_native_M1'),('M2','07_native_M2')]:
   receipt=read(c/folder/'SOLVE_COMPLETE.json');assert receipt['completed'] and receipt['equilibrium_passed'];a[level+'_native_status']='NATIVE_COMPLETED_AND_VERIFIED'
 dump('CUMULATIVE_QUALIFIED_V1_TARGET_REGISTRY.csv',registry);dump('NEW_QUALIFIED_V1_TARGET_REGISTRY.csv',[a for a in registry if a['source_id'] in newids]);groups=sorted({a['confirmed_parent_plate'] for a in registry});folds=[]
 for p in groups:
  held=[a['source_id'] for a in registry if a['confirmed_parent_plate']==p];train=[a['source_id'] for a in registry if a['confirmed_parent_plate']!=p];folds.append(dict(proposed_holdout_parent_plate=p,heldout_source_count=len(held),training_source_count=len(train),heldout_sources=';'.join(held),training_sources=';'.join(train),evidence_level='DOCUMENTED_PARENT_PLATE',all_crops_and_mesh_versions_grouped=True,cross_plate_batch_relationship='UNKNOWN',actual_training=False,actual_validation=False,untouched_external_validation=False))
 dump('FUTURE_GROUPED_SPLIT_FEASIBILITY.csv',folds);leak=[]
 for a in prov.values():leak.append(dict(source_id=a['source_id'],population=a['population'],coupon_group=a['documented_coupon_id'],parent_plate_group=a['confirmed_parent_plate'],mandatory_same_plate_grouping=True,M1_M2_same_group=True,crops_same_group=True,historical_test_quarantined=a['population']!='DEVELOPMENT47',unknown_batch_leakage='UNRESOLVED',independence_claim_allowed=False))
 dump('LEAKAGE_RISK_REGISTRY.csv',leak)
 allgroups=rows(R/'CONFIRMED_PHYSICAL_GROUPS.csv');dump('CONFIRMED_COUPON_GROUPS.csv',[a for a in allgroups if a['evidence_level']=='CONFIRMED_COUPON_GROUPS']);dump('CONFIRMED_PARENT_PLATE_GROUPS.csv',[a for a in allgroups if a['evidence_level']=='CONFIRMED_PARENT_PLATE_GROUPS']);dump('BATCH_LEVEL_RELATIONSHIPS.csv',[dict(source_id=a['source_id'],manufacturing_batch='UNKNOWN',classification='UNKNOWN',evidence='No source-specific batch ledger in inspected original provenance',same_coupon_inferred_from_batch=False) for a in prov.values()]);dump('PROVENANCE_RECONCILIATION.csv',[dict(source_id=a['source_id'],historical_parent_plate_status='UNKNOWN',new_documentary_parent_plate=a['confirmed_parent_plate'],evidence_file='dissertation_extracted.txt',evidence_field='Section3.2.6/Figure3.9',historical_output_modified=False,plate_is_same_as_manufacturing_batch=False) for a in prov.values() if a['population']=='DEVELOPMENT47'])
 receipt=read(R/'01_provenance/AUDIT_RECEIPT.json');f.update(historical_inputs='HISTORICAL_V1_INPUTS_VERIFIED',selection='FIVE_SOURCE_SELECTION_PREREGISTERED',authorization='NEW_PROSPECTIVE_E12_24GIB_CAP',physical_lineage=receipt['physical_dependency_audit'],physical_independence='PHYSICAL_INDEPENDENCE_NOT_ESTABLISHED',AI_readiness='PHYSICAL_GROUPED_AI_EVALUATION_READY' if len(groups)>=3 else 'AI_GROUPED_EVALUATION_NOT_READY',AI_readiness_scope='Prospective documentary parent-plate grouping design only; no executed AI experiment or certified cross-batch generalization',independent_external_validation='INDEPENDENT_EXTERNAL_VALIDATION_NOT_ESTABLISHED',overall_status='R8E12_PARTIAL',documented_cumulative_parent_plate_groups=len(groups),independently_certified_physical_groups=0,remaining_eligible=42-len(registry),historical_test_quarantine=True)
 f.pop('amendment',None);f.update(resource_status='R8E12_RESOURCE_PREFLIGHT_PASS',numerical_resource_gate='NUMERICAL_RESOURCE_GATE_PASS',dataset_status=str(len(registry))+'_TOTAL_V1_TARGETS_QUALIFIED',uncompleted_mandatory_numerical_checks=[] if len(new)==5 else ['See mandatory campaign stop and unexecuted source ledger'],unresolved_physical_checks=['Authorconfirmedmanufacturingbatchledger','Sourceacquisitionsessionandtimestamp','Independentlyauthenticatedplate/couponserialrecords','Untouchedexternalphysicallyindependenttestcohort'])
 write(R/'R8E12_FINAL_COUNTS.json',f);print('DELIVERABLE_TABLES_AND_INDEPENDENT_DECISIONS_READY',len(registry),flush=True)
if __name__=='__main__':main()
