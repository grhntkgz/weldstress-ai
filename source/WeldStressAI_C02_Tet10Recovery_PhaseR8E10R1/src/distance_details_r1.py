from common_r1 import *

def main():
 protect();m=np.load(R/'00_integrity/baseline/mesh.npz');source=np.load(R/'01_frozen_protocol/source/xyz.npy');tri=np.load(R/'01_frozen_protocol/source/triangles.npy');t=source[tri];a=t[:,0];ab=t[:,1]-a;ac=t[:,2]-a;n=np.cross(ab,ac);n2=np.sum(n*n,axis=1);aa=np.sum(ab*ab,axis=1);bb=np.sum(ab*ac,axis=1);cc=np.sum(ac*ac,axis=1);records=rows(R/'INVALID_ELEMENT_NODE_COORDINATES.csv');d=read(R/'01_frozen_protocol/PARENT_DATUM.json');norm=float(np.sqrt(1+d['slope_X']**2+d['slope_Y']**2));memo={}
 for rec in records:
  i=int(rec['node_index'])
  if i not in memo:
   p=m['xyz'][i];ap=p-a;plane=np.sum(ap*n,axis=1);proj=ap-plane[:,None]/n2[:,None]*n;u=(np.sum(proj*ab,axis=1)*cc-np.sum(proj*ac,axis=1)*bb)/(aa*cc-bb*bb);v=(np.sum(proj*ac,axis=1)*aa-np.sum(proj*ab,axis=1)*bb)/(aa*cc-bb*bb);dist=np.where((u>=0)&(v>=0)&(u+v<=1),plane*plane/n2,np.inf)
   for j,k in [(0,1),(1,2),(2,0)]:
    edge=t[:,k]-t[:,j];vec=p-t[:,j];s=np.clip(np.sum(vec*edge,axis=1)/np.sum(edge*edge,axis=1),0,1);dist=np.minimum(dist,np.sum((vec-s[:,None]*edge)**2,axis=1))
   nearest=int(np.argmin(dist));rear=(p[2]-d['intercept_Z_mm']-d['slope_X']*(p[0]-d['origin_X_mm'])-d['slope_Y']*(p[1]-d['origin_Y_mm'])+19*norm)/norm;memo[i]=dict(actual_closest_original_T0_distance_mm=float(np.sqrt(dist[nearest])),nearest_original_source_triangle_index=nearest,rear_plane_normal_distance_mm=float(rear),cap_plane_distance_lower_bound_mm=float(min(p[0]-119.975,179.975-p[0],p[1]-16,44-p[1])))
  rec.update(memo[i])
 table(R/'INVALID_ELEMENT_NODE_COORDINATES.csv',records)
 support=np.load(R/'03_local_mesh_topology/LOCAL_SUPPORT.npz');one=support['ring1_nodes'];two=support['ring2_nodes'];boundary=support['boundary_nodes'];corners=np.unique(m['tet10'][:,:4]);node_rows=[]
 for i in two:
  node_rows.append(dict(node_index=int(i),original_Gmsh_node_tag=int(m['node_tags'][i]),X_mm=float(m['xyz'][i,0]),Y_mm=float(m['xyz'][i,1]),Z_mm=float(m['xyz'][i,2]),ring=1 if i in one else 2,boundary=bool(i in boundary),corner=bool(i in corners),selected_free_midside=bool(i in support['movable_interior_midside_indices'])))
 table(R/'03_local_mesh_topology/LOCAL_TOPOLOGY_NODE_REGISTRY.csv',node_rows);mask=np.isin(m['tri6'][:,:3],one).any(1);f=np.flatnonzero(mask);np.savez_compressed(R/'03_local_mesh_topology/LOCAL_BOUNDARY_FACE_GEOMETRY.npz',original_boundary_face_indices=f,original_node_indices=m['tri6'][f],original_Gmsh_node_tags=m['node_tags'][m['tri6'][f]],actual_quadratic_node_coordinates=m['xyz'][m['tri6'][f]])
 write(R/'02_invalid_element_diagnosis/DISTANCE_METHOD.json',dict(UTC=now(),source_id=SID,candidate_id='ORIGINAL_M1',protocol_version=VERSION,closest_T0_method='Exhaustive analytic point-to-triangle distance across all134400 canonical measured source triangles, including plane/edge/vertex cases; no nearest-node approximation',source_nodes_checked=len(memo),metadata_records=len(records),CAD_vs_measured_distinction='front_vertical_gap in node CSV is against frozen CAD graph; actual_closest_original_T0_distance is against measured canonical triangles',rear_method='Exact normal distance to frozen plane, whose footprint contains the local perpendicular foot',caps_method='Coordinate-plane distances are lower bounds to finite caps, sufficient to reject junction proximity; not mislabeled closest cap distances',local_two_ring_nodes=len(two),local_one_ring_nodes=len(one),local_boundary_faces=len(f)))
 print('LOCAL_DISTANCE_AND_NODE_DETAILS_COMPLETE',len(memo),len(two),len(f),flush=True)
if __name__=='__main__':main()
