from pathlib import Path
import json,hashlib,shutil,zipfile
import numpy as np,pandas as pd
D=Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRevision_R2');O=D.parent;R=O/'WeldStressAI_FinalResearch_PhaseR8E16';info=json.loads((D/'qa/SOURCE_SPATIAL_INPUTS.json').read_text());registry=pd.read_csv(R/'QUALIFIED13_SOURCE_REGISTRY.csv');audit=[];labels=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
project=Path(r'E:\welding\WeldScan-FEA');zfile=project/'data/raw/csv_files.zip';assert sha(zfile)=='3243b6a74a6f25dcc181350967ea3d30c78308d2dbdc1222cd104a0d5c66afff'
with zipfile.ZipFile(zfile) as z:
 for name in ['weldtoe_geometry.csv','scan_files.csv','metadata.csv']:
  member=next(n for n in z.namelist() if Path(n).name==name);p=project/'data/metadata'/name;b=z.read(member);assert p.read_bytes()==b,(name,'archive mismatch');dest=D/'source_snapshot/metadata'/name;dest.parent.mkdir(exist_ok=True);shutil.copy2(p,dest);audit.append(dict(path=str(p),SHA256=sha(p),verification='EXACT_MATCH_TO_HASH_VERIFIED_ORIGINAL_ZIP_MEMBER',status='PASS'))
toe=pd.read_csv(project/'data/metadata/weldtoe_geometry.csv');toe=toe[toe.SpecimenName.isin(info)];toe.to_csv(D/'DOCUMENTARY_AVERAGED_TOE_PARAMETERS.csv',index=False)
F=O/'WeldScan_ToeDefinition_Phase5C';ix={x['path']:x['sha256'] for x in json.loads((F/'REPRODUCIBILITY_MANIFEST.json').read_text())['files']}
for rel in ['tables/TOE_TRAJECTORY_PROFILES.csv','tables/REAL_PATH_COVERAGE.csv','PHASE5C_RESEARCH_REPORT.md','EXPERT_ANNOTATION_PROTOCOL.md','GEOMETRY_EXPORT_SPECIFICATION.md']:
 p=F/rel;assert sha(p)==ix[rel];dest=D/'source_snapshot/toe_history'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);audit.append(dict(path=str(p),SHA256=sha(p),verification='ORIGINAL_PHASE5C_MANIFEST',status='PASS'))
tracks=pd.read_csv(F/'tables/TOE_TRAJECTORY_PROFILES.csv');candidates=set(tracks.specimen)
for sid in info:
 rows=toe[toe.SpecimenName==sid]
 labels += [dict(source_id=sid,label='Processed original front XYZ and original point IDs',classification='DOCUMENTED_MEASURED_GEOMETRY',availability='available',scope='Publisher-processed surface; raw registration unresolved; not physical toe-coordinate validation'),dict(source_id=sid,label='Published per-notch radius/angle averages',classification='DOCUMENTED_MEASURED_GEOMETRY' if len(rows) else 'NOT_AVAILABLE',availability=f'{len(rows)} documentary rows' if len(rows) else 'absent',scope='Derived scan descriptors averaged along notches; no XYZ trajectory or point-ID map; not independently validated radius'),dict(source_id=sid,label='Original qualified 0/1/2 region labels',classification='EXISTING_GEOMETRY_DERIVED_PROXY',availability='available',scope='Parent-plane-normal relief >=0.5mm plus <=2mm XY collar; not toe truth'),dict(source_id=sid,label='Phase5C algorithmic trajectory',classification='EXISTING_GEOMETRY_DERIVED_PROXY' if sid in candidates else 'NOT_AVAILABLE',availability='available as unreviewed operational candidate' if sid in candidates else 'not present in inspected registry',scope='No independent expert labels or qualified mechanical-coordinate registration; not used as physical toe truth'),dict(source_id=sid,label='Independently documented measured toe trajectory in qualified FE frame',classification='NOT_AVAILABLE',availability='not established',scope='No curve with authenticated point IDs and measurement/registration uncertainty was found'),dict(source_id=sid,label='New retrospective toe trajectory',classification='NOT_AVAILABLE',availability='not constructed',scope='Stress peaks and height contours were not promoted into toe labels')]
pd.DataFrame(labels).to_csv(D/'SPATIAL_LABEL_EVIDENCE_REGISTRY.csv',index=False)
native=[]
for sid,src in info.items():
 case=Path(src['case']);root=Path(src['root']);r=registry[registry.source_id==sid].iloc[0]
 if (case/'SELECTED_MESHES.json').exists():
  selected=json.loads((case/'SELECTED_MESHES.json').read_text())['M2'];p=Path(selected.get('path',str(Path(selected.get('folder',''))/'mesh.npz')))
 elif (case/'SELECTED_MESH_HASHES.json').exists():p=Path(json.loads((case/'SELECTED_MESH_HASHES.json').read_text())['M2']['path'])
 else:raise RuntimeError('No selected native M2 mesh record: '+sid)
 assert sha(p)==r.M2_mesh_hash,(sid,str(p));mesh=np.load(p);xyz=mesh['xyz'];tri=mesh['tri6'];faces=pd.read_csv(case/'02_mesh_import/M2/PORT_FACE_REGISTRY.csv');pins=pd.read_csv(src['gauge_path']);ports={}
 for patch,z in faces.groupby('patch'):
  verts=xyz[tri[z.face_index.to_numpy()]];ports[patch]=dict(Xmin=float(verts[:,:,0].min()),Xmax=float(verts[:,:,0].max()),Ymin=float(verts[:,:,1].min()),Ymax=float(verts[:,:,1].max()))
 assert len(ports)==2;left=ports['XMIN_CAP']['Xmin'];right=ports['XMAX_CAP']['Xmax'];assert abs(right-left-60)<1e-8
 assert all(abs(v['Xmax']-v['Xmin'])<1e-9 for v in ports.values());assert np.allclose(xyz[pins.node.to_numpy()-1],pins[['X','Y','Z']],atol=1e-10,rtol=0)
 row=dict(source_id=sid,left_cap_X_mm=left,right_cap_X_mm=right,cap_positions_verified_on_actual_quadratic_mesh=True,all_six_gauge_coordinates_match_native_mesh=True,mesh_path=str(p),mesh_SHA256=sha(p),geometry_association='EXISTING_GEOMETRY_DERIVED_PROXY',boundary_causal_influence='UNRESOLVED_WITH_EXISTING_SINGLE_BVP');native.append(row);audit.append(dict(path=str(p),SHA256=sha(p),verification='QUALIFIED_M2_MESH_HASH_AND_ACTUAL_NATIVE_PORT_FACE_CONNECTIVITY',status='PASS'))
pd.DataFrame(native).to_csv(D/'ACTUAL_NATIVE_MESH_BOUNDARIES.csv',index=False);pd.DataFrame(audit).to_csv(D/'qa/ADDITIONAL_GEOMETRY_METADATA_HASHES.csv',index=False)
spatial=pd.read_csv(D/'R2_GEOMETRY_STRESS_SPATIAL_AUDIT.csv');spatial['engineering_classification']='GEOMETRIC_PROXY_ASSOCIATION_ONLY';spatial.to_csv(D/'R2_GEOMETRY_STRESS_SPATIAL_AUDIT.csv',index=False)
print('METADATA_AND_NATIVE_PORTS_VERIFIED',len(native),'documentary toe rows',len(toe),'candidate specimens',sorted(candidates))
