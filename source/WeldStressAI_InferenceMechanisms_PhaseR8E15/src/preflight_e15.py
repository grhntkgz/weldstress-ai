from common_e15 import *
import numpy as np
from metric_e14 import metric,quantile

def main():
 verify_protocol();gate();checks=[]
 # Analytic fixtures, independent arithmetic expectations.
 m=metric(np.array([1.,3.]),np.array([2.,2.]),np.array([1.,3.]),np.array([[0.,0,0],[1.,0,0]]));assert abs(m['MAE_MPa']-1)<1e-14 and abs(m['L2']-(1/7)**.5)<1e-14;assert abs(quantile(np.array([1.,3.]),np.array([1.,3.]))-(1+2*(.95-.25)/.75))<1e-14
 z=np.array([2.,6.,4.]);idx=np.array([0,0,1]);raw=np.array([1.,3.,2.]);den=np.bincount(idx,weights=raw);ww=raw/den[idx];assert np.allclose(np.bincount(idx,weights=ww),1,atol=1e-15);assert np.array_equal(np.bincount(idx,weights=ww*z),np.array([5.,4.]));checks.append(dict(check='analytic_metric_weight_fixtures',passed=True))
 for a in rows(R/'07_same_point_contexts/SHIFT_GEOMETRY_REGISTRY.csv'):
  g=dict(np.load(a['geometry_path']));sid=a['source_id'];full=dict(np.load(H/'02_geometry'/(sid+'.npz')));ii=np.searchsorted(full['source_ids'],g['source_ids']);assert np.array_equal(g['source_ids'],full['source_ids'][ii]);assert np.array_equal(g['xyz'],full['xyz'][ii]);assert np.isfinite(g['features']).all();assert len(set(g['source_ids'][g['context']]))==4096;assert float(a['query_margin_mm'])>3
  # Separate bincount reconstruction of visible incident areas and normals.
  t=g['triangles'];v=g['xyz'];cross=np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]]);aa=np.linalg.norm(cross,axis=1)/2;n=len(v);area=np.bincount(t.ravel(),weights=np.repeat(aa/3,3),minlength=n);nr=np.column_stack([np.bincount(t.ravel(),weights=np.repeat(cross[:,k]/2,3),minlength=n) for k in range(3)]);nr/=np.linalg.norm(nr,axis=1)[:,None];assert np.allclose(area,g['area'],rtol=1e-12,atol=1e-12);assert np.allclose(nr,g['normal'],rtol=1e-12,atol=1e-12);assert np.max(abs((nr.astype('f4')-g['features'][:,3:6])))==0
  checks.append(dict(check='independent_visible_geometry_'+sid+'_'+a['condition']+'_'+a['tile'],passed=True))
 for rr in rows(R/'02_source_geometry/CORE_REGISTRY.csv'):
  s=dict(np.load(rr['path']));counts=np.zeros(len(s['source_ids']),int);w=np.zeros(len(counts));ws=[];pos=[]
  for t in [a for a in rows(R/'ORIGINAL_TILE_TOPOLOGY.csv') if a['source_id']==rr['source_id']]:
   loc=np.flatnonzero((s['xyz'][:,0]>=float(t['overlap_query_min_mm'])-1e-8)&(s['xyz'][:,0]<=float(t['overlap_query_max_mm'])+1e-8));r=(float(t['query_X_max_mm'])-float(t['query_X_min_mm']))/2+1;weight=np.maximum(1e-6,1-abs(s['xyz'][loc,0]-float(t['center_X_mm']))/r);counts[loc]+=1;w[loc]+=weight;ws.append(weight);pos.append(loc)
  assert (counts>0).all();assert (counts>1).any();assert np.max(abs(np.bincount(np.concatenate(pos),weights=np.concatenate(ws)/w[np.concatenate(pos)],minlength=len(counts))-1))<=1e-12;checks.append(dict(check='coverage_and_weight_'+rr['source_id'],passed=True))
 table(R/'18_independent_verification/PREEXECUTION_CHECKS.csv',checks);write(R/'18_independent_verification/PREFLIGHT_PASS.json',dict(UTC=now(),passed=True,checks=len(checks),resource=gate()));print('PREFLIGHT_PASS',len(checks),flush=True)
if __name__=='__main__':main()
