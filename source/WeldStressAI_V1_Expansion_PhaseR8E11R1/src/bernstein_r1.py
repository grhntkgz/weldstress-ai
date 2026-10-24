"""Exact-rational cubic Bernstein determinant bound for changed Tet10 elements."""
from fractions import Fraction as F
from math import factorial
import itertools
from common_r1 import *
from quality_r1 import NATIVE_PERM,NATIVE_EDGES

ALPHA=[(a,b,c,3-a-b-c) for a in range(4) for b in range(4-a) for c in range(4-a-b)]
def inverse_fraction(A):
 n=len(A);m=[row[:]+[F(int(i==j)) for j in range(n)] for i,row in enumerate(A)]
 for j in range(n):
  pivot=next(i for i in range(j,n) if m[i][j]);m[j],m[pivot]=m[pivot],m[j];v=m[j][j];m[j]=[x/v for x in m[j]]
  for i in range(n):
   if i!=j and m[i][j]:v=m[i][j];m[i]=[a-v*b for a,b in zip(m[i],m[j])]
 return [row[n:] for row in m]
def determinant(co,bary):
 dl=[[-1,-1,-1],[1,0,0],[0,1,0],[0,0,1]];d=[]
 for i in range(4):d.append([(4*bary[i]-1)*v for v in dl[i]])
 for a,b in NATIVE_EDGES:d.append([4*(bary[a]*dl[b][j]+bary[b]*dl[a][j]) for j in range(3)])
 J=[[sum(co[i][a]*d[i][b] for i in range(10)) for b in range(3)] for a in range(3)]
 return J[0][0]*(J[1][1]*J[2][2]-J[1][2]*J[2][1])-J[0][1]*(J[1][0]*J[2][2]-J[1][2]*J[2][0])+J[0][2]*(J[1][0]*J[2][1]-J[1][1]*J[2][0])
def certify(coords,indices,candidate):
 L=[[F(v,3) for v in a] for a in ALPHA];V=[]
 for bary in L:
  row=[]
  for a in ALPHA:
   multi=F(factorial(3),np.prod([factorial(i) for i in a]).item());value=multi
   for x,p in zip(bary,a):value*=x**p
   row.append(value)
  V.append(row)
 inv=inverse_fraction(V);results=[];certificates=[]
 for e,raw in zip(indices,coords[:,NATIVE_PERM]):
  co=[[F.from_float(float(v)) for v in p] for p in raw];origin=co[0];co=[[v-o for v,o in zip(p,origin)] for p in co];vals=[determinant(co,l) for l in L];coef=[sum(a*b for a,b in zip(row,vals)) for row in inv];lower=min(coef);upper=max(coef);results.append(dict(element_index=int(e),exact_positive_Bernstein_bound=lower>0,lower_detJ_mm3=float(lower),upper_detJ_mm3=float(upper)));certificates.append(dict(element_index=int(e),multiindices=ALPHA,exact_Bernstein_coefficients=[str(v) for v in coef],positive=lower>0))
 write(R/'08_quadratic_quality'/(candidate+'_EXACT_BERNSTEIN_CERTIFICATES.json'),dict(candidate_id=candidate,source_id=SID,protocol_version=VERSION,method='Exact Fraction arithmetic on exact binary64 node coordinates; determinant cubic in barycentric coordinates; degree3 Bernstein convex-hull bounds. No floating roundoff in coefficient signs.',scope='Affected elements only, not a whole-mesh positivity certificate',elements=certificates));return results
