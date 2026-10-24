from common_r2 import *
import subprocess,re,gc

def initialize():
 for name in ['00_integrity','01_protocol_freeze','02_mesh_import','03_native_shape_checks','04_BVP_assembly','05_mechanical_preflight','06_native_M1','07_native_M2','08_equilibrium','09_tensor_recovery','10_source_mapping','11_T2_M1','12_T2_M2','13_numerical_qualification','14_historical_comparison','15_figures','16_reports','17_reproducibility','tmp']:(R/name).mkdir(exist_ok=True)
 assert not (R/'00_integrity/INITIALIZED.json').exists(),'Already initialized; do not overwrite'
 source=Path('C:/Users/grhnt.DESKTOP-KRBB26F/.codex/attachments/9cfbf0db-173b-4eaf-9c21-a091b9c3c193/Pasted text.txt');shutil.copy2(source,R/'01_protocol_freeze/USER_EXECUTION_SPECIFICATION.txt')
 audit=[];manifest=read(R1/'REPRODUCIBILITY_MANIFEST.json');seal=read(R1/'14_reproducibility/RELEASE_SEAL.json');assert sha(R1/'REPRODUCIBILITY_MANIFEST.json')==seal['manifest_SHA256']
 for a in manifest['files']:
  p=R1/a['path'];h=sha(p);audit.append(dict(path=str(p),expected_sha256=a['sha256'],actual_sha256=h,passed=h==a['sha256'],basis='R1 sealed manifest'))
 for a in rows(R1/'00_integrity/HISTORICAL_HASHES.csv'):
  p=Path(a['path']);h=sha(p);audit.append(dict(path=str(p),expected_sha256=a['sha256'],actual_sha256=h,passed=h==a['sha256'],basis='R1 historical preservation manifest'))
 for p in [R1/'REPRODUCIBILITY_MANIFEST.json',R1/'14_reproducibility/RELEASE_SEAL.json',R1/'14_reproducibility/INDEPENDENT_RELEASE_VERIFICATION.json']:
  h=sha(p);audit.append(dict(path=str(p),expected_sha256=h,actual_sha256=h,passed=True,basis='R2 initial snapshot'))
 table(R/'HISTORICAL_INTEGRITY_AUDIT.csv',audit);assert all(a['passed'] for a in audit)
 shutil.copytree(R1/'01_frozen_protocol',R/'01_protocol_freeze/R1_frozen',dirs_exist_ok=True)
 for name in ['MESH_PAIR_RELEASE.json','FINAL_R8E10R1_DECISION.md','R8E10R1_MASTER_REPORT.md','PRE_SOLVER_GATE_DECISIONS.csv'] :shutil.copy2(R1/name,R/'00_integrity'/name)
 selected={k:dict(path=str(v/'mesh.npz'),sha256=sha(v/'mesh.npz'),M1_SOURCE='RECOVERED_R8E10R1_M1' if k=='M1' else 'R8E10R1_M2_C1') for k,v in LEVELS.items()}
 release=read(R1/'MESH_PAIR_RELEASE.json')
 for k,a in zip(['M1','M2'],release['meshes']):assert selected[k]['sha256']==a['files']['mesh.npz']['sha256']
 old=np.load(R1/'00_integrity/baseline/mesh.npz');new=np.load(LEVELS['M1']/'mesh.npz');change=np.where(np.any(old['xyz']!=new['xyz'],axis=1))[0];assert len(change)==1 and new['node_tags'][change[0]]==86669;assert np.array_equal(old['tet10'],new['tet10'])
 selected['actual_M1_changed_node_count']=1;selected['actual_changed_Gmsh_node_tag']=86669;selected['retained_coordinate_delta_mm']=(new['xyz'][change]-old['xyz'][change]).tolist()
 write(R/'SELECTED_MESH_HASHES.json',selected);write(R/'MESH_PAIR_INPUT_HASHES.json',selected);write(R/'FROZEN_SOURCE_HASHES.json',release['source_arrays']);write(R/'00_integrity/INITIALIZED.json',dict(UTC=now(),historical_paths=len(audit),all_passed=True,resources=memory()))
 print('INTEGRITY_PASS',len(audit),'actual moved M1 nodes',len(change),flush=True)

def prepare(level):
 folder=R/'02_mesh_import'/level;folder.mkdir(exist_ok=True);assert not (folder/'preprocess.dat').exists()
 m=np.load(LEVELS[level]/'mesh.npz');xyz=m['xyz'];tet=m['tet10'];surf=m['tri6'];labels=np.load(LEVELS[level]/'FULL_SOURCE_FIDELITY.npz')['patch_labels'];n=len(xyz);ne=len(tet);native=tet[:,PERM]+1
 assert (n,ne)==({'M1':(145527,82498),'M2':(193962,109737)}[level])
 # Complete reversible maps, unchanged shared midside identities and one connected Tet10 component.
 table(folder/'GMSH_TO_ANSYS_NODE_MAP.csv',[dict(native_id=i+1,gmsh_tag=int(tag)) for i,tag in enumerate(m['node_tags'])]);table(folder/'GMSH_TO_ANSYS_ELEMENT_MAP.csv',[dict(native_id=i+1,gmsh_tag=int(tag)) for i,tag in enumerate(m['element_tags'])])
 edge=np.sort(tet[:,EDGES].reshape(-1,2),axis=1);mid=tet[:,4:].ravel();order=np.lexsort((edge[:,1],edge[:,0]));edge=edge[order];mid=mid[order];same=np.all(edge[1:]==edge[:-1],axis=1);assert np.all(mid[1:][same]==mid[:-1][same]);assert len(np.unique(np.sort(tet[:,:4],axis=1),axis=0))==ne
 # Native local edges independently specified (ANSYS I,J,K,L,M,N,O,P,Q,R).
 native_edges=np.array([[0,1],[1,2],[2,0],[0,3],[1,3],[2,3]]); gm_lookup={tuple(sorted(e)):4+j for j,e in enumerate(EDGES)}
 independently_ordered=np.c_[tet[:,:4],np.column_stack([tet[:,gm_lookup[tuple(sorted(e))]] for e in native_edges])]+1;assert np.array_equal(native,independently_ordered)
 table(folder/'SHARED_MIDSIDE_COMPATIBILITY.csv',[dict(level=level,edge_occurrences=len(mid),shared_edge_occurrences=int(same.sum()),incompatible_shared_midnodes=0,passed=True)])
 table(folder/'SOLID187_LOCAL_ORDERING_AUDIT.csv',[dict(level=level,native_position=j+1,gmsh_position=int(PERM[j])+1,all_elements_exact=True) for j in range(10)])
 table(folder/'SOLID187_CONNECTIVITY_AUDIT.csv',[dict(level=level,elements=ne,nodes=n,independent_permutation_exact=True,coordinates_modified=0,duplicate_elements=0)])
 forces=np.zeros((n,3));ports=[];face_records=[];resultants=[];origin=np.array([149.975,30,-9.37643484024406]);F=53200.
 for patch,side in [('XMIN_CAP',-1),('XMAX_CAP',1)]:
  fc=surf[labels==patch];co=xyz[fc];A=np.zeros((3,3));data=[]
  for r,s,w in Q:
   N,dr,ds=tri(r,s);p=np.einsum('i,eij->ej',N,co);cross=np.cross(np.einsum('i,eij->ej',dr,co),np.einsum('i,eij->ej',ds,co));ar=w*np.linalg.norm(cross,axis=1);b=np.c_[np.ones(len(p)),p[:,1]-origin[1],p[:,2]-origin[2]];A+=np.einsum('ni,nj,n->ij',b,b,ar);data.append((N,p,ar,b));assert (abs(cross[:,0])/np.linalg.norm(cross,axis=1)).min()>1-1e-10
  coeff=np.linalg.solve(A,[side*F,0,0]);ff=np.zeros(fc.shape);tr=[]
  for N,p,ar,b in data:
   traction=b@coeff;tr.extend(abs(traction));ff+=ar[:,None]*traction[:,None]*N
  pf=np.zeros_like(forces);np.add.at(pf[:,0],fc,ff);forces+=pf;net=pf.sum(0);moment=np.cross(xyz-origin,pf).sum(0);assert np.linalg.norm(net-[side*F,0,0])/F<1e-8 and np.linalg.norm(moment)/(F*19)<1e-8;assert min(tr)>=50 and max(tr)<=150
  resultants.append(dict(level=level,side=patch,Fx=net[0],Fy=net[1],Fz=net[2],Mx=moment[0],My=moment[1],Mz=moment[2],force_relative=float(np.linalg.norm(net-[side*F,0,0])/F),moment_over_Ft=float(np.linalg.norm(moment)/(F*19))))
  ports.append(dict(level=level,patch=patch,area_mm2=sum(v[2].sum() for v in data),tri6=len(fc),coefficients=coeff.tolist(),traction_min_MPa=min(tr),traction_max_MPa=max(tr)))
  face_records.extend(dict(level=level,patch=patch,face_index=int(i)) for i in np.flatnonzero(labels==patch))
 pins=read(R1/'11_mechanical_mesh_preflight'/(level+'_C1.json'))['pins'];rigid=[];gauges=[]
 for p in pins:
  i=p['node_index'];assert np.array_equal(xyz[i],p['xyz']);q=xyz[i]-origin;rot=np.array([[0,q[2],-q[1]],[-q[2],0,q[0]],[q[1],-q[0],0]])
  for dof in p['dofs']:
   j=['UX','UY','UZ'].index(dof);rigid.append(np.r_[np.eye(3)[j],rot[j]]);gauges.append(dict(level=level,node=i+1,dof=dof,X=xyz[i,0],Y=xyz[i,1],Z=xyz[i,2]))
 assert np.linalg.matrix_rank(rigid)==6 and len(gauges)==6
 table(folder/'GAUGE_CONSTRAINT_REGISTRY.csv',gauges);table(folder/'PORT_FACE_REGISTRY.csv',face_records);table(folder/'SIGNED_FORCE_MOMENT_RESULTANTS.csv',resultants)
 table(folder/'NODAL_LOAD_ASSEMBLY.csv',[dict(level=level,node=i+1,Fx=v[0],Fy=v[1],Fz=v[2]) for i,v in enumerate(forces) if np.any(v)])
 write(folder/'BVP_ASSEMBLY.json',dict(level=level,force_N=F,nominal_thickness_mm=19,loadline_origin=origin,ports=ports,pins=pins,rigid_gauge_rank=6,all_assembly_gates_passed=True))
 np.savez_compressed(folder/'assembled_BVP.npz',forces=forces,origin=origin)
 # SHPP active during import and CHECK, no SOLVE or mesh generation anywhere.
 deck=['/BATCH','/NOPR','/PREP7','/UNITS,MPA','ET,1,187','MP,EX,1,210000','MP,PRXY,1,.30','TYPE,1','MAT,1','SHPP,ON']
 deck += [f'N,{i+1},{x:.17g},{y:.17g},{z:.17g}' for i,(x,y,z) in enumerate(xyz)]
 deck += [f'EBLOCK,19,SOLID,{ne},{ne}','(19i10)']
 for i,c in enumerate(native):
  v=[1,1,1,1,0,0,0,0,10,0,i+1]+c.tolist();deck+=[''.join(f'{z:10d}' for z in v[:19]),''.join(f'{z:10d}' for z in v[19:])]
 deck += [f'{-1:10d}']
 for p in pins:
  for dof in p['dofs']:deck.append(f'D,{p["node_index"]+1},{dof},0')
 for i,v in enumerate(forces[:,0]):
  if v!=0:deck.append(f'F,{i+1},FX,{v:.17g}')
 deck += ['ALLSEL,ALL','/GOPR','SHPP,ON','CHECK','*GET,NC,NODE,0,COUNT','*GET,EC,ELEM,0,COUNT','*GET,ENAM,ETYP,1,ATTR,ENAM','*CFOPEN,native_counts,csv','*VWRITE,NC,EC,ENAM','(3(F14.0,","))','*CFCLOS','CDWRITE,DB,MODEL,cdb','SAVE,PREFLIGHT,db','FINISH','/EXIT,NOSAVE']
 assert not any(z.strip().upper()=='SOLVE' for z in deck)
 (folder/'preprocess.dat').write_text('\n'.join(deck)+'\n',encoding='ascii');write(folder/'EXPORT_RECEIPT.json',dict(level=level,UTC=now(),input_sha256=sha(folder/'preprocess.dat'),mesh_sha256=sha(LEVELS[level]/'mesh.npz'),nodes=n,elements=ne,geometry_changes=0,permutation=PERM,solve_commands=0))
 print('PREPARED',level,n,ne,ports,flush=True)

def run_preprocess(level):
 folder=R/'02_mesh_import'/level;ledger=R/'17_reproducibility/NATIVE_INVOCATION_LEDGER.json';entries=read(ledger) if ledger.exists() else [];assert not any(a['level']==level and a['kind']=='PREPROCESS' and a['status']!='LAUNCH_NOT_EXECUTED' for a in entries),'No automatic repeated native invocation'
 assert not any((p.info['name'] or '').lower()=='ansys231.exe' for p in psutil.process_iter(['name'])),'Native process already running'
 mem=resource_gate(ram=int(1.5*1024**3),commit=int(2*1024**3),disk=int(.6*1024**3));write(folder/'RESOURCE_PREFLIGHT.json',dict(resources=mem,estimated_job_RAM_bytes=int(1.5*1024**3),estimated_job_commit_bytes=int(2*1024**3),basis='Import only; historical native allocation1536MB with3GiBreserve'))
 entry=dict(level=level,kind='PREPROCESS',UTC=now(),status='STARTED',input_sha256=sha(folder/'preprocess.dat'));entries.append(entry);write(ledger,entries)
 si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0;t=time.time();samples=[]
 with (folder/'stdout.log').open('wb') as out,(folder/'stderr.log').open('wb') as err:
  p=subprocess.Popen([str(EXE),'-b','-smp','-np','2','-m','1536','-j','file','-dir',str(folder),'-i',str(folder/'preprocess.dat'),'-o',str(folder/'preprocess.out')],executable=str(EXE),cwd=folder,startupinfo=si,stdout=out,stderr=err)
  while p.poll() is None:
   mm=memory();mm['elapsed_s']=time.time()-t
   try:mm['job_RSS_bytes']=sum(q.memory_info().rss for q in [psutil.Process(p.pid)]+psutil.Process(p.pid).children(recursive=True))
   except psutil.Error:mm['job_RSS_bytes']=0
   samples.append(mm);time.sleep(2)
 table(folder/'RESOURCES.csv',samples);txt=(folder/'preprocess.out').read_text(errors='replace');errors=re.findall(r'\*\*\* ERROR \*\*\*.*?(?=\*\*\*|\Z)',txt,re.S);warnings=re.findall(r'\*\*\* WARNING \*\*\*.*?(?=\*\*\*|\Z)',txt,re.S)
 counts=np.loadtxt(folder/'native_counts.csv',delimiter=',',usecols=[0,1,2],ndmin=1).astype(int).tolist() if (folder/'native_counts.csv').exists() else []
 receipt=dict(level=level,UTC=now(),exit_code=p.returncode,native_counts=counts,errors=len(errors),warnings=len(warnings),run_completed='RUN COMPLETED' in txt,elapsed_s=time.time()-t,passed=p.returncode==0 and not errors and counts==({'M1':[145527,82498,187],'M2':[193962,109737,187]}[level]),solve_invocations=0)
 table(folder/'NATIVE_SHAPE_ERRORS.csv',[dict(level=level,index=i+1,text=e) for i,e in enumerate(errors)],['level','index','text']);table(folder/'NATIVE_SHAPE_WARNINGS.csv',[dict(level=level,index=i+1,text=e) for i,e in enumerate(warnings)],['level','index','text']);write(folder/'NATIVE_PREFLIGHT_RECEIPT.json',receipt);entry.update(status='PASS' if receipt['passed'] else 'FAILED',receipt_SHA256=sha(folder/'NATIVE_PREFLIGHT_RECEIPT.json'));write(ledger,entries);print('NATIVE_PREFLIGHT',receipt,flush=True);return receipt

if __name__=='__main__':
 protect()
 if sys.argv[1]=='init':initialize()
 elif sys.argv[1]=='prepare':
  for level in ['M1','M2']:prepare(level)
 elif sys.argv[1]=='native':run_preprocess(sys.argv[2])
