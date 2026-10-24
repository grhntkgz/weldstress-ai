from common_r1 import *
def original_height(ref,points):
 x=ref['x'];y=ref['y'];z=ref['front'];i=np.clip(np.searchsorted(x,points[:,0],side='right')-1,0,len(x)-2);j=np.clip(np.searchsorted(y,points[:,1],side='right')-1,0,len(y)-2);u=(points[:,0]-x[i])/(x[i+1]-x[i]);v=(points[:,1]-y[j])/(y[j+1]-y[j]);A=z[i,j];B=z[i+1,j];C=z[i,j+1];D=z[i+1,j+1];return np.where(v<=u,A*(1-u)+B*(u-v)+D*v,A*(1-v)+C*(v-u)+D*u)

def closest_T0(ref,points):
 # All possible nearer original graph triangles lie within this stencil when distance<.04mm.
 # Omitted cells are >=2*dx or >=dy away in XY; recorded and checked below.
 x=ref['x'];y=ref['y'];z=ref['front'];answer=[]
 for st in range(0,len(points),2000):
  p=points[st:st+2000];ii=np.clip(np.searchsorted(x,p[:,0])-1,0,len(x)-2);jj=np.clip(np.searchsorted(y,p[:,1])-1,0,len(y)-2);cand=[]
  for di in [-2,-1,0,1,2]:
   for dj in [-1,0,1]:
    i=np.clip(ii+di,0,len(x)-2);j=np.clip(jj+dj,0,len(y)-2);a=np.c_[x[i],y[j],z[i,j]];b=np.c_[x[i+1],y[j],z[i+1,j]];c=np.c_[x[i],y[j+1],z[i,j+1]];d=np.c_[x[i+1],y[j+1],z[i+1,j+1]];cand.extend([np.stack([a,b,d],axis=1),np.stack([a,d,c],axis=1)])
  t=np.stack(cand,axis=1);a=t[:,:,0];ab=t[:,:,1]-a;ac=t[:,:,2]-a;ap=p[:,None]-a;nn=np.cross(ab,ac);n2=(nn*nn).sum(-1);distplane=(ap*nn).sum(-1);proj=ap-distplane[...,None]/n2[...,None]*nn;aa=(ab*ab).sum(-1);bb=(ab*ac).sum(-1);cc=(ac*ac).sum(-1);u=((proj*ab).sum(-1)*cc-(proj*ac).sum(-1)*bb)/(aa*cc-bb*bb);v=((proj*ac).sum(-1)*aa-(proj*ab).sum(-1)*bb)/(aa*cc-bb*bb);dd=np.where((u>=0)&(v>=0)&(u+v<=1),distplane**2/n2,np.inf)
  for k,l in [(0,1),(1,2),(2,0)]:
   a=t[:,:,k];edge=t[:,:,l]-a;ap=p[:,None]-a;s=np.clip((ap*edge).sum(-1)/(edge*edge).sum(-1),0,1);dd=np.minimum(dd,((ap-s[...,None]*edge)**2).sum(-1))
  answer.extend(np.sqrt(dd.min(1)))
 out=np.array(answer);assert out.max()<min(2*np.diff(x).min(),np.diff(y).min()),'Closest T0 search stencil cannot certify global closest triangle';return out
