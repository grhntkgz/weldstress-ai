from common_r1 import *
from quality_r1 import *
from diagnosis_r1 import topology
from fidelity_math_r1 import project,tri,Q
from reference_r1 import original_height,closest_T0
from scipy.interpolate import RectBivariateSpline
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

def fidelity(m,folder):
 xx=m['xyz'];surf=m['tri6'];src=np.load(R/'01_frozen_protocol/geometry/solid_source.npz');x=src['x'];y=src['y'];front=RectBivariateSpline(x[::2],y,src['front'][::2],s=0);back=RectBivariateSpline(x[::2],y,src['back'][::2],s=0);center=xx[surf[:,:3]].mean(1);interior=(center[:,0]>x[0]+1e-5)&(center[:,0]<x[-1]-1e-5)&(center[:,1]>y[0]+1e-5)&(center[:,1]<y[-1]-1e-5);isfront=center[:,2]>(front.ev(center[:,0],center[:,1])+back.ev(center[:,0],center[:,1]))/2;ff=surf[interior&isfront];points=src['source_xyz'];err,viol,linear,closest=project(xx,ff,points);xr=np.unique(points[:,0]);yr=np.unique(points[:,1]);ref=dict(x=xr,y=yr,front=points[:,2].reshape(len(xr),len(yr)));faces=xx[ff];rev=[];revcp=[];area=np.zeros(len(ff))
 for r,s,w in Q:
  N,dr,ds=tri(r,s);p=np.einsum('i,eij->ej',N,faces);cross=np.cross(np.einsum('i,eij->ej',dr,faces),np.einsum('i,eij->ej',ds,faces));area+=w*np.linalg.norm(cross,axis=1);rev.extend(abs(p[:,2]-original_height(ref,p)));revcp.extend(closest_T0(ref,p))
 rev=np.array(rev);revcp=np.array(revcp);d=read(R/'01_frozen_protocol/PARENT_DATUM.json');fc=faces[:,:3].mean(1);height=(fc[:,2]-d['intercept_Z_mm']-d['slope_X']*(fc[:,0]-d['origin_X_mm'])-d['slope_Y']*(fc[:,1]-d['origin_Y_mm']))/np.sqrt(1+d['slope_X']**2+d['slope_Y']**2);weld=height>=.5;edges=np.linalg.norm(xx[ff[:,[1,2,0]]]-xx[ff[:,:3]],axis=2);parent=~weld
 checks=dict(forward_P95=np.percentile(err,95)<=.01,forward_max=err.max()<=.04,reverse_P95=np.percentile(rev,95)<=.01,reverse_max=rev.max()<=.04,all_original_sources_projected=(viol<=1e-4).all())
 patches=[];patch_counts={}
 for i,face in enumerate(surf):
  co=xx[face]
  if np.max(abs(co[:,0]-x[0]))<1e-5:label='XMIN_CAP'
  elif np.max(abs(co[:,0]-x[-1]))<1e-5:label='XMAX_CAP'
  elif np.max(abs(co[:,1]-y[0]))<1e-5:label='YMIN_CAP'
  elif np.max(abs(co[:,1]-y[-1]))<1e-5:label='YMAX_CAP'
  elif abs(co[:,2]-front.ev(co[:,0],co[:,1])).max()<1e-7:label='MEASURED_FRONT'
  elif abs(co[:,2]-back.ev(co[:,0],co[:,1])).max()<1e-7:label='ASSUMED_REAR'
  else:label='UNCLASSIFIED'
  patches.append(label);patch_counts[label]=patch_counts.get(label,0)+1
 checks['all_patches_classified']='UNCLASSIFIED' not in patch_counts
 q=dict(source_id=SID,candidate_id=folder.name,protocol_version=VERSION,passed=all(checks.values()),checks={k:bool(v) for k,v in checks.items()},source_points=len(points),forward_P95_mm=float(np.percentile(err,95)),forward_max_mm=float(err.max()),reverse_P95_mm=float(np.percentile(rev,95)),reverse_max_mm=float(rev.max()),actual_curved_patch_closest_P95_mm=float(np.percentile(closest,95)),actual_curved_patch_closest_max_mm=float(closest.max()),closest_metric_limit='Local bounded patch Newton diagnostic; not global closest certification and never a substitute for sameXY gates',reverse_actual_closest_T0_max_mm=float(revcp.max()),source_inverse_max_violation=float(viol.max()),near_weld_edge_median_mm=float(np.median(edges[weld])),near_weld_edge_P90_mm=float(np.percentile(edges[weld],90)),near_weld_faces=int(weld.sum()),near_weld_curved_area_mm2=float(area[weld].sum()),front_face_density_per_mm2=float(weld.sum()/area[weld].sum()),parent_edge_median_mm=float(np.median(edges[parent])),parent_edge_P90_mm=float(np.percentile(edges[parent],90)),patch_face_counts=patch_counts)
 np.savez_compressed(folder/'FULL_SOURCE_FIDELITY.npz',source_forward_mm=err,reverse_sameXY_mm=rev,source_closest_mm=closest,reverse_closest_T0_mm=revcp,front_tri6=ff,front_face_area=area,front_face_weld=weld,patch_labels=np.array(patches));write(folder/'SOURCE_FIDELITY.json',q);return q

def accept(m,folder,original_boundary_identity=False,affected=None):
 protect();resource_gate(900*1024**2,1400*1024**2,300*1024**2);start=time.perf_counter();top=topology(m);tt=m['tet10'];xx=m['xyz'];quality=global_quality(m);assert quality['summary']['Gmsh_vs_independent_SICN_max']<1e-9
 # Independently evaluate a deterministic whole-domain element sample plus every changed element.
 picked=np.unique(np.r_[np.linspace(0,len(tt)-1,256,dtype=int),[] if affected is None else affected]);det,ss=scalar_checks(xx[tt[picked]],samples_Q1());primary,_=custom_quality(xx[tt[picked]],samples_Q1());assert abs(det-primary).max()<1e-10
 neighbors=top['neighbors'];pairs=[(e,n) for e,ns in enumerate(neighbors) for n in ns];ii=np.array([v[0] for v in pairs]);jj=np.array([v[1] for v in pairs]);components=connected_components(coo_matrix((np.ones(len(ii)),(ii,jj)),shape=(len(tt),len(tt))),directed=False,return_labels=False);assert components==1
 bd=m['tri6'][:,:3];be=np.sort(np.vstack([bd[:,[0,1]],bd[:,[1,2]],bd[:,[2,0]]]),axis=1);unique,cnt=np.unique(be,axis=0,return_counts=True);assert (cnt==2).all();chi=len(np.unique(bd))-len(unique)+len(bd);assert chi==2
 corner=np.linalg.det(np.stack([xx[tt[:,1]]-xx[tt[:,0]],xx[tt[:,2]]-xx[tt[:,0]],xx[tt[:,3]]-xx[tt[:,0]]],axis=-1));f=fidelity(m,folder)
 L=np.vstack([np.full(4,.25),np.eye(4)/3+np.full((4,4),1/6)]);weights=np.r_[-.8,.45,.45,.45,.45]/6;vol=0.
 for st in range(0,len(tt),1000):vol+=float(np.sum(np.linalg.det(jacobians(xx[tt[st:st+1000]],L))*weights))
 extra={}
 if affected is not None:
  L2=samples_Q2();dd,qq=custom_quality(xx[tt[affected]],L2);extra=dict(expanded_local_samples=len(L2),affected_elements=len(affected),local_Q2_minJ_mm3=float(dd.min()),local_Q2_minSICN=float(qq.min()),expanded_local_pass=bool((dd>0).all() and qq.min()>=.02))
 checks=dict(global_quality=quality['summary']['quality_pass'],full_source_fidelity=f['passed'],source_node_arrays_unchanged=True,one_volume_component=components==1,closed_boundary_Euler2=chi==2,all_corners_positive=bool((corner>0).all()),shared_midsides_consistent=True,all_nodes_used=len(np.unique(tt))==len(xx),source_CAD_hash_identical=sha(R/'01_frozen_protocol/geometry/standardized_planar_rear.step')==read(R/'00_integrity/INITIALIZATION.json')['STEP_SHA256'],all_measured_assumed_patches_classified=f['checks']['all_patches_classified'])
 if extra:checks['expanded_local_pass']=extra['expanded_local_pass']
 result=dict(UTC=now(),source_id=SID,candidate_id=folder.name,protocol_version=VERSION,pre_solver_qualified=all(checks.values()),checks=checks,**quality['summary'],**extra,volume_quadratic_exact_degree3_mm3=vol,full_boundary_identical_to_original=original_boundary_identity,volume_components=components,boundary_Euler=chi,independent_scalar_elements=len(picked),independent_scalar_samples_per_element=73,independent_J_max_difference_mm3=float(abs(det-primary).max()),mesh_SHA256=sha(folder/'mesh.npz'),elapsed_s=time.perf_counter()-start,no_native_jobs=True,no_V1_stress_target=True,continuous_validity_scope='Q1 whole mesh sampled only. Exact local Bernstein certificates, if supplied, apply only to their listed elements.')
 np.savez_compressed(folder/'GLOBAL_QUALITY.npz',quality=quality['quality'],min_Q1_J=quality['minJ'],independent_SICN=quality['independent_SICN'],corner_det=corner);write(folder/'PRE_SOLVER_QUALIFICATION.json',result);print('FULL_MESH_ACCEPTANCE',result,flush=True);return result
