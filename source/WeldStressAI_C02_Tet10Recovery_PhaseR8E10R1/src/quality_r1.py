from common_r1 import *
NATIVE_PERM=np.array([0,1,2,3,4,5,6,7,9,8]);GM_EDGES=np.array([[0,1],[1,2],[2,0],[0,3],[2,3],[1,3]]);NATIVE_EDGES=np.array([[0,1],[1,2],[2,0],[0,3],[1,3],[2,3]])
DL=np.array([[-1.,-1.,-1.],[1.,0,0],[0,1.,0],[0,0,1.]])
W=np.array([[1,.5,.5],[0,np.sqrt(3)/2,np.sqrt(3)/6],[0,0,np.sqrt(2/3)]]);WI=np.linalg.inv(W)
def derivative(L):
 L=np.asarray(L);return np.concatenate([(4*L[...,None]-1)*DL,4*(L[...,NATIVE_EDGES[:,0],None]*DL[NATIVE_EDGES[:,1]]+L[...,NATIVE_EDGES[:,1],None]*DL[NATIVE_EDGES[:,0]])],axis=-2)
def lattice(order):return np.array([[a,b,c,order-a-b-c] for a in range(order+1) for b in range(order+1-a) for c in range(order+1-a-b)],float)/order
def samples_Q1():return np.load(R/'00_integrity/baseline/QUADRATIC_GEOMETRY_AUDIT.npz')['Jacobian_samples']
def samples_Q2():return np.unique(np.vstack([samples_Q1(),lattice(8),lattice(12),np.random.default_rng(20261021).dirichlet(np.full(4,.25),256)]),axis=0)
def jacobians(coords,L):return np.einsum('eia,qib->eqab',coords[:,NATIVE_PERM],derivative(L))
def sicn_J(J):
 A=J@WI;det=np.linalg.det(A);cof=np.stack([np.cross(A[...,1,:],A[...,2,:]),np.cross(A[...,2,:],A[...,0,:]),np.cross(A[...,0,:],A[...,1,:])],axis=-2);return 3*det/np.sqrt(np.sum(A*A,axis=(-1,-2))*np.sum(cof*cof,axis=(-1,-2)))
def custom_quality(coords,L):
 J=jacobians(coords,L);return np.linalg.det(J),sicn_J(J)
def scalar_checks(coords,L):
 # Independently construct each derivative and matrix in scalar loops, without derivative()/einsum.
 dets=[];ss=[]
 for co in coords[:,NATIVE_PERM]:
  dd=[];qq=[]
  for bary in L:
   d=np.empty((10,3))
   for i in range(4):d[i]=(4*bary[i]-1)*DL[i]
   for k,(a,b) in enumerate(NATIVE_EDGES):d[4+k]=4*(bary[a]*DL[b]+bary[b]*DL[a])
   J=co.T@d;v=float(np.linalg.det(J));A=J@WI;adj=np.cross(A[[1,2,0]],A[[2,0,1]]);value=3*np.linalg.det(A)/(np.linalg.norm(A)*np.linalg.norm(adj));dd.append(v);qq.append(value)
  dets.append(dd);ss.append(qq)
 return np.array(dets),np.array(ss)
def gmsh_quality(xyz,tet10,node_tags,element_tags,write_path=None,tri6=None):
 import gmsh
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',2)
 try:
  gmsh.model.add('R1_read_only_quality_representation');gmsh.model.addDiscreteEntity(3,1);gmsh.model.mesh.addNodes(3,1,node_tags,xyz.ravel());gmsh.model.mesh.addElementsByType(1,11,element_tags,node_tags[tet10].ravel());q=np.array(gmsh.model.mesh.getElementQualities(element_tags,'minSICN'))
  if write_path is not None:
   assert Path(write_path).resolve().is_relative_to(R)
   if tri6 is not None:
    gmsh.model.addDiscreteEntity(2,2);gmsh.model.mesh.addElementsByType(2,9,np.arange(int(np.max(element_tags))+1,int(np.max(element_tags))+1+len(tri6)),node_tags[tri6].ravel())
   gmsh.option.setNumber('Mesh.Binary',1);gmsh.write(str(write_path))
  return q
 finally:gmsh.finalize()
def global_quality(m,xyz=None):
 xx=m['xyz'] if xyz is None else xyz;tt=m['tet10'];out=[];qs=[];L=samples_Q1();Lq=lattice(2)
 for st in range(0,len(tt),500):
  d,_=custom_quality(xx[tt[st:st+500]],L);out.extend(d.min(1));qs.extend(custom_quality(xx[tt[st:st+500]],Lq)[1].min(1))
 mins=np.array(out);independent=np.array(qs);gm=gmsh_quality(xx,tt,m['node_tags'],m['element_tags']);return dict(minJ=mins,quality=gm,independent_SICN=independent,summary=dict(nodes=len(xx),Tet10=len(tt),minSICN=float(gm.min()),SICN_P01=float(np.percentile(gm,1)),SICN_P05=float(np.percentile(gm,5)),SICN_P50=float(np.median(gm)),below_SICN020=int((gm<.02).sum()),minimum_Q1_J_mm3=float(mins.min()),negative_J_elements=int((mins<0).sum()),zero_J_elements=int((mins==0).sum()),near_zero_J_elements_1e12=int((abs(mins)<1e-12).sum()),Gmsh_vs_independent_SICN_max=float(abs(gm-independent).max()),quality_pass=bool(gm.min()>=.02 and (mins>0).all() and len(xx)<=350000 and len(tt)<=230000)))
