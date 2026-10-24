from common_e10 import *
from scipy.interpolate import RectBivariateSpline
from scipy.spatial import cKDTree
from geometry_e10 import original_height,closest_T0
sys.path.insert(0,str(R/'src/vendor'))
from shape5e import tri,Q

def tetshape(L):
 edges=np.array([[0,1],[1,2],[2,0],[0,3],[1,3],[2,3]]);DL=np.array([[-1.,-1.,-1.],[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])
 return np.concatenate([L*(2*L-1),4*L[...,edges[:,0]]*L[...,edges[:,1]]],axis=-1),np.concatenate([(4*L[...,None]-1)*DL,4*(L[...,edges[:,0],None]*DL[edges[:,1]]+L[...,edges[:,1],None]*DL[edges[:,0]])],axis=-2)

def project(xyz,ff,points):
 ec=xyz[ff];tree=cKDTree(ec[:,:3,:2].mean(1));out=[];viols=[];linear=[];closest=[]
 for st in range(0,len(points),1500):
  pp=points[st:st+1500];_,ix=tree.query(pp[:,:2],k=min(20,len(ec)));co=ec[ix];a=co[:,:,0,:2];J=np.stack([co[:,:,1,:2]-a,co[:,:,2,:2]-a],axis=-1);rs0=np.linalg.solve(J,(pp[:,None,:2]-a)[...,None])[...,0];rs=rs0.copy()
  for _ in range(8):
   N,dr,ds=tri(rs[:,:,0],rs[:,:,1]);p=np.einsum('nki,nkij->nkj',N,co[:,:,:,:2]);jr=np.einsum('nki,nkij->nkj',dr,co[:,:,:,:2]);js=np.einsum('nki,nkij->nkj',ds,co[:,:,:,:2]);rs-=np.linalg.solve(np.stack([jr,js],axis=-1),(p-pp[:,None,:2])[...,None])[...,0]
  viol=np.maximum.reduce([-rs[:,:,0],-rs[:,:,1],rs.sum(-1)-1,np.zeros(rs.shape[:2])]);j=viol.argmin(1);row=np.arange(len(pp));coord=co[row,j];rs=rs[row,j];N,_,_=tri(rs[:,0],rs[:,1]);mapped=np.einsum('ni,nij->nj',N,coord);out.extend(np.linalg.norm(mapped-pp,axis=1));viols.extend(viol[row,j]);r0=rs0[row,j];lin=coord[:,0]*(1-r0.sum(1))[:,None]+coord[:,1]*r0[:,0,None]+coord[:,2]*r0[:,1,None];linear.extend(np.linalg.norm(lin-pp,axis=1))
  # Closest point on the actual curved quadratic patch; bounded projected Gauss-Newton.
  rr=rs.copy()
  for _ in range(12):
   N,dr,ds=tri(rr[:,0],rr[:,1]);p=np.einsum('ni,nij->nj',N,coord);jr=np.einsum('ni,nij->nj',dr,coord);js=np.einsum('ni,nij->nj',ds,coord);J=np.stack([jr,js],axis=-1);delta=np.linalg.solve(np.einsum('nai,naj->nij',J,J),np.einsum('nai,na->ni',J,p-pp)[...,None])[...,0];rr=np.maximum(0,rr-delta);rr/=np.maximum(1,rr.sum(1))[:,None]
  N,_,_=tri(rr[:,0],rr[:,1]);closest.extend(np.linalg.norm(np.einsum('ni,nij->nj',N,coord)-pp,axis=1))
 return np.array(out),np.array(viols),np.array(linear),np.array(closest)

def audit(sid,level,folder):
 m=np.load(folder/'mesh.npz');xx=m['xyz'];tt=m['tet10'];surf=m['tri6'];src=np.load(R/'04_standardized_solids'/sid/'solid_source.npz');sp={k:RectBivariateSpline(src['x'][::2],src['y'],src[k][::2],s=0) for k in ['front','back']};cent=xx[surf[:,:3]].mean(1);x=src['x'];y=src['y'];mask=(cent[:,0]>x[0]+1e-5)&(cent[:,0]<x[-1]-1e-5)&(cent[:,1]>y[0]+1e-5)&(cent[:,1]<y[-1]-1e-5)&(cent[:,2]>(sp['front'].ev(cent[:,0],cent[:,1])+sp['back'].ev(cent[:,0],cent[:,1]))/2);ff=surf[mask];points=src['source_xyz'];err,viol,linear,cp=project(xx,ff,points)
 xr=np.unique(points[:,0]);yr=np.unique(points[:,1]);ref=dict(x=xr,y=yr,front=points[:,2].reshape(len(xr),len(yr)));faces=xx[ff];reverse=[];reversecp=[];area=np.zeros(len(ff))
 for r,s,w in Q:
  N,dr,ds=tri(r,s);p=np.einsum('i,eij->ej',N,faces);cross=np.cross(np.einsum('i,eij->ej',dr,faces),np.einsum('i,eij->ej',ds,faces));area+=w*np.linalg.norm(cross,axis=1);reverse.extend(abs(p[:,2]-original_height(ref,p)));reversecp.extend(closest_T0(ref,p))
 reverse=np.array(reverse);reversecp=np.array(reversecp);GP=np.full((4,4),(5-np.sqrt(5))/20);np.fill_diagonal(GP,(5+3*np.sqrt(5))/20);samples=np.vstack([np.eye(4),GP,np.full((1,4),.25),np.random.default_rng(20261020).dirichlet(np.ones(4),64)]);dn=tetshape(samples)[1];mins=[];perm=[0,1,2,3,4,5,6,7,9,8]
 for st in range(0,len(tt),500):mins.extend(np.linalg.det(np.einsum('eia,qib->eqab',xx[tt[st:st+500]][:,perm],dn)).min(1))
 mins=np.array(mins);datum=read(R/'03_parent_datum'/(sid+'.json'));fc=faces[:,:3].mean(1);parent=datum['intercept_Z_mm']+datum['slope_X']*(fc[:,0]-datum['origin_X_mm'])+datum['slope_Y']*(fc[:,1]-datum['origin_Y_mm']);weld=(fc[:,2]-parent)/np.sqrt(1+datum['slope_X']**2+datum['slope_Y']**2)>=.5;edges=np.linalg.norm(xx[ff[:,[1,2,0]]]-xx[ff[:,:3]],axis=2)
 checks=dict(node_limit=len(xx)<=350000,element_limit=len(tt)<=230000,minSICN=float(m['quality'].min())>=.02,positive_sampled_J=bool(np.isfinite(mins).all() and (mins>0).all()),all_nodes_used=len(np.unique(tt))==len(xx),source_projection=bool((viol<=1e-4).all()),source_forward_P95=bool(np.percentile(err,95)<=.01),source_forward_max=bool(err.max()<=.04),reverse_P95=bool(np.percentile(reverse,95)<=.01),reverse_max=bool(reverse.max()<=.04))
 q=dict(UTC=now(),source_id=sid,level=level,passed=all(checks.values()),checks=checks,nodes=len(xx),elements=len(tt),front_faces=len(ff),minSICN=float(m['quality'].min()),quality_P01=float(np.percentile(m['quality'],1)),minimum_sampled_J_mm3=float(mins.min()),negative_J_elements=int((mins<0).sum()),zero_J_elements=int((mins==0).sum()),Jacobian_samples_per_element=73,continuous_J_proven=False,source_forward_P95_mm=float(np.percentile(err,95)),source_forward_max_mm=float(err.max()),source_linear_P95_mm=float(np.percentile(linear,95)),source_linear_max_mm=float(linear.max()),actual_quadface_closest_P95_mm=float(np.percentile(cp,95)),actual_quadface_closest_max_mm=float(cp.max()),quadface_closest_method='bounded Gauss-Newton on same-XY candidate patch; diagnostic, no substitution for frozen sameXY gate',reverse_P95_mm=float(np.percentile(reverse,95)),reverse_max_mm=float(reverse.max()),reverse_actual_closest_T0_P95_mm=float(np.percentile(reversecp,95)),reverse_actual_closest_T0_max_mm=float(reversecp.max()),near_weld_edge_median_mm=float(np.median(edges[weld])),near_weld_edge_P90_mm=float(np.percentile(edges[weld],90)),near_weld_front_faces=int(weld.sum()),near_weld_front_face_area_mm2=float(area[weld].sum()),inverse_XY_max_violation=float(viol.max()),mesh_SHA256=sha(folder/'mesh.npz'))
 np.savez_compressed(folder/'QUADRATIC_GEOMETRY_AUDIT.npz',source_forward_mm=err,source_linear_mm=linear,source_closest_mm=cp,reverse_sameXY_mm=reverse,reverse_closest_T0_mm=reversecp,front_tri6=ff,front_face_area=area,front_face_weld=weld,min_sampled_J=mins,Jacobian_samples=samples)
 write(folder/'MESH_QUALIFICATION.json',q);return q

def run(sid,level):
 protect();resource_gate(1800*1024**2,2500*1024**2,1500*1024**2);assert not (R/'17_reproducibility/CAMPAIGN_STOP.json').exists();assert read(R/'04_standardized_solids'/sid/'CAD_QUALIFICATION.json')['passed'];folder=R/('06_M1_meshes' if level=='M1' else '07_M2_meshes')/sid;folder.mkdir(parents=True,exist_ok=True);assert not (folder/'mesh.npz').exists()
 ledgerpath=R/'17_reproducibility/MESH_ATTEMPTS.json';ledger=read(ledgerpath) if ledgerpath.exists() else [];assert sum(z['source_id']==sid and z['level']==level for z in ledger)<3;entry=dict(UTC=now(),source_id=sid,level=level,attempt=1,status='STARTED');ledger.append(entry);write(ledgerpath,ledger)
 src=np.load(R/'04_standardized_solids'/sid/'solid_source.npz');x=src['x'];y=src['y'];sp={s:RectBivariateSpline(x[::2],y,src[s][::2],s=0) for s in ['front','back']};datum=read(R/'03_parent_datum'/(sid+'.json'));h=.4 if level=='M1' else .3
 # Geometry-only sizing: measured height proxy plus2mm collar, fixed before stress.
 points=src['source_xyz'];parent=datum['intercept_Z_mm']+datum['slope_X']*(points[:,0]-datum['origin_X_mm'])+datum['slope_Y']*(points[:,1]-datum['origin_Y_mm']);proxy=(points[:,2]-parent)/np.sqrt(1+datum['slope_X']**2+datum['slope_Y']**2)>=.5;tree=cKDTree(points[proxy,:2]);_,i=tree.query(points[:,:2]);dist=np.linalg.norm(points[:,:2]-points[proxy,:2][i],axis=1);weight=np.clip(1-dist/2,0,1).reshape(len(x),len(y));hs=.6-(.6-h)*weight;hs=hs[::2];xs=x[::2];nx=len(xs);ny=len(y);ztable=np.stack([src['front'][::2],src['back'][::2]])
 write(folder/'SIZING_FREEZE.json',dict(UTC=now(),weld_size_mm=h,parent_size_mm=.6,bulk_max_mm=2.5,growth=1.,criterion='heightnormal>=.5mm plus2mm geometry collar;back parent.6',stress_inspected=False))
 import gmsh
 def callback(dim,tag,X,Y,Z,lc):
  u=np.clip((X-xs[0])/(xs[1]-xs[0]),0,nx-1-1e-9);v=np.clip((Y-y[0])/(y[1]-y[0]),0,ny-1-1e-9);i=int(u);j=int(v);a=u-i;b=v-j;w=np.array([(1-a)*(1-b),a*(1-b),(1-a)*b,a*b]);zz=ztable[:,[i,i+1,i,i+1],[j,j,j+1,j+1]]@w;s=0 if abs(Z-zz[0])<=abs(Z-zz[1]) else 1;size=float(hs[[i,i+1,i,i+1],[j,j,j+1,j+1]]@w) if s==0 else .6;return min(2.5,size+abs(Z-zz[s]))
 start=time.perf_counter();gmsh.initialize();gmsh.logger.start();gmsh.option.setNumber('General.NumThreads',2);gmsh.model.add(sid+'_'+level)
 try:
  gmsh.model.occ.importShapes(str(R/'04_standardized_solids'/sid/'standardized_planar_rear.step'));gmsh.model.occ.synchronize();assert len(gmsh.model.getEntities(3))==1;tags=[]
  for dim,tag in gmsh.model.getEntities(2):
   b=gmsh.model.getBoundingBox(dim,tag)
   if b[3]-b[0]>.99*(x[-1]-x[0]) and b[4]-b[1]>.99*(y[-1]-y[0]):tags.append(tag)
  assert len(tags)==2;tags=sorted(tags,key=lambda z:gmsh.model.occ.getCenterOfMass(2,z)[2],reverse=True)
  for k,v in [('Mesh.MeshSizeMin',h),('Mesh.MeshSizeMax',2.5),('Mesh.MeshSizeFromPoints',0),('Mesh.MeshSizeFromCurvature',0),('Mesh.MeshSizeExtendFromBoundary',0),('Mesh.Algorithm3D',1),('Mesh.RandomSeed',20261017),('Mesh.SecondOrderLinear',1),('Mesh.Binary',1)]:gmsh.option.setNumber(k,v)
  gmsh.model.mesh.setSizeCallback(callback);gmsh.model.mesh.generate(3);gmsh.model.mesh.optimize('Netgen');gmsh.write(str(folder/'linear_checkpoint.msh'));gmsh.model.mesh.setOrder(2);ids,xyz,_=gmsh.model.mesh.getNodes();order=np.argsort(ids);ids=ids[order];xyz=np.array(xyz).reshape(-1,3)[order]
  for side,tag in zip(['front','back'],tags):
   nn,_,_=gmsh.model.mesh.getNodes(2,tag,includeBoundary=True);ix=np.searchsorted(ids,nn);xyz[ix,2]=sp[side].ev(xyz[ix,0],xyz[ix,1])
   for node,p in zip(nn,xyz[ix]):_,param,_,_=gmsh.model.mesh.getNode(int(node));gmsh.model.mesh.setNode(int(node),p.tolist(),param)
  gmsh.model.mesh.rebuildNodeCache(False);eids,tet=gmsh.model.mesh.getElementsByType(11);tt=np.searchsorted(ids,np.array(tet).reshape(-1,10));_,surf=gmsh.model.mesh.getElementsByType(9);ff=np.searchsorted(ids,np.array(surf).reshape(-1,6));quality=np.asarray(gmsh.model.mesh.getElementQualities(eids,'minSICN'));gmsh.write(str(folder/'mesh.msh'));(folder/'gmsh.log').write_text('\n'.join(gmsh.logger.get()),encoding='utf8')
 finally:gmsh.logger.stop();gmsh.finalize()
 np.savez_compressed(folder/'mesh.npz',xyz=xyz,tet10=tt,tri6=ff,quality=quality,node_tags=ids,element_tags=eids);write(folder/'MESH_GENERATION.json',dict(UTC=now(),source_id=sid,level=level,elapsed_s=time.perf_counter()-start,nodes=len(xyz),Tet10=len(tt),minSICN=float(quality.min()),mesh_SHA256=sha(folder/'mesh.npz')))
 q=audit(sid,level,folder);entry.update(status='COMPLETE',passed=q['passed']);write(ledgerpath,ledger)
 if not q['passed']:write(R/'17_reproducibility/CAMPAIGN_STOP.json',dict(UTC=now(),source_id=sid,level=level,stage='QUADRATIC_MESH',evidence=str(folder/'MESH_QUALIFICATION.json')))
 print('MESH_QUALIFICATION',q,flush=True);return q
if __name__=='__main__':run(sys.argv[1],sys.argv[2])
