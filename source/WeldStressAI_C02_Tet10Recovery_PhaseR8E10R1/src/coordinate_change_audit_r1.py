from common_r1 import *
def main():
 protect();old=np.load(R/'00_integrity/baseline/mesh.npz');new=np.load(R/'06_recovered_M1/M1_C1/mesh.npz');indices=np.flatnonzero(np.any(old['xyz']!=new['xyz'],axis=1));support=np.flatnonzero(np.isin(old['tet10'],indices).any(1));assert indices.tolist()==[86668];boundary=np.unique(old['tri6']);assert not np.isin(indices,boundary).any();assert np.array_equal(old['tet10'],new['tet10']) and np.array_equal(old['tri6'],new['tri6']);assert np.array_equal(old['xyz'][boundary],new['xyz'][boundary]);delta=new['xyz'][indices]-old['xyz'][indices]
 write(R/'14_reproducibility/ACTUAL_COORDINATE_CHANGE_AUDIT.json',dict(UTC=now(),source_id=SID,candidate_id='M1_C1',protocol_version=VERSION,optimization_variable_nodes=4,actually_changed_nodes=1,changed_node_indices=indices.tolist(),changed_Gmsh_node_tags=old['node_tags'][indices].tolist(),delta_XYZ_mm=delta.tolist(),maximum_displacement_mm=float(np.linalg.norm(delta,axis=1).max()),actually_changed_element_indices=support.tolist(),actually_changed_element_count=len(support),potential_optimization_support_elements=14,all_boundary_nodes_byte_identical=True,all_corner_nodes_byte_identical=True,connectivity_byte_identical=True,mesh_SHA256=sha(R/'06_recovered_M1/M1_C1/mesh.npz'),correction='Earlier prose described four eligible optimization nodes as moved. Exact full-coordinate comparison shows only node86669 moved; three eligible nodes retained exactly zero displacement. Numerical mesh/quality/fidelity results are unchanged.'))
 records=rows(R/'LOCAL_NODE_DISPLACEMENTS.csv')
 for z in records:z['optimization_variable']=True;z['actual_coordinates_changed']=int(z['node_index']) in indices
 table(R/'LOCAL_NODE_DISPLACEMENTS.csv',records)
 path=R/'src/report_r1.py';text=path.read_text(encoding='utf8');changes={
 'S1 subsequently restored validity by moving interior midsides only.':'S1 subsequently restored validity by moving one eligible interior midside only.',
 'Instead, four interior midsides move coherently in the shared support star.':'Instead, one of the four eligible interior midsides moves; the other three stay exactly fixed.',
 'Four interior midsides moved. Their original Gmsh node tags are86668,86669,86670 and100559; exact old/new coordinates are in LOCAL_NODE_DISPLACEMENTS.csv.':'Four interior midsides were eligible variables, but only Gmsh node86669 actually moved. Nodes86668,86670 and100559 remained byte-identical. Exact old/new coordinates and the full-coordinate audit are retained.',
 'One S1 trial moved four interior midsides;':'One S1 trial moved one of four eligible interior midsides;',
 'Four interior midsides changed positions: original node tags86668,86669,86670,100559. All M1 corners, connectivity and boundary coordinates stayed exact. Values are in LOCAL_NODE_DISPLACEMENTS.csv.':'Only original Gmsh node86669 changed: deltaXYZ=(-0.004512989,+0.000673633,-0.019113710) mm. Three other eligible nodes had zero displacement. All corners, connectivity and external boundary coordinates stayed exact.',
 'by moving only four interior midsides,':'by moving only one of four eligible interior midsides,',
 '14 affected elements':'14 potential-support elements',
 'All14 affected support elements':'All14 potential-support elements',
 '## Explicit answers to35 requested questions':'## Explicit answers to the35 requested questions'
 }
 for a,b in changes.items():text=text.replace(a,b)
 path.write_text(text,encoding='utf8')
 path=R/'src/figures_r1.py';text=path.read_text(encoding='utf8');start=text.index(" changed=np.flatnonzero(");end=text.index(" fig=plt.figure(figsize=(12,5))",start)
 replacement=""" changed=np.flatnonzero(np.any(old['xyz']!=m1['xyz'],axis=1));p=old['xyz'][changed];delta=m1['xyz'][changed]-p;fig=plt.figure(figsize=(12,5));ax=fig.add_subplot(121);ax.bar(['dX','dY','dZ'],delta[0],color=['#6587a2','#a88f4e','#b7634d']);ax.axhline(0,c='k',lw=.7);ax.set_ylabel('Coordinate change (mm)');ax.set_title('Only Gmsh node86669 moved;4 eligible variables',fontsize=10);ax=fig.add_subplot(122,projection='3d');ax.quiver(0,0,0,*delta[0],color='#447f9e',arrow_length_ratio=.15);ax.scatter(0,0,0,c='#b5654c',s=35,label='Original');ax.scatter(*delta[0],c='#447f9e',s=35,label='Repaired');ax.set(xlabel='dX (mm)',ylabel='dY (mm)',zlabel='dZ (mm)',xlim=(-.006,.001),ylim=(-.001,.002),zlim=(-.022,.002));ax.view_init(25,-68);ax.legend(fontsize=8);save(13,fig,'ACTUAL_COORDINATE_CHANGE_AUDIT.json','One actual interior-node displacement; actual mm scale')
"""
 text=text[:start]+replacement+text[end:];text=text.replace('One S1 trial; four interior midsides; boundary unchanged','One S1 trial;1of4eligible nodes moved;boundary unchanged');path.write_text(text,encoding='utf8')
 print('COORDINATE_AUDIT',len(indices),'actual node;',len(support),'actual element supports;',14,'checked potential supports',flush=True)
if __name__=='__main__':main()
