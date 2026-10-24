from common_e16 import *
import psutil
def main():
 path=R/'09_resource_preflight/RESUMED_RESOURCE_SAMPLES.csv';fields=['UTC','RAM_available_bytes','commit_available_bytes','E_free_bytes','C_free_bytes','workspace_bytes','phase_PID','phase_RSS_bytes','phase_command'];started=time.monotonic()
 with path.open('w',encoding='utf8',newline='',buffering=1024*1024) as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  while time.monotonic()-started<14400:
   r=resources();found=[]
   for p in psutil.process_iter(['pid','name','cmdline','memory_info']):
    try:
     cmd=' '.join(p.info['cmdline'] or []);name=p.info['name'] or ''
     if name.lower().startswith('python') and str(R).lower() in cmd.lower() and 'resource_watch_e16.py' not in cmd:found.append((p.pid,p.info['memory_info'].rss,cmd))
    except (psutil.NoSuchProcess,psutil.AccessDenied):pass
   for pid,rss,cmd in found or [(0,0,'no phase Python observed')]:w.writerow({**{k:r[k] for k in fields[:6]},'phase_PID':pid,'phase_RSS_bytes':rss,'phase_command':cmd})
   f.flush()
   if (R/'22_reproducibility/EXPERIMENT_MATRIX_COMPLETE.json').exists():break
   time.sleep(2)
 print('RESOURCE_WATCH_COMPLETE',flush=True)
if __name__=='__main__':main()
