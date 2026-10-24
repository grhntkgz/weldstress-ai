import numpy as np
from scipy.interpolate import RectBivariateSpline
from OCP.Geom import Geom_BSplineSurface
from OCP.TColgp import TColgp_Array2OfPnt
from OCP.TColStd import TColStd_Array1OfReal,TColStd_Array1OfInteger
from OCP.gp import gp_Pnt
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
import cadquery as cq
def fit(x,y,z,stride=2):
    ids=np.unique(np.r_[np.arange(0,len(x),stride),len(x)-1])
    return RectBivariateSpline(x[ids],y,z[ids,:],kx=3,ky=3,s=0)
def cad_surface(spline):
    tx,ty=spline.get_knots(); kx,ky=spline.degrees
    nx=len(tx)-kx-1; ny=len(ty)-ky-1
    coeff=spline.get_coeffs().reshape(nx,ny)
    gx=np.array([np.mean(tx[i+1:i+kx+1]) for i in range(nx)])
    gy=np.array([np.mean(ty[i+1:i+ky+1]) for i in range(ny)])
    poles=TColgp_Array2OfPnt(1,nx,1,ny)
    for i in range(nx):
        for j in range(ny): poles.SetValue(i+1,j+1,gp_Pnt(float(gx[i]),float(gy[j]),float(coeff[i,j])))
    def knots(t):
        u,m=np.unique(t,return_counts=True); a=TColStd_Array1OfReal(1,len(u)); b=TColStd_Array1OfInteger(1,len(u))
        for i,(v,n) in enumerate(zip(u,m)): a.SetValue(i+1,float(v)); b.SetValue(i+1,int(n))
        return a,b
    ax,mx=knots(tx); ay,my=knots(ty)
    surf=Geom_BSplineSurface(poles,ax,ay,mx,my,kx,ky,False,False)
    face=cq.Face(BRepBuilderAPI_MakeFace(surf,1e-7).Face())
    return surf,face
