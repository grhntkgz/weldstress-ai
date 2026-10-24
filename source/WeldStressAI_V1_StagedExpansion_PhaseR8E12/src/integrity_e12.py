"""Read-only historical verification; all logs and fresh-hash cache are phase-local."""
from pathlib import Path
import sys,os,hashlib,runpy,contextlib,json,csv,time
R=Path(__file__).resolve().parents[1];B=R.parent
for k in ['TEMP','TMP','MPLCONFIGDIR']:os.environ[k]=str(R/'tmp')
os.environ['PYTHONDONTWRITEBYTECODE']='1';sys.dont_write_bytecode=True
cache={}
def sha(p):
 p=Path(p).resolve();s=p.stat();key=(str(p),s.st_size,s.st_mtime_ns)
 if key not in cache:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
  assert p.stat().st_mtime_ns==s.st_mtime_ns and p.stat().st_size==s.st_size
  cache[key]=h.hexdigest()
 return cache[key]
def main():
 jobs=[('WeldStressAI_C02_NativeV1_PhaseR8E10R2','verify_release_r2.py','R2'),('WeldStressAI_G08X10_NativeV1_PhaseR8E10R3','verify_release_r3.py','R3'),('WeldStressAI_V1_Expansion_PhaseR8E11','verify_e11.py','E11'),('WeldStressAI_V1_Expansion_PhaseR8E11R1','verify_release_e11r1.py','E11R1')]
 for folder,name,label in jobs:
  print('VERIFY',label,flush=True);p=B/folder/'src'/name;sys.path.insert(0,str(p.parent));d=runpy.run_path(str(p),run_name='historical_read_only');d['main'].__globals__['sha']=sha
  with (R/'00_integrity'/f'{label}_READONLY_VERIFICATION.log').open('w',encoding='utf8') as f,contextlib.redirect_stdout(f):d['main']()
  print('VERIFIED',label,'fresh_unique_hashes',len(cache),flush=True)
  sys.path.pop(0)
 bindings=[]
 for folder,_,label in jobs+ [('WeldStressAI_PhysicsConsistentLearning_PhaseR8E9','','E9')]:
  root=B/folder;m=json.loads((root/'REPRODUCIBILITY_MANIFEST.json').read_text(encoding='utf-8-sig'))
  for a in m['files']:
   p=root/a['path'];actual=sha(p);assert actual==a['sha256'];bindings.append(dict(path=str(p),sha256=actual,bytes=p.stat().st_size,kind=label))
 with (R/'00_integrity/HISTORICAL_HASHES.csv').open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(bindings[0]));w.writeheader();w.writerows(bindings)
 (R/'HISTORICAL_RELEASE_HASHES.json').write_text(json.dumps(dict(status='PASS',historical_bindings=len(bindings),fresh_unique_SHA256_reads=len(cache),releases=[dict(root=str(B/a),manifest_SHA256=sha(B/a/'REPRODUCIBILITY_MANIFEST.json')) for a,_,_ in jobs]),indent=2),encoding='utf8')
 print('ALL_HISTORICAL_VERIFIED',len(bindings),flush=True)
if __name__=='__main__':main()
