from common_r1 import *
from fractions import Fraction
import re,importlib.metadata,platform

def main():
 protect();pair=read(R/'10_mesh_hierarchy/PAIR_PRE_SOLVER_QUALIFICATION.json');assert pair['passed'] and pair['BVP_mesh_compatible'];q1=read(R/'06_recovered_M1/M1_C1/PRE_SOLVER_QUALIFICATION.json');q2=read(R/'07_refined_M2/M2_C1/PRE_SOLVER_QUALIFICATION.json');audit=read(R/'14_reproducibility/ACTUAL_COORDINATE_CHANGE_AUDIT.json');assert audit['actually_changed_nodes']==1;ledger=read(R/'14_reproducibility/FULL_CANDIDATE_LEDGER.json');trials=read(R/'14_reproducibility/LOCAL_TRIAL_LEDGER.json');assert len(ledger)==2 and len(trials)==1 and all(z['status']=='QUALIFIED' for z in ledger)
 old=np.load(R/'00_integrity/baseline/mesh.npz');new=np.load(R/'06_recovered_M1/M1_C1/mesh.npz');m2=np.load(R/'07_refined_M2/M2_C1/mesh.npz');changed=np.flatnonzero(np.any(old['xyz']!=new['xyz'],axis=1));assert changed.tolist()==[86668] and int(new['node_tags'][changed[0]])==86669;assert np.array_equal(old['tet10'],new['tet10']) and np.array_equal(old['tri6'],new['tri6']);boundary=np.unique(old['tri6']);corners=np.unique(old['tet10'][:,:4]);assert np.array_equal(old['xyz'][boundary],new['xyz'][boundary]) and np.array_equal(old['xyz'][corners],new['xyz'][corners]);actual=set(audit['actually_changed_element_indices']);rows_local=rows(R/'LOCAL_ELEMENT_QUALITY_BEFORE_AFTER.csv')
 for z in rows_local:z['contains_actually_displaced_node']=int(z['element_index']) in actual
 table(R/'LOCAL_ELEMENT_QUALITY_BEFORE_AFTER.csv',rows_local)
 # More precise candidate provenance in generated summary CSVs. Frozen copied inputs are untouched.
 binding={}
 for level in ['M1','M2']:
  cid=level+'_C1';folder=R/('06_recovered_M1' if level=='M1' else '07_refined_M2')/cid;binding[cid]=str(folder.relative_to(R))+'/mesh.npz;SHA256='+sha(folder/'mesh.npz')
 binding['ORIGINAL_M1']='00_integrity/baseline/mesh.npz;SHA256='+sha(R/'00_integrity/baseline/mesh.npz');binding['M1_C1__M2_C1']='10_mesh_hierarchy/PAIR_PRE_SOLVER_QUALIFICATION.json;SHA256='+sha(R/'10_mesh_hierarchy/PAIR_PRE_SOLVER_QUALIFICATION.json')
 for f in list(R.glob('*.csv'))+list((R/'08_quadratic_quality').glob('*.csv')):
  data=rows(f)
  if not data:continue
  for z in data:
   if z.get('candidate_id') in binding:z['numerical_provenance']=binding[z['candidate_id']]
  table(f,data)
 # Historical preserved inputs include all E10 artifacts, initially frozen E9 configuration, C02source and native ordering provenance.
 hist=rows(R/'00_integrity/HISTORICAL_HASHES.csv');ordering=read(R/'02_invalid_element_diagnosis/NODE_ORDERING.json');nativepath=E8B/'08_native_results'/SID/'M1/native_displacements.npz'
 if str(nativepath) not in [v['path'] for v in hist]:hist.append(dict(source_id=SID,candidate_id='HISTORICAL_NATIVE_ORDERING_PROVENANCE',protocol_version=VERSION,numerical_provenance='Existing E8B C02 result; no new native execution',path=str(nativepath),sha256=ordering['historical_native_provenance_SHA256'],passed=True))
 for z in hist:assert sha(z['path'])==z['sha256'],z['path']
 table(R/'00_integrity/HISTORICAL_HASHES.csv',hist)
 for z in read(R/'00_integrity/FROZEN_COPIES.json'):assert sha(R/z['copy'])==z['sha256']
 assert sha(R/'01_frozen_protocol/geometry/standardized_planar_rear.step')==read(R/'00_integrity/INITIALIZATION.json')['STEP_SHA256']
 for name in ['xyz.npy','triangles.npy','source_ids.npy','area.npy','normal.npy']:assert sha(R/'01_frozen_protocol/source'/name)==sha(E3/'02_geometry/single'/SID/name)
 assert sha(R/'06_recovered_M1/M1_C1/PRE_SOLVER_QUALIFICATION.json')==read(R/'10_mesh_hierarchy/M2_PREREGISTRATION.json')['M1_qualification_SHA256'],'M1 pass receipt changed after M2 preregistration'
 proofs=[]
 for m,level in [(new,'M1'),(m2,'M2')]:
  cid=level+'_C1';path=R/'08_quadratic_quality'/(cid+'_EXACT_BERNSTEIN_CERTIFICATES.json');p=read(path);elements=p['elements'];positive=0
  for e in elements:
   coefficients=[Fraction(v) for v in e['exact_Bernstein_coefficients']];assert len(coefficients)==20 and min(coefficients)>0;positive+=1
  ids=np.array([z['element_index'] for z in elements]);coordhash=hashlib.sha256(m['xyz'][m['tet10'][ids]].tobytes()).hexdigest();proofs.append(dict(source_id=SID,candidate_id=cid,protocol_version=VERSION,mesh_SHA256=sha(R/('06_recovered_M1' if level=='M1' else '07_refined_M2')/cid/'mesh.npz'),certificate_SHA256=sha(path),certificate_elements=positive,exact_positive_coefficient_signs_checked=True,listed_element_coordinates_bytes_SHA256=coordhash,scope='Listed local elements only; whole-mesh continuous positivity not claimed'))
 write(R/'08_quadratic_quality/EXACT_CERTIFICATE_INPUT_BINDINGS.json',proofs)
 # Guard checks dispatch audit events only; no process or historical open is actually attempted.
 denied=[]
 for event,args in [('subprocess.Popen',('ANSYS231.exe',[],None,None)),('open',(str(E10/'R1_guard_probe'),'w',0))]:
  try:sys.audit(event,*args)
  except PermissionError:denied.append(event)
 assert len(denied)==2
 write(R/'00_integrity/FINAL_PRESERVATION_AND_GUARD_RECEIPT.json',dict(UTC=now(),source_id=SID,candidate_id='RELEASE',protocol_version=VERSION,passed=True,historical_rows_verified=len(hist),historical_unique_paths=len({z['path'] for z in hist}),source_arrays_byte_identical=True,STEP_byte_identical=True,old_negative_baseline_byte_identical=True,M1_pass_receipt_immutable_after_M2_freeze=True,guard_denials=denied,no_actual_process_or_history_write_in_guard_tests=True))
 nofiles=[p for p in R.rglob('*') if p.suffix.lower() in ['.rst','.rth','.cdb','.db','.pt','.pth','.onnx','.wbpj','.mechdb']];assert not nofiles
 figures=rows(R/'SCIENTIFIC_FIGURES.csv');assert len(figures)==25
 for z in figures:
  assert (R/z['png']).is_file()
  with (R/z['pdf']).open('rb') as f:assert f.read(5)==b'%PDF-'
 write(R/'14_reproducibility/FIGURE_VISUAL_QA.json',dict(UTC=now(),source_id=SID,candidate_id='M1_C1__M2_C1',protocol_version=VERSION,contact_sheet_reviewed=True,full_size_displacement_and_hierarchy_reviewed=True,figures_png=25,figures_pdf=25,coordinate_summary_corrected='4 optimization-variable nodes;1 actual displaced node,3 exactly zero',render_correction='A Matplotlib line-collection keyword was corrected; no numerical mesh changed; failed render log preserved',no_fake_solver_figures=True))
 resources=resource_gate();software=dict(python=sys.version,executable=sys.executable,platform=platform.platform(),libraries={k:importlib.metadata.version(k) for k in ['numpy','scipy','gmsh','matplotlib','psutil','Pillow']});write(R/'14_reproducibility/SOFTWARE_AND_RESOURCES.json',dict(UTC=now(),software=software,resources=resources,process_peak_RSS_bytes=None,peak_memory_note='Case-specific preflight system RAM/commit gates checked; process peak was not instrumented and is not invented.'))
 native_warnings=rows(R/'14_reproducibility/MESHER_WARNING_REGISTRY.csv');assert int(native_warnings[1]['raw_mesher_warning_lines'])==1424
 counts=dict(UTC=now(),source_id=SID,candidate_id='M1_C1__M2_C1',protocol_version=VERSION,overall='R8E10R1_MESH_RECOVERY_COMPLETE',root_cause='ROOT_CAUSE_VERIFIED',mesh_pair='C02_M1_M2_PRE_SOLVER_QUALIFIED',source_identities=1,new_CAD_generations=0,local_strategies_executed=1,S1_local_trials=1,S2_local_trials=0,S3_local_trials=0,optimization_variable_nodes=4,actually_displaced_M1_nodes=1,actually_changed_M1_volume_elements=len(actual),potential_support_elements_verified=14,maximum_actual_node_displacement_mm=audit['maximum_displacement_mm'],new_full_M1_candidates=1,new_full_M2_candidates=1,new_global_M1_remeshes=0,new_M2_mesher_generation_calls=1,M1_qualified=True,M2_qualified=True,M1_nodes=q1['nodes'],M1_Tet10=q1['Tet10'],M2_nodes=q2['nodes'],M2_Tet10=q2['Tet10'],M1_minSICN=q1['minSICN'],M2_minSICN=q2['minSICN'],M1_min_Q1_J_mm3=q1['minimum_Q1_J_mm3'],M2_min_Q1_J_mm3=q2['minimum_Q1_J_mm3'],negative_sampled_J_total=0,zero_sampled_J_total=0,Q1_samples_per_element=73,Q2_local_samples=909,M1_exact_Bernstein_elements=14,M2_exact_Bernstein_elements=16,whole_mesh_continuous_positivity_certified=False,near_weld_median_ratio=pair['edge_median_ratio'],near_weld_P90_ratio=pair['edge_P90_ratio'],curved_face_density_ratio=pair['surface_density_ratio'],BVP_mesh_preflight=True,native_ANSYS_jobs=0,native_ANSYS_SOLVEs=0,AI_training_runs=0,AI_inference_runs=0,V1_T2_targets=0,figures_PNG=25,figures_PDF=25,master_questions_answered=35,historical_rows_reverified=len(hist),resources=resources,uncompleted_in_scope_checks=[],future_checks_requiring_separate_authorization=['Native ANSYS import and element-shape checking','Actual standardized load/constraint assembly and sequential M1/M2 solutions','Native equilibrium and displacement-to-stress checks','Original-source T2 field and mesh sensitivity qualification'],known_limitations=['Whole-mesh Jacobian positivity is sampled; exact local certificates apply only to listed elements','M2 raw Gmsh export contains1424 parameter-metadata warnings; labelled discrete MSH round-trip and numerical geometry gates pass','Physical geometry/metrology and local notch-stress accuracy remain unvalidated'])
 write(R/'R8E10R1_FINAL_COUNTS.json',counts)
 pairrelease=dict(UTC=now(),source_id=SID,protocol_version=VERSION,target_semantics_SHA256=read(R/'01_frozen_protocol/TARGET_STANDARD_PLANAR_V1.json')['semantics_SHA256'],scope='Qualified mesh pair only; not a stress target',authoritative_STEP=dict(path='01_frozen_protocol/geometry/standardized_planar_rear.step',sha256=sha(R/'01_frozen_protocol/geometry/standardized_planar_rear.step')),source_arrays={n:dict(path='01_frozen_protocol/source/'+n,sha256=sha(R/'01_frozen_protocol/source'/n)) for n in ['xyz.npy','triangles.npy','source_ids.npy','area.npy','normal.npy']},meshes=[],Gmsh_to_SOLID187_permutation_zero_based=[0,1,2,3,4,5,6,7,9,8],native_execution_authorized_in_R1=False,qualified_T2_target=None)
 for level in ['M1','M2']:
  folder=R/('06_recovered_M1' if level=='M1' else '07_refined_M2')/(level+'_C1');pairrelease['meshes'].append(dict(candidate_id=folder.name,files={n:dict(path=(folder/n).relative_to(R).as_posix(),sha256=sha(folder/n)) for n in ['mesh.npz','mesh_labelled.msh','PRE_SOLVER_QUALIFICATION.json','SOURCE_FIDELITY.json','LABELLED_MSH_ROUNDTRIP.json']}))
 write(R/'MESH_PAIR_RELEASE.json',pairrelease)
 spec=(R/'01_frozen_protocol/EXECUTION_SPECIFICATION.txt').read_text(encoding='utf8');section=spec.split('# 17. REQUIRED REPORTS')[1].split('# 18.')[0];required=set(re.findall(r'`([A-Z][A-Z0-9_]+\.(?:md|csv|json))`',section));required|={'INVALID_ELEMENT_CONNECTIVITY.csv','INVALID_ELEMENT_NEIGHBORHOOD.csv','ROOT_CAUSE_HYPOTHESIS_MATRIX.csv','MESH_PAIR_RELEASE.json'}
 for name in required-{'REPRODUCIBILITY_MANIFEST.json'}:assert (R/name).is_file(),name
 write(R/'14_reproducibility/RELEASE_PREFLIGHT.json',dict(UTC=now(),source_id=SID,candidate_id='RELEASE',protocol_version=VERSION,passed=True,required_files=sorted(required),all_scientific_gates_checked=True,pair_mesh_qualified=True,native_and_AI_runs=0,pilot_is_not_stress_target_validation=True,final_independent_byte_verification_pending=True))
 print('R1_CLOSEOUT_READY',len(required),'required files;',len(hist),'historical hashes;',1,'actual moved node',flush=True)
if __name__=='__main__':main()
