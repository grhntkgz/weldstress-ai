from common_r1 import *
import ast,urllib.request
def main():
 for d in ['00_integrity/baseline','01_frozen_protocol/geometry','01_frozen_protocol/source','01_frozen_protocol/reference_code','02_invalid_element_diagnosis','03_local_mesh_topology','04_repair_strategies','05_local_repair_trials','06_recovered_M1','07_refined_M2','08_quadratic_quality','09_source_geometry_fidelity','10_mesh_hierarchy','11_mechanical_mesh_preflight','12_figures','13_reports','14_reproducibility','src/vendor','tmp']:(R/d).mkdir(parents=True,exist_ok=True)
 protect();resource_gate(500*1024**2,800*1024**2,1024**3);shutil.copyfile(Path('C:/Users/grhnt.DESKTOP-KRBB26F/.codex/attachments/a2620bb8-b31b-4a1c-a700-8f968bd50192/Pasted text.txt'),R/'01_frozen_protocol/EXECUTION_SPECIFICATION.txt')
 manifest=read(E10/'REPRODUCIBILITY_MANIFEST.json');seal=read(E10/'17_reproducibility/RELEASE_SEAL.json');assert sha(E10/'REPRODUCIBILITY_MANIFEST.json')==seal['manifest_SHA256'];checks=[]
 for z in manifest['files']:assert sha(E10/z['path'])==z['sha256'];checks.append(dict(path=str(E10/z['path']),sha256=z['sha256'],passed=True))
 for z in read(E9/'06_evidence/PROTOCOL_FREEZE.json')['files']:assert sha(E9/z['path'])==z['sha256'];checks.append(dict(path=str(E9/z['path']),sha256=z['sha256'],passed=True))
 selections={'R8E10_MASTER_REPORT.md':'01_frozen_protocol/R8E10_MASTER_REPORT.md','R8E10_GATE_DECISIONS.csv':'01_frozen_protocol/R8E10_GATE_DECISIONS.csv','SOURCE_CAD_FIDELITY.csv':'01_frozen_protocol/SOURCE_CAD_FIDELITY.csv','SOURCE_FE_FIDELITY.csv':'01_frozen_protocol/SOURCE_FE_FIDELITY.csv','M1_M2_MESH_QUALITY.csv':'01_frozen_protocol/M1_M2_MESH_QUALITY.csv','MEASURED_ASSUMED_PATCHES.csv':'01_frozen_protocol/MEASURED_ASSUMED_PATCHES.csv','17_reproducibility/CAMPAIGN_STOP.json':'01_frozen_protocol/ORIGINAL_CAMPAIGN_STOP.json','08_mesh_quality/INVALID_ELEMENT_COORDINATES.csv':'01_frozen_protocol/INVALID_ELEMENT_COORDINATES.csv','08_mesh_quality/INDEPENDENT_FAILURE_VERIFICATION.json':'01_frozen_protocol/INDEPENDENT_FAILURE_VERIFICATION.json'}
 for name in ['mesh.npz','mesh.msh','linear_checkpoint.msh','MESH_QUALIFICATION.json','QUADRATIC_GEOMETRY_AUDIT.npz','MESH_GENERATION.json']:selections[f'06_M1_meshes/{SID}/{name}']='00_integrity/baseline/'+name
 for name in ['standardized_planar_rear.step','solid_source.npz','CAD_QUALIFICATION.json']:selections[f'04_standardized_solids/{SID}/{name}']='01_frozen_protocol/geometry/'+name
 selections[f'03_parent_datum/{SID}.json']='01_frozen_protocol/PARENT_DATUM.json';selections[f'09_mechanical_BVP/{SID}_ANALYTIC.json']='01_frozen_protocol/ANALYTIC_BVP.json'
 copied=[]
 for old,new in selections.items():shutil.copyfile(E10/old,R/new);copied.append(dict(path=str(E10/old),copy=new,sha256=sha(R/new)))
 for name in ['TARGET_VERSION_SCHEMA.json','STANDARD_BVP_SCHEMA.json','REAR_PLANE_RULE_SCHEMA.json','QUALIFICATION_GATE_DEFINITIONS.json']:
  shutil.copyfile(E9/name,R/'01_frozen_protocol'/name)
 for name in ['TARGET_STANDARD_PLANAR_V1.json','REAR_PLANE_RULE_V1.json','STANDARD_BVP_V1.json','NEXT_FE_PILOT_PREREGISTRATION.json']:
  shutil.copyfile(E9/'03_config'/name,R/'01_frozen_protocol'/name)
 for name in ['xyz.npy','triangles.npy','source_ids.npy','area.npy','normal.npy']:
  p=E3/'02_geometry/single'/SID/name;shutil.copyfile(p,R/'01_frozen_protocol/source'/name);checks.append(dict(path=str(p),sha256=sha(p),passed=True))
 for name in ['shape5e.py']:shutil.copyfile(E10/'src/vendor'/name,R/'src/vendor'/name)
 # Exact established geometry evaluator functions relocated; candidate generator is not imported.
 code=(E10/'src/geometry_e10.py').read_text(encoding='utf8');tree=ast.parse(code);func=[ast.get_source_segment(code,n) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['original_height','closest_T0']];(R/'src/reference_r1.py').write_text('from common_r1 import *\n'+'\n\n'.join(func)+'\n',encoding='utf8')
 code=(E10/'src/mesh_e10.py').read_text(encoding='utf8');tree=ast.parse(code);func=[ast.get_source_segment(code,n) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['project','tetshape']];(R/'src/fidelity_math_r1.py').write_text("from common_r1 import *\nfrom scipy.spatial import cKDTree\nsys.path.insert(0,str(R/'src/vendor'))\nfrom shape5e import tri,Q\n"+'\n\n'.join(func)+'\n',encoding='utf8')
 for name in ['mesh_e10.py','geometry_e10.py','diagnose_e10.py']:shutil.copyfile(E10/'src'/name,R/'01_frozen_protocol/reference_code'/name)
 # Official version-pinned implementation is retained for independent SICN definition/provenance.
 urls=[('CondNumBasis.cpp','https://raw.githubusercontent.com/gmsh-project/gmsh/gmsh_4_15_2/src/numeric/CondNumBasis.cpp'),('GradientBasis.cpp','https://raw.githubusercontent.com/gmsh-project/gmsh/gmsh_4_15_2/src/numeric/GradientBasis.cpp'),('MElement.cpp','https://raw.githubusercontent.com/gmsh-project/gmsh/gmsh_4_15_2/src/geo/MElement.cpp')];refs=[]
 for name,url in urls:
  dest=R/'01_frozen_protocol/reference_code'/name
  try:dest.write_bytes(urllib.request.urlopen(url,timeout=30).read());refs.append(dict(url=url,path=str(dest.relative_to(R)),sha256=sha(dest),status='DOWNLOADED_PRIMARY_VERSION_PINNED_SOURCE'))
  except Exception as e:refs.append(dict(url=url,path=None,sha256=None,status=str(e)))
 write(R/'01_frozen_protocol/METHOD_REFERENCES.json',refs);table(R/'00_integrity/HISTORICAL_HASHES.csv',checks);write(R/'00_integrity/FROZEN_COPIES.json',copied)
 write(R/'00_integrity/INITIALIZATION.json',dict(UTC=now(),passed=True,E10_verified=336,E9_frozen_files=158,original_mesh_SHA256=sha(R/'00_integrity/baseline/mesh.npz'),STEP_SHA256=sha(R/'01_frozen_protocol/geometry/standardized_planar_rear.step'),native_jobs_authorized=0,AI_runs_authorized=0,source_identity=SID,resources=memory(),authority='R1 explicitly authorizes bounded C02 recovery despite preserved historical stop. No G08/X10 work.'))
 print('R1_INITIALIZED',sha(R/'01_frozen_protocol/geometry/standardized_planar_rear.step'),flush=True)
if __name__=='__main__':main()
