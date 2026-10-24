from common_r1 import *
from scipy.spatial import cKDTree
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
