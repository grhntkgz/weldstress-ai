from common_r2 import *
import importlib.metadata,platform
def main():
 protect();assert len(rows(R/'SCIENTIFIC_FIGURES.csv'))==34;assert len(list((R/'15_figures').glob('*.png')))==34 and len(list((R/'15_figures').glob('*.pdf')))==34
 assert not any((p.info['name'] or '').lower()=='ansys231.exe' for p in psutil.process_iter(['name']))
 g=read(R/'05_mechanical_preflight/PRE_SOLVE_GATE_SEALED.json')
 for z in g['files']:assert sha(R/z['path'])==z['sha256'],z['path']
 after=[]
 for a in rows(R/'HISTORICAL_INTEGRITY_EXTENDED_AUDIT.csv'):
  h=sha(a['path']);after.append(dict(path=a['path'],expected_sha256=a['expected_sha256'],actual_sha256=h,passed=h==a['expected_sha256']))
 table(R/'17_reproducibility/HISTORICAL_AFTER_CHECK.csv',after);assert all(z['passed'] for z in after)
 env=dict(UTC=now(),Python=sys.version,platform=str(sys.getwindowsversion()),packages={k:importlib.metadata.version(k) for k in ['numpy','scipy','matplotlib','psutil','gmsh','cadquery','Pillow']},ANSYS_executable=str(EXE),ANSYS_executable_SHA256=sha(EXE),ANSYS_version_basis='2023R1Build23.1UP20221128fromactualnativeoutputlogs',resources=memory(),plot_visual_QA=['22_M2_T2_stress_map.png','34_Final_research_decision.png'],source_code_scope='Allsrcfilesincludedinthefinalmanifest')
 write(R/'17_reproducibility/ENVIRONMENT.json',env)
 # Explain any superseded host receipt without deleting the evidence.
 write(R/'17_reproducibility/HOST_INCIDENTS.json',dict(launch_guard=dict(native_invocations=0,reason='Python audit hook received executable=None before CreateProcess; subsequent invocation supplied explicit authorized executable.'),coordinate_audit=dict(native_jobs_repeated=0,observed_native_coordinate_roundoff_mm=1.1368683772161603e-13,interpretation='No intentional geometry change; bitwise assertion corrected to disclosed machine roundoff audit.'),completion_parser=dict(native_jobs_repeated=0,native_failure=False,superseded_file='06_native_M1/SOLVE_FAILED.json',actual_evidence=['Exitcode0','LOADSTEP1SUBSTEP1COMPLETED','RUNCOMPLETED','validRST','validU','reactionbalance','finitetensors'],reason='Initial hostparser searched SOLUTION DONE; actualnativecompletionmarker differs. Corrected by auditing existing outputs only.'),historical_audit_extension=dict(initial_sealed_audit='HISTORICAL_INTEGRITY_AUDIT.csv',expanded_separate_audit='HISTORICAL_INTEGRITY_EXTENDED_AUDIT.csv',sealed_bytes_verified=True),scientific_configurations_changed=0))
 source=read(R1/'MESH_PAIR_RELEASE.json');write(R/'17_reproducibility/ABSOLUTE_INPUT_BINDINGS.json',dict(R1_workspace=str(R1),selected_meshes=read(R/'SELECTED_MESH_HASHES.json'),source_arrays={k:dict(**v,absolute_path=str(R1/v['path']),R2_copy=str(R/'01_protocol_freeze/R1_frozen/source'/k)) for k,v in source['source_arrays'].items()},STEP=dict(**source['authoritative_STEP'],absolute_path=str(R1/source['authoritative_STEP']['path'])),protocol_version=VERSION))
 excluded=['REPRODUCIBILITY_MANIFEST.json','REPRODUCIBILITY_MANIFEST.csv','17_reproducibility/RELEASE_SEAL.json','17_reproducibility/INDEPENDENT_RELEASE_VERIFICATION.json','tmp/**']
 files=[]
 for p in sorted(R.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(R).as_posix()
  if rel in excluded or rel.startswith('tmp/'):continue
  files.append(dict(path=rel,bytes=p.stat().st_size,sha256=sha(p)))
 write(R/'REPRODUCIBILITY_MANIFEST.json',dict(UTC=now(),source_id=SID,status='R8E10R2_COMPLETE',qualified_target='C02_V1_T2_QUALIFIED',protocol_version=VERSION,target_semantics_SHA256=source['target_semantics_SHA256'],historical_paths_rehashed=len(after),excluded=excluded,files=files));table(R/'REPRODUCIBILITY_MANIFEST.csv',files)
 write(R/'17_reproducibility/RELEASE_SEAL.json',dict(UTC=now(),manifest_SHA256=sha(R/'REPRODUCIBILITY_MANIFEST.json'),manifest_CSV_SHA256=sha(R/'REPRODUCIBILITY_MANIFEST.csv'),durable_artifacts=len(files),pre_solve_gate_SHA256=sha(R/'05_mechanical_preflight/PRE_SOLVE_GATE_SEALED.json'),qualified_target_SHA256=rows(R/'QUALIFIED_V1_TARGET_REGISTRY.csv')[0]['target_hash'],scope='Seal binds finaldurablefilemanifest; independentverificationreceiptisexplicitlyexcludedfromself-reference.'))
 print('RELEASE_SEALED',len(files),'historical',len(after),'manifest',sha(R/'REPRODUCIBILITY_MANIFEST.json'),flush=True)
if __name__=='__main__':main()

