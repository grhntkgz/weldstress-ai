from common_r2 import *
import subprocess,re,gc

def folder_for(level):return R/('06_native_M1' if level=='M1' else '07_native_M2')
def run(level,audit_only=False):
 if audit_only:
  folder=folder_for(level);txt=(folder/'solve.out').read_text(errors='replace');ledger=R/'17_reproducibility/NATIVE_INVOCATION_LEDGER.json';ls=read(ledger);entry=next(e for e in ls if e['kind']=='SOLVE' and e['level']==level)
  assert entry['exit_code']==0 and '*** ERROR ***' not in txt and 'RUN COMPLETED' in txt and re.search(r'LOAD STEP\s+1\s+SUBSTEP\s+1\s+COMPLETED',txt),'Actual native failure; no postaudit recovery allowed'
  entry['prior_parser_status']=entry['status'];entry['interpretation_correction']='Native solution completed; initial Python verifier searched unavailable SOLUTION DONE text instead of actual LOAD STEP/SUBSTEP COMPLETED marker. Native outputs unchanged; zero reruns.';write(ledger,ls)
  return finish_audit(level)
 gate=R/'05_mechanical_preflight/PRE_SOLVE_GATE_SEALED.json';g=read(gate);assert g['decision']=='PASS'
 for f in g['files']:assert sha(R/f['path'])==f['sha256'],'Sealed pre-solve input changed'
 ledger=R/'17_reproducibility/NATIVE_INVOCATION_LEDGER.json';ls=read(ledger);solves=[v for v in ls if v['kind']=='SOLVE'];assert len(solves)<2 and not any(v['level']==level for v in solves)
 if level=='M2':assert read(folder_for('M1')/'SOLVE_COMPLETE.json')['completed'] and read(folder_for('M1')/'SOLVE_COMPLETE.json')['equilibrium_passed']
 assert not any((p.info['name'] or '').lower()=='ansys231.exe' for p in psutil.process_iter(['name']))
 folder=folder_for(level);assert not (folder/'input.dat').exists();pre=R/'02_mesh_import'/level;shutil.copy2(pre/'PREFLIGHT.db',folder/'PREFLIGHT.db');assert sha(pre/'PREFLIGHT.db')==sha(folder/'PREFLIGHT.db')
 m=np.load(LEVELS[level]/'mesh.npz');n=len(m['xyz']);ne=len(m['tet10']);bvp=read(pre/'BVP_ASSEMBLY.json');pins=bvp['pins'];native=m['tet10'][:,PERM]+1
 selected=np.unique(np.r_[np.linspace(0,ne-1,128,dtype=int),[4560,11398] if level=='M1' else []]);np.save(folder/'native_tensor_selected_elements.npy',selected+1)
 deck=['/BATCH','/NOPR','RESUME,PREFLIGHT,db','/SOLU','ALLSEL,ALL','ANTYPE,STATIC','NLGEOM,OFF','SHPP,ON','EQSLV,PCG,1e-8','OUTRES,ALL,ALL','SOLVE','FINISH','SAVE,MODEL,db','/POST1','SET,LAST','RSYS,0','ALLSEL,ALL',f'*DIM,UU,ARRAY,{n},3']
 for j,dof in enumerate('XYZ',1):deck += [f'*VGET,UU(1,{j}),NODE,1,U,{dof}']
 deck += ['*CFOPEN,nodal_U,csv','*VWRITE,UU(1,1),UU(1,2),UU(1,3)','(3(E25.17,","))','*CFCLOS','*CFOPEN,reactions,csv']
 for p in pins:
  for dof in 'XYZ':deck += [f'*GET,R{dof},NODE,{p["node_index"]+1},RF,F{dof}']
  deck += [f'*VWRITE,{p["node_index"]+1},RX,RY,RZ','(F12.0,3(",",E25.17))']
 deck += ['*CFCLOS']
 for name,comp in zip(['TXX','TYY','TZZ','TXY','TYZ','TXZ'],['X','Y','Z','XY','YZ','XZ']):deck += [f'ETABLE,{name},S,{comp}']
 deck += ['*CFOPEN,native_element_stress,csv']
 for eid in selected+1:
  for name in ['TXX','TYY','TZZ','TXY','TYZ','TXZ']:deck += [f'*GET,{name}V,ELEM,{eid},ETAB,{name}']
  deck += [f'*VWRITE,{eid},TXXV,TYYV,TZZV,TXYV,TYZV,TXZV','(F12.0,6(",",E25.17))']
 deck += ['*CFCLOS','FINISH','/EXIT,NOSAVE'];assert deck.count('SOLVE')==1;(folder/'input.dat').write_text('\n'.join(deck)+'\n')
 mem=resource_gate(ram=2*1024**3,commit=int(2.8*1024**3),disk=int(1.2*1024**3));write(folder/'RESOURCE_PREFLIGHT.json',mem)
 command=[str(EXE),'-b','-smp','-np','2','-m','1536','-j','file','-dir',str(folder),'-i',str(folder/'input.dat'),'-o',str(folder/'solve.out')];entry=dict(level=level,kind='SOLVE',UTC=now(),status='STARTED',input_sha256=sha(folder/'input.dat'),gate_sha256=sha(gate),command=command);ls.append(entry);write(ledger,ls)
 si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0;t=time.time();samples=[]
 with (folder/'stdout.log').open('wb') as out,(folder/'stderr.log').open('wb') as err:
  p=subprocess.Popen(command,executable=str(EXE),cwd=folder,startupinfo=si,stdout=out,stderr=err)
  while p.poll() is None:
   mm=memory();mm['elapsed_s']=time.time()-t;mm['job_RSS_bytes']=0;mm['job_private_bytes']=0
   try:
    for q in [psutil.Process(p.pid)]+psutil.Process(p.pid).children(recursive=True):
     info=q.memory_info();mm['job_RSS_bytes']+=info.rss;mm['job_private_bytes']+=getattr(info,'private',0)
   except psutil.Error:pass
   samples.append(mm);time.sleep(2)
 table(folder/'RESOURCES.csv',samples);txt=(folder/'solve.out').read_text(errors='replace');errcount=len(re.findall(r'\*\*\* ERROR \*\*\*',txt));warncount=len(re.findall(r'\*\*\* WARNING \*\*\*',txt))
 logok=p.returncode==0 and errcount==0 and 'RUN COMPLETED' in txt and bool(re.search(r'LOAD STEP\s+1\s+SUBSTEP\s+1\s+COMPLETED',txt)) and (folder/'file.rst').exists()
 entry.update(status='NATIVE_COMPLETED_PENDING_AUDIT' if logok else 'FAILED',exit_code=p.returncode);write(ledger,ls)
 if not logok:write(folder/'SOLVE_FAILED.json',dict(UTC=now(),errors=errcount,exit_code=p.returncode,log_success=False,rerun_prohibited=True));raise RuntimeError('Native SOLVE failed; budget consumed. No automatic rerun or M2afterM1failure.')
 return finish_audit(level)

def finish_audit(level):
 folder=folder_for(level);pre=R/'02_mesh_import'/level;m=np.load(LEVELS[level]/'mesh.npz');n=len(m['xyz']);native=m['tet10'][:,PERM]+1;bvp=read(pre/'BVP_ASSEMBLY.json');pins=bvp['pins'];ledger=R/'17_reproducibility/NATIVE_INVOCATION_LEDGER.json';ls=read(ledger);entry=next(e for e in ls if e['kind']=='SOLVE' and e['level']==level);txt=(folder/'solve.out').read_text(errors='replace');errcount=len(re.findall(r'\*\*\* ERROR \*\*\*',txt));warncount=len(re.findall(r'\*\*\* WARNING \*\*\*',txt));logok=entry['exit_code']==0 and errcount==0 and 'RUN COMPLETED' in txt and bool(re.search(r'LOAD STEP\s+1\s+SUBSTEP\s+1\s+COMPLETED',txt));assert logok;samples=[{k:float(v) for k,v in z.items() if k!='UTC'} for z in rows(folder/'RESOURCES.csv')];t=time.time()-max(v['elapsed_s'] for v in samples)
 u=np.loadtxt(folder/'nodal_U.csv',delimiter=',',usecols=[0,1,2]);rf=np.loadtxt(folder/'reactions.csv',delimiter=',',ndmin=2);assert u.shape==(n,3) and np.isfinite(u).all();native_xyz=np.loadtxt(R/'03_native_shape_checks'/f'native_xyz_{level}.csv',delimiter=',',usecols=[0,1,2]);forces=np.load(pre/'assembled_BVP.npz')['forces'];origin=np.array(bvp['loadline_origin']);appF=forces.sum(0);appM=np.cross(native_xyz-origin,forces).sum(0);reactF=rf[:,1:].sum(0);reactM=np.cross(native_xyz[rf[:,0].astype(int)-1]-origin,rf[:,1:]).sum(0);fres=appF+reactF;mres=appM+reactM;fr=float(np.linalg.norm(fres)/53200);mr=float(np.linalg.norm(mres)/(53200*19));eq=fr<=1e-5 and mr<=1e-5
 gauge=max(abs(u[p['node_index'],['UX','UY','UZ'].index(dof)]) for p in pins for dof in p['dofs']);mag=np.linalg.norm(u,axis=1);elong=float(np.mean(u[abs(native_xyz[:,0]-179.975)<1e-8,0])-np.mean(u[abs(native_xyz[:,0]-119.975)<1e-8,0]));s=np.loadtxt(folder/'native_element_stress.csv',delimiter=',',ndmin=2);valid_stress=np.isfinite(s).all() and np.max(abs(s[:,1:]))>0
 # Broad physical-scale diagnostic against 60mm*100MPa/E, not a convergence threshold.
 no_runaway=gauge<=1e-10 and 0<elong<.3 and mag.max()<1
 receipt=dict(level=level,UTC=now(),completed=bool(logok and eq and no_runaway and valid_stress),native_log_success=logok,equilibrium_passed=eq,force_residual_relative=fr,moment_residual_over_Ft=mr,applied_force_N=appF,reaction_force_N=reactF,signed_force_residual_N=fres,applied_moment_Nmm=appM,reaction_moment_Nmm=reactM,signed_moment_residual_Nmm=mres,reference_origin_mm=origin,Umax_mm=float(mag.max()),Umean_mm=float(mag.mean()),UX_minmax_mm=[float(u[:,0].min()),float(u[:,0].max())],UY_minmax_mm=[float(u[:,1].min()),float(u[:,1].max())],UZ_minmax_mm=[float(u[:,2].min()),float(u[:,2].max())],gauge_motion_max_mm=float(gauge),mean_end_axial_extension_mm=elong,no_RB_runaway=bool(no_runaway),native_stress_finite=bool(valid_stress),elapsed_s=time.time()-t,peak_RSS_bytes=max(v['job_RSS_bytes'] for v in samples),peak_private_bytes=max(v['job_private_bytes'] for v in samples),native_errors=errcount,native_warnings=warncount,numerical_target_qualified=False,files={p.name:sha(p) for p in folder.iterdir() if p.suffix.lower() in ['.db','.rst','.dat','.csv']})
 np.savez_compressed(folder/'native_displacements.npz',xyz=native_xyz,u=u,connectivity_native=native-1,connectivity_gmsh=m['tet10'],native_node_ids=np.arange(1,n+1));write(folder/'SOLVE_COMPLETE.json',receipt);entry['status']='PASS' if receipt['completed'] else 'FAILED_AUDIT';write(ledger,ls);print('SOLVE_RECEIPT',receipt,flush=True);assert receipt['completed'],'Equilibrium, stress or displacement audit failed; stop before nextsolve'

if __name__=='__main__':protect();run(sys.argv[1],audit_only='--audit-only' in sys.argv)
