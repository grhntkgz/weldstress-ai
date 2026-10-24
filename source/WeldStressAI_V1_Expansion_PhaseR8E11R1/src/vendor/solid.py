import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing
from OCP.TopoDS import TopoDS
from OCP.BRepLib import BRepLib
def solid(front,back):
    def key(e):
        a=e.startPoint(); b=e.endPoint()
        return ('x',round(a.x,5)) if abs(a.x-b.x)<1e-6 else ('y',round(a.y,5))
    # Pair boundaries by XY projection. Front/back parameter bounds are identical.
    a=sorted(front.Edges(),key=key); b=sorted(back.Edges(),key=key)
    sides=[]
    for u,v in zip(a,b):
        assert key(u)==key(v)
        us=u.startPoint(); vs=v.startPoint(); ve=v.endPoint()
        if (us.x-vs.x)**2+(us.y-vs.y)**2 > (us.x-ve.x)**2+(us.y-ve.y)**2:
            v=cq.Edge(v.wrapped.Reversed())
        sides.append(cq.Face.makeRuledSurface(u,v))
    faces=[front,back]+sides
    sewing=BRepBuilderAPI_Sewing(1e-6)
    for f in faces: sewing.Add(f.wrapped)
    sewing.Perform()
    shell=cq.Shell(TopoDS.Shell_s(sewing.SewedShape()))
    out=cq.Solid.makeSolid(shell)
    BRepLib.OrientClosedSolid_s(out.wrapped)
    if not out.isValid() or out.Volume()<=0: raise ValueError('Invalid sewn solid')
    return out
def export(shape,path): cq.exporters.export(shape,str(path),exportType='STEP')
