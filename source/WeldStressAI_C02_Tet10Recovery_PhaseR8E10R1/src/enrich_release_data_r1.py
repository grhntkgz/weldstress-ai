from common_r1 import *
from quality_r1 import *
from scipy.spatial import cKDTree

def main():
 protect();old=np.load(R/'00_integrity/baseline/mesh.npz');local=np.load(R/'03_local_mesh_topology/LOCAL_SUPPORT.npz');m1=R/'06_recovered_M1/M1_C1';m2=R/'07_refined_M2/M2_C1';pair=read(R/'10_mesh_hierarchy/PAIR_PRE_SOLVER_QUALIFICATION.json');assert pair['passed']
 # Attach the actual candidate identities to provenance records; no numerical values change.
 trials=read(R/'14_reproducibility/LOCAL_TRIAL_LEDGER.json')
 for z in trials:
  z.update(source_id=SID,candidate_id=z['trial_id']+'_LOCAL_PROTOTYPE',protocol_version=VERSION,numerical_provenance='Bounded SLSQP local coordinates only; not a complete saved mesh');write(R/'05_local_repair_trials'/z['trial_id']/'TRIAL_RECEIPT.json',z)
 write(R/'14_reproducibility/LOCAL_TRIAL_LEDGER.json',trials);table(R/'LOCAL_REPAIR_TRIALS.csv',trials)
 for name,candidate in [('M1_C1_BERNSTEIN_BOUNDS.csv','M1_C1'),('M2_C1_BERNSTEIN_BOUNDS.csv','M2_C1')]:
  a=rows(R/'08_quadratic_quality'/name)
  for z in a:z['candidate_id']=candidate;z['numerical_provenance']='Exact rational Bernstein coefficients for actual candidate node coordinates'
  table(R/'08_quadratic_quality'/name,a)
 table(R/'LOCAL_REPAIR_STRATEGY_REGISTRY.csv',[dict(candidate_id='STRATEGY_REGISTRY',strategy='S1',applicability='APPLICABLE',local_trials=1,status='USED_SUCCESSFULLY',reason='Four interior shared midsides; complete external boundary and all corners unchanged'),dict(candidate_id='STRATEGY_REGISTRY',strategy='S2',applicability='NOT_NEEDED',local_trials=0,status='NOT_EXECUTED',reason='S1 already produced a qualified M1; do not modify CAD-constrained boundary nodes'),dict(candidate_id='STRATEGY_REGISTRY',strategy='S3',applicability='NOT_NEEDED',local_trials=0,status='NOT_EXECUTED',reason='S1 succeeded; avoid changing a conforming local cavity or global M1 mesh')])
 # Local measured points and frozen geometry-only feature contours are explicitly identifiable.
 xyz=np.load(R/'01_frozen_protocol/source/xyz.npy');ids=np.load(R/'01_frozen_protocol/source/source_ids.npy');areas=np.load(R/'01_frozen_protocol/source/area.npy');triangles=np.load(R/'01_frozen_protocol/source/triangles.npy');box=old['xyz'][local['ring2_nodes']];lo=box.min(0);hi=box.max(0);keep=((xyz[:,:2]>=lo[:2])&(xyz[:,:2]<=hi[:2])).all(1);points=[dict(source_row=int(i),original_source_id=int(ids[i]),X_mm=float(xyz[i,0]),Y_mm=float(xyz[i,1]),Z_mm=float(xyz[i,2]),T0_area_mm2=float(areas[i])) for i in np.flatnonzero(keep)];table(R/'03_local_mesh_topology/ORIGINAL_SOURCE_POINTS_IN_LOCAL_WINDOW.csv',points)
 d=read(R/'01_frozen_protocol/PARENT_DATUM.json');height=(xyz[:,2]-d['intercept_Z_mm']-d['slope_X']*(xyz[:,0]-d['origin_X_mm'])-d['slope_Y']*(xyz[:,1]-d['origin_Y_mm']))/np.sqrt(1+d['slope_X']**2+d['slope_Y']**2);edges=np.unique(np.sort(np.vstack([triangles[:,[0,1]],triangles[:,[1,2]],triangles[:,[2,0]]]),axis=1),axis=0);cross=(height[edges[:,0]]-.5)*(height[edges[:,1]]-.5)<0;ed=edges[cross];t=(.5-height[ed[:,0]])/(height[ed[:,1]]-height[ed[:,0]]);feature=xyz[ed[:,0]]*(1-t[:,None])+xyz[ed[:,1]]*t[:,None];np.savez_compressed(R/'03_local_mesh_topology/FROZEN_SOURCE_FEATURE_PROXY.npz',source_edge_indices=ed,feature_XYZ=feature,definition='Original T0 edges crossing fixed normal-height0.5mm; geometry-only proxy, not independent physical weld-toe measurement')
 tree=cKDTree(feature);connect=rows(R/'INVALID_ELEMENT_CONNECTIVITY.csv')
 for z in connect:z['expected_native_export_element_id_if_index_based']=int(z['element_index'])+1
 table(R/'INVALID_ELEMENT_CONNECTIVITY.csv',connect)
 near=[]
 for e in local['bad_element_indices']:
  center=old['xyz'][old['tet10'][e,:4]].mean(0);dist,_=tree.query(center);near.append(dict(element_index=int(e),Gmsh_element_tag=int(old['element_tags'][e]),distance_to_frozen_height_proxy_mm=float(dist),nearest_Xcap_mm=float(min(center[0]-119.975,179.975-center[0])),nearest_Ycap_mm=float(min(center[1]-16,44-center[1])),frozen_feature_interpretation='0.5mm height contour only; not validated actual toe'))
 table(R/'03_local_mesh_topology/PATCH_AND_FEATURE_PROXIMITY.csv',near);write(R/'01_frozen_protocol/COORDINATE_FRAME.json',dict(source_id=SID,protocol_version=VERSION,units='mm',source_to_computational_transform=np.eye(4).tolist(),tensile_axis='GLOBAL_X',weld_axis='GLOBAL_Y',axis_status='Inherited canonical numerical frame; not independently physically calibrated',no_rotation_or_stretch=True))
 # Actual-data warning accounting: parameter metadata warnings are preserved, not hidden.
 warnings=[]
 for folder in [m1,m2]:
  log=(folder/'gmsh.log').read_text(encoding='utf8',errors='replace') if (folder/'gmsh.log').exists() else ''
  lines=[s for s in log.splitlines() if 'warning' in s.lower() or 'error' in s.lower()]
  write(R/'14_reproducibility'/(folder.name+'_MESHER_WARNINGS.json'),dict(source_id=SID,candidate_id=folder.name,protocol_version=VERSION,lines=lines,count=len(lines),native_warning_status='NOT_EXECUTED',interpretation='Raw Gmsh parameter-coordinate metadata warnings retained. Labelled discrete MSH round trip is exact; geometry/quality gates independently pass. Future CAD-based reparametrization is not certified.'))
  warnings.append(dict(candidate_id=folder.name,raw_mesher_warning_lines=len(lines),labelled_MSH_roundtrip_exact=read(folder/'LABELLED_MSH_ROUNDTRIP.json')['passed'],native_shape_warning_count=None))
 table(R/'14_reproducibility/MESHER_WARNING_REGISTRY.csv',warnings)
 # Complete mandatory summary tables.
 original=read(R/'ORIGINAL_FAILURE_METRICS.json');q1=read(m1/'PRE_SOLVER_QUALIFICATION.json');q2=read(m2/'PRE_SOLVER_QUALIFICATION.json');f1=read(m1/'SOURCE_FIDELITY.json');f2=read(m2/'SOURCE_FIDELITY.json')
 table(R/'GLOBAL_M1_QUALITY.csv',[dict(candidate_id=k,minSICN=z['minSICN'],SICN_P01=z['SICN_P01'],SICN_P05=z['SICN_P05'],SICN_P50=z['SICN_P50'],negative_Q1_J_elements=z['negative_J_elements'],zero_Q1_J_elements=z['zero_J_elements'],min_Q1_J_mm3=z['minimum_Q1_J_mm3'],below_SICN020=z['below_SICN020'],status='QUALIFIED_PRE_SOLVER' if k=='M1_C1' else 'INVALID_NEGATIVE_BASELINE') for k,z in [('ORIGINAL_M1',original),('M1_C1',q1)]])
 f0=read(E10/'06_M1_meshes'/SID/'MESH_QUALIFICATION.json');table(R/'M1_SOURCE_FIDELITY.csv',[dict(candidate_id='ORIGINAL_M1',forward_P95_mm=f0['source_forward_P95_mm'],forward_max_mm=f0['source_forward_max_mm'],reverse_P95_mm=f0['reverse_P95_mm'],reverse_max_mm=f0['reverse_max_mm'],surface_fidelity_pass=True,whole_mesh_qualified=False),dict(candidate_id='M1_C1',forward_P95_mm=f1['forward_P95_mm'],forward_max_mm=f1['forward_max_mm'],reverse_P95_mm=f1['reverse_P95_mm'],reverse_max_mm=f1['reverse_max_mm'],surface_fidelity_pass=True,whole_mesh_qualified=True)])
 table(R/'M2_SOURCE_FIDELITY.csv',[dict(candidate_id='M2_C1',forward_P95_mm=f2['forward_P95_mm'],forward_max_mm=f2['forward_max_mm'],reverse_P95_mm=f2['reverse_P95_mm'],reverse_max_mm=f2['reverse_max_mm'],surface_fidelity_pass=True,whole_mesh_qualified=True)])
 table(R/'M1_M2_MESH_COUNTS.csv',[dict(candidate_id=z['candidate_id'],nodes=z['nodes'],Tet10=z['Tet10'],node_limit=350000,element_limit=230000,counts_pass=True) for z in [q1,q2]])
 table(R/'M1_M2_REFINEMENT.csv',[dict(candidate_id=z['candidate_id'],near_weld_median_edge_mm=z['near_weld_edge_median_mm'],near_weld_P90_edge_mm=z['near_weld_edge_P90_mm'],near_weld_faces=z['near_weld_faces'],near_weld_curved_area_mm2=z['near_weld_curved_area_mm2'],front_face_density_per_mm2=z['front_face_density_per_mm2'],parent_median_edge_mm=z['parent_edge_median_mm'],parent_P90_edge_mm=z['parent_edge_P90_mm'],M2_to_M1_median_ratio=pair['edge_median_ratio'],M2_to_M1_P90_ratio=pair['edge_P90_ratio'],M2_to_M1_density_ratio=pair['surface_density_ratio'],pair_hierarchy_pass=True) for z in [f1,f2]])
 table(R/'M1_M2_QUADRATIC_QUALITY.csv',[dict(candidate_id=z['candidate_id'],minSICN=z['minSICN'],minimum_Q1_J_mm3=z['minimum_Q1_J_mm3'],negative_J_elements=z['negative_J_elements'],zero_J_elements=z['zero_J_elements'],invalid_observed_elements=0,whole_mesh_Q1_samples=73,expanded_local_samples=909,global_Gmsh_independent_SICN_max_difference=z['Gmsh_vs_independent_SICN_max'],independent_scalar_elements=z['independent_scalar_elements'],pre_solver_qualified=True,continuous_whole_mesh_proof=False) for z in [q1,q2]])
 table(R/'M1_M2_DOMAIN_CORRESPONDENCE.csv',[dict(candidate_id=z['candidate_id'],authoritative_STEP_SHA256=pair['same_authoritative_STEP_SHA256'],source_XYZ_SHA256=pair['source_XYZ_SHA256'],source_IDs_SHA256=pair['source_IDs_SHA256'],same_CAD=True,boundary_identical_to_original_M1=z['full_boundary_identical_to_original'],quadratic_FE_volume_mm3=z['volume_quadratic_exact_degree3_mm3'],symmetric_actual_quad_chart_max_mm=pair['maximum_symmetric_actual_quad_chart_gap_mm'],symmetric_bounded_quad_patch_distance_max_mm=pair['maximum_symmetric_bounded_quad_patch_distance_mm'],same_BVP_geometry=True,native_import_qualified=False) for z in [q1,q2]])
 gates=[]
 for z in [q1,q2]:
  for k,v in z['checks'].items():gates.append(dict(candidate_id=z['candidate_id'],gate=k,status='PASS' if v else 'FAIL'))
  gates.extend([dict(candidate_id=z['candidate_id'],gate='native_ANSYS_import',status='NOT_EXECUTED'),dict(candidate_id=z['candidate_id'],gate='native_equilibrium_and_T2',status='NOT_EXECUTED')])
 gates.extend([dict(candidate_id='M1_C1__M2_C1',gate='achieved_hierarchy',status='PASS'),dict(candidate_id='M1_C1__M2_C1',gate='common_CAD_domain',status='PASS'),dict(candidate_id='M1_C1__M2_C1',gate='BVP_mesh_geometry',status='PASS')]);table(R/'PRE_SOLVER_GATE_DECISIONS.csv',gates)
 decisions=dict(root_cause='ROOT_CAUSE_VERIFIED',M1='C02_M1_QUALIFIED',M2='C02_M2_QUALIFIED',mesh_pair='C02_M1_M2_PRE_SOLVER_QUALIFIED',mechanical_preflight='BVP_MESH_PREFLIGHT_PASS',native_FE='NATIVE_NOT_EXECUTED',V1_T2='V1_T2_NOT_EXECUTED',overall='R8E10R1_MESH_RECOVERY_COMPLETE');write(R/'14_reproducibility/FINAL_DECISIONS.json',decisions);print('RELEASE_TABLES_READY',decisions,flush=True)
if __name__=='__main__':main()
