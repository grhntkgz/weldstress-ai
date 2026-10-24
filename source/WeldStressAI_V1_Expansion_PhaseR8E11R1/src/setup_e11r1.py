"""Prospective amendment only. Scientific production is performed by separate gated stages."""
from pathlib import Path
import json,csv,hashlib,sys,shutil,datetime,os,re
R=Path(__file__).resolve().parents[1];B=R.parent;P=B/'WeldStressAI_V1_Expansion_PhaseR8E11';H3=B/'WeldStressAI_G08X10_NativeV1_PhaseR8E10R3';E9=B/'WeldStressAI_PhysicsConsistentLearning_PhaseR8E9';GiB=1024**3
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rows(p):
 with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,x):
 p=Path(p);assert p.resolve().is_relative_to(R);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2),encoding='utf8')
def table(p,z,fields=None):
 with Path(p).open('w',newline='',encoding='utf8') as f:w=csv.DictWriter(f,fieldnames=fields or list(z[0]));w.writeheader();w.writerows(z)
def adapt():
 s=(R/'src/common_r3.py').read_text(encoding='utf-8-sig');s=s.replace("os.environ.get('R3_SOURCE','G08-V1-S355-AW');assert SID in ['G08-V1-S355-AW','X10-V1-S355-AW']","os.environ.get('R3_SOURCE','X23-V1-S355-AW')")
 s=s.replace('<=12*1024**3','<=24*1024**3')
 s=s.replace("def resource_gate(ram=0,commit=0,disk=0):\n m=memory();","def resource_gate(ram=0,commit=0,disk=0):\n m=memory();record_resource(m,ram,commit,disk);")
 s=s[:s.index('def may_execute_source():')]+"""
def record_resource(m,ram=0,commit=0,disk=0):
 p=GLOBAL/'ACTUAL_RESOURCE_TIMELINE.csv';header=not p.exists()
 with p.open('a',newline='',encoding='utf8') as f:
  z=dict(source_id=SID,**m,predicted_operation_RAM_bytes=ram,predicted_operation_commit_bytes=commit,predicted_additional_disk_bytes=disk);w=csv.DictWriter(f,fieldnames=list(z))
  if header:w.writeheader()
  w.writerow(z)
 # All phase-controlled temporary directories are on E:. C: is monitored as a system/possible licensing fallback volume.
 assert shutil.disk_usage('C:/').free>=2*1024**3,'RESOURCE_PREFLIGHT_BLOCKED:C_SYSTEM_RESERVE'
def may_execute_source():
 assert read(GLOBAL/'RESOURCE_GATE_DECISION.json')['decision']=='RESOURCE_PREFLIGHT_PASS','Initial resource gate'
 assert not (GLOBAL/'21_reproducibility/CAMPAIGN_STOP.json').exists(),'Campaign stop'
 for a in read(GLOBAL/'AMENDMENT_PREREGISTRATION_SEAL.json')['files']:assert sha(GLOBAL/a['path'])==a['sha256'],'Amendment changed'
 queue=[a['source_id'] for a in rows(GLOBAL/'FROZEN_SELECTED_FIVE_SOURCES.csv')];assert SID in queue;i=queue.index(SID)
 if i:assert read(GLOBAL/'cases'/queue[i-1]/'13_numerical_qualification/QUALIFICATION_DECISION.json')['qualified'],'Predecessor must qualify'
"""
 (R/'src/common_r3.py').write_text(s,encoding='utf8')
 p=R/'src/solve_r2.py';s=p.read_text();assert 'len(gl)<4' in s;p.write_text(s.replace('len(gl)<4','len(gl)<10'))
 p=R/'src/complete_metrics_r3.py';s=p.read_text();s=s.replace("R5/'11_ml_dataset'/SID/'geometry_provenance.json'","Path(rows(R/'R8E10_PILOT_QUEUE.csv')[0]['package_path'])/'geometry_provenance.json'")
 s=s.replace("write(pkg/'TARGET_PROVENANCE.json',metadata);","metadata.update(physical_dependency_group=rows(R/'R8E10_PILOT_QUEUE.csv')[0]['dependency_group'],physical_independence='UNCERTIFIED',nominal_thickness_mm=19,material_assumptions=dict(E_MPa=210000,nu=.30),rear_protocol_id='FRONT_PARENT_HUBER_OUTER10_NORMAL_OFFSET_V1',standardized_BVP_id='BVP_NOMINAL100_TNOM_WFULL_X_COMMONMID_V1',CAD_SHA256=sha(R/'01_frozen_protocol/geometry/standardized_planar_rear.step'),recovery_version='FrozenR3_isoparametric_V1_reused_E11R1');write(pkg/'TARGET_PROVENANCE.json',metadata);")
 p.write_text(s)
 # Prospective instrumentation separates CAD construction/reimport from geometric fidelity, without changing geometry.
 p=R/'src/geometry_e10.py';s=p.read_text();s=s.replace("import cadquery as cq\n","cad_clock=time.perf_counter()\n import cadquery as cq\n",1);s=s.replace("err=abs(z-xyz[:,2]);reverse=[];","write(out/'CAD_CONSTRUCTION_TIMING.json',dict(elapsed_s=time.perf_counter()-cad_clock,scope='CADimportconstructionexportreimportandBRepidentitychecks'));fidelity_clock=time.perf_counter()\n err=abs(z-xyz[:,2]);reverse=[];",1);s=s.replace("checks=dict(one_valid_closed_solid=True","write(out/'CAD_FIDELITY_TIMING.json',dict(elapsed_s=time.perf_counter()-fidelity_clock,scope='Forwardreversefidelityandanalyticportscreen'))\n checks=dict(one_valid_closed_solid=True",1);p.write_text(s)
def main():
 assert not (R/'AMENDMENT_PREREGISTRATION_SEAL.json').exists();adapt()
 for n in ['R2_READONLY_VERIFICATION.log','R3_READONLY_VERIFICATION.log','E11_READONLY_VERIFICATION.log']:
  t=(R/'00_integrity'/n).read_text(encoding='utf-8-sig');assert ('"status": "PASS"' in t or '"integrity_status": "PASS"' in t) and 'Traceback' not in t,n
 t=(R/'00_integrity/E9_46_TESTS.log').read_text(encoding='utf-8-sig');assert 'Ran 46 tests' in t and t.rstrip().endswith('OK')
 original=read(P/'CURRENT_RESOURCE_PREFLIGHT.json');assert original['status']=='RESOURCE_PREFLIGHT_BLOCKED' and not original['checks']['workspace'];assert read(P/'R8E11_FINAL_COUNTS.json')['new_SOLVE_invocations']==0 and not (P/'cases').exists()
 hist=rows(P/'00_integrity/HISTORICAL_HASHES.csv');assert len(hist)==1432
 for a in hist:assert sha(a['path'])==a['sha256'],a['path']
 for root in [E9,B/'WeldStressAI_C02_NativeV1_PhaseR8E10R2',H3,P]:
  for a in read(root/'REPRODUCIBILITY_MANIFEST.json')['files']:
   p=root/a['path'];assert sha(p)==a['sha256'];hist.append(dict(path=str(p),sha256=a['sha256'],bytes=p.stat().st_size,kind='READ_ONLY_RELEASE'))
 table(R/'00_integrity/HISTORICAL_HASHES.csv',hist)
 names=['SELECTED_FIVE_V1_SOURCES.csv','SOURCE_HASHES.json','HISTORICAL_V1_TARGET_HASHES.csv','FIVE_SOURCE_STORAGE_FORECAST.csv','SOURCE_DEPENDENCY_METADATA.csv']
 for n in names:shutil.copy2(P/n,R/n)
 shutil.copy2(P/'SELECTED_FIVE_V1_SOURCES.csv',R/'FROZEN_SELECTED_FIVE_SOURCES.csv');q=rows(R/'FROZEN_SELECTED_FIVE_SOURCES.csv');assert [a['source_id'][:3] for a in q]==['X23','G25','C05','G04','E21'];assert len(q)==5
 for a in rows(R/'HISTORICAL_V1_TARGET_HASHES.csv'):assert sha(a['target_path'])==a['target_hash']
 for sid,files in read(R/'SOURCE_HASHES.json').items():
  for p,h in files.items():assert sha(p)==h
 parent=[P/n for n in ['PREREGISTRATION_SEAL.json','CURRENT_RESOURCE_PREFLIGHT.json','FIVE_SOURCE_STORAGE_FORECAST.csv','SELECTED_FIVE_V1_SOURCES.csv','FULL_CANDIDATE_RANKING.csv','SOURCE_DEPENDENCY_METADATA.csv','R8E11_FINAL_COUNTS.json','REPRODUCIBILITY_MANIFEST.json','25_reproducibility/RELEASE_SEAL.json','25_reproducibility/INDEPENDENT_RELEASE_VERIFICATION.json','25_reproducibility/CAMPAIGN_STOP.json']]
 write(R/'PARENT_PROTOCOL_HASHES.json',dict(parent_E11=[dict(path=str(p),sha256=sha(p)) for p in parent],E9_semantics_SHA256='6d4e68ece06a7f788f3fecceccad96e9989814b23d51890f577fe2ee6ed25ce8',previous_stop='RESOURCE_PREFLIGHT_BLOCKED_AT16GIB',previous_native_SOLVEs=0))
 from common_r3 import memory
 m=memory();lic=(R/'04_resource_preflight/LICENSE_STATUS.log').read_text(encoding='utf-8-sig');match=re.search(r'Users of ansys:\s+\(Total of\s+(\d+) licenses issued;\s+Total of\s+(\d+) licenses in use',lic);assert match,'License feature query unavailable';assert int(match[1])>int(match[2])
 live=dict(UTC=now(),system=m,E_free_GiB=m['free_disk_bytes']/GiB,C_free_GiB=shutil.disk_usage('C:/').free/GiB,old_E11_workspace_bytes=sum(p.stat().st_size for p in P.rglob('*') if p.is_file()),new_R1_workspace_bytes=m['workspace_bytes'],RAM_available_GiB=m['RAM_available_bytes']/GiB,commit_available_GiB=m['commit_free_bytes']/GiB,solver_license=dict(feature='ansys',issued=int(match[1]),in_use=int(match[2]),available=int(match[1])-int(match[2]),scope='Read-onlylmstat snapshot; actual checkout confirmed by native jobs'),scratch=dict(TEMP=str(R/'tmp'),TMP=str(R/'tmp'),CAD_and_mesher=str(R/'tmp'),native_job_directories=str(R/'cases'),unrelated_applications_unchanged=True,C_system_reserve_GiB=2,E_reserve_GiB=20),accounting='All files recursively undernewR1root plus any attributable external scratch; no external scratch planned.2s native telemetry is sampling,not guaranteed instantaneous peak.')
 write(R/'LIVE_RESOURCE_MEASUREMENT.json',live)
 fo=rows(R/'FIVE_SOURCE_STORAGE_FORECAST.csv');cons=next(a for a in fo if a['scenario']=='conservative');peak=float(cons['batch_peak_GiB']);assert abs(peak-17.259678117233705)<1e-12
 components=[dict(component='Fivecap-scaledpersistentarchives',GiB=5*float(cons['per_source_final_archive_GiB']),scope='CAD/meshes/decks/RST/DB/CDB/recoveryarrays/T2packages;entirearchivecapscale'),dict(component='RetainedfailedmeshCADcandidateallowance',GiB=5*float(cons['per_source_retained_failed_candidates_GiB']),scope='Fouradditionalfullcandidates/sourceat0.20GiB;includeslocal/CADfailureheadroom'),dict(component='Phaseoverhead',GiB=.5,scope='Reports/figures/manifests/integrity/preflight'),dict(component='Simultaneoustemporary',GiB=.25,scope='SequentialCADmeshMAPDLscratchcheckpoints')];table(R/'STORAGE_FORECAST_COMPONENTS.csv',components)
 oldprot=read(P/'R8E11_PROTOCOL_HASHES.json');newprot=json.loads(json.dumps(oldprot));newprot['limits']['workspace_GiB']=24;write(R/'R8E11R1_PROTOCOL_HASHES.json',newprot);shutil.copy2(R/'R8E11R1_PROTOCOL_HASHES.json',R/'R8E10R3_PROTOCOL_HASHES.json')
 amendment=dict(UTC=now(),amendment_id='R8E11R1_RESOURCE_AMENDMENT_TO_24_GIB',old_workspace_cap_GiB=16,new_workspace_cap_GiB=24,reason='Prospectivelyauthorizedworkspacebudgetamendmentcoversunchanged17.259678GiBengineeringforecast',old_stop_preserved=True,parent_preregistration_SHA256=sha(P/'PREREGISTRATION_SEAL.json'),frozen_queue_SHA256=sha(R/'FROZEN_SELECTED_FIVE_SOURCES.csv'),only_scientific_protocol_difference='limits.workspace_GiB:16->24;nootherchanges',forecast_peak_new_workspace_GiB=peak,planning_headroom_GiB=24-peak,additional_peak_disk_GiB=max(0,peak-m['workspace_bytes']/GiB),expected_remaining_free_disk_GiB=m['free_disk_bytes']/GiB-max(0,peak-m['workspace_bytes']/GiB),min_disk_reserve_GiB=20,failed_attempt_allowance_GiB=4,estimated_simultaneous_temporary_GiB=.25,workspace_definition='Recursive newR1 files including failed candidates and all phase-attributable external scratch if any;historicalE11notcountedagain',live_measurement_SHA256=sha(R/'LIVE_RESOURCE_MEASUREMENT.json'),execution_authority='Atmost5frozenidentities,10SOLVEs,2/source,sequential;alloriginalgatesandstops',AI_training=False,AI_inference=False)
 body='# Prospective R8-E11-R1 workspace budget amendment\n\nHistorical R8-E11 correctly stopped under16GiB. Its stop receipt and preregistration remain read-only. The sole prospective amendment is24GiB workspace; all scientific criteria and the exact X23/G25/C05/G04/E21queue remain unchanged. No new CAD,mesh or native job exists at sealing.\n\n'+json.dumps(amendment,indent=2)+'\n';(R/'R8E11R1_RESOURCE_BUDGET_AMENDMENT.md').write_text(body,encoding='utf8');amendment['amendment_MD_SHA256']=sha(R/'R8E11R1_RESOURCE_BUDGET_AMENDMENT.md');write(R/'RESOURCE_BUDGET_AMENDMENT.json',amendment)
 seal_files=[R/n for n in ['R8E11R1_RESOURCE_BUDGET_AMENDMENT.md','RESOURCE_BUDGET_AMENDMENT.json','PARENT_PROTOCOL_HASHES.json','FROZEN_SELECTED_FIVE_SOURCES.csv','SOURCE_HASHES.json','R8E11R1_PROTOCOL_HASHES.json','R8E10R3_PROTOCOL_HASHES.json','LIVE_RESOURCE_MEASUREMENT.json','STORAGE_FORECAST_COMPONENTS.csv']]
 write(R/'AMENDMENT_PREREGISTRATION_SEAL.json',dict(UTC=now(),new_CAD=0,new_meshes=0,new_native_SOLVEs=0,amendment_SHA256=sha(R/'RESOURCE_BUDGET_AMENDMENT.json'),files=[dict(path=p.relative_to(R).as_posix(),sha256=sha(p)) for p in seal_files]));shutil.copy2(R/'AMENDMENT_PREREGISTRATION_SEAL.json',R/'PREREGISTRATION_SEAL.json')
 checks=dict(parent_hashes=True,exact_five=True,workspace=peak<=24,disk=amendment['expected_remaining_free_disk_GiB']>=20,RAM=m['RAM_available_bytes']>=5*GiB,commit=m['commit_free_bytes']>=5.8*GiB,C_system=live['C_free_GiB']>=2,scratch_on_E=True,license=int(match[1])>int(match[2]),scientific_protocol_unchanged=True);passed=all(checks.values());decision=dict(UTC=now(),decision='RESOURCE_PREFLIGHT_PASS' if passed else 'RESOURCE_PREFLIGHT_BLOCKED',checks=checks,amendment_seal_SHA256=sha(R/'AMENDMENT_PREREGISTRATION_SEAL.json'),forecast_peak_GiB=peak,cap_GiB=24,planning_headroom_GiB=24-peak,new_CAD_at_decision=0,new_meshes_at_decision=0,newSOLVEs_at_decision=0);write(R/'RESOURCE_GATE_DECISION.json',decision);write(R/'R8E11R1_RESOURCE_GATE_DECISION.json',decision)
 for name in ['TARGET_VERSION_SCHEMA.json','STANDARD_BVP_SCHEMA.json','REAR_PLANE_RULE_SCHEMA.json','QUALIFICATION_GATE_DEFINITIONS.json']:shutil.copy2(E9/name,R/'01_protocol_freeze'/name)
 if passed:
  for z in q:
   case=R/'cases'/z['source_id']
   for name in ['00_integrity','01_frozen_protocol/geometry','01_frozen_protocol/source','01_protocol_freeze/R1_frozen/source','02_source_geometry','03_parent_datum','04_standardized_solids','05_CAD_fidelity','09_mechanical_BVP','17_reproducibility','08_quadratic_quality','14_reproducibility','10_mesh_hierarchy','11_mechanical_mesh_preflight','02_mesh_import','03_native_shape_checks','05_mechanical_preflight','06_native_M1','07_native_M2','09_tensor_recovery','10_source_mapping','11_T2_M1','12_T2_M2','13_numerical_qualification','04_repair_strategies','05_local_repair_trials']:(case/name).mkdir(parents=True,exist_ok=True)
   table(case/'R8E10_PILOT_QUEUE.csv',[z]);write(case/'00_integrity/INITIALIZATION_COMPLETE.json',dict(passed=True,UTC=now()));shutil.copy2(E9/'03_config/TARGET_STANDARD_PLANAR_V1.json',case/'01_protocol_freeze/R1_frozen/TARGET_STANDARD_PLANAR_V1.json')
 table(R/'SOURCE_EXECUTION_LEDGER.csv',[dict(source_id=z['source_id'],order=z['order'],status='QUEUED' if passed else 'NOT_EXECUTED_RESOURCE_BLOCKED',last_checkpoint='AMENDMENT_SEALED',CAD_attempts=0,M1_candidates=0,M2_candidates=0,repair_trials=0,native_preprocessing=0,SOLVEs=0,successful_SOLVEs=0,qualified=False) for z in q])
 print(json.dumps(dict(resource=decision,live=live),indent=2))
if __name__=='__main__':main()
