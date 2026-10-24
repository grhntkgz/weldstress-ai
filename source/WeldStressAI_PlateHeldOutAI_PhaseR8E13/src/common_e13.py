from pathlib import Path
import os,sys,json,csv,hashlib,datetime,time,ctypes,shutil
R=Path(__file__).resolve().parents[1]; O=R.parent
E12=O/'WeldStressAI_V1_StagedExpansion_PhaseR8E12'; E3=O/'WeldStressAI_SingleSurface_Transfer_PhaseR8E3'
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='2'
for k in ['TEMP','TMP','MPLCONFIGDIR']:os.environ[k]=str(R/'tmp')
os.environ['PYTHONDONTWRITEBYTECODE']='1'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rows(p):
 with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(p,x):
 p=Path(p);assert p.is_relative_to(R);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(x,indent=2,default=lambda a:a.item() if hasattr(a,'item') else str(a)),encoding='utf8');t.replace(p)
def table(p,data,fields=None):
 data=list(data);p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields or (list(data[0]) if data else ['status']));w.writeheader();w.writerows(data)
_cache={}
def sha(p):
 p=Path(p).resolve();s=p.stat();key=(str(p),s.st_size,s.st_mtime_ns)
 if key not in _cache:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
  a=p.stat();assert a.st_size==s.st_size and a.st_mtime_ns==s.st_mtime_ns;_cache[key]=h.hexdigest()
 return _cache[key]
def commit():
 from ctypes import wintypes
 class P(ctypes.Structure):_fields_=[('cb',wintypes.DWORD)]+[(n,ctypes.c_size_t) for n in ['CommitTotal','CommitLimit','CommitPeak','PhysicalTotal','PhysicalAvailable','SystemCache','KernelTotal','KernelPaged','KernelNonpaged','PageSize']]+[(n,wintypes.DWORD) for n in ['HandleCount','ProcessCount','ThreadCount']]
 p=P();p.cb=ctypes.sizeof(p);assert ctypes.windll.psapi.GetPerformanceInfo(ctypes.byref(p),p.cb);return (p.CommitLimit-p.CommitTotal)*p.PageSize
def resources():
 import psutil
 return dict(UTC=now(),RAM_available_bytes=psutil.virtual_memory().available,commit_available_bytes=commit(),E_free_bytes=shutil.disk_usage('E:/').free,C_free_bytes=shutil.disk_usage('C:/').free,RSS_bytes=psutil.Process().memory_info().rss,workspace_bytes=sum(p.stat().st_size for p in R.rglob('*') if p.is_file()))
def gate():
 x=resources();assert x['RAM_available_bytes']>=3*1024**3,'RAM_RESERVE';assert x['commit_available_bytes']>=3*1024**3,'COMMIT_RESERVE';assert x['E_free_bytes']>=20*1024**3 and x['C_free_bytes']>=2*1024**3;assert x['workspace_bytes']<16*1024**3;return x
def verify_seal():
 for x in read(R/'PREREGISTRATION_SEAL.json')['files']:assert sha(R/x['path'])==x['sha256'],x
def guard(train_ids=None,infer=False):
 allowed=set(train_ids or [])
 def hook(event,args):
  if event in ['subprocess.Popen','os.system']:raise PermissionError('CHILD_EXECUTION_FORBIDDEN')
  if event=='open' and args and isinstance(args[0],(str,bytes,os.PathLike)):
   p=str(args[0]).replace('\\','/').lower();mode=args[1] if len(args)>1 else None;flags=args[2] if len(args)>2 and isinstance(args[2],int) else 0;writing=(isinstance(mode,str) and any(k in mode for k in 'wax+')) or bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
   if writing and p.startswith('e:/welding/') and not p.startswith(str(R).replace('\\','/').lower()+'/'):raise PermissionError('HISTORY_READ_ONLY')
   if not writing and (p.endswith('.pt') or p.endswith('.pth')) and not p.startswith(str(R).replace('\\','/').lower()+'/'):raise PermissionError('HISTORICAL_WEIGHTS_FORBIDDEN')
   if not writing and '/01_dataset/targets/' in p:
    assert not infer,'INFERENCE_LABEL_ACCESS';assert any('/'+s.lower()+'.npz' in p for s in allowed),'HELDOUT_LABEL_ACCESS'
 sys.addaudithook(hook)
