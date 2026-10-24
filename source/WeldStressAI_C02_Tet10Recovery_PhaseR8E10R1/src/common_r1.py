from pathlib import Path
import os,sys,json,csv,time,datetime,hashlib,shutil,ctypes
R=Path(__file__).resolve().parents[1];BASE=R.parent;E10=BASE/'WeldStressAI_StandardizedFE_Pilot_PhaseR8E10';E9=BASE/'WeldStressAI_PhysicsConsistentLearning_PhaseR8E9';E8B=BASE/'WeldStressAI_RearSurfaceSensitivity_PhaseR8E8B';E3=BASE/'WeldStressAI_SingleSurface_Transfer_PhaseR8E3';SID='C02-V1-S355-AW'
VERSION='T2_STANDARD_PLANAR_REAR_V1__LE210000_NU030__NOM100_TW_XMID__FRONT_HUBER_NORMALOFFSET__CORE11_3__V231_QT10_2M__PBA_CHORD1_T0'
for k in ['TEMP','TMP','MPLCONFIGDIR']:os.environ[k]=str(R/'tmp')
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='2'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import numpy as np,psutil
PY=BASE/'WeldScan_MechanicalBenchmark_Phase5E/.venv/Scripts/python.exe'
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
 p=Path(p);assert p.resolve().is_relative_to(R);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_name(p.name+'.tmp');q.write_text(json.dumps(x,indent=2,allow_nan=False,default=lambda v:v.tolist() if isinstance(v,np.ndarray) else v.item() if hasattr(v,'item') else str(v)),encoding='utf8');q.replace(p)
def table(p,data,fields=None):
 p=Path(p);assert p.resolve().is_relative_to(R);p.parent.mkdir(parents=True,exist_ok=True)
 if data:
  data=[dict(source_id=SID,candidate_id='ORIGINAL_M1',protocol_version=VERSION,numerical_provenance='Original E10 mesh / frozen source; R1 calculation',**{k:v for k,v in z.items() if k not in ['source_id','candidate_id','protocol_version','numerical_provenance']})|{k:z[k] for k in ['source_id','candidate_id','protocol_version','numerical_provenance'] if k in z} for z in data]
 with p.open('w',encoding='utf8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields or list(data[0]));w.writeheader();w.writerows(data)
def doc(name,title,text):
 p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('# '+title+'\n\n'+text+'\n',encoding='utf8')
def memory():
 from ctypes import wintypes
 class PERF(ctypes.Structure):_fields_=[('cb',wintypes.DWORD)]+[(n,ctypes.c_size_t) for n in ['CommitTotal','CommitLimit','CommitPeak','PhysicalTotal','PhysicalAvailable','SystemCache','KernelTotal','PagedPool','NonpagedPool','PageSize']]+[(n,wintypes.DWORD) for n in ['Handles','Processes','Threads']]
 p=PERF();p.cb=ctypes.sizeof(p);assert ctypes.windll.psapi.GetPerformanceInfo(ctypes.byref(p),p.cb)
 return dict(UTC=now(),RAM_available_bytes=psutil.virtual_memory().available,commit_free_bytes=(p.CommitLimit-p.CommitTotal)*p.PageSize,free_disk_bytes=shutil.disk_usage(R).free,workspace_bytes=sum(q.stat().st_size for q in R.rglob('*') if q.is_file()))
def resource_gate(ram=0,commit=0,disk=0):
 m=memory();assert m['RAM_available_bytes']>=ram+3*1024**3,'RAM_RESERVE';assert m['commit_free_bytes']>=commit+3*1024**3,'COMMIT_RESERVE';assert m['free_disk_bytes']>=disk+20*1024**3,'DISK_RESERVE';assert m['workspace_bytes']+disk<=12*1024**3,'WORKSPACE_LIMIT';return m
def protect():
 def hook(event,args):
  if event in ['subprocess.Popen','os.system']:raise PermissionError('R1_NO_EXTERNAL_PROCESS_NO_NATIVE_SOLVER')
  if event=='open' and args and isinstance(args[0],(str,bytes,os.PathLike)):
   p=str(args[0]).replace('\\','/').lower();mode=args[1] if len(args)>1 else None;fl=args[2] if len(args)>2 and isinstance(args[2],int) else 0;writing=(isinstance(mode,str) and any(v in mode for v in 'wax+')) or bool(fl&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
   if writing and p.startswith('e:/welding/') and not p.startswith(R.as_posix().lower()+'/'):raise PermissionError('HISTORY_READ_ONLY '+p)
 sys.addaudithook(hook)
