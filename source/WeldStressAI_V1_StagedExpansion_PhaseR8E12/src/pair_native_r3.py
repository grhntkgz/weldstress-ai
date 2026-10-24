from common_r3 import *
from fidelity_math_r1 import project,Q,tri
from quality_r1 import custom_quality,samples_Q2
from bernstein_r1 import certify
import re

def pair():
 from pair_preflight_r1 import mechanical
 sel=read(R/'SELECTED_MESHES.json');assert set(sel)=={'M1','M2'}
 for l in ['M1','M2']:
  assert sha(LEVELS[l]/'mesh.npz')==sel[l]['sha256'];assert read(LEVELS[l]/'PRE_SOLVER_QUALIFICATION.json')['pre_solver_qualified'];mechanical(LEVELS[l])
 a=read(LEVELS['M1']/'SOURCE_FIDELITY.json');b=read(LEVELS['M2']/'SOURCE_FIDELITY.json');receipt=dict(source_id=SID,UTC=now(),median_edge_ratio=b['near_weld_edge_median_mm']/a['near_weld_edge_median_mm'],P90_edge_ratio=b['near_weld_edge_P90_mm']/a['near_weld_edge_P90_mm'],surface_density_ratio=b['front_face_density_per_mm2']/a['front_face_density_per_mm2'],same_authoritative_STEP_SHA256=sha(R/'01_frozen_protocol/geometry/standardized_planar_rear.step'))
 receipt['passed']=receipt['median_edge_ratio']<=.98 and receipt['P90_edge_ratio']<=.98 and receipt['surface_density_ratio']>1
 comparison=[]
 for source,target in [('M1','M2'),('M2','M1')]:
  sm=np.load(LEVELS[source]/'mesh.npz');tm=np.load(LEVELS[target]/'mesh.npz');sf=np.load(LEVELS[source]/'FULL_SOURCE_FIDELITY.npz');tf=np.load(LEVELS[target]/'FULL_SOURCE_FIDELITY.npz')
  for patch in ['MEASURED_FRONT','ASSUMED_REAR','XMIN_CAP','XMAX_CAP','YMIN_CAP','YMAX_CAP']:
   co=sm['xyz'][sm['tri6'][sf['patch_labels']==patch]];faces=tm['tri6'][tf['patch_labels']==patch];pts=np.concatenate([np.einsum('i,eij->ej',tri(r,s)[0],co) for r,s,w in Q]);perm=[0,1,2] if patch in ['MEASURED_FRONT','ASSUMED_REAR'] else [1,2,0] if patch.startswith('X') else [0,2,1];gap,viol,linear,cl=project(tm['xyz'][:,perm],faces,pts[:,perm]);comparison.append(dict(source_id=SID,direction=source+'to'+target,patch=patch,samples=len(pts),quad_chart_P95_mm=float(np.percentile(gap,95)),quad_chart_max_mm=float(gap.max()),bounded_quad_closest_max_mm=float(cl.max())))
 table(R/'10_mesh_hierarchy/QUADRATIC_DOMAIN_COMPARISON.csv',comparison);receipt['maximum_symmetric_quadratic_chart_gap_mm']=max(z['quad_chart_max_mm'] for z in comparison);write(R/'10_mesh_hierarchy/PAIR_QUALIFICATION.json',receipt)
 from gate_r2 import freeze_support
 freeze_support();print('PAIR_GEOMETRY_PREFLIGHT',receipt,flush=True);assert receipt['passed']

def independent_loads():
 from scipy.special import roots_legendre
 r,w=roots_legendre(6);r=(r+1)/2;w=w/2;origin=case_origin();result=[]
 for l in ['M1','M2']:
  m=np.load(LEVELS[l]/'mesh.npz');xx=m['xyz'];labels=np.load(LEVELS[l]/'FULL_SOURCE_FIDELITY.npz')['patch_labels'];bvp=read(R/'02_mesh_import'/l/'BVP_ASSEMBLY.json');saved=np.load(R/'02_mesh_import'/l/'assembled_BVP.npz')['forces'];ind=np.zeros_like(xx)
  for port,side in zip(bvp['ports'],[-1,1]):
   fc=m['tri6'][labels==port['patch']];co=xx[fc];M=np.zeros((3,3));data=[]
   for a,wa in zip(r,w):
    for b,wb in zip(r,w):
     N,dr,ds=tri(a,(1-a)*b);p=np.einsum('i,eij->ej',N,co);ar=np.linalg.norm(np.cross(np.einsum('i,eij->ej',dr,co),np.einsum('i,eij->ej',ds,co)),axis=1)*wa*wb*(1-a);basis=np.c_[np.ones(len(p)),p[:,1]-origin[1],p[:,2]-origin[2]];M+=np.einsum('ni,nj,n->ij',basis,basis,ar);data.append((N,ar,basis))
   coeff=np.linalg.solve(M,[side*53200,0,0]);ff=np.zeros(fc.shape)
   for N,ar,basis in data:ff+=N[None,:]*(ar*(basis@coeff))[:,None]
   np.add.at(ind[:,0],fc,ff);result.append(dict(source_id=SID,level=l,port=port['patch'],area_Duffy36_mm2=float(M[0,0]),area_Dunavant7_mm2=port['area_mm2'],max_coefficient_difference=float(abs(coeff-port['coefficients']).max())))
  assert abs(ind-saved).max()<1e-8;write(R/'02_mesh_import'/l/'INDEPENDENT_LOAD_AUDIT.json',dict(source_id=SID,level=l,max_nodal_force_difference_N=float(abs(ind-saved).max()),net_force_difference_N=(ind-saved).sum(0),net_moment_difference_Nmm=np.cross(xx-origin,ind-saved).sum(0),passed=True))
 table(R/'10_mesh_hierarchy/INDEPENDENT_PORT_QUADRATURE.csv',result)

def seal():
 independent_loads();warnings=[];receipts=[]
 for l in ['M1','M2']:
  f=R/'02_mesh_import'/l;a=read(f/'NATIVE_PREFLIGHT_RECEIPT.json');assert a['passed'];receipts.append(a);txt=(f/'file.err').read_text(errors='replace');eids=np.unique([int(s) for s in re.findall(r'(?:Tetrahedron|element)\s+(\d+)',txt,re.I)]);m=np.load(LEVELS[l]/'mesh.npz');q=np.load(LEVELS[l]/'GLOBAL_QUALITY.npz');source=np.load(R/'01_frozen_protocol/geometry/solid_source.npz')
  for eid in eids:
   co=m['xyz'][m['tet10'][eid-1]];center=co[:4].mean(0);dd,ss=custom_quality(co[None],samples_Q2());assert dd.min()>0 and q['quality'][eid-1]>=.02;core=source['x'][0]+11<=center[0]<=source['x'][-1]-11 and source['y'][0]+3<=center[1]<=source['y'][-1]-3;warnings.append(dict(source_id=SID,level=l,native_element_id=int(eid),gmsh_tag=int(m['element_tags'][eid-1]),X=center[0],Y=center[1],Z=center[2],projected_core=bool(core),minSICN=float(q['quality'][eid-1]),min_Q2_J_mm3=float(dd.min()),decision='PERMITTED_DIAGNOSTIC_WARNING',policy='Frozenfatalshapeerrorreject;warningretainedwithindependentqualityandlocation'))
  if len(eids):table(f/'WARNING_BERNSTEIN_BOUNDS.csv',certify(m['xyz'][m['tet10'][eids-1]],eids-1,l+'_NATIVE_WARNINGS'))
 table(R/'NATIVE_SHAPE_WARNINGS.csv',warnings,['source_id','level','native_element_id','gmsh_tag','X','Y','Z','projected_core','minSICN','min_Q2_J_mm3','decision','policy']);write(R/'03_native_shape_checks/WARNING_CLASSIFICATION.json',dict(source_id=SID,distinct_warned_elements=len(warnings),M1_messages=receipts[0]['warnings'],M2_messages=receipts[1]['warnings'],native_errors=0,all_reviewed=True))
 rt=read(R/'03_native_shape_checks/INDEPENDENT_NATIVE_ROUNDTRIP.json');assert all(z['passed'] for z in rt);sup=read(R/'01_protocol_freeze/TARGET_SUPPORT_RECEIPT.json');assert sup['geometric_complete_core_area_fraction']>=.99
 # Check geometry eligibility and source preservation again before the irreversible solution budget.
 assert read(R/'03_parent_datum'/(SID+'.json'))['screen_pass'];assert read(R/'04_standardized_solids'/SID/'CAD_QUALIFICATION.json')['passed'];assert read(R/'10_mesh_hierarchy/PAIR_QUALIFICATION.json')['passed']
 for path,h in read(GLOBAL/'SOURCE_HASHES.json')[SID].items():assert sha(path)==h
 mem=resource_gate(ram=2*1024**3,commit=int(2.8*1024**3),disk=int(2.5*1024**3));write(R/'05_mechanical_preflight/RESOURCE_ESTIMATE.json',dict(resources=mem,job_RAM_estimate_bytes=2*1024**3,job_commit_estimate_bytes=int(2.8*1024**3),basis='Conservative over actualC02R2RSS1.48GB/private2.26GB;3GiBreserves'))
 names=['SOURCE_HASH_PASS','R8E9_PROTOCOL_PASS','PARENT_DATUM_PASS','NOMINAL_THICKNESS_PASS','STANDARDIZED_SOLID_PASS','SOURCE_CAD_FIDELITY_PASS','M1_QUADRATIC_FIDELITY_PASS','M2_QUADRATIC_FIDELITY_PASS','M1_QUALITY_PASS','M2_QUALITY_PASS','MESH_HIERARCHY_PASS','M1_NATIVE_IMPORT_PASS','M2_NATIVE_IMPORT_PASS','M1_NATIVE_SHAPE_PASS','M2_NATIVE_SHAPE_PASS','MATERIAL_PASS','MECHANICAL_BVP_PASS','FORCE_MOMENT_PASS','GAUGE_PASS','T2_SUPPORT_FROZEN','RESOURCE_PREFLIGHT_PASS'];table(R/'PRE_SOLVE_GATES.csv',[dict(source_id=SID,gate=n,passed=True,UTC=now()) for n in names])
 files=[R/'PRE_SOLVE_GATES.csv',R/'SELECTED_MESHES.json',R/'10_mesh_hierarchy/PAIR_QUALIFICATION.json',R/'03_native_shape_checks/INDEPENDENT_NATIVE_ROUNDTRIP.json',R/'03_native_shape_checks/WARNING_CLASSIFICATION.json',R/'01_protocol_freeze/TARGET_GEOMETRY_SUPPORT.npz',R/'01_protocol_freeze/TARGET_SUPPORT_RECEIPT.json',R/'05_mechanical_preflight/RESOURCE_ESTIMATE.json']
 for l in ['M1','M2']:
  files += [R/'02_mesh_import'/l/f for f in ['preprocess.dat','PREFLIGHT.db','NATIVE_PREFLIGHT_RECEIPT.json','BVP_ASSEMBLY.json','assembled_BVP.npz','INDEPENDENT_LOAD_AUDIT.json']];files += [LEVELS[l]/f for f in ['mesh.npz','PRE_SOLVER_QUALIFICATION.json','SOURCE_FIDELITY.json']]
 write(R/'05_mechanical_preflight/PRE_SOLVE_GATE_SEALED.json',dict(UTC=now(),decision='PASS',source_id=SID,protocol_version=VERSION,SOLVE_invocations_at_seal=0,global_preregistration_SHA256=sha(GLOBAL/'PREREGISTRATION_SEAL.json'),files=[dict(path=str(p.relative_to(R)),sha256=sha(p)) for p in files]));print('SOURCE_PRESOLVE_GATE_SEALED',SID,sha(R/'05_mechanical_preflight/PRE_SOLVE_GATE_SEALED.json'),flush=True)

if __name__=='__main__':
 protect();may_execute_source()
 if sys.argv[1]=='pair':pair()
 elif sys.argv[1]=='prepare':
  from preflight_r2 import prepare
  for l in ['M1','M2']:prepare(l)
 elif sys.argv[1]=='native':
  from preflight_r2 import run_preprocess
  a=run_preprocess(sys.argv[2]);assert a['passed']
 elif sys.argv[1]=='audit':
  from gate_r2 import native_audit
  native_audit()
 elif sys.argv[1]=='seal':seal()
