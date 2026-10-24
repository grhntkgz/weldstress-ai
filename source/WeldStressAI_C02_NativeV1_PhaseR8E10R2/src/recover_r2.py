from common_r2 import *
from scipy.spatial import cKDTree
import math
ED=np.array([[0,1],[1,2],[2,0],[0,3],[1,3],[2,3]])
DL=np.array([[-1.,-1.,-1.],[1.,0,0],[0,1.,0],[0,0,1.]])
def evaluate(x,u,L):
 N=np.concatenate([L*(2*L-1),4*L[...,ED[:,0]]*L[...,ED[:,1]]],axis=-1)
 dn=np.concatenate([(4*L[...,None]-1)*DL,4*(L[...,ED[:,0],None]*DL[ED[:,1]]+L[...,ED[:,1],None]*DL[ED[:,0]])],axis=-2)
 J=np.einsum('...ia,...ib->...ab',x,dn);det=np.linalg.det(J);assert np.isfinite(det).all() and (det>0).all();dx=dn@np.linalg.inv(J);grad=np.einsum('...ia,...ib->...ab',u,dx);eps=(grad+np.swapaxes(grad,-1,-2))*.5;stress=210000/1.3*eps+(210000*.3/(1.3*.4))*np.trace(eps,axis1=-2,axis2=-1)[...,None,None]*np.eye(3)
 return dict(xyz=np.einsum('...i,...ia->...a',N,x),u=np.einsum('...i,...ia->...a',N,u),stress=stress,strain=eps,sigma1=np.linalg.eigvalsh(stress)[...,-1],detJ=det)
def pack(s):return np.stack([s[...,0,0],s[...,1,1],s[...,2,2],s[...,0,1],s[...,1,2],s[...,0,2]],axis=-1)
def independent(x,u,L):
 out=[]
 for points,displacements,bary in zip(x,u,L):
  D=[]
  for i in range(4):D.append((4*bary[i]-1)*DL[i])
  for a,b in [(0,1),(1,2),(2,0),(0,3),(1,3),(2,3)]:D.append(4*(bary[a]*DL[b]+bary[b]*DL[a]))
  D=np.array(D);J=points.T@D;spatial=np.linalg.solve(J.T,D.T).T;G=displacements.T@spatial;eps=(G+G.T)/2
  # Independently explicit Voigt constitutive operator with engineering shear.
  E=210000.;nu=.3;C=np.zeros((6,6));C[:3,:3]=E*nu/((1+nu)*(1-2*nu));np.fill_diagonal(C[:3,:3],E*(1-nu)/((1+nu)*(1-2*nu)));C[3:,3:]=np.eye(3)*E/(2*(1+nu));v=C@np.array([eps[0,0],eps[1,1],eps[2,2],2*eps[0,1],2*eps[1,2],2*eps[0,2]]);out.append(v)
 return np.array(out)
def tribatch(r,s):
 l=1-r-s;z=np.zeros_like(r)
 return np.stack([l*(2*l-1),r*(2*r-1),s*(2*s-1),4*l*r,4*r*s,4*s*l],-1),np.stack([1-4*l,4*r-1,z,4*(l-r),4*s,-4*s],-1),np.stack([1-4*l,z,4*s-1,-4*r,4*r,4*(l-s)],-1)

def run(level):
 folder=R/('06_native_M1' if level=='M1' else '07_native_M2');assert read(folder/'SOLVE_COMPLETE.json')['completed'];out=R/'10_source_mapping'/level;out.mkdir(exist_ok=True);assert not (out/'MAPPING_AUDIT.json').exists()
 a=np.load(folder/'native_displacements.npz');xyz=a['xyz'];u=a['u'];tet=a['connectivity_native'];m=np.load(LEVELS[level]/'mesh.npz');faces=m['tri6'];labels=np.load(LEVELS[level]/'FULL_SOURCE_FIDELITY.npz')['patch_labels'];g=np.load(R/'01_protocol_freeze/TARGET_GEOMETRY_SUPPORT.npz');p=g['xyz'];area=g['area'];mask=g['halo'];ids=g['source_ids'];n=len(p)
 hosts={}
 for corners in [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]:
  for i,v in enumerate(tet[:,corners]):
   key=tuple(sorted(map(int,v)));hosts[key]=None if key in hosts else i
 fid=np.flatnonzero(labels=='MEASURED_FRONT');f=faces[fid];co=xyz[f];host=np.array([hosts[tuple(sorted(map(int,v)))] for v in f[:,:3]],int);local=np.array([[np.flatnonzero(tet[h,:4]==v)[0] for v in ff[:3]] for h,ff in zip(host,f)]);tree=cKDTree(co[:,:3,:2].mean(1));query=np.flatnonzero(mask)
 valid=np.zeros(n,bool);sig=np.full(n,np.nan);tensor=np.full((n,6),np.nan);Lsave=np.full((n,4),np.nan);proj=np.full(n,np.nan);eid=np.full(n,-1,int);faceid=np.full(n,-1,int);actual=np.full_like(p,np.nan);UU=np.full_like(p,np.nan);invres=np.full(n,np.nan)
 for chunk in np.array_split(query,int(np.ceil(len(query)/1000))):
  q=p[chunk,:2];_,ix=tree.query(q,k=20);coords=co[ix];aa=coords[:,:,0,:2];jac=np.stack([coords[:,:,1,:2]-aa,coords[:,:,2,:2]-aa],axis=-1);rs=np.linalg.solve(jac,(q[:,None]-aa)[...,None])[...,0]
  for _ in range(10):
   N,dr,ds=tribatch(rs[:,:,0],rs[:,:,1]);xy=np.einsum('nki,nkij->nkj',N,coords[...,:2]);jr=np.einsum('nki,nkij->nkj',dr,coords[...,:2]);js=np.einsum('nki,nkij->nkj',ds,coords[...,:2]);rs-=np.linalg.solve(np.stack([jr,js],axis=-1),(xy-q[:,None])[...,None])[...,0]
  violation=np.maximum.reduce([-rs[:,:,0],-rs[:,:,1],rs.sum(-1)-1,np.zeros(rs.shape[:2])]);ok=violation<=1e-5;row=np.arange(len(chunk));choice=np.argmin(np.where(ok,host[ix],np.iinfo(np.int64).max),axis=1);ff=ix[row,choice];hh=host[ff];L=np.zeros((len(chunk),4));L[row[:,None],local[ff]]=np.c_[1-rs[row,choice].sum(1),rs[row,choice]];v=evaluate(xyz[tet[hh]],u[tet[hh]],L);dist=np.linalg.norm(v['xyz']-p[chunk],axis=1);good=ok.any(1)&(dist<=.04);valid[chunk]=good;sig[chunk]=np.where(good,np.maximum(v['sigma1'],0),np.nan);tensor[chunk]=pack(v['stress']);Lsave[chunk]=L;proj[chunk]=dist;eid[chunk]=hh+1;faceid[chunk]=fid[ff];actual[chunk]=v['xyz'];UU[chunk]=v['u'];invres[chunk]=np.linalg.norm(v['xyz'][:,:2]-q,axis=1)
 coverage=float(area[valid].sum()/area[mask].sum());receipt=dict(level=level,total_source_points=n,queried_halo_points=int(mask.sum()),valid_mapped_points=int(valid.sum()),failures_in_queried_halo=int(np.sum(mask&~valid)),not_queried_points=int((~mask).sum()),valid_mapped_area_mm2=float(area[valid].sum()),query_area_mm2=float(area[mask].sum()),area_weighted_mapping_coverage=coverage,projection_P95_mm=float(np.percentile(proj[valid],95)),projection_max_mm=float(proj[valid].max()),inverse_XY_residual_max_mm=float(invres[valid].max()),passed=coverage>=.99,regions={str(k):dict(coverage=float(area[valid&(g['region']==k)].sum()/area[mask&(g['region']==k)].sum()),query_points=int(np.sum(mask&(g['region']==k)))) for k in [0,1,2]},max_raw_tensile_principal_MPa=float(sig[valid].max()),scope='Mapping-only on frozen halo; full-front geometry fidelity separately inherited from verified R1all-source audit. Unqueried exterior points retained, not stress-labelled.')
 np.savez_compressed(out/'SOURCE_MAPPING.npz',source_ids=ids,xyz=p,area=area,valid=valid,halo=mask,sigma1_tensile=sig,tensor=tensor,L=Lsave,native_element_id=eid,boundary_face_id=faceid,projection_distance_mm=proj,actual_FE_xyz=actual,FE_displacement=UU,inverse_XY_residual_mm=invres)
 write(out/'MAPPING_AUDIT.json',receipt)
 # Native ETABLE S component is element average of extrapolated corner-node values;
 # compare to equal-weight average of four direct constitutive Gauss tensors.
 nat=np.loadtxt(folder/'native_element_stress.csv',delimiter=',',ndmin=2);et=nat[:,0].astype(int)-1;GP=np.full((4,4),(5-np.sqrt(5))/20);np.fill_diagonal(GP,(5+3*np.sqrt(5))/20);v=evaluate(xyz[tet[et]][:,None],u[tet[et]][:,None],GP[None]);directgp=pack(v['stress']).mean(1);delta=directgp-nat[:,1:]
 table(R/'09_tensor_recovery'/f'{level}_NATIVE_ETABLE_COMPARISON.csv',[dict(level=level,element_id=int(e+1),native_ETABLE_SXX=float(nat[j,1]),direct_mean_four_GP_SXX=float(directgp[j,0]),max_component_difference_MPa=float(abs(delta[j]).max())) for j,e in enumerate(et)])
 take=np.flatnonzero(valid)[np.linspace(0,int(valid.sum())-1,256,dtype=int)];hh=eid[take]-1;ind=independent(xyz[tet[hh]],u[tet[hh]],Lsave[take]);error=float(abs(ind-tensor[take]).max());assert error<=1e-7
 # Independent scalar recovery also checks every four-GP sample for native-selected elements.
 indgp=independent(np.repeat(xyz[tet[et]],4,axis=0),np.repeat(u[tet[et]],4,axis=0),np.tile(GP,(len(et),1))).reshape(len(et),4,6).mean(1);native_error=float(abs(indgp-nat[:,1:]).max());relative=float(np.linalg.norm(indgp-nat[:,1:])/np.linalg.norm(nat[:,1:]));write(R/'09_tensor_recovery'/f'{level}_INDEPENDENT_TENSOR_RECEIPT.json',dict(level=level,source_points=256,independent_direct_tensor_max_error_MPa=error,inherited_tolerance_MPa=1e-7,native_elements=len(et),native_ETABLE_interpretation='Component average of extrapolated corner stresses, compared with equal four-Gauss-point mean; no nodal smoothing used for source targets',native_ETABLE_max_error_MPa=native_error,native_ETABLE_relative_L2=relative,native_comparison_diagnostic=True,independent_qualified=True))
 table(R/f'SOURCE_MAPPING_{level}.csv',[dict(source_id=int(ids[i]),X=p[i,0],Y=p[i,1],Z=p[i,2],T0_area_mm2=area[i],queried=bool(mask[i]),valid=bool(valid[i]),native_element_id=int(eid[i]) if mask[i] else '',projection_mm=float(proj[i]) if mask[i] else '',SXX=float(tensor[i,0]) if valid[i] else '',SYY=float(tensor[i,1]) if valid[i] else '',SZZ=float(tensor[i,2]) if valid[i] else '',SXY=float(tensor[i,3]) if valid[i] else '',SYZ=float(tensor[i,4]) if valid[i] else '',SXZ=float(tensor[i,5]) if valid[i] else '',SIGMA1_TENSILE=float(sig[i]) if valid[i] else '') for i in range(n)])
 print('MAPPING',receipt,'tensor_error',error,'native_mean_error',native_error,relative,flush=True)
 assert receipt['passed']

if __name__=='__main__':protect();run(sys.argv[1])
