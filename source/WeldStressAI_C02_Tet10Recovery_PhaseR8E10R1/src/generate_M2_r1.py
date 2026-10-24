from common_r1 import *
from quality_r1 import *
from acceptance_r1 import accept
from bernstein_r1 import certify
from scipy.interpolate import RectBivariateSpline
from scipy.spatial import cKDTree

def main():
 protect();assert read(R/'06_recovered_M1/FINAL_M1.json')['qualified'];resource_gate(1800*1024**2,2500*1024**2,1500*1024**2);ledgerpath=R/'14_reproducibility/FULL_CANDIDATE_LEDGER.json';ledger=read(ledgerpath);assert not any(z['mesh_level']=='M2' and z['status']=='QUALIFIED' for z in ledger),'Do not improve an already qualified M2';assert sum(z['mesh_level']=='M2' for z in ledger)<2;folder=R/'07_refined_M2/M2_C1';assert not folder.exists();folder.mkdir(parents=True)
 entry=dict(UTC=now(),source_id=SID,candidate_id='M2_C1',protocol_version=VERSION,mesh_level='M2',strategy='INDEPENDENT_GEOMETRY_CONSTRAINED_REFINEMENT',status='STARTED');ledger.append(entry);write(ledgerpath,ledger)
 src=np.load(R/'01_frozen_protocol/geometry/solid_source.npz');x=src['x'];y=src['y'];front=src['front'];back=src['back'];sp={s:RectBivariateSpline(x[::2],y,src[s][::2],s=0) for s in ['front','back']};d=read(R/'01_frozen_protocol/PARENT_DATUM.json');p=src['source_xyz'];height=(p[:,2]-d['intercept_Z_mm']-d['slope_X']*(p[:,0]-d['origin_X_mm'])-d['slope_Y']*(p[:,1]-d['origin_Y_mm']))/np.sqrt(1+d['slope_X']**2+d['slope_Y']**2);proxy=height>=.5;tree=cKDTree(p[proxy,:2]);dist,_=tree.query(p[:,:2]);weight=np.clip(1-dist/2,0,1).reshape(len(x),len(y));hs=(.6-.3*weight)[::2];ztable=np.stack([front[::2],back[::2]]);xs=x[::2];nx=len(xs);ny=len(y);center=np.array([128.7532390566058,31.783373546459362]);radius=1.2
 write(R/'10_mesh_hierarchy/M2_PREREGISTRATION.json',dict(UTC=now(),source_id=SID,candidate_id='M2_C1',protocol_version=VERSION,M1_qualification_SHA256=sha(R/'06_recovered_M1/M1_C1/PRE_SOLVER_QUALIFICATION.json'),unchanged_STEP_SHA256=sha(R/'01_frozen_protocol/geometry/standardized_planar_rear.step'),method='Independent M2 permitted by R1; uniform eight-child subdivision of all82498M1 elements would exceed230000Tet10 cap, so not used',weld_size_mm=.3,parent_size_mm=.6,bulk_max_mm=2.5,growth=1.,local_measured_front_constraint=dict(center_XY_mm=center.tolist(),radius_mm=radius,minimum_surface_size_mm=.3,transition='cubic smoothstep to parent.6 at radius; applies only nearfront; fixed from original invalid region beforeM2generation'),mesh_seed=20261017,max_full_M2=2,no_native=True))
 def callback(dim,tag,X,Y,Z,lc):
  u=np.clip((X-xs[0])/(xs[1]-xs[0]),0,nx-1-1e-9);v=np.clip((Y-y[0])/(y[1]-y[0]),0,ny-1-1e-9);i=int(u);j=int(v);a=u-i;b=v-j;w=np.array([(1-a)*(1-b),a*(1-b),(1-a)*b,a*b]);zz=ztable[:,[i,i+1,i,i+1],[j,j,j+1,j+1]]@w;side=0 if abs(Z-zz[0])<=abs(Z-zz[1]) else 1;h=float(hs[[i,i+1,i,i+1],[j,j,j+1,j+1]]@w) if side==0 else .6
  if side==0:
   r=min(1,float(np.linalg.norm(np.array([X,Y])-center))/radius);h=min(h,.3+.3*r*r*(3-2*r))
  return min(2.5,h+abs(Z-zz[side]))
 import gmsh
 start=time.perf_counter();gmsh.initialize();gmsh.logger.start();gmsh.option.setNumber('General.NumThreads',2);gmsh.model.add('C02_M2_C1');patches={}
 try:
  gmsh.model.occ.importShapes(str(R/'01_frozen_protocol/geometry/standardized_planar_rear.step'));gmsh.model.occ.synchronize();assert len(gmsh.model.getEntities(3))==1;measured=[]
  for dim,tag in gmsh.model.getEntities(2):
   bb=gmsh.model.getBoundingBox(dim,tag)
   if bb[3]-bb[0]>.99*np.ptp(x) and bb[4]-bb[1]>.99*np.ptp(y):measured.append(tag)
   elif bb[3]-bb[0]<1e-4:patches[tag]='XMIN_CAP' if abs(bb[0]-x[0])<1e-4 else 'XMAX_CAP'
   else:patches[tag]='YMIN_CAP' if abs(bb[1]-y[0])<1e-4 else 'YMAX_CAP'
  assert len(measured)==2;measured.sort(key=lambda z:gmsh.model.occ.getCenterOfMass(2,z)[2],reverse=True);patches[measured[0]]='MEASURED_FRONT';patches[measured[1]]='ASSUMED_REAR'
  for k,v in [('Mesh.MeshSizeMin',.3),('Mesh.MeshSizeMax',2.5),('Mesh.MeshSizeFromPoints',0),('Mesh.MeshSizeFromCurvature',0),('Mesh.MeshSizeExtendFromBoundary',0),('Mesh.Algorithm3D',1),('Mesh.RandomSeed',20261017),('Mesh.SecondOrderLinear',1),('Mesh.Binary',1)]:gmsh.option.setNumber(k,v)
  gmsh.model.mesh.setSizeCallback(callback);gmsh.model.mesh.generate(3);gmsh.model.mesh.optimize('Netgen');gmsh.model.mesh.setOrder(2);ids,xyz,_=gmsh.model.mesh.getNodes();order=np.argsort(ids);ids=ids[order];xyz=np.array(xyz).reshape(-1,3)[order];maxshift=0.
  for side,tag in zip(['front','back'],measured):
   nn,_,_=gmsh.model.mesh.getNodes(2,tag,includeBoundary=True);ix=np.searchsorted(ids,nn);z=sp[side].ev(xyz[ix,0],xyz[ix,1]);maxshift=max(maxshift,float(abs(z-xyz[ix,2]).max()));xyz[ix,2]=z
   for node,co in zip(nn,xyz[ix]):_,param,_,_=gmsh.model.mesh.getNode(int(node));gmsh.model.mesh.setNode(int(node),co.tolist(),param)
  gmsh.model.mesh.rebuildNodeCache(False);eids,tet=gmsh.model.mesh.getElementsByType(11);tt=np.searchsorted(ids,np.array(tet).reshape(-1,10));_,surf=gmsh.model.mesh.getElementsByType(9);ff=np.searchsorted(ids,np.array(surf).reshape(-1,6));quality=np.array(gmsh.model.mesh.getElementQualities(eids,'minSICN'))
  for tag,name in patches.items():physical=gmsh.model.addPhysicalGroup(2,[tag]);gmsh.model.setPhysicalName(2,physical,name)
  physical=gmsh.model.addPhysicalGroup(3,[gmsh.model.getEntities(3)[0][1]]);gmsh.model.setPhysicalName(3,physical,'STANDARDIZED_C02_SOLID');gmsh.write(str(folder/'mesh.msh'));(folder/'gmsh.log').write_text('\n'.join(gmsh.logger.get()),encoding='utf8')
 finally:gmsh.logger.stop();gmsh.finalize()
 m=dict(xyz=xyz,tet10=tt,tri6=ff,quality=quality,node_tags=ids,element_tags=eids);np.savez_compressed(folder/'mesh.npz',**m);write(folder/'GENERATION_RECEIPT.json',dict(UTC=now(),source_id=SID,candidate_id='M2_C1',protocol_version=VERSION,elapsed_s=time.perf_counter()-start,nodes=len(xyz),Tet10=len(tt),quality_min_before_full_acceptance=float(quality.min()),maximum_boundary_node_initialization_shift_mm=maxshift,STEP_SHA256=sha(R/'01_frozen_protocol/geometry/standardized_planar_rear.step'),CAD_patch_entities=patches,mesh_SHA256=sha(folder/'mesh.npz')))
 # Expanded independent checks include the original failure region and the16 lowest-SICN elements.
 center3=xyz[tt[:,:4]].mean(1);roi=(np.linalg.norm(center3[:,:2]-center,axis=1)<.6)&(abs(center3[:,2]-sp['front'].ev(center3[:,0],center3[:,1]))<.7);selected=np.unique(np.r_[np.flatnonzero(roi),np.argsort(quality)[:16]]);result=accept(m,folder,affected=selected);proof_ids=np.argsort(quality)[:16];proof=certify(xyz[tt[proof_ids]],proof_ids,'M2_C1');table(R/'08_quadratic_quality/M2_C1_BERNSTEIN_BOUNDS.csv',proof);result['exact_Bernstein_checked_lowest_SICN_elements']=len(proof);result['exact_Bernstein_positive_elements']=sum(z['exact_positive_Bernstein_bound'] for z in proof);write(folder/'PRE_SOLVER_QUALIFICATION.json',result)
 entry.update(status='QUALIFIED' if result['pre_solver_qualified'] else 'FAILED',mesh_SHA256=sha(folder/'mesh.npz'));write(ledgerpath,ledger);write(R/'07_refined_M2/FINAL_M2.json',dict(candidate_id='M2_C1',qualified=result['pre_solver_qualified'],status='C02_M2_QUALIFIED' if result['pre_solver_qualified'] else 'C02_M2_PARTIAL',receipt=str((folder/'PRE_SOLVER_QUALIFICATION.json').relative_to(R)),mesh_SHA256=sha(folder/'mesh.npz')));print('M2_FINAL',result,flush=True)
if __name__=='__main__':main()
