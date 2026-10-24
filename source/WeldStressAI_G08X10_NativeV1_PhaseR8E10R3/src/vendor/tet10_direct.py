"""Independent isoparametric SOLID187 pure-displacement kinematics. No stress-export input."""
from tensor_ai import np,pack,principal
EDGES=np.array([[0,1],[1,2],[2,0],[0,3],[1,3],[2,3]])
DL=np.array([[-1.,-1.,-1.],[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])
NODES=np.concatenate([np.eye(4),np.eye(4)[EDGES].mean(1)])
GP=np.full((4,4),(5-np.sqrt(5))/20);np.fill_diagonal(GP,(5+3*np.sqrt(5))/20)
FACEQ=[]
for face in [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]:
 for j in range(3):
  a=np.zeros(4);a[face]=1/6;a[face[j]]=2/3;FACEQ.append(a)
FACEQ=np.array(FACEQ)
def shape(L):
 L=np.asarray(L);N=np.concatenate([L*(2*L-1),4*L[...,EDGES[:,0]]*L[...,EDGES[:,1]]],axis=-1)
 dn=np.concatenate([(4*L[...,None]-1)*DL,4*(L[...,EDGES[:,0],None]*DL[EDGES[:,1]]+L[...,EDGES[:,1],None]*DL[EDGES[:,0]])],axis=-2)
 return N,dn
def bmatrix(d):
 B=np.zeros(d.shape[:-2]+(6,30))
 B[...,0,0::3]=d[...,0];B[...,1,1::3]=d[...,1];B[...,2,2::3]=d[...,2]
 B[...,3,0::3]=d[...,1];B[...,3,1::3]=d[...,0];B[...,4,1::3]=d[...,2];B[...,4,2::3]=d[...,1];B[...,5,0::3]=d[...,2];B[...,5,2::3]=d[...,0]
 return B
def constitutive(eps,E=210000.,nu=.30):
 G=E/(2*(1+nu));lam=E*nu/((1+nu)*(1-2*nu));return 2*G*eps+lam*np.trace(eps,axis1=-2,axis2=-1)[...,None,None]*np.eye(3)
def evaluate(x,u,L):
 N,dn=shape(L);J=np.einsum('...ia,...ib->...ab',x,dn);det=np.linalg.det(J)
 if not (np.isfinite(det).all() and (det>0).all()):raise ValueError('Invalid nonpositive Tet10 Jacobian')
 inv=np.linalg.inv(J);dx=np.einsum('...ib,...ba->...ia',dn,inv);grad=np.einsum('...ia,...ib->...ab',u,dx);eps=(grad+np.swapaxes(grad,-1,-2))/2;sig=constitutive(eps)
 return dict(xyz=np.einsum('...i,...ia->...a',N,x),u=np.einsum('...i,...ia->...a',N,u),J=J,detJ=det,dNdx=dx,gradient=grad,strain=eps,stress=sig,sigma1=principal(sig),principal_strains=np.linalg.eigvalsh(eps))
