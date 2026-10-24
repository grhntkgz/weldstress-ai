from common_r3 import *
from quality_r1 import *
from acceptance_r1 import accept
from diagnosis_r1 import topology
from bernstein_r1 import certify
from scipy.interpolate import RectBivariateSpline
from scipy.spatial import cKDTree
from scipy.optimize import minimize

def save_selected(level,folder):
 p=R/'SELECTED_MESHES.json';s=read(p) if p.exists() else {};s[level]=dict(folder=str(folder),sha256=sha(folder/'mesh.npz'),qualification_SHA256=sha(folder/'PRE_SOLVER_QUALIFICATION.json'));write(p,s)

def generate(level,attempt,focus=None):
 resource_gate(1800*1024**2,2500*1024**2,1500*1024**2);folder=R/('06_recovered_M1' if level=='M1' else '07_refined_M2')/(level+'_C'+str(attempt))
 if (folder/'mesh.npz').exists():
  ledgerpath=R/'14_reproducibility/FULL_CANDIDATE_LEDGER.json';ledger=read(ledgerpath);entry=next(z for z in ledger if z['candidate_id']==folder.name);assert entry['status']=='STARTED','Completed candidate cannot be regenerated';m=dict(np.load(folder/'mesh.npz'));q=accept(m,folder);entry.update(status='QUALIFIED' if q['pre_solver_qualified'] else 'REJECTED',mesh_SHA256=sha(folder/'mesh.npz'),audit_resumed_without_new_mesh_generation=True);write(ledgerpath,ledger);return folder,m,q
 assert not folder.exists();folder.mkdir(parents=True)
 path=R/'14_reproducibility/FULL_CANDIDATE_LEDGER.json';ledger=read(path) if path.exists() else [];assert sum(z['mesh_level']==level for z in ledger)<3;entry=dict(UTC=now(),source_id=SID,candidate_id=folder.name,mesh_level=level,kind='FULL_MESH_GENERATION',status='STARTED');ledger.append(entry);write(path,ledger)
 src=np.load(R/'01_frozen_protocol/geometry/solid_source.npz');x=src['x'];y=src['y'];sp={s:RectBivariateSpline(x[::2],y,src[s][::2],s=0) for s in ['front','back']};d=read(R/'01_frozen_protocol/PARENT_DATUM.json');p=src['source_xyz'];height=(p[:,2]-d['intercept_Z_mm']-d['slope_X']*(p[:,0]-d['origin_X_mm'])-d['slope_Y']*(p[:,1]-d['origin_Y_mm']))/np.sqrt(1+d['slope_X']**2+d['slope_Y']**2);tree=cKDTree(p[height>=.5,:2]);dist,_=tree.query(p[:,:2]);h=.4 if level=='M1' else .3;hs=(.6-(.6-h)*np.clip(1-dist/2,0,1).reshape(len(x),len(y)))[::2];ztable=np.stack([src['front'][::2],src['back'][::2]]);xs=x[::2];nx=len(xs);ny=len(y)
 write(folder/'SIZING_FREEZE.json',dict(UTC=now(),source_id=SID,level=level,weld_h_mm=h,parent_h_mm=.6,bulk_max_mm=2.5,growth=1,seed=20261017,geometry_only_focus=focus,stress_inspected=False,source_STEP_SHA256=sha(R/'01_frozen_protocol/geometry/standardized_planar_rear.step')))
 def callback(dim,tag,X,Y,Z,lc):
  u=np.clip((X-xs[0])/(xs[1]-xs[0]),0,nx-1-1e-9);v=np.clip((Y-y[0])/(y[1]-y[0]),0,ny-1-1e-9);i=int(u);j=int(v);a=u-i;b=v-j;w=np.array([(1-a)*(1-b),a*(1-b),(1-a)*b,a*b]);zz=ztable[:,[i,i+1,i,i+1],[j,j,j+1,j+1]]@w;s=0 if abs(Z-zz[0])<=abs(Z-zz[1]) else 1;size=float(hs[[i,i+1,i,i+1],[j,j,j+1,j+1]]@w) if s==0 else .6
  if focus is not None and s==0:
   for center in focus['centers_XY_mm']:
    r=min(1,float(np.linalg.norm(np.array([X,Y])-center))/focus['radius_mm']);size=min(size,h+(.6-h)*r*r*(3-2*r))
  return min(2.5,size+abs(Z-zz[s]))
 import gmsh
 t=time.perf_counter();gmsh.initialize();gmsh.logger.start();gmsh.option.setNumber('General.NumThreads',2);gmsh.model.add(SID+'_'+level);patches={}
 try:
  gmsh.model.occ.importShapes(str(R/'01_frozen_protocol/geometry/standardized_planar_rear.step'));gmsh.model.occ.synchronize();assert len(gmsh.model.getEntities(3))==1;measured=[]
  for dim,tag in gmsh.model.getEntities(2):
   bb=gmsh.model.getBoundingBox(dim,tag)
   if bb[3]-bb[0]>.99*np.ptp(x) and bb[4]-bb[1]>.99*np.ptp(y):measured.append(tag)
   elif bb[3]-bb[0]<1e-4:patches[tag]='XMIN_CAP' if abs(bb[0]-x[0])<1e-4 else 'XMAX_CAP'
   else:patches[tag]='YMIN_CAP' if abs(bb[1]-y[0])<1e-4 else 'YMAX_CAP'
  assert len(measured)==2;measured.sort(key=lambda z:gmsh.model.occ.getCenterOfMass(2,z)[2],reverse=True);patches[measured[0]]='MEASURED_FRONT';patches[measured[1]]='ASSUMED_REAR'
  for k,v in [('Mesh.MeshSizeMin',h),('Mesh.MeshSizeMax',2.5),('Mesh.MeshSizeFromPoints',0),('Mesh.MeshSizeFromCurvature',0),('Mesh.MeshSizeExtendFromBoundary',0),('Mesh.Algorithm3D',1),('Mesh.RandomSeed',20261017),('Mesh.SecondOrderLinear',1),('Mesh.Binary',1)]:gmsh.option.setNumber(k,v)
  gmsh.model.mesh.setSizeCallback(callback);gmsh.model.mesh.generate(3);gmsh.model.mesh.optimize('Netgen');gmsh.write(str(folder/'linear_checkpoint.msh'));gmsh.model.mesh.setOrder(2);ids,xyz,_=gmsh.model.mesh.getNodes();order=np.argsort(ids);ids=ids[order];xyz=np.array(xyz).reshape(-1,3)[order];shifts=[]
  for side,tag in zip(['front','back'],measured):
   nn,_,_=gmsh.model.mesh.getNodes(2,tag,includeBoundary=True);ix=np.searchsorted(ids,nn);z=sp[side].ev(xyz[ix,0],xyz[ix,1]);shifts.append(float(abs(z-xyz[ix,2]).max()));xyz[ix,2]=z
   for node,co in zip(nn,xyz[ix]):_,param,_,_=gmsh.model.mesh.getNode(int(node));gmsh.model.mesh.setNode(int(node),co.tolist(),param)
  gmsh.model.mesh.rebuildNodeCache(False);eids,tet=gmsh.model.mesh.getElementsByType(11);tt=np.searchsorted(ids,np.array(tet).reshape(-1,10));_,surf=gmsh.model.mesh.getElementsByType(9);ff=np.searchsorted(ids,np.array(surf).reshape(-1,6));quality=np.array(gmsh.model.mesh.getElementQualities(eids,'minSICN'))
  for tag,name in patches.items():physical=gmsh.model.addPhysicalGroup(2,[tag]);gmsh.model.setPhysicalName(2,physical,name)
  physical=gmsh.model.addPhysicalGroup(3,[gmsh.model.getEntities(3)[0][1]]);gmsh.model.setPhysicalName(3,physical,'STANDARDIZED_'+SID+'_SOLID');gmsh.write(str(folder/'mesh.msh'));(folder/'gmsh.log').write_text('\n'.join(gmsh.logger.get()),encoding='utf8')
 finally:gmsh.logger.stop();gmsh.finalize()
 m=dict(xyz=xyz,tet10=tt,tri6=ff,quality=quality,node_tags=ids,element_tags=eids);np.savez_compressed(folder/'mesh.npz',**m);write(folder/'GENERATION_RECEIPT.json',dict(UTC=now(),source_id=SID,candidate_id=folder.name,elapsed_s=time.perf_counter()-t,nodes=len(xyz),Tet10=len(tt),min_initial_SICN=float(quality.min()),maximum_initial_boundary_projection_shift_mm=max(shifts),STEP_SHA256=sha(R/'01_frozen_protocol/geometry/standardized_planar_rear.step'),CAD_patch_entities=patches))
 q=accept(m,folder);entry.update(status='QUALIFIED' if q['pre_solver_qualified'] else 'REJECTED',mesh_SHA256=sha(folder/'mesh.npz'));write(path,ledger);return folder,m,q

def repair_s1(m,level,baseline):
 q=np.load(baseline/'GLOBAL_QUALITY.npz');failed=np.flatnonzero((q['quality']<.02)|(q['min_Q1_J']<=0));assert len(failed)>0;top=topology(m);tt=m['tet10'];xx=m['xyz'];movable=np.setdiff1d(np.unique(tt[failed,4:]),top['boundary_nodes']);corner=np.linalg.det(np.stack([xx[tt[:,1]]-xx[tt[:,0]],xx[tt[:,2]]-xx[tt[:,0]],xx[tt[:,3]]-xx[tt[:,0]]],axis=-1));assert (corner>0).all()
 write(baseline/'FAILURE_DIAGNOSIS.json',dict(source_id=SID,level=level,failed_elements=failed,failed_Gmsh_tags=m['element_tags'][failed],failed_min_J=q['min_Q1_J'][failed],failed_SICN=q['quality'][failed],positive_corner_orientation=True,shared_midsides_compatible=True,movable_interior_midsides=movable,source_defect_assumed=False,actual_boundary_node_count=len(top['boundary_nodes']),method='Actual high-order samples and topology, not a copied C02rootcause'))
 if len(movable)==0 or len(failed)>24:return None
 affected=np.flatnonzero(np.isin(tt,movable).any(1));coords=xx[tt[affected]].copy();distance=np.linalg.norm(coords[:,:4][:,:,None]-coords[:,:4][:,None,:],axis=-1);h=float(np.median(distance[distance>0]));L=samples_Q2();dn=derivative(L);positions=[np.where(tt[affected]==node) for node in movable];base=coords-coords[:,:4].mean(1)[:,None];path=R/'14_reproducibility/LOCAL_TRIAL_LEDGER.json';ledger=read(path) if path.exists() else [];allowed=read(GLOBAL/'R8E10R3_PROTOCOL_HASHES.json')['recovery']['S1_trials']
 for j,trial in enumerate(allowed,1):
  if sum(a['strategy']=='S1' for a in ledger)>=3:return None
  cap=trial['cap_over_h'];margin=trial['margin'];entry=dict(UTC=now(),strategy='S1',level=level,trial=j,status='STARTED',movable_nodes=len(movable),affected_elements=len(affected),cap_mm=cap*h,quality_margin=margin);ledger.append(entry);write(path,ledger);t=time.perf_counter()
  def placed(v):
   co=base.copy()
   for k,(ee,nn) in enumerate(positions):co[ee,nn]+=v.reshape(-1,3)[k]*h
   return co
  def constraint(v):return np.r_[(sicn_J(jacobians(placed(v),L))-margin).ravel(),cap**2-np.sum(v.reshape(-1,3)**2,axis=1)]
  res=minimize(lambda v:float(v@v),np.zeros(3*len(movable)),jac=lambda v:2*v,method='SLSQP',bounds=[(-cap,cap)]*(3*len(movable)),constraints=[dict(type='ineq',fun=constraint)],options=dict(maxiter=trial['maxiter'],ftol=1e-10,disp=False));delta=res.x.reshape(-1,3)*h;localcoords=coords.copy()
  for k,(ee,nn) in enumerate(positions):localcoords[ee,nn]+=delta[k]
  det,sicn=custom_quality(localcoords,L);feasible=bool((det>0).all() and sicn.min()>=.02 and np.linalg.norm(delta,axis=1).max()<=cap*h+1e-8);trialfolder=R/'05_local_repair_trials'/f'S1_{level}_{len(ledger)}';trialfolder.mkdir();np.savez_compressed(trialfolder/'LOCAL_PROTOTYPE.npz',node_indices=movable,old_coordinates=xx[movable],new_coordinates=xx[movable]+delta,displacements=delta,affected_element_indices=affected,local_Q2_det=det,local_Q2_SICN=sicn,Q2_samples=L);entry.update(status='LOCAL_FEASIBLE' if feasible else 'LOCAL_FAILED',optimizer_success=bool(res.success),message=str(res.message),elapsed_s=time.perf_counter()-t,maximum_displacement_mm=float(np.linalg.norm(delta,axis=1).max()),min_Q2_J_mm3=float(det.min()),min_Q2_SICN=float(sicn.min()));write(path,ledger);print('S1_TRIAL',entry,flush=True)
  if feasible:return dict(movable=movable,new=xx[movable]+delta,affected=affected,trial=str(trialfolder))
 return None

def main(level):
 protect();may_execute_source();assert read(R/'04_standardized_solids'/SID/'CAD_QUALIFICATION.json')['passed']
 if level=='M2':assert 'M1' in read(R/'SELECTED_MESHES.json') and read(LEVELS['M1']/'PRE_SOLVER_QUALIFICATION.json')['pre_solver_qualified']
 if (R/'SELECTED_MESHES.json').exists():assert level not in read(R/'SELECTED_MESHES.json'),'Do not improve qualified mesh'
 folder,m,q=generate(level,1)
 if not q['pre_solver_qualified']:
  if q['checks']['full_source_fidelity'] and not q['quality_pass']:
   local=repair_s1(m,level,folder)
   if local is not None:
    original=m;nm={k:v.copy() for k,v in m.items()};nm['xyz'][local['movable']]=local['new'];assert np.array_equal(nm['xyz'][np.unique(m['tri6'])],m['xyz'][np.unique(m['tri6'])]);assert np.array_equal(nm['xyz'][np.unique(m['tet10'][:,:4])],m['xyz'][np.unique(m['tet10'][:,:4])]);assert np.array_equal(nm['tet10'],m['tet10']);path=R/'14_reproducibility/FULL_CANDIDATE_LEDGER.json';ledger=read(path);assert sum(a['mesh_level']==level for a in ledger)<3;newfolder=folder.parent/(level+'_C2');newfolder.mkdir();entry=dict(UTC=now(),source_id=SID,candidate_id=newfolder.name,mesh_level=level,kind='MATERIALIZED_S1_REPAIR',status='STARTED');ledger.append(entry);write(path,ledger);nm['quality']=gmsh_quality(nm['xyz'],nm['tet10'],nm['node_tags'],nm['element_tags']);np.savez_compressed(newfolder/'mesh.npz',**nm);newq=accept(nm,newfolder,original_boundary_identity=True,affected=local['affected']);proof=certify(nm['xyz'][nm['tet10'][local['affected']]],local['affected'],newfolder.name);table(newfolder/'BERNSTEIN_BOUNDS.csv',proof);changed=np.flatnonzero(np.any(nm['xyz']!=original['xyz'],axis=1));table(newfolder/'LOCAL_NODE_DISPLACEMENTS.csv',[dict(node_index=int(i),gmsh_node_tag=int(nm['node_tags'][i]),old_X=original['xyz'][i,0],old_Y=original['xyz'][i,1],old_Z=original['xyz'][i,2],new_X=nm['xyz'][i,0],new_Y=nm['xyz'][i,1],new_Z=nm['xyz'][i,2],displacement_mm=float(np.linalg.norm(nm['xyz'][i]-original['xyz'][i])),boundary=False) for i in changed]);entry.update(status='QUALIFIED' if newq['pre_solver_qualified'] else 'REJECTED',mesh_SHA256=sha(newfolder/'mesh.npz'));write(path,ledger);folder,m,q=newfolder,nm,newq
  if not q['pre_solver_qualified']:
   # Remaining full candidate uses only prior failure locations, with no source or CAD edits.
   ledger=read(R/'14_reproducibility/FULL_CANDIDATE_LEDGER.json');attempt=sum(a['mesh_level']==level for a in ledger)+1
   if attempt<=3:
    quality=np.load(folder/'GLOBAL_QUALITY.npz');bad=np.flatnonzero((quality['quality']<.02)|(quality['min_Q1_J']<=0));centers=m['xyz'][m['tet10'][bad,:4]].mean(1)[:,:2] if len(bad) else np.empty((0,2));focus=dict(centers_XY_mm=centers.tolist(),radius_mm=1.2);folder,m,q=generate(level,attempt,focus)
 if not q['pre_solver_qualified']:
  write(GLOBAL/'21_reproducibility/CAMPAIGN_STOP.json',dict(UTC=now(),source_id=SID,stage=level+'_MESH_FINAL_FAILURE',evidence=str(folder/'PRE_SOLVER_QUALIFICATION.json'),candidate_budget_exhausted_or_nonrecoverable=True));print('CAMPAIGN_STOP',SID,level,flush=True);return
 selected=np.argsort(m['quality'])[:16];det,_=custom_quality(m['xyz'][m['tet10'][selected]],samples_Q2());assert (det>0).all();table(folder/'LOWEST16_BERNSTEIN_BOUNDS.csv',certify(m['xyz'][m['tet10'][selected]],selected,folder.name+'_LOWEST16'));save_selected(level,folder);print('MESH_SELECTED',SID,level,str(folder),q,flush=True)
if __name__=='__main__':main(sys.argv[1])
