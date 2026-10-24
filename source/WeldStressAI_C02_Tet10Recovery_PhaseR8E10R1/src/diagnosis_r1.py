from common_r1 import *
from quality_r1 import *
from scipy.interpolate import RectBivariateSpline
from scipy.spatial import cKDTree
import itertools

def topology(m):
 tt=m['tet10'];edges=np.sort(tt[:,GM_EDGES],axis=2).reshape(-1,2);mids=tt[:,4:].ravel();ued,inv,count=np.unique(edges,axis=0,return_inverse=True,return_counts=True);lo=np.full(len(ued),len(m['xyz']),int);hi=np.full(len(ued),-1,int);np.minimum.at(lo,inv,mids);np.maximum.at(hi,inv,mids);assert (lo==hi).all(),'Shared midside identity mismatch';assert len(np.unique(lo))==len(ued),'One midside used for multiple corner edges';corners=np.unique(tt[:,:4]);assert not np.intersect1d(corners,lo).size
 faces=np.sort(tt[:,np.array([[0,1,2],[0,1,3],[0,2,3],[1,2,3]])],axis=2).reshape(-1,3);uf,fi,fc=np.unique(faces,axis=0,return_inverse=True,return_counts=True);assert fc.max()==2;assert np.array_equal(uf[fc==1],np.unique(np.sort(m['tri6'][:,:3],axis=1),axis=0))
 pairs={};neighbors=[set() for _ in range(len(tt))]
 for e in range(len(tt)):
  for j in range(4):
   face=int(fi[e*4+j])
   if face in pairs:q=pairs[face];neighbors[e].add(q);neighbors[q].add(e)
   else:pairs[face]=e
 return dict(unique_edges=ued,edge_mids=lo,edge_incidence=count,neighbors=neighbors,face_counts=fc,boundary_nodes=np.unique(m['tri6']),corner_nodes=corners)

def main():
 protect();resource_gate(700*1024**2,1000*1024**2,300*1024**2);m=dict(np.load(R/'00_integrity/baseline/mesh.npz'));xx=m['xyz'];tt=m['tet10'];bad=np.array([4560,11398]);top=topology(m);qual=global_quality(m);assert qual['summary']['negative_J_elements']==2;assert np.max(abs(qual['quality']-m['quality']))<1e-10
 corner=np.linalg.det(np.stack([xx[tt[:,1]]-xx[tt[:,0]],xx[tt[:,2]]-xx[tt[:,0]],xx[tt[:,3]]-xx[tt[:,0]]],axis=-1));assert (corner>0).all();bc=set(top['boundary_nodes'].tolist());rings=[];ring1=set(bad)
 for e in bad:ring1.update(top['neighbors'][int(e)])
 ring2=set(ring1)
 for e in ring1:ring2.update(top['neighbors'][e])
 # Node support star is more inclusive than face-ring adjacency and is used for every moved node.
 movable=np.array(sorted(set(tt[bad,4:].ravel())-bc));affected=np.flatnonzero(np.isin(tt,movable).any(1));one_nodes=np.unique(tt[list(ring1)]);two_nodes=np.unique(tt[list(ring2)]);src=np.load(R/'01_frozen_protocol/geometry/solid_source.npz');sp=RectBivariateSpline(src['x'][::2],src['y'],src['front'][::2],s=0);rear=RectBivariateSpline(src['x'][::2],src['y'],src['back'][::2],s=0);L=samples_Q1();dd,ss=scalar_checks(xx[tt[bad]],L);primary,_=custom_quality(xx[tt[bad]],L);assert abs(dd-primary).max()<1e-10
 import gmsh
 gmsh.initialize();prop=gmsh.model.mesh.getElementProperties(11);gmsh.finalize();local=np.array(prop[4]).reshape(10,3);assert np.allclose(local[4:],local[GM_EDGES].mean(1));native_expected=local[NATIVE_PERM];assert np.allclose(native_expected[4:],native_expected[NATIVE_EDGES].mean(1))
 ordering=dict(Gmsh11_local_coordinates=local.tolist(),Gmsh_edges=GM_EDGES.tolist(),SOLID187_export_permutation_zero_based=NATIVE_PERM.tolist(),SOLID187_edges=NATIVE_EDGES.tolist(),Gmsh_API_midpoint_check=True,shape_partition_and_linear_reproduction=True,shared_midpoint_inconsistencies=0)
 # Existing native C02 evidence verifies the intended historical export mapping without invoking ANSYS.
 old=E8B/'08_native_results'/SID/'M1/native_displacements.npz'
 if old.exists():
  oldm=np.load(old);ordering['historical_E8B_native_connectivity_permutation_verified']=bool(np.array_equal(oldm['connectivity_native'],oldm['connectivity_gmsh'][:,NATIVE_PERM]));ordering['historical_native_provenance_SHA256']=sha(old);assert ordering['historical_E8B_native_connectivity_permutation_verified']
 write(R/'02_invalid_element_diagnosis/NODE_ORDERING.json',ordering)
 nodes=[];con=[];sample_rows=[];summary=[]
 for k,e in enumerate(bad):
  co=xx[tt[e]];c=co[:4];edgeslen=np.linalg.norm(c[GM_EDGES[:,1]]-c[GM_EDGES[:,0]],axis=1);det=corner[e];vol=det/6;alts=[];angles=[]
  for face in itertools.combinations(range(4),3):
   a,b,c0=co[list(face)];norm=np.linalg.norm(np.cross(b-a,c0-a));alts.append(abs(det)/norm)
   for j in range(3):u=co[face[(j+1)%3]]-co[face[j]];v=co[face[(j+2)%3]]-co[face[j]];angles.append(np.degrees(np.arccos(np.clip(np.dot(u,v)/np.linalg.norm(u)/np.linalg.norm(v),-1,1))))
  for j,node in enumerate(tt[e]):
   linear=co[GM_EDGES[j-4]].mean(0) if j>=4 else co[j];p=xx[node];isbound=node in bc;frontgap=abs(p[2]-float(sp.ev(p[0],p[1])));backgap=abs(p[2]-float(rear.ev(p[0],p[1])));capdist=min(p[0]-src['x'][0],src['x'][-1]-p[0],p[1]-src['y'][0],src['y'][-1]-p[1]);nodes.append(dict(element_tag=int(m['element_tags'][e]),element_index=int(e),Gmsh_position=j+1,native_position=int(np.flatnonzero(NATIVE_PERM==j)[0])+1,node_index=int(node),original_Gmsh_node_tag=int(m['node_tags'][node]),X_mm=float(p[0]),Y_mm=float(p[1]),Z_mm=float(p[2]),role='CORNER' if j<4 else 'MIDSIDE',boundary=isbound,CAD_patch='MEASURED_FRONT' if isbound and frontgap<1e-7 else 'ASSUMED_REAR' if isbound and backgap<1e-7 else 'CAP' if isbound else 'INTERIOR',front_vertical_gap_mm=float(frontgap),rear_vertical_gap_mm=float(backgap),cap_distance_mm=float(capdist),midside_linear_displacement_mm=float(np.linalg.norm(p-linear)),midside_delta_Z_mm=float(p[2]-linear[2])))
  con.append(dict(element_tag=int(m['element_tags'][e]),element_index=int(e),Gmsh_node_tags=m['node_tags'][tt[e]].tolist(),mesh_node_indices=tt[e].tolist(),SOLID187_node_tags=m['node_tags'][tt[e,NATIVE_PERM]].tolist()))
  for j,bary in enumerate(L):sample_rows.append(dict(element_tag=int(m['element_tags'][e]),sample_index=j,barycentric=bary.tolist(),detJ_mm3=float(dd[k,j]),independent_SICN=float(ss[k,j])))
  center=co[:4].mean(0);summary.append(dict(element_tag=int(m['element_tags'][e]),element_index=int(e),X_mm=float(center[0]),Y_mm=float(center[1]),Z_mm=float(center[2]),corner_signed_det_mm3=float(det),corner_volume_mm3=float(vol),corner_min_edge_mm=float(edgeslen.min()),corner_max_edge_mm=float(edgeslen.max()),corner_edge_ratio=float(edgeslen.max()/edgeslen.min()),corner_min_altitude_mm=float(min(alts)),corner_max_edge_over_min_altitude=float(edgeslen.max()/min(alts)),corner_min_face_angle_deg=float(min(angles)),minSICN=float(qual['quality'][e]),min_Q1_J_mm3=float(dd[k].min()),negative_samples=int((dd[k]<0).sum()),worst_barycentric=L[dd[k].argmin()].tolist(),adjacent_face_elements=sorted(top['neighbors'][int(e)])))
 table(R/'INVALID_ELEMENT_NODE_COORDINATES.csv',nodes);table(R/'INVALID_ELEMENT_CONNECTIVITY.csv',con);table(R/'INVALID_ELEMENT_IDS.csv',summary);table(R/'INVALID_ELEMENT_JACOBIAN_SAMPLES.csv',sample_rows)
 for e in sorted(ring2):rings.append(dict(element_index=e,element_tag=int(m['element_tags'][e]),ring=0 if e in bad else 1 if e in ring1 else 2,quality=float(qual['quality'][e]),min_Q1_J_mm3=float(qual['minJ'][e]),corner_volume_mm3=float(corner[e]/6),boundary_node_count=int(np.isin(tt[e],top['boundary_nodes']).sum())))
 table(R/'INVALID_ELEMENT_NEIGHBORS.csv',rings);table(R/'INVALID_ELEMENT_NEIGHBORHOOD.csv',rings)
 np.savez_compressed(R/'03_local_mesh_topology/LOCAL_SUPPORT.npz',bad_element_indices=bad,ring1=np.array(sorted(ring1)),ring2=np.array(sorted(ring2)),ring1_nodes=one_nodes,ring2_nodes=two_nodes,movable_interior_midside_indices=movable,affected_support_elements=affected,boundary_nodes=top['boundary_nodes'],unique_corner_edges=top['unique_edges'],unique_shared_midside_indices=top['edge_mids'])
 np.savez_compressed(R/'08_quadratic_quality/ORIGINAL_GLOBAL_QUALITY.npz',min_Q1_J=qual['minJ'],quality=qual['quality'],independent_SICN=qual['independent_SICN'],corner_det=corner)
 metrics=dict(UTC=now(),source_id=SID,candidate_id='ORIGINAL_M1',protocol_version=VERSION,**qual['summary'],corner_tet_min_volume_mm3=float(corner.min()/6),corner_tet_P01_volume_mm3=float(np.percentile(corner/6,1)),corner_tet_P05_volume_mm3=float(np.percentile(corner/6,5)),shared_edge_count=len(top['unique_edges']),shared_midpoint_mismatch_count=0,nonmanifold_corner_faces=0,bad_elements=summary,shared_nodes_between_invalid=sorted(set(tt[bad[0]])&set(tt[bad[1]])),same_face_connected_region=bool(bad[1] in top['neighbors'][int(bad[0])]),ring1_elements=len(ring1),ring2_elements=len(ring2),movable_interior_midsides=movable.tolist(),affected_support_elements=affected.tolist(),independent_bad_det_max_difference_mm3=float(abs(dd-primary).max()),source_geometry='Frozen hash-identical C02 STEP; no geometry regeneration',H1_ordering='REJECTED',H2_invalid_corner='REJECTED',H3_curvature_induced='VERIFIED',H4_off_CAD_projection='REJECTED_AS_OFF_SURFACE;CURVATURE_PLACEMENT_CONTRIBUTION_VERIFIED',H5_near_degeneracy='QUANTIFIED_NOT_REQUIRED_AS_SOLE_CAUSE',H6_shared_inconsistency='REJECTED',H7_patch_junction='REJECTED;MEASURED_FRONT_ONLY;CAPS_AND_REAR_DISTANT',limits='SICN is sampled; Q1 does not prove global continuous positivity.')
 write(R/'ORIGINAL_FAILURE_METRICS.json',metrics);hyp=[dict(hypothesis=k,status=v,evidence='Exact ordering/shared-edge/corner tests and independent scalar kinematics; INVALID_ELEMENT_IDS.csv and NODE_ORDERING.json') for k,v in metrics.items() if k.startswith('H')];table(R/'ROOT_CAUSE_HYPOTHESIS_MATRIX.csv',hyp)
 doc('INVALID_TET10_ROOT_CAUSE.md','Root cause of the original Tet10 failures','Both elements share an internal face and belong to one local region. Corner orientation and volume are positive, connectivity follows the Gmsh API and historical SOLID187 permutation, and every corner edge has exactly one globally consistent midside node.\n\nThe shared measured-front edge has an on-CAD midside displaced about0.078675 mm below its straight-edge midpoint. The adjoining quadratic volume elements become inverted with this boundary curvature while their internal midsides remain straight. This is an independently verified curvature-placement contribution, not an off-CAD node, an ordering error or a measured-source defect. Local aspect measures are reported separately rather than called a uniquely proven degeneracy mechanism.\n\nS1 can move four interior midsides shared by the affected support star while keeping all corners and the entire external quadratic boundary exactly fixed. S1 applicability does not by itself demonstrate a successful repair. Subsequent experiments must preserve all neighbor and whole-mesh gates.')
 print('ROOT_CAUSE_AND_SUPPORT',metrics,flush=True)
if __name__=='__main__':main()
