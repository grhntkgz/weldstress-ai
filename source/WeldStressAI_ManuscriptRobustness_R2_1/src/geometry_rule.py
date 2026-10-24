"""Only geometry enters this module. No FE/prediction arrays or learned models."""
import numpy as np

def transition_segments(xyz,triangles,normal_relief):
    h=np.asarray(normal_relief,dtype=float)-.5
    selected=triangles[(h[triangles].min(1)<=0)&(h[triangles].max(1)>=0)]
    segments=[];ambiguous=0
    for t in selected:
        points=[]
        for a,b in [(t[0],t[1]),(t[1],t[2]),(t[2],t[0])]:
            if h[a]==0:points.append(xyz[a,:2])
            if h[a]*h[b]<0:points.append(xyz[a,:2]+(-h[a]/(h[b]-h[a]))*(xyz[b,:2]-xyz[a,:2]))
        unique=[]
        for p in points:
            if not any(np.linalg.norm(p-q)<=1e-10 for q in unique):unique.append(p)
        if len(unique)==2 and np.linalg.norm(unique[1]-unique[0])>1e-10:segments.append(unique)
        elif len(unique)>2:ambiguous+=1
    if ambiguous or not segments:return None,dict(status='NOT_EVALUABLE',ambiguous_triangles=ambiguous,segments=len(segments))
    seg=np.asarray(segments,dtype=float)
    if not np.isfinite(seg).all():return None,dict(status='NOT_EVALUABLE',reason='nonfinite segments')
    # Components are descriptive; retain every component with no score-dependent filtering.
    vertices={};parents=[]
    def vertex(p):
        key=tuple(np.round(p,8))
        if key not in vertices:vertices[key]=len(parents);parents.append(len(parents))
        return vertices[key]
    def find(a):
        while parents[a]!=a:parents[a]=parents[parents[a]];a=parents[a]
        return a
    for a,b in seg:
        ia,ib=vertex(a),vertex(b);parents[find(ia)]=find(ib)
    return seg,dict(status='EVALUABLE',segments=len(seg),components=len({find(a) for a in range(len(parents))}),ambiguous_triangles=0)

def distance_to_segments(xy,segments):
    a=segments[:,0];v=segments[:,1]-a;den=np.sum(v*v,axis=1);out=np.empty(len(xy))
    for start in range(0,len(xy),512):
        d=xy[start:start+512,None,:]-a[None,:,:];u=np.clip(np.sum(d*v[None,:,:],axis=2)/den[None,:],0,1);out[start:start+512]=np.sqrt(np.min(np.sum((d-u[:,:,None]*v[None,:,:])**2,axis=2),axis=1))
    return out
