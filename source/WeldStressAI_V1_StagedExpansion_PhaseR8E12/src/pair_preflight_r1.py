from common_r1 import *
from quality_r1 import *
from fidelity_math_r1 import project,tri,Q
from scipy.interpolate import RectBivariateSpline
from scipy.spatial import cKDTree

def labelled_export(folder):
 # Serialization of the same candidate with explicit six-patch labels; no coordinate/connectivity edits.
 import gmsh
 m=np.load(folder/'mesh.npz');a=np.load(folder/'FULL_SOURCE_FIDELITY.npz');labels=a['patch_labels'];gmsh.initialize();gmsh.option.setNumber('General.Terminal',0)
 try:
  gmsh.model.add(folder.name);gmsh.model.addDiscreteEntity(3,1);gmsh.model.mesh.addNodes(3,1,m['node_tags'],m['xyz'].ravel());gmsh.model.mesh.addElementsByType(1,11,m['element_tags'],m['node_tags'][m['tet10']].ravel());nexttag=int(m['element_tags'].max())+1
  for tag,name in enumerate(sorted(np.unique(labels)),10):
   faces=m['tri6'][labels==name];gmsh.model.addDiscreteEntity(2,tag);gmsh.model.mesh.addElementsByType(tag,9,np.arange(nexttag,nexttag+len(faces)),m['node_tags'][faces].ravel());nexttag+=len(faces);physical=gmsh.model.addPhysicalGroup(2,[tag]);gmsh.model.setPhysicalName(2,physical,str(name))
  physical=gmsh.model.addPhysicalGroup(3,[1]);gmsh.model.setPhysicalName(3,physical,'STANDARDIZED_C02_SOLID');gmsh.model.mesh.reclassifyNodes();gmsh.option.setNumber('Mesh.Binary',1);gmsh.write(str(folder/'mesh_labelled.msh'))
 finally:gmsh.finalize()
 # Independent file round trip verifies the exported candidate still has exact full node/element identity.
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0)
 try:
  gmsh.open(str(folder/'mesh_labelled.msh'));ids,xx,_=gmsh.model.mesh.getNodes();order=np.argsort(ids);ids=ids[order];xx=np.array(xx).reshape(-1,3)[order];assert np.array_equal(ids,m['node_tags']) and np.array_equal(xx,m['xyz']);e,con=gmsh.model.mesh.getElementsByType(11);perm=np.argsort(e);assert np.array_equal(np.array(e)[perm],np.sort(m['element_tags']));oldorder=np.argsort(m['element_tags']);assert np.array_equal(np.array(con).reshape(-1,10)[perm],m['node_tags'][m['tet10'][oldorder]]);names=sorted(gmsh.model.getPhysicalName(dim,t) for dim,t in gmsh.model.getPhysicalGroups() if dim==2);assert names==sorted(np.unique(labels));quality=np.array(gmsh.model.mesh.getElementQualities(np.array(e)[perm],'minSICN'));assert np.max(abs(quality-m['quality'][oldorder]))<1e-10
 finally:gmsh.finalize()
 write(folder/'LABELLED_MSH_ROUNDTRIP.json',dict(UTC=now(),source_id=SID,candidate_id=folder.name,protocol_version=VERSION,passed=True,node_coordinates_exact=True,node_tags_exact=True,connectivity_exact=True,SICN_recomputed=True,patch_names=names,labelled_MSH_SHA256=sha(folder/'mesh_labelled.msh'),scope='Same candidate export format; not a new full candidate or native ANSYS import test'))

def mechanical(folder):
 m=np.load(folder/'mesh.npz');xx=m['xyz'];surf=m['tri6'];src=np.load(R/'01_frozen_protocol/geometry/solid_source.npz');d=read(R/'01_frozen_protocol/PARENT_DATUM.json');x=src['x'];y=src['y'];t=19.;F=100*t*np.ptp(y);Y=(y[0]+y[-1])/2;Z=d['intercept_Z_mm']-.5*t*np.sqrt(1+d['slope_X']**2+d['slope_Y']**2);sc=xx[surf];ports=[]
 for side,X in [('LEFT',x[0]),('RIGHT',x[-1])]:
  take=np.max(abs(sc[:,:,0]-X),axis=1)<1e-5;co=sc[take];assert len(co)>0;A=np.zeros((3,3));ar=0;normal=[];records=[]
  for r,s,w in Q:
   N,dr,ds=tri(r,s);p=np.einsum('i,eij->ej',N,co);cross=np.cross(np.einsum('i,eij->ej',dr,co),np.einsum('i,eij->ej',ds,co));area=w*np.linalg.norm(cross,axis=1);b=np.c_[np.ones(len(p)),p[:,1]-Y,p[:,2]-Z];A+=np.einsum('ni,nj,n->ij',b,b,area);ar+=area.sum();normal.extend(abs(cross[:,0])/np.linalg.norm(cross,axis=1));records.append(b)
  coefficients=np.linalg.solve(A,[F,0,0]);tr=np.concatenate([b@coefficients for b in records]);assert tr.min()>=50 and tr.max()<=150;assert np.linalg.matrix_rank(A)==3 and min(normal)>1-1e-9
  ports.append(dict(candidate_id=folder.name,side=side,port_triangles=int(take.sum()),port_area_mm2=float(ar),nominal_reference_area_mm2=float(t*np.ptp(y)),defined_force_N=float(F),mean_defined_traction_MPa=float(F/ar),traction_feasibility_min_MPa=float(tr.min()),traction_feasibility_max_MPa=float(tr.max()),moment_matrix_condition=float(np.linalg.cond(A)),moment_matrix_rank=3,port_normal_axis='GLOBAL_X',loadline_Y_mm=float(Y),loadline_Z_mm=float(Z),loads_applied=False,native_equilibrium=None))
 front=RectBivariateSpline(x[::2],y,src['front'][::2],s=0);back=RectBivariateSpline(x[::2],y,src['back'][::2],s=0);pins=[];rigid=[]
 for p,dofs in [(np.array([x[0],y[0],float(back.ev(x[0],y[0]))]),['UX','UY','UZ']),(np.array([x[0],y[-1],float(back.ev(x[0],y[-1]))]),['UX','UZ']),(np.array([x[0],y[0],float(front.ev(x[0],y[0]))]),['UX'])]:
  i=int(np.linalg.norm(xx-p,axis=1).argmin());assert np.linalg.norm(xx[i]-p)<1e-8;r=xx[i]-[0,Y,Z];rot=np.array([[0,r[2],-r[1]],[-r[2],0,r[0]],[r[1],-r[0],0]])
  for dof in dofs:j=['UX','UY','UZ'].index(dof);rigid.append(np.r_[np.eye(3)[j],rot[j]])
  pins.append(dict(node_index=i,node_tag=int(m['node_tags'][i]),xyz=xx[i].tolist(),dofs=dofs,maximum_target_gap_mm=float(np.linalg.norm(xx[i]-p))))
 assert np.linalg.matrix_rank(rigid)==6
 result=dict(UTC=now(),source_id=SID,candidate_id=folder.name,protocol_version=VERSION,mesh_geometry_preflight_pass=True,canonical_axes=dict(tensile='GLOBAL_X',weld_longitudinal='GLOBAL_Y',physical_axis_calibration='NOT_INDEPENDENTLY_VALIDATED'),design_Y_span_mm=float(np.ptp(y)),nominal_thickness_mm=19,nominal_thickness_basis='DOCUMENTED_NOMINAL',defined_reference_MPa=100,defined_force_N=float(F),ports=ports,rigid_gauge_rank=6,pins=pins,actual_nodal_loads_generated=False,actual_displacement_constraints_applied=False,native_jobs=0,native_import_validated=False,native_equilibrium=None)
 write(R/'11_mechanical_mesh_preflight'/(folder.name+'.json'),result);return result

def main():
 protect();m1=R/'06_recovered_M1/M1_C1';m2=R/'07_refined_M2/M2_C1';assert read(m1/'PRE_SOLVER_QUALIFICATION.json')['pre_solver_qualified'] and read(m2/'PRE_SOLVER_QUALIFICATION.json')['pre_solver_qualified'];a=read(m1/'SOURCE_FIDELITY.json');b=read(m2/'SOURCE_FIDELITY.json');hierarchy=dict(edge_median_ratio=b['near_weld_edge_median_mm']/a['near_weld_edge_median_mm'],edge_P90_ratio=b['near_weld_edge_P90_mm']/a['near_weld_edge_P90_mm'],curved_weld_area_ratio=b['near_weld_curved_area_mm2']/a['near_weld_curved_area_mm2'],surface_density_ratio=b['front_face_density_per_mm2']/a['front_face_density_per_mm2'],near_weld_face_ratio=b['near_weld_faces']/a['near_weld_faces']);hierarchy['passed']=hierarchy['edge_median_ratio']<=.98 and hierarchy['edge_P90_ratio']<=.98 and hierarchy['surface_density_ratio']>1
 labelled_export(m1);labelled_export(m2);mechanics=[mechanical(f) for f in [m1,m2]];table(R/'11_mechanical_mesh_preflight/PORT_GEOMETRY.csv',[p for m in mechanics for p in m['ports']])
 # Same-element one-midside counterfactuals are diagnostic only, never new repair trials/candidates.
 old=np.load(R/'00_integrity/baseline/mesh.npz');bad=np.array([4560,11398]);variants=[]
 for e in bad:
  for j in range(4,10):
   co=old['xyz'][old['tet10'][e]].copy();delta=co[GM_EDGES[j-4]].mean(0)-co[j];co[j]+=delta;dd,qq=custom_quality(co[None],samples_Q2());variants.append(dict(element_index=int(e),element_tag=int(old['element_tags'][e]),changed_midside_node_tag=int(old['node_tags'][old['tet10'][e,j]]),Gmsh_local_position=j+1,linearization_displacement_mm=float(np.linalg.norm(delta)),min_Q2_J_mm3=float(dd.min()),min_Q2_SICN=float(qq.min()),counterfactual_only=True,on_CAD_requirement_not_asserted=True))
 table(R/'02_invalid_element_diagnosis/SINGLE_MIDSIDE_CAUSAL_DIAGNOSTICS.csv',variants)
 # Actual quadratic boundary comparisons; no linear-facet substitution.
 pair=[]
 for source,target in [(m2,m1),(m1,m2)]:
  sm=np.load(source/'mesh.npz');tm=np.load(target/'mesh.npz');sf=np.load(source/'FULL_SOURCE_FIDELITY.npz');tf=np.load(target/'FULL_SOURCE_FIDELITY.npz')
  for patch in ['MEASURED_FRONT','ASSUMED_REAR','XMIN_CAP','XMAX_CAP','YMIN_CAP','YMAX_CAP']:
   srcfaces=sm['xyz'][sm['tri6'][sf['patch_labels']==patch]];targetfaces=tm['tri6'][tf['patch_labels']==patch];pts=np.concatenate([np.einsum('i,eij->ej',tri(r,s)[0],srcfaces) for r,s,w in Q]);perm=[0,1,2] if patch in ['MEASURED_FRONT','ASSUMED_REAR'] else [1,2,0] if patch.startswith('X') else [0,2,1];gap,viol,lin,cl=project(tm['xyz'][:,perm],targetfaces,pts[:,perm]);pair.append(dict(candidate_id=source.name+'__TO__'+target.name,patch=patch,source_quadrature_points=len(pts),actual_quad_chart_P95_mm=float(np.percentile(gap,95)),actual_quad_chart_max_mm=float(gap.max()),bounded_actual_quad_patch_distance_P95_mm=float(np.percentile(cl,95)),bounded_actual_quad_patch_distance_max_mm=float(cl.max()),maximum_inverse_violation=float(viol.max()),metric='7point actual curved sourcepatch -> actual quadratic targetpatch; chart-inverse and bounded local closest diagnostics; not linear matching or global closest certification'));print('PAIR_PATCH',source.name,target.name,patch,pair[-1]['bounded_actual_quad_patch_distance_max_mm'],flush=True)
 table(R/'10_mesh_hierarchy/QUADRATIC_BOUNDARY_COMPARISON.csv',pair);q1=read(m1/'PRE_SOLVER_QUALIFICATION.json');q2=read(m2/'PRE_SOLVER_QUALIFICATION.json');hierarchy.update(source_id=SID,candidate_id='M1_C1__M2_C1',protocol_version=VERSION,node_ratio=q2['nodes']/q1['nodes'],element_density_ratio=q2['Tet10']/q1['Tet10'],same_authoritative_STEP_SHA256=sha(R/'01_frozen_protocol/geometry/standardized_planar_rear.step'),source_XYZ_SHA256=sha(R/'01_frozen_protocol/source/xyz.npy'),source_IDs_SHA256=sha(R/'01_frozen_protocol/source/source_ids.npy'),maximum_symmetric_actual_quad_chart_gap_mm=max(v['actual_quad_chart_max_mm'] for v in pair),maximum_symmetric_bounded_quad_patch_distance_mm=max(v['bounded_actual_quad_patch_distance_max_mm'] for v in pair),M1_volume_mm3=q1['volume_quadratic_exact_degree3_mm3'],M2_volume_mm3=q2['volume_quadratic_exact_degree3_mm3'],M2_minus_M1_volume_mm3=q2['volume_quadratic_exact_degree3_mm3']-q1['volume_quadratic_exact_degree3_mm3'],BVP_mesh_compatible=all(v['mesh_geometry_preflight_pass'] for v in mechanics),native_SOLVEs=0,V1_T2_targets=0)
 write(R/'10_mesh_hierarchy/PAIR_PRE_SOLVER_QUALIFICATION.json',hierarchy);print('PAIR_PRE_SOLVER',hierarchy,flush=True)
if __name__=='__main__':main()
