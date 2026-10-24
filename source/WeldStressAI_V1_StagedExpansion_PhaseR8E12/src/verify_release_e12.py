"""Independent read-only release verification. No scientific/native jobs can be launched."""
from pathlib import Path
import json,csv,hashlib,sys,re,datetime,math,shutil
import numpy as np
R=Path(__file__).resolve().parents[1];P=R.parent/'WeldStressAI_V1_Expansion_PhaseR8E11R1';GiB=1024**3
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rows(p):
 with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
_hash_cache={}
def sha(p):
 p=Path(p).resolve();st=p.stat();key=(str(p),st.st_size,st.st_mtime_ns)
 if key not in _hash_cache:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
  assert p.stat().st_mtime_ns==st.st_mtime_ns and p.stat().st_size==st.st_size
  _hash_cache[key]=h.hexdigest()
 return _hash_cache[key]

def independent_quantile(v,w):
 pairs=sorted(zip(v,w),key=lambda a:float(a[0]));total=math.fsum(float(b) for a,b in pairs);cum=0.;prev=0.;pv=float(pairs[0][0])
 for value,weight in pairs:
  cum+=float(weight);frac=cum/total
  if frac>=.95:return pv+(float(value)-pv)*(.95-prev)/(frac-prev)
  prev=frac;pv=float(value)
def independent_tensor(points,u,L):
 dL=np.array([[-1.,-1.,-1.],[1.,0,0],[0,1.,0],[0,0,1.]])
 D=np.array([(4*L[i]-1)*dL[i] for i in range(4)]+[4*(L[a]*dL[b]+L[b]*dL[a]) for a,b in [(0,1),(1,2),(2,0),(0,3),(1,3),(2,3)]])
 jac=points.T@D;spatial=np.linalg.solve(jac.T,D.T).T;grad=u.T@spatial;eps=(grad+grad.T)/2;mu=210000/(2*1.30);lam=210000*.30/(1.30*.40);stress=2*mu*eps+lam*np.trace(eps)*np.eye(3);return np.array([stress[0,0],stress[1,1],stress[2,2],stress[0,1],stress[1,2],stress[0,2]]),max(0,float(np.linalg.eigvalsh(stress)[-1]))
def main():
 seal=read(R/'25_reproducibility/RELEASE_SEAL.json');manifest=read(R/'REPRODUCIBILITY_MANIFEST.json');assert sha(R/'REPRODUCIBILITY_MANIFEST.json')==seal['manifest_SHA256'];assert sha(R/'REPRODUCIBILITY_MANIFEST.csv')==seal['CSV_SHA256']
 for a in manifest['files']:
  p=R/a['path'];assert p.exists() and p.stat().st_size==a['bytes'] and sha(p)==a['sha256'],str(p)
 listed={a['path'] for a in manifest['files']}
 for p in R.rglob('*'):
  if p.is_file():
   rel=p.relative_to(R).as_posix();assert rel in listed or rel in manifest['excluded'] or rel.startswith('tmp/'),rel
 hist=rows(R/'00_integrity/HISTORICAL_HASHES.csv');assert len(hist)>=1432
 for a in hist:assert sha(a['path'])==a['sha256'],a['path']
 for a in rows(R/'25_reproducibility/HISTORICAL_AFTER_CHECK.csv'):assert sha(a['path'])==a['expected_sha256']==a['actual_sha256'] and a['passed']=='True'
 for a in read(R/'PREREGISTRATION_SEAL.json')['files']:assert sha(R/a['path'])==a['sha256']
 gate=read(R/'RESOURCE_GATE_DECISION.json');assert gate['decision']=='RESOURCE_PREFLIGHT_PASS' and all(gate['checks'].values())
 queue=rows(R/'FROZEN_SELECTED_FIVE_SOURCES.csv');assert len(queue)==5 and len({a['source_id'] for a in queue})==5
 for a in read(R/'SOURCE_SELECTION_SEAL.json')['files']:assert sha(R/a['path'])==a['sha256']
 from selection_audit_e12 import audit_selection
 audit_selection()
 from audit_lineage_e12 import audit_lineage
 assert audit_lineage()['status']=='PASS'
 for a in rows(R/'25_reproducibility/ORIGINAL_ARCHIVE_SHA256_VERIFICATION.csv'):assert sha(a['path'])==a['expected_SHA256']==a['actual_SHA256']
 for a in read(R/'00_integrity/SCIENTIFIC_KERNEL_REUSE.json')['modules']:assert sha(R/'src'/a['module'])==a['new_SHA256']==a['historical_SHA256']
 final=read(R/'R8E12_FINAL_COUNTS.json');gl=read(R/'21_reproducibility/NATIVE_SOLVE_LEDGER.json') if (R/'21_reproducibility/NATIVE_SOLVE_LEDGER.json').exists() else [];assert len(gl)<=10 and len({(a['source_id'],a['level']) for a in gl})==len(gl);assert len(gl)==final['actual_native_SOLVE_invocations']
 reg=rows(R/'CUMULATIVE_QUALIFIED_V1_TARGET_REGISTRY.csv');new=rows(R/'NEW_QUALIFIED_V1_TARGET_REGISTRY.csv');assert len(reg)==8+len(new)==final['cumulative_qualified_targets'];assert len({a['source_id'] for a in reg})==len(reg);assert len(new)==final['new_qualified_targets']
 for a in reg:assert sha(a['qualified_M2_target_path'])==a['qualified_M2_target_SHA256']
 for a in rows(R/'HISTORICAL_V1_TARGET_HASHES.csv'):assert sha(a['target_path'])==a['target_hash']
 test=(R/'00_integrity/E9_46_TESTS.log').read_text(encoding='utf-8-sig');assert 'Ran 46 tests' in test and test.rstrip().endswith('OK')
 for n in ['R2_READONLY_VERIFICATION.log','R3_READONLY_VERIFICATION.log','E11_READONLY_VERIFICATION.log','E11R1_READONLY_VERIFICATION.log']:
  text=(R/'00_integrity'/n).read_text(encoding='utf-8-sig');assert ('"status": "PASS"' in text or '"integrity_status": "PASS"' in text) and 'Traceback' not in text
 for sid,files in read(R/'SOURCE_HASHES.json').items():
  for p,h in files.items():assert sha(p)==h
 qualified={a['source_id'] for a in new};solve_success=preprocessing=packages=scalar_tensor_points=scalar_T2_points=0;max_tensor_error=max_t2_error=0.;prior_end=None;observed_stage_order=[]
 for z in queue:
  sid=z['source_id'];c=R/'cases'/sid;ls=read(c/'CONTROL_STAGE_LEDGER.json') if (c/'CONTROL_STAGE_LEDGER.json').exists() else []
  if not ls:continue
  assert datetime.datetime.fromisoformat(ls[0]['UTC'])>datetime.datetime.fromisoformat(gate['UTC'])
  if prior_end:assert datetime.datetime.fromisoformat(ls[0]['UTC']).timestamp()>=prior_end
  if sid not in qualified:
   assert (R/'21_reproducibility/CAMPAIGN_STOP.json').exists()
   for a in ls:
    if a.get('log_SHA256'):assert sha(c/(a['stage']+'.log'))==a['log_SHA256']
   nl=read(c/'17_reproducibility/NATIVE_INVOCATION_LEDGER.json') if (c/'17_reproducibility/NATIVE_INVOCATION_LEDGER.json').exists() else []
   preprocessing+=sum(a['kind'].startswith('PREPROCESS') for a in nl)
   invoked=[a for a in nl if a['kind']=='SOLVE'];assert len(invoked)<=2 and len({a['level'] for a in invoked})==len(invoked)
   for a in invoked:
    l=a['level'];observed_stage_order.append((sid,l));fol=c/('06_native_M1' if l=='M1' else '07_native_M2');assert sha(fol/'input.dat')==a['input_sha256']
    if (fol/'SOLVE_COMPLETE.json').exists():
     comp=read(fol/'SOLVE_COMPLETE.json');assert comp['completed'] and comp['equilibrium_passed'] and comp['native_errors']==0
     for name,h in comp['files'].items():assert sha(fol/name)==h
     solve_success+=1
   continue
  assert all(a['status']=='COMPLETED' for a in ls);prior_end=datetime.datetime.fromisoformat(ls[-1]['UTC']).timestamp()+ls[-1]['elapsed_s']
  for a in ls:assert sha(c/(a['stage']+'.log'))==a['log_SHA256']
  source=c/'01_frozen_protocol/source';support=np.load(c/'01_protocol_freeze/TARGET_GEOMETRY_SUPPORT.npz');ids=np.load(source/'source_ids.npy');xyz=np.load(source/'xyz.npy');area=np.load(source/'area.npy');assert np.array_equal(ids,support['source_ids']) and np.array_equal(xyz,support['xyz']) and np.array_equal(area,support['area'])
  for n in ['xyz.npy','source_ids.npy','triangles.npy','area.npy','normal.npy']:
   assert any(sha(source/n)==h for p,h in read(R/'SOURCE_HASHES.json')[sid].items() if Path(p).name==n)
  presolve=read(c/'05_mechanical_preflight/PRE_SOLVE_GATE_SEALED.json');assert presolve['decision']=='PASS'
  for a in presolve['files']:assert sha(c/a['path'])==a['sha256']
  assert read(c/'01_frozen_protocol/SCHEMA_AUDIT.json')['BVP_schema_pass'];assert read(c/'04_standardized_solids'/sid/'CAD_QUALIFICATION.json')['passed'];assert read(c/'10_mesh_hierarchy/PAIR_QUALIFICATION.json')['passed']
  cadledger=read(c/'17_reproducibility/CAD_ATTEMPTS.json');assert len(cadledger)<=2
  candidates=read(c/'14_reproducibility/FULL_CANDIDATE_LEDGER.json');assert all(sum(a['mesh_level']==l for a in candidates)<=3 for l in ['M1','M2']);nledger=read(c/'17_reproducibility/NATIVE_INVOCATION_LEDGER.json');preprocessing+=sum(a['kind'].startswith('PREPROCESS') for a in nledger)
  solves=[a for a in nledger if a['kind']=='SOLVE'];assert [a['level'] for a in solves]==['M1','M2'];assert all(a['status']=='NATIVE_COMPLETED_AND_VERIFIED' and a['exit_code']==0 for a in solves)
  selected=read(c/'SELECTED_MESHES.json');raws={}
  for l,folder in [('M1','06_native_M1'),('M2','07_native_M2')]:
   observed_stage_order.append((sid,l));native=c/folder;s=read(native/'SOLVE_COMPLETE.json');assert s['completed'] and s['equilibrium_passed'] and s['force_residual_relative']<=1e-5 and s['moment_residual_over_Ft']<=1e-5 and s['native_errors']==0
   for name,h in s['files'].items():assert sha(native/name)==h
   txt=(native/'solve.out').read_text(errors='replace');assert 'RUN COMPLETED' in txt and re.search(r'LOAD STEP\s+1\s+SUBSTEP\s+1\s+COMPLETED',txt);deck=(native/'input.dat').read_text();assert deck.splitlines().count('SOLVE')==1 and 'NLGEOM,OFF' in deck and 'EQSLV,PCG,1e-8' in deck
   mesh=np.load(Path(selected[l]['folder'])/'mesh.npz');assert sha(Path(selected[l]['folder'])/'mesh.npz')==selected[l]['sha256'];qq=read(Path(selected[l]['folder'])/'PRE_SOLVER_QUALIFICATION.json');assert qq['pre_solver_qualified'] and qq['minSICN']>=.02 and qq['minimum_Q1_J_mm3']>0 and qq['nodes']<=350000 and qq['Tet10']<=230000;assert read(Path(selected[l]['folder'])/'SOURCE_FIDELITY.json')['passed'];u=np.load(native/'native_displacements.npz');assert np.array_equal(u['connectivity_native'],mesh['tet10'][:,[0,1,2,3,4,5,6,7,9,8]]);assert abs(u['xyz']-mesh['xyz']).max()<1e-12
   mapping=np.load(c/'10_source_mapping'/l/'SOURCE_MAPPING.npz');assert np.array_equal(mapping['xyz'],xyz) and np.array_equal(mapping['source_ids'],ids) and np.array_equal(mapping['area'],area);assert read(c/'10_source_mapping'/l/'MAPPING_AUDIT.json')['passed'];valid=mapping['valid'];tensor=mapping['tensor'];sigma=mapping['sigma1_tensile'];nativeID=mapping['native_element_id'];bary=mapping['L'];conn=u['connectivity_native'];positions=np.flatnonzero(valid);pick=positions[np.linspace(0,len(positions)-1,32,dtype=int)]
   for i in pick:
    nodes=conn[nativeID[i]-1];v,pmax=independent_tensor(u['xyz'][nodes],u['u'][nodes],bary[i]);err=max(float(abs(v-tensor[i]).max()),abs(pmax-sigma[i]));assert err<=1e-7;max_tensor_error=max(max_tensor_error,err);scalar_tensor_points+=1
   target=np.load(c/('11_T2_M1' if l=='M1' else '12_T2_M2')/'SOURCE_T2.npz');assert np.array_equal(target['xyz'],xyz) and np.array_equal(target['source_ids'],ids) and np.array_equal(target['area'],area) and np.array_equal(target['core'],support['core']);assert np.isfinite(target['T2_MPa'][target['valid']]).all();assert np.isnan(target['T2_MPa'][~target['valid']]).all();raws[l]=target['T2_MPa'].copy();ii=np.flatnonzero(target['valid']);pick=ii[np.linspace(0,len(ii)-1,64,dtype=int)]
   for i in pick:
    nb=np.flatnonzero(np.sum((xyz-xyz[i])**2,axis=1)<=(1+1e-7)**2);assert valid[nb].all();value=math.fsum(float(area[j])*float(sigma[j]) for j in nb)/math.fsum(float(area[j]) for j in nb);err=abs(value-target['T2_MPa'][i]);assert err<=1e-8;max_t2_error=max(max_t2_error,err);scalar_T2_points+=1
   # CSV roundtrip: full original XYZ/ID/T0area and every valid T2 value.
   rr=rows(c/f'SOURCE_T2_{l}.csv');assert len(rr)==len(xyz);assert np.array_equal([int(a['source_id']) for a in rr],ids);assert np.array_equal([[float(a[k]) for k in ['X','Y','Z']] for a in rr],xyz);assert np.array_equal([float(a['T0_area_mm2']) for a in rr],area);assert np.array_equal([float(a['T2_MPa']) for a in rr if a['valid_T2']=='True'],target['T2_MPa'][target['valid']]);solve_success+=1
  field=np.load(c/'13_numerical_qualification/COMPARISON_FIELDS.npz');mask=field['common'];v1=raws['M1'];v2=raws['M2'];assert np.array_equal(field['area'],area);qual=read(c/'13_numerical_qualification/QUALIFICATION_DECISION.json');assert qual['qualified'] and all(qual['checks'].values());met=read(c/'13_numerical_qualification/COMPLETE_METRICS.json')
  l2=math.sqrt(math.fsum(float(w)*float(a-b)**2 for w,a,b in zip(area[mask],v1[mask],v2[mask]))/math.fsum(float(w)*float(b)**2 for w,b in zip(area[mask],v2[mask])));assert abs(l2-met['whole_L2'])<1e-12 and l2<=.02
  regionvalues=[]
  for region in [0,1,2]:
   mk=mask&(field['region']==region);val=math.sqrt(math.fsum(float(w)*float(a-b)**2 for w,a,b in zip(area[mk],v1[mk],v2[mk]))/math.fsum(float(w)*float(b)**2 for w,b in zip(area[mk],v2[mk])));regionvalues.append(val)
  assert abs(max(regionvalues)-met['worst_regional_L2'])<1e-12 and max(regionvalues)<=.03
  q1=independent_quantile(v1[mask],area[mask]);q2=independent_quantile(v2[mask],area[mask]);ha=mask&(v1>=q1);hb=mask&(v2>=q2);iou=math.fsum(float(w) for w in area[ha&hb])/math.fsum(float(w) for w in area[ha|hb]);assert abs(iou-met['high95_area_IoU'])<1e-12 and iou>=.8
  for name,values in [('M1_mean_T2_MPa',v1[mask]),('M2_mean_T2_MPa',v2[mask])]:
   mean=math.fsum(float(w)*float(v) for w,v in zip(area[mask],values))/math.fsum(float(w) for w in area[mask]);assert abs(mean-met[name])<1e-9
  for a in rows(c/'T2_COMPLETE_INDEPENDENT_AUDIT.csv'):assert a['passed']=='True'
  pkg=c/'QUALIFIED_V1_PACKAGE';pm=read(pkg/'REPRODUCIBILITY_MANIFEST.json')
  for a in pm['files']:assert sha(pkg/a['path'])==a['sha256'];packages+=1
  pmeta=read(pkg/'TARGET_PROVENANCE.json');assert pmeta['source_id']==sid and not pmeta['AI_training'] and not pmeta['AI_inference'];assert pmeta['CAD_SHA256']==sha(c/'01_frozen_protocol/geometry/standardized_planar_rear.step');assert sha(pkg/'T2_M2.npz')==pmeta['target_SHA256'];assert np.array_equal(np.load(pkg/'original_T0_triangles.npy'),np.load(source/'triangles.npy'))
  print('SOURCE_INDEPENDENTLY_VERIFIED',sid,flush=True)
 assert [(a['source_id'],a['level']) for a in gl]==observed_stage_order;assert solve_success==final['successful_native_solutions'];assert preprocessing==final['native_preprocessing_jobs']
 samples=rows(R/'04_resource_preflight/CONTROLLER_RESOURCE_SAMPLES.csv');assert max(int(a['workspace_bytes']) for a in samples)<=24*GiB;assert min(int(a['E_free_bytes']) for a in samples)>=20*GiB;assert min(int(a['C_free_bytes']) for a in samples)>=2*GiB;assert min(int(a['RAM_available_bytes']) for a in samples)>=3*GiB and min(int(a['commit_free_bytes']) for a in samples)>=3*GiB
 workspace=sum(p.stat().st_size for p in R.rglob('*') if p.is_file());assert workspace<=24*GiB and shutil.disk_usage(R).free>=20*GiB
 spec=(R/'R8E12_USER_SPECIFICATION.txt').read_text(encoding='utf-8-sig');required=re.findall(r'\x60([^\x60]+\.(?:md|json|csv))\x60',spec.split('# 27. REQUIRED REPORTS')[1].split('# 29.')[0]);assert all((R/n).exists() for n in required);assert len(re.findall(r'^### \d+\.',(R/'R8E12_MASTER_REPORT.md').read_text(),re.M))==56
 from PIL import Image
 figs=rows(R/'SCIENTIFIC_FIGURES.csv')
 for a in figs:
  with Image.open(R/a['PNG']) as im:im.verify()
  assert (R/a['PDF']).read_bytes().startswith(b'%PDF')
 out=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),integrity_status='PASS',campaign_status=final['campaign_status'],durable_artifacts_verified=len(manifest['files']),historical_bindings_rehashed=len(hist),protocol_tests=46,prospective_E12_authorization=True,selection_independently_replayed=True,selection_before_production=True,actual_SOLVEs=len(gl),successful_solutions=solve_success,repeated_SOLVEs=0,native_preprocessing_jobs=preprocessing,new_qualified_targets=len(new),cumulative_qualified_targets=len(reg),source_CSV_roundtrip='EXACT',new_independent_scalar_tensor_points=scalar_tensor_points,max_new_tensor_error_MPa=max_tensor_error,new_independent_bruteforce_T2_points=scalar_T2_points,max_new_T2_error_MPa=max_t2_error,independent_whole_regional_L2_high95_means='PASS',qualified_package_files_rehashed=packages,actual_final_workspace_bytes=workspace,current_free_E_bytes=shutil.disk_usage(R).free,sampled_workspace_peak_bytes=max(int(a['workspace_bytes']) for a in samples),minimum_sampled_free_E_bytes=min(int(a['E_free_bytes']) for a in samples),minimum_sampled_free_C_bytes=min(int(a['C_free_bytes']) for a in samples),sampling_not_continuous_peak=True,figures_PNG_PDF_pairs=len(figs),questions_explicitly_answered=56,required_named_outputs=len(required),historical_files_modified=False,AI_training=False,AI_inference=False,external_predictions=False,physical_validation=False,independent_generalization=False,manifest_SHA256=seal['manifest_SHA256'])
 out.update(minimum_sampled_available_RAM_bytes=min(int(a['RAM_available_bytes']) for a in samples),minimum_sampled_available_commit_bytes=min(int(a['commit_free_bytes']) for a in samples))
 if '--write-receipt' in sys.argv:(R/'25_reproducibility/INDEPENDENT_RELEASE_VERIFICATION.json').write_text(json.dumps(out,indent=2),encoding='utf8')
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
