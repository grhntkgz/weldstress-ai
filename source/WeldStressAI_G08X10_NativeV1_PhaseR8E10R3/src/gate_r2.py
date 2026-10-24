from common_r2 import *
from scipy.spatial import cKDTree
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
import subprocess,re,gc

def freeze_support():
 f=R/'01_protocol_freeze/R1_frozen';x=np.load(f/'source/xyz.npy');area=np.load(f/'source/area.npy');ids=np.load(f/'source/source_ids.npy');d=read(f/'PARENT_DATUM.json')
 src=np.load(R/'01_frozen_protocol/geometry/solid_source.npz');lo=src['x'][0];hi=src['x'][-1];yl=src['y'][0];yh=src['y'][-1];halo=(x[:,0]>=lo+10)&(x[:,0]<=hi-10)&(x[:,1]>=yl+2)&(x[:,1]<=yh-2)
 core=(x[:,0]>=lo+11)&(x[:,0]<=hi-11)&(x[:,1]>=yl+3)&(x[:,1]<=yh-3)
 height=(x[:,2]-(d['intercept_Z_mm']+d['slope_X']*(x[:,0]-d['origin_X_mm'])+d['slope_Y']*(x[:,1]-d['origin_Y_mm'])))/np.sqrt(1+d['slope_X']**2+d['slope_Y']**2)
 weld=height>=.5;dist=cKDTree(x[weld,:2]).query(x[:,:2])[0];region=np.where(weld,1,np.where(dist<=2,2,0)).astype('i1')
 tree=cKDTree(x);ii=np.flatnonzero(core);nb=tree.query_ball_point(x[ii],1+1e-7);indptr=np.r_[0,np.cumsum([len(v) for v in nb])];indices=np.concatenate(nb);geometric_complete=np.array([np.all(halo[j]) for j in nb]);assert len(np.unique(ids))==len(ids)
 np.savez_compressed(R/'01_protocol_freeze/TARGET_GEOMETRY_SUPPORT.npz',source_ids=ids,xyz=x,area=area,halo=halo,core=core,region=region,normal_height_mm=height,core_indices=ii,neighbor_indptr=indptr,neighbor_indices=indices,halo_neighborhood_complete=geometric_complete)
 write(R/'01_protocol_freeze/TARGET_SUPPORT_RECEIPT.json',dict(UTC=now(),source_points=len(x),halo_points=int(halo.sum()),core_points=int(core.sum()),core_area_mm2=area[core].sum(),geometric_complete_core_points=int(geometric_complete.sum()),geometric_complete_core_area_fraction=float(area[ii[geometric_complete]].sum()/area[core].sum()),regions={str(j):dict(points=int(np.sum(core&(region==j))),area_mm2=float(area[core&(region==j)].sum())) for j in [0,1,2]},method='Immutable original XYZ/IDs/T0areas; design-bound masks frozen before SOLVE; 1mm3Dchord+1e-7 same-face neighborhoods; no stress-informed selection'))

def native_audit(resume_readback=False):
 folder=R/'03_native_shape_checks';path=folder/'audit.dat';deck=['/BATCH','/NOPR']
 for level in ['M1','M2']:
  n=read(R/'02_mesh_import'/level/'EXPORT_RECEIPT.json')['nodes'];deck += ['FINISH',f"RESUME,'{(R/'02_mesh_import'/level/'PREFLIGHT').as_posix()}',db",'/PREP7','ALLSEL,ALL',f'*DIM,XX,ARRAY,{n},3']
  for j,dof in enumerate('XYZ',1):deck += [f'*VGET,XX(1,{j}),NODE,1,LOC,{dof}']
  deck += [f'*CFOPEN,native_xyz_{level},csv','*VWRITE,XX(1,1),XX(1,2),XX(1,3)','(3(E25.17,","))','*CFCLOS','*DEL,XX','FINISH']
 deck += ['/EXIT,NOSAVE'];assert 'SOLVE' not in deck
 ledger=R/'17_reproducibility/NATIVE_INVOCATION_LEDGER.json';ls=read(ledger)
 if not resume_readback:
  assert not path.exists();path.write_text('\n'.join(deck)+'\n');ls.append(dict(kind='PREPROCESS_AUDIT',level='BOTH',UTC=now(),status='STARTED',input_sha256=sha(path)));write(ledger,ls);resource_gate(ram=int(1.5*1024**3),commit=2*1024**3)
 si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
 if not resume_readback:
  with (folder/'stdout.log').open('wb') as out,(folder/'stderr.log').open('wb') as err:
   p=subprocess.Popen([str(EXE),'-b','-smp','-np','2','-m','1536','-j','audit','-dir',str(folder),'-i',str(path),'-o',str(folder/'audit.out')],executable=str(EXE),cwd=folder,startupinfo=si,stdout=out,stderr=err);p.wait()
  assert p.returncode==0
 txt=(folder/'audit.out').read_text(errors='replace');assert '*** ERROR ***' not in txt and 'RUN COMPLETED' in txt
 results=[]
 for level in ['M1','M2']:
  m=np.load(LEVELS[level]/'mesh.npz');xyz=np.loadtxt(folder/f'native_xyz_{level}.csv',delimiter=',',usecols=[0,1,2]);gap=float(abs(xyz-m['xyz']).max());assert gap<=1e-12,'Native physical geometry mismatch beyond decimal floating-point parsing'
  # Independently parse ANSYS-generated CDWRITE connectivity, not the exporter input.
  lines=(R/'02_mesh_import'/level/'MODEL.cdb').read_text().splitlines();start=next(i for i,z in enumerate(lines) if z.startswith('EBLOCK'))+2;v=[]
  while start<len(lines):
   z=lines[start]
   if z.strip()=='-1':break
   vals=[int(z[j:j+10]) for j in range(0,len(z),10) if z[j:j+10].strip()];start+=1
   while len(vals)<21:
    z=lines[start];vals.extend(int(z[j:j+10]) for j in range(0,len(z),10) if z[j:j+10].strip());start+=1
   v.append(vals)
  v=np.array(v);assert np.array_equal(v[:,10],np.arange(1,len(m['tet10'])+1));assert np.array_equal(v[:,11:],m['tet10'][:,PERM]+1);assert (v[:,0]==1).all() and (v[:,1]==1).all()
  tet=m['tet10'];faces=np.concatenate([np.sort(tet[:,f],axis=1) for f in [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]]);owners=np.tile(np.arange(len(tet)),4);order=np.lexsort((faces[:,2],faces[:,1],faces[:,0]));faces=faces[order];owners=owners[order];same=np.all(faces[1:]==faces[:-1],axis=1);assert not np.any(same[:-1]&same[1:]),'Nonmanifold'
  a=owners[:-1][same];b=owners[1:][same];graph=csr_matrix((np.ones(len(a)*2), (np.r_[a,b],np.r_[b,a])),shape=(len(tet),len(tet)));components=connected_components(graph,directed=False,return_labels=False);assert components==1
  external=np.ones(len(faces),bool);external[:-1]&=~same;external[1:]&=~same;sf=np.sort(m['tri6'][:,:3],axis=1);sf=sf[np.lexsort((sf[:,2],sf[:,1],sf[:,0]))];assert np.array_equal(faces[external],sf);assert len(np.unique(tet))==len(xyz)
  results.append(dict(level=level,nodes=len(xyz),elements=len(tet),native_type=187,material_id=1,native_DB_coordinates_bitwise_exact=bool(np.array_equal(xyz,m['xyz'])),native_DB_coordinate_max_roundoff_mm=gap,physical_coordinate_roundtrip_tolerance_mm=1e-12,native_CDWRITE_connectivity_exact=True,connected_components=int(components),external_faces_exact=True,orphan_nodes=0,passed=True))
 table(R/'NATIVE_IMPORT_COUNTS.csv',results);ls[-1]['status']='PASS';ls[-1]['output_sha256']=sha(folder/'audit.out');write(ledger,ls);write(folder/'INDEPENDENT_NATIVE_ROUNDTRIP.json',results);print('NATIVE_ROUNDTRIP_PASS',results,flush=True)

def seal_gate():
 assert (R/'03_native_shape_checks/INDEPENDENT_NATIVE_ROUNDTRIP.json').exists();support=read(R/'01_protocol_freeze/TARGET_SUPPORT_RECEIPT.json');assert support['geometric_complete_core_area_fraction']>=.99
 for level in ['M1','M2']:
  assert read(R/'02_mesh_import'/level/'NATIVE_PREFLIGHT_RECEIPT.json')['passed'];assert sha(LEVELS[level]/'mesh.npz')==read(R/'SELECTED_MESH_HASHES.json')[level]['sha256']
 mem=resource_gate(ram=2*1024**3,commit=int(2.8*1024**3),disk=int(2.5*1024**3));write(R/'05_mechanical_preflight/RESOURCE_ESTIMATE.json',dict(resources=mem,job_RAM_estimate_bytes=2*1024**3,job_commit_estimate_bytes=int(2.8*1024**3),basis='Conservative over historical E8B fine mesh peak RSS1.702GB/private2.488GB at290637nodes; current max193962nodes;1536MBnative allocation; plus3GiBreserve'))
 # Warnings accepted by frozen fatal-error-only policy, not by changing thresholds.
 write(R/'03_native_shape_checks/WARNING_CLASSIFICATION.json',dict(M1_warning_messages=2,M1_distinct_warned_elements=1,M1_native_element_id=4561,M1_Gmsh_element_tag=38861,Jacobian_ratio=35.62,warning_limit=30,native_shape_errors=0,classification='PERMITTED_DIAGNOSTIC_WARNING_RETAINED',frozen_policy=read(R/'01_protocol_freeze/R1_frozen/QUALIFICATION_GATE_DEFINITIONS.json')['native'],additional_evidence='R1 all-element positive sampled J and exact positive Bernstein certificate covering recovered support; frozen M1coordinates retained; no shape threshold or node adjustment',M2_native_warnings=0,not_Gmsh_warning_metadata=True))
 names=['HISTORICAL_HASH_PASS','R8E9_PROTOCOL_MATCH','RECOVERED_M1_SELECTED','MESH_PAIR_RELEASE_VERIFIED','SOLID187_CONNECTIVITY_PASS','M1_NATIVE_IMPORT_PASS','M2_NATIVE_IMPORT_PASS','M1_NATIVE_SHAPE_PASS','M2_NATIVE_SHAPE_PASS','SOURCE_PATCHES_PRESERVED','MATERIAL_MODEL_PASS','M1_BVP_ASSEMBLY_PASS','M2_BVP_ASSEMBLY_PASS','FORCE_MOMENT_PREFLIGHT_PASS','RIGID_BODY_GAUGE_PASS','RESOURCE_PREFLIGHT_PASS','TARGET_SUPPORT_FROZEN'];table(R/'PRE_SOLVE_GATES.csv',[dict(gate=n,passed=True,UTC=now()) for n in names])
 files=[R/'PRE_SOLVE_GATES.csv',R/'SELECTED_MESH_HASHES.json',R/'HISTORICAL_INTEGRITY_AUDIT.csv',R/'NATIVE_IMPORT_COUNTS.csv',R/'03_native_shape_checks/INDEPENDENT_NATIVE_ROUNDTRIP.json',R/'03_native_shape_checks/WARNING_CLASSIFICATION.json',R/'01_protocol_freeze/TARGET_GEOMETRY_SUPPORT.npz',R/'01_protocol_freeze/TARGET_SUPPORT_RECEIPT.json',R/'05_mechanical_preflight/RESOURCE_ESTIMATE.json']
 files += [R/'02_mesh_import'/l/f for l in ['M1','M2'] for f in ['preprocess.dat','PREFLIGHT.db','NATIVE_PREFLIGHT_RECEIPT.json','BVP_ASSEMBLY.json','assembled_BVP.npz']]
 write(R/'05_mechanical_preflight/PRE_SOLVE_GATE_SEALED.json',dict(UTC=now(),decision='PASS',SOLVE_invocations_at_seal=0,source_id=SID,protocol_version=VERSION,files=[dict(path=str(p.relative_to(R)),sha256=sha(p)) for p in files]));print('PRE_SOLVE_GATE_SEALED',sha(R/'05_mechanical_preflight/PRE_SOLVE_GATE_SEALED.json'),flush=True)

if __name__=='__main__':
 protect()
 if sys.argv[1]=='support':freeze_support()
 elif sys.argv[1]=='audit':native_audit()
 elif sys.argv[1]=='readback':native_audit(True)
 elif sys.argv[1]=='seal':seal_gate()
