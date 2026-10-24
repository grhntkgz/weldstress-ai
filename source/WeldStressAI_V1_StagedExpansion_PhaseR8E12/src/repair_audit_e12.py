"""Actual repair-node and support audit; no mesh construction or changes."""
from common_r3 import *
from quality_r1 import custom_quality,samples_Q1,GM_EDGES
def main():
 protect();result=[];nodes=[]
 ledger=read(R/'14_reproducibility/FULL_CANDIDATE_LEDGER.json')
 for a in ledger:
  if a['kind']!='MATERIALIZED_S1_REPAIR':continue
  l=a['mesh_level'];base=R/('06_recovered_M1' if l=='M1' else '07_refined_M2')/(l+'_C1');final=base.parent/a['candidate_id'];old=np.load(base/'mesh.npz');new=np.load(final/'mesh.npz');changed=np.flatnonzero(np.any(old['xyz']!=new['xyz'],axis=1));boundary=np.unique(old['tri6']);corners=np.unique(old['tet10'][:,:4]);assert not np.intersect1d(changed,boundary).size and not np.intersect1d(changed,corners).size;assert np.array_equal(old['tet10'],new['tet10']) and np.array_equal(old['tri6'],new['tri6']);actual=np.flatnonzero(np.isin(old['tet10'],changed).any(1));d=read(base/'FAILURE_DIAGNOSIS.json');bad=np.array(d['failed_elements'],int);co=old['xyz'][old['tet10'][bad]];linear=co.copy();linear[:,4:]=co[:,GM_EDGES].mean(2);det,q=custom_quality(linear,samples_Q1())
  result.append(dict(source_id=SID,level=l,baseline=base.name,final=final.name,failed_elements=bad.tolist(),old_sampled_J_min=min(d['failed_min_J']),old_min_SICN=min(d['failed_SICN']),actual_moved_nodes=len(changed),actual_affected_elements=len(actual),eligible_optimizer_nodes=len(d['movable_interior_midsides']),all_corners_unchanged=True,all_external_boundary_unchanged=True,connectivity_unchanged=True,linear_midside_counterfactual_J_min=float(det.min()),linear_midside_counterfactual_SICN_min=float(q.min()),counterfactual_is_diagnostic_not_candidate=True,cause_scope='High-order placement quality diagnosed from actual sample Jacobians/topology and linear-midside counterfactual; no claim of source defect or universal cause.'))
  for i in changed:
   v=new['xyz'][i]-old['xyz'][i];nodes.append(dict(source_id=SID,level=l,candidate=final.name,node_index=int(i),gmsh_node_tag=int(old['node_tags'][i]),old_X=old['xyz'][i,0],old_Y=old['xyz'][i,1],old_Z=old['xyz'][i,2],new_X=new['xyz'][i,0],new_Y=new['xyz'][i,1],new_Z=new['xyz'][i,2],displacement_mm=float(np.linalg.norm(v))))
 table(R/'ACTUAL_MOVED_NODES.csv',nodes,['source_id','level','candidate','node_index','gmsh_node_tag','old_X','old_Y','old_Z','new_X','new_Y','new_Z','displacement_mm']);write(R/'08_quadratic_quality/ACTUAL_REPAIR_AUDIT.json',dict(source_id=SID,repairs=result,actual_moved_nodes=len(nodes),source_geometry_changed=False));print('REPAIR_AUDIT',SID,len(result),'repairs',len(nodes),'actualmoved')
if __name__=='__main__':main()
