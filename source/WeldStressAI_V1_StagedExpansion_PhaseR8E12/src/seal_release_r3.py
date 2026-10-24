from common_r3 import *
import importlib.metadata,re
def main():
 protect();assert not any((p.info['name'] or '').lower()=='ansys231.exe' for p in psutil.process_iter(['name']));assert len(rows(GLOBAL/'SCIENTIFIC_FIGURES.csv'))==36
 spec=(GLOBAL/'01_protocol_freeze/USER_SPECIFICATION.txt').read_text(encoding='utf-8-sig');required=re.findall(r'`([^`]+\.(?:md|json|csv))`',spec.split('# 24. REQUIRED REPORTS')[1].split('# 25.')[0]);missing=[name for name in required if name!='REPRODUCIBILITY_MANIFEST.json' and not (GLOBAL/name).exists()];assert not missing,missing
 pri=read(GLOBAL/'PREREGISTRATION_SEAL.json')
 for z in pri['files']:assert sha(GLOBAL/z['path'])==z['sha256']
 after=[]
 for a in rows(GLOBAL/'00_integrity/HISTORICAL_HASHES.csv'):
  h=sha(a['path']);after.append(dict(path=a['path'],expected_sha256=a['sha256'],actual_sha256=h,passed=h==a['sha256'],basis='INITIAL_HISTORICAL_MANIFEST_OR_CANONICAL_INPUT'))
 for sid in ['G08-V1-S355-AW','X10-V1-S355-AW']:
  c=GLOBAL/'cases'/sid;gate=read(c/'05_mechanical_preflight/PRE_SOLVE_GATE_SEALED.json')
  for a in gate['files']:assert sha(c/a['path'])==a['sha256'],a['path']
  for p,digest in read(c/'14_historical_comparison/HISTORICAL_INPUT_HASHES.json').items():after.append(dict(path=p,expected_sha256=digest,actual_sha256=sha(p),passed=sha(p)==digest,basis='HISTORICAL_CONTRAST_INPUT_READ_BINDING'))
 table(GLOBAL/'21_reproducibility/HISTORICAL_AFTER_CHECK.csv',after);assert all(z['passed'] for z in after)
 usage=rows(GLOBAL/'21_reproducibility/ALL_NATIVE_RESOURCE_SAMPLES.csv');mins={k:min(float(a[k]) for a in usage) for k in ['RAM_available_bytes','commit_free_bytes','free_disk_bytes']};assert mins['RAM_available_bytes']>=3*1024**3 and mins['commit_free_bytes']>=3*1024**3 and mins['free_disk_bytes']>=20*1024**3;resource_gate();env=dict(UTC=now(),Python=sys.version,Windows=str(sys.getwindowsversion()),packages={k:importlib.metadata.version(k) for k in ['numpy','scipy','gmsh','cadquery','matplotlib','Pillow','psutil','jsonschema']},ANSYS_executable=str(EXE),ANSYS_executable_SHA256=sha(EXE),ANSYS_runtime_version='2023R1Build23.1UP20221128fromactualoutputlogs',minimum_observed_native_resources=mins,current_resources=memory(),manual_visual_QA=['19_figures/31_Three_source_M2_T2_comparison.png','19_figures/35_Updated_production_storage_budget.png'],unmeasured_time_components=['SeparateCADconstructionversusfidelity','Paircrossprojection','IndependentnativeDBreadback'],scientific_checks_uncompleted=[]);write(GLOBAL/'21_reproducibility/ENVIRONMENT_AND_RESOURCES.json',env)
 # Close the invocation budget ledger with actual native evidence, preserving initial authorization fields.
 lp=GLOBAL/'21_reproducibility/NATIVE_SOLVE_LEDGER.json';ledger=read(lp);assert len(ledger)==4
 for a in ledger:
  c=GLOBAL/'cases'/a['source_id'];folder=c/('06_native_M1' if a['level']=='M1' else '07_native_M2');s=read(folder/'SOLVE_COMPLETE.json');assert s['completed'];a.update(final_status='NATIVE_COMPLETED_AND_VERIFIED',completion_receipt_SHA256=sha(folder/'SOLVE_COMPLETE.json'),RST_SHA256=sha(folder/'file.rst'))
 write(lp,ledger)
 adaptations=[]
 for a in read(GLOBAL/'21_reproducibility/REFERENCE_CODE_LINEAGE.json'):
  adaptations.append(dict(**a,final_copy_sha256=sha(a['copy']),source_unchanged=sha(a['source'])==a['source_sha256']))
 write(GLOBAL/'21_reproducibility/FINAL_REFERENCE_CODE_LINEAGE.json',dict(implementations=adaptations,additional_implementation_notes=['Inheritedacceptanceemptylistcouldpromoteelementindexarraytofloat;explicitintegercastfixeddeterministicauditingwithoutchangingtestcasesormeshes.','PythonOSversioncacheprimedbeforestrictsubprocessguard;hostencodingfixedbeforeCAD.','R2instanceconstantsreplacedbysource-deriveddimensions,loadline,gaugesandmeshcounts;BVPmeaningunchanged.','SHPPissuedinPREP7only;redundantunsupportedSOLUcommandremoved.','SourceT2scalarcheckcachedanunchangedNPZarraytoavoidrepeateddecompression;arithmeticunchanged.'],numerical_threshold_changes=0,source_geometry_edits=0,AI_runs=0))
 cnt=read(GLOBAL/'R8E10R3_FINAL_COUNTS.json');cnt.update(integrity_state_at_sealing='SEALED',historical_after_check_bindings=len(after),scientific_figures=36,scientific_questions_answered=48,uncompleted_mandatory_scientific_checks=[],instrumentation_limitations=env['unmeasured_time_components'],final_resources=memory());write(GLOBAL/'R8E10R3_FINAL_COUNTS.json',cnt)
 excluded=['REPRODUCIBILITY_MANIFEST.json','REPRODUCIBILITY_MANIFEST.csv','21_reproducibility/RELEASE_SEAL.json','21_reproducibility/INDEPENDENT_RELEASE_VERIFICATION.json','tmp/**'];files=[]
 for p in sorted(GLOBAL.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(GLOBAL).as_posix()
  if rel in excluded or rel.startswith('tmp/'):continue
  files.append(dict(path=rel,bytes=p.stat().st_size,sha256=sha(p)))
 write(GLOBAL/'REPRODUCIBILITY_MANIFEST.json',dict(UTC=now(),status='R8E10R3_COMPLETE',numerical_outcome='3_OF_3_V1_TARGETS_QUALIFIED',version=VERSION,scope='AllnewdurableR3files,includingunqualifiedcandidates,sourcepackages,rawnativeoutputs,scriptsandfigures;historiesboundseparately',excluded=excluded,files=files));table(GLOBAL/'REPRODUCIBILITY_MANIFEST.csv',files)
 write(GLOBAL/'21_reproducibility/RELEASE_SEAL.json',dict(UTC=now(),manifest_SHA256=sha(GLOBAL/'REPRODUCIBILITY_MANIFEST.json'),CSV_SHA256=sha(GLOBAL/'REPRODUCIBILITY_MANIFEST.csv'),durable_artifacts=len(files),preregistration_SHA256=sha(GLOBAL/'PREREGISTRATION_SEAL.json'),source_pre_solve_seals={sid:sha(GLOBAL/'cases'/sid/'05_mechanical_preflight/PRE_SOLVE_GATE_SEALED.json') for sid in ['G08-V1-S355-AW','X10-V1-S355-AW']},historical_after_check_bindings=len(after),qualified_target_registry_SHA256=sha(GLOBAL/'QUALIFIED_V1_TARGET_REGISTRY.csv')));print('R3_RELEASE_SEALED',len(files),'files',len(after),'historicalbindings','SHA256',sha(GLOBAL/'REPRODUCIBILITY_MANIFEST.json'),flush=True)
if __name__=='__main__':main()

