from pathlib import Path
import json,hashlib,csv,shutil,urllib.request,time
R=Path(r'E:\welding\outputs\WeldStressAI_FinalResearch_PhaseR8E16')
D=Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRevision_R1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=R/'REPRODUCIBILITY_MANIFEST.json'
assert sha(manifest)=='b3e10116f7a149bd003f86343059984f259135d7a68c34d7cfa7d085f905cd50'
index={x['path']:x for x in json.loads(manifest.read_text())['files']}
files=[p for p in R.iterdir() if p.is_file() and p.suffix in ('.csv','.md','.json') and p.name not in ('XGBOOST_SAMPLE_IDS.csv','REPRODUCIBILITY_MANIFEST.json')]
for folder in ['00_integrity','04_feature_mechanisms','06_observable_geometry_contract','08_experimental_preregistration','10_training_validation','14_source_metrics','15_plate_metrics','16_high95_localization','17_model_comparisons','18_independent_verification','19_scientific_figures','20_manuscript','21_reports','22_reproducibility']:
 for p in (R/folder).rglob('*'):
  if p.is_file() and p.suffix.lower() in ('.csv','.md','.json','.png','.pdf') and p.stat().st_size<15_000_000 and p.relative_to(R).as_posix() in index: files.append(p)
audit=[]
for p in sorted(set(files)):
 rel=p.relative_to(R);key=rel.as_posix();h=sha(p);expected=index[key]['SHA256'];assert h==expected,(key,h,expected)
 dest=D/'source_snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);assert sha(dest)==h
 audit.append(dict(source_path=str(p),relative_path=key,bytes=p.stat().st_size,manifest_SHA256=expected,observed_SHA256=h,copy_SHA256=sha(dest),status='PASS'))
shutil.copy2(manifest,D/'source_snapshot'/manifest.name)
with (D/'SOURCE_INTEGRITY_AUDIT.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(audit[0]));w.writeheader();w.writerows(audit)
shutil.copy2(Path(r'C:\Users\grhnt.DESKTOP-KRBB26F\.codex\attachments\b21039c1-3918-4fd7-9476-5a523704d2f7\Pasted text.txt'),D/'source_snapshot'/'MANUSCRIPT_REVISION_REQUEST.txt')
dois=['10.1016/j.engstruct.2021.112266','10.3390/met11050822','10.3390/app12126089','10.1016/j.prostr.2024.03.014','10.1016/j.jcsr.2024.108745','10.1016/j.jcsr.2025.109724','10.1115/1.4044097','10.1016/j.neunet.2026.108560','10.1109/CVPR.2017.16','10.1109/ICCV48922.2021.01600','10.1145/2939672.2939785','10.1007/978-3-319-23757-2','10.1016/j.jcsr.2017.08.009']
records=[]
for doi in dois:
 dest=D/'literature'/('crossref_'+doi.replace('/','_')+'.json')
 try:
  if dest.exists(): data=json.loads(dest.read_text(encoding='utf-8'))
  else:
   req=urllib.request.Request('https://api.crossref.org/works/'+doi,headers={'User-Agent':'WeldStressAI-ManuscriptAudit/1.0'})
   with urllib.request.urlopen(req,timeout=30) as res:data=json.load(res)
   dest.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
  m=data['message']; records.append(dict(doi=doi,title=m.get('title',[''])[0],authors='; '.join((a.get('given','')+' '+a.get('family','')).strip() for a in m.get('author',[])),year=m.get('published',m.get('issued',{})).get('date-parts',[['']])[0][0],venue=m.get('container-title',[''])[0],type=m.get('type'),volume=m.get('volume'),issue=m.get('issue'),pages=m.get('page',m.get('article-number','')),URL=m.get('URL'),status='CROSSREF_METADATA_VERIFIED'))
 except Exception as e:records.append(dict(doi=doi,status='ERROR',error=str(e)))
(D/'literature'/'CROSSREF_SUMMARY.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'snapshot_files':len(audit),'manifest_SHA256':sha(manifest),'references':records},ensure_ascii=False,indent=2))
