from pathlib import Path
import json,hashlib,csv,datetime
D=Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRevision_R2');O=D.parent
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
summary={}
for name,mname in [('WeldStressAI_ManuscriptRevision_R1','REVISION_REPRODUCIBILITY_MANIFEST.json'),('WeldStressAI_FinalResearch_PhaseR8E16','REPRODUCIBILITY_MANIFEST.json')]:
 root=O/name;manifest=root/mname;m=json.loads(manifest.read_text());rows=[]
 for x in m['files']:
  p=root/x['path'];h=sha(p);rows.append(dict(path=str(p),expected_SHA256=x['SHA256'],actual_SHA256=h,status='PASS' if h==x['SHA256'] else 'FAIL'))
 assert all(x['status']=='PASS' for x in rows)
 with (D/'qa'/(name+'_FULL_HASH_AUDIT.csv')).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 summary[name]=dict(files=len(rows),manifest_SHA256=sha(manifest),status='PASS');print(name,len(rows),'PASS',flush=True)
summary['UTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();(D/'qa'/'RELEASE_INTEGRITY_PASS.json').write_text(json.dumps(summary,indent=2))
