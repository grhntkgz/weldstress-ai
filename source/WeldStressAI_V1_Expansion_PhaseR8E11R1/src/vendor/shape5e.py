import numpy as np
# Gmsh order: corners 0,1,2; midsides 01,12,20.
def tri(r,s):
 r,s=np.broadcast_arrays(r,s);l=1-r-s
 N=np.stack([l*(2*l-1),r*(2*r-1),s*(2*s-1),4*l*r,4*r*s,4*s*l],axis=-1)
 dr=np.stack([1-4*l,4*r-1,np.zeros_like(r),4*(l-r),4*s,-4*s],axis=-1)
 ds=np.stack([1-4*l,np.zeros_like(r),4*s-1,-4*r,4*r,4*(l-s)],axis=-1)
 return N,dr,ds
# Dunavant degree-5 quadrature; weights integrate over triangle area 1/2.
Q=np.array([[1/3,1/3,.225],[.05971587178977,.470142064105115,.132394152788506],[.470142064105115,.05971587178977,.132394152788506],[.470142064105115,.470142064105115,.132394152788506],[.797426985353087,.101286507323456,.125939180544827],[.101286507323456,.797426985353087,.125939180544827],[.101286507323456,.101286507323456,.125939180544827]])
Q[:,2]*=.5
def principal(S):
 t=np.zeros(S.shape[:-1]+(3,3));t[...,0,0]=S[...,0];t[...,1,1]=S[...,1];t[...,2,2]=S[...,2];t[...,0,1]=t[...,1,0]=S[...,3];t[...,1,2]=t[...,2,1]=S[...,4];t[...,0,2]=t[...,2,0]=S[...,5];return np.linalg.eigvalsh(t)[...,-1]
