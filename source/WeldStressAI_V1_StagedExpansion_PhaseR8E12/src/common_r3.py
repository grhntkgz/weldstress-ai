from pathlib import Path
import os,sys,json,csv,time,hashlib,shutil,ctypes,datetime
GLOBAL=Path(__file__).resolve().parents[1];BASE=GLOBAL.parent;SID=os.environ.get('R3_SOURCE','X23-V1-S355-AW');R=GLOBAL/'cases'/SID
sys.path.insert(0,str(GLOBAL/'src/vendor'))
E9=BASE/'WeldStressAI_PhysicsConsistentLearning_PhaseR8E9';E10=BASE/'WeldStressAI_StandardizedFE_Pilot_PhaseR8E10';HIST_R1=BASE/'WeldStressAI_C02_Tet10Recovery_PhaseR8E10R1';HIST_R2=BASE/'WeldStressAI_C02_NativeV1_PhaseR8E10R2';E3=BASE/'WeldStressAI_SingleSurface_Transfer_PhaseR8E3';E8B=BASE/'WeldStressAI_RearSurfaceSensitivity_PhaseR8E8B';R5=BASE/'WeldStressAI_Remaining37_PhaseR5';R1=R
for k in ['TEMP','TMP','MPLCONFIGDIR']:os.environ[k]=str(GLOBAL/'tmp')
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='2'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import numpy as np,psutil,platform
platform.uname() # Read-only OS version cache before the strict scientific subprocess guard.
VERSION='T2_STANDARD_PLANAR_REAR_V1__LE210000_NU030__NOM100_TW_XMID__FRONT_HUBER_NORMALOFFSET__CORE11_3__V231_QT10_2M__PBA_CHORD1_T0'
EXE=ANSYS=Path('C:/Program Files/ANSYS Inc/v231/ansys/bin/winx64/ANSYS231.exe');PY=BASE/'WeldScan_MechanicalBenchmark_Phase5E/.venv/Scripts/python.exe'
LEVELS={'M1':R/'06_recovered_M1/M1_C1','M2':R/'07_refined_M2/M2_C1'};PERM=np.array([0,1,2,3,4,5,6,7,9,8]);EDGES=np.array([[0,1],[1,2],[2,0],[0,3],[2,3],[1,3]])
if (R/'SELECTED_MESHES.json').exists():
 for level,info in json.loads((R/'SELECTED_MESHES.json').read_text(encoding='utf8')).items():LEVELS[level]=Path(info['folder'])
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rows(p):
 with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def write(p,x):
 p=Path(p);assert p.resolve().is_relative_to(GLOBAL);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False,default=lambda v:v.tolist() if isinstance(v,np.ndarray) else v.item() if hasattr(v,'item') else str(v)),encoding='utf8')
def table(p,data,fields=None):
 p=Path(p);assert p.resolve().is_relative_to(GLOBAL);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',newline='',encoding='utf8') as f:w=csv.DictWriter(f,fieldnames=fields or list(data[0]));w.writeheader();w.writerows(data)
def doc(name,title,s):
 p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('# '+title+'\n\n'+s+'\n',encoding='utf8')
def canonical(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def memory():
 from ctypes import wintypes
 class PERF(ctypes.Structure):_fields_=[('cb',wintypes.DWORD)]+[(n,ctypes.c_size_t) for n in ['CommitTotal','CommitLimit','CommitPeak','PhysicalTotal','PhysicalAvailable','SystemCache','KernelTotal','PagedPool','NonpagedPool','PageSize']]+[(n,wintypes.DWORD) for n in ['Handles','Processes','Threads']]
 p=PERF();p.cb=ctypes.sizeof(p);assert ctypes.windll.psapi.GetPerformanceInfo(ctypes.byref(p),p.cb)
 return dict(UTC=now(),RAM_available_bytes=psutil.virtual_memory().available,commit_free_bytes=(p.CommitLimit-p.CommitTotal)*p.PageSize,free_disk_bytes=shutil.disk_usage(GLOBAL).free,workspace_bytes=sum(q.stat().st_size for q in GLOBAL.rglob('*') if q.is_file()))
def resource_gate(ram=0,commit=0,disk=0):
 m=memory();record_resource(m,ram,commit,disk);assert m['RAM_available_bytes']>=ram+3*1024**3,'RESOURCE_PREFLIGHT_BLOCKED:RAM';assert m['commit_free_bytes']>=commit+3*1024**3,'RESOURCE_PREFLIGHT_BLOCKED:COMMIT';assert m['free_disk_bytes']>=disk+20*1024**3,'RESOURCE_PREFLIGHT_BLOCKED:DISK';assert m['workspace_bytes']+disk<=24*1024**3,'RESOURCE_PREFLIGHT_BLOCKED:WORKSPACE';return m
def protect():
 def hook(event,args):
  if event=='os.system':raise PermissionError('No shell subprocess')
  if event=='subprocess.Popen':assert args[0] and Path(args[0]).resolve()==EXE.resolve(),'Only authorized ANSYS executable allowed'
  if event=='open' and args and isinstance(args[0],(str,bytes,os.PathLike)):
   p=str(args[0]).replace('\\','/').lower();mode=args[1] if len(args)>1 else None;fl=args[2] if len(args)>2 and isinstance(args[2],int) else 0;writing=(isinstance(mode,str) and any(v in mode for v in 'wax+')) or bool(fl&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
   if writing and p.startswith('e:/welding/') and not p.startswith(GLOBAL.as_posix().lower()+'/'):raise PermissionError('HISTORY_READ_ONLY '+p)
 sys.addaudithook(hook)
def tri(r,s):
 l=1-r-s;return np.array([l*(2*l-1),r*(2*r-1),s*(2*s-1),4*l*r,4*r*s,4*s*l]),np.array([1-4*l,4*r-1,0,4*(l-r),4*s,-4*s]),np.array([1-4*l,0,4*s-1,-4*r,4*r,4*(l-s)])
Q=np.array([[1/3,1/3,.225],[.05971587178977,.470142064105115,.132394152788506],[.470142064105115,.05971587178977,.132394152788506],[.470142064105115,.470142064105115,.132394152788506],[.797426985353087,.101286507323456,.125939180544827],[.101286507323456,.797426985353087,.125939180544827],[.101286507323456,.101286507323456,.125939180544827]]);Q[:,2]*=.5
def case_origin():
 d=read(R/'01_frozen_protocol/PARENT_DATUM.json');s=np.load(R/'01_frozen_protocol/geometry/solid_source.npz');return np.array([np.mean(s['x'][[0,-1]]),np.mean(s['y'][[0,-1]]),d['intercept_Z_mm']-9.5*np.sqrt(1+d['slope_X']**2+d['slope_Y']**2)])

def record_resource(m,ram=0,commit=0,disk=0):
 p=GLOBAL/'ACTUAL_RESOURCE_TIMELINE.csv';header=not p.exists()
 with p.open('a',newline='',encoding='utf8') as f:
  z=dict(source_id=SID,**m,predicted_operation_RAM_bytes=ram,predicted_operation_commit_bytes=commit,predicted_additional_disk_bytes=disk);w=csv.DictWriter(f,fieldnames=list(z))
  if header:w.writeheader()
  w.writerow(z)
 # All phase-controlled temporary directories are on E:. C: is monitored as a system/possible licensing fallback volume.
 assert shutil.disk_usage('C:/').free>=2*1024**3,'RESOURCE_PREFLIGHT_BLOCKED:C_SYSTEM_RESERVE'
def may_execute_source():
 assert read(GLOBAL/'RESOURCE_GATE_DECISION.json')['decision']=='RESOURCE_PREFLIGHT_PASS','Initial resource gate'
 assert not (GLOBAL/'21_reproducibility/CAMPAIGN_STOP.json').exists(),'Campaign stop'
 for a in read(GLOBAL/'SOURCE_SELECTION_SEAL.json')['files']:assert sha(GLOBAL/a['path'])==a['sha256'],'Prospective selection changed'
 queue=[a['source_id'] for a in rows(GLOBAL/'FROZEN_SELECTED_FIVE_SOURCES.csv')];assert SID in queue;i=queue.index(SID)
 if i:assert read(GLOBAL/'cases'/queue[i-1]/'13_numerical_qualification/QUALIFICATION_DECISION.json')['qualified'],'Predecessor must qualify'
