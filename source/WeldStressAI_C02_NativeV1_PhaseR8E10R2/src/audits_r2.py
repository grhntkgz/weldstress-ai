from common_r2 import *
from scipy.special import roots_legendre
import re,math

def main():
 # Read all E9 manifest entries, including those not already in R1's selected dependency snapshot.
 e9=R.parent/'WeldStressAI_PhysicsConsistentLearning_PhaseR8E9';manifest=read(e9/'REPRODUCIBILITY_MANIFEST.json');print('E9_MANIFEST_SCHEMA',list(manifest),flush=True)
 entries=manifest.get('files',manifest.get('artifacts',[]));audit=rows(R/'HISTORICAL_INTEGRITY_AUDIT.csv');known={a['path'] for a in audit}
 for a in entries:
  p=e9/a['path'];expected=a.get('sha256',a.get('SHA256'));assert expected;h=sha(p);assert h==expected
  if str(p) not in known:audit.append(dict(path=str(p),expected_sha256=expected,actual_sha256=h,passed=True,basis='Complete E9 manifest independent R2 audit'));known.add(str(p))
 table(R/'HISTORICAL_INTEGRITY_EXTENDED_AUDIT.csv',audit)
 # Applied load verification via independent tensor-product Gauss/Duffy quadrature,
 # separate from original seven-point Dunavant assembly.
 results=[];r,w=roots_legendre(6);r=(r+1)/2;w=w/2;origin=np.array([149.975,30,-9.37643484024406])
 for level in ['M1','M2']:
  m=np.load(LEVELS[level]/'mesh.npz');labels=np.load(LEVELS[level]/'FULL_SOURCE_FIDELITY.npz')['patch_labels'];bvp=read(R/'02_mesh_import'/level/'BVP_ASSEMBLY.json');xyz=m['xyz'];saved=np.load(R/'02_mesh_import'/level/'assembled_BVP.npz')['forces'];ind=np.zeros_like(saved)
  for port,side in zip(bvp['ports'],[-1,1]):
   faces=m['tri6'][labels==port['patch']];co=xyz[faces];M=np.zeros((3,3));data=[]
   for a,wa in zip(r,w):
    for b,wb in zip(r,w):
     N,dr,ds=tri(a,(1-a)*b);p=np.einsum('i,eij->ej',N,co);ds1=np.einsum('i,eij->ej',dr,co);ds2=np.einsum('i,eij->ej',ds,co);ar=np.linalg.norm(np.cross(ds1,ds2),axis=1)*wa*wb*(1-a);basis=np.c_[np.ones(len(p)),p[:,1]-30,p[:,2]-origin[2]];M+=np.einsum('ni,nj,n->ij',basis,basis,ar);data.append((N,ar,basis))
   coeff=np.linalg.solve(M,[side*53200,0,0]);ff=np.zeros(faces.shape)
   for N,ar,basis in data:ff+=N[None,:]*(ar*(basis@coeff))[:,None]
   np.add.at(ind[:,0],faces,ff);results.append(dict(level=level,port=port['patch'],Duffy36_area_mm2=M[0,0],Dunavant7_area_mm2=port['area_mm2'],area_difference_mm2=M[0,0]-port['area_mm2'],max_affine_coefficient_difference=float(abs(coeff-port['coefficients']).max())))
  assert np.max(abs(ind-saved))<1e-8;write(R/'04_BVP_assembly'/f'{level}_INDEPENDENT_LOAD_AUDIT.json',dict(level=level,quadrature='Independent6x6GaussDuffy36versusDunavant7',max_nodal_force_difference_N=float(abs(ind-saved).max()),net_force_difference_N=(ind-saved).sum(0),net_moment_difference_Nmm=np.cross(xyz-origin,ind-saved).sum(0),passed=True))
 table(R/'04_BVP_assembly/INDEPENDENT_PORT_QUADRATURE.csv',results)
 # Aggregate complete native warnings, distinguish shape from ignored duplicate SHPPinSOLU.
 warning=[];errors=[]
 for level in ['M1','M2']:
  for stage,folder,name in [('IMPORT',R/'02_mesh_import'/level,'preprocess.out'),('SOLVE',R/('06_native_M1' if level=='M1' else '07_native_M2'),'solve.out')]:
   txt=(folder/name).read_text(errors='replace');chunks=re.split(r'(?=\*\*\* (?:WARNING|ERROR) \*\*\*)',txt)
   for c in chunks[1:]:
    first=c.split('*** NOTE ***')[0].split('*** WARNING ***',1)[-1] if c.startswith('*** WARNING ***') else c
    msg=' '.join(first.splitlines()[:6]);row=dict(level=level,stage=stage,category='IGNORED_REDUNDANT_SHPP_IN_SOLU' if 'not a recognized SOLUTION command' in c[:700] else 'NATIVE_SHAPE_WARNING' if 'shape' in c[:700].lower() or 'Jacobian' in c[:700] else 'OTHER',message=msg,source_log=str(folder/name))
    (warning if c.startswith('*** WARNING ***') else errors).append(row)
 table(R/'NATIVE_SHAPE_WARNINGS.csv',warning,['level','stage','category','message','source_log']);table(R/'NATIVE_SHAPE_ERRORS.csv',errors,['level','stage','category','message','source_log'])
 # Aggregate required complete reversible maps and BVP tables without silent level-ID collisions.
 for name in ['GMSH_TO_ANSYS_NODE_MAP.csv','GMSH_TO_ANSYS_ELEMENT_MAP.csv','SOLID187_CONNECTIVITY_AUDIT.csv','SOLID187_LOCAL_ORDERING_AUDIT.csv','SHARED_MIDSIDE_COMPATIBILITY.csv','PORT_FACE_REGISTRY.csv','NODAL_LOAD_ASSEMBLY.csv','SIGNED_FORCE_MOMENT_RESULTANTS.csv','GAUGE_CONSTRAINT_REGISTRY.csv']:
  combined=[]
  for level in ['M1','M2']:combined.extend(dict(level=level,**{k:v for k,v in z.items() if k!='level'}) for z in rows(R/'02_mesh_import'/level/name))
  table(R/name,combined)
 solve=[];balance=[];disp=[];tensors=[];resources=[]
 for level in ['M1','M2']:
  folder=R/('06_native_M1' if level=='M1' else '07_native_M2');s=read(folder/'SOLVE_COMPLETE.json');txt=(folder/'solve.out').read_text(errors='replace');dur=re.findall(r'Elapsed Time \(sec\) =\s*([\d.]+)',txt);native_elapsed=float(dur[-1]) if dur else None
  solve.append(dict(level=level,completed=s['completed'],native_errors=s['native_errors'],native_warning_messages=s['native_warnings'],native_elapsed_log_s=native_elapsed,resource_sampler_last_s=s['elapsed_s'],peak_RSS_bytes=s['peak_RSS_bytes'],peak_private_bytes=s['peak_private_bytes'],RST_SHA256=sha(folder/'file.rst'),DB_SHA256=sha(folder/'MODEL.db')))
  balance.append(dict(level=level,force_relative=s['force_residual_relative'],moment_over_Ft=s['moment_residual_over_Ft'],**{k:json.dumps(s[k]) for k in ['applied_force_N','reaction_force_N','signed_force_residual_N','applied_moment_Nmm','reaction_moment_Nmm','signed_moment_residual_Nmm']},passed=s['equilibrium_passed']))
  disp.append(dict(level=level,**{k:s[k] for k in ['Umax_mm','Umean_mm','gauge_motion_max_mm','mean_end_axial_extension_mm','no_RB_runaway']},UX_min=s['UX_minmax_mm'][0],UX_max=s['UX_minmax_mm'][1],UY_min=s['UY_minmax_mm'][0],UY_max=s['UY_minmax_mm'][1],UZ_min=s['UZ_minmax_mm'][0],UZ_max=s['UZ_minmax_mm'][1]))
  tensors.append(read(R/'09_tensor_recovery'/f'{level}_INDEPENDENT_TENSOR_RECEIPT.json'))
  for q in rows(folder/'RESOURCES.csv'):resources.append(dict(level=level,**q))
 table(R/'NATIVE_SOLVE_REGISTRY.csv',solve);table(R/'NATIVE_REACTION_BALANCE.csv',balance);table(R/'NATIVE_DISPLACEMENT_METRICS.csv',disp);table(R/'INDEPENDENT_TENSOR_CHECKS.csv',tensors);table(R/'17_reproducibility/RESOURCE_SAMPLES.csv',resources)
 print('INDEPENDENT_ASSEMBLY_AUDITED; historical_paths',len(audit),flush=True)

if __name__=='__main__':protect();main()
