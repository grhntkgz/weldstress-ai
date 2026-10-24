from pathlib import Path
import json,urllib.request
import pandas as pd
D=Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRevision_R1')
refs=json.loads((D/'literature'/'VERIFIED_REFERENCE_RECORDS.json').read_text(encoding='utf-8'))
if len(refs)==15:
 doi='10.1016/j.marstruc.2026.104059'
 with urllib.request.urlopen('https://api.crossref.org/works/'+doi,timeout=30) as f:data=json.load(f)
 (D/'literature'/('crossref_'+doi.replace('/','_')+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');m=data['message'];assert m['title'][0]=='Finite element model reconstruction of welded tubular joints from incomplete point cloud scans'
 r=dict(reference_id=16,doi=doi,title=m['title'][0],authors='; '.join((a.get('given','')+' '+a.get('family','')).strip() for a in m['author']),year=2026,venue=m['container-title'][0],type=m['type'],volume=m.get('volume',''),issue='',pages=m.get('page',m.get('article-number','')),URL='https://doi.org/'+doi,primary_URL='https://www.sciencedirect.com/science/article/pii/S0951833926000535',access_scope='publisher abstract and article preview plus Crossref metadata',contribution='Incomplete tubular-joint scans are completed with explicit geometric assumptions for FE reconstruction.',accessed='2026-10-23',verification='VERIFIED_WITH_STATED_ACCESS_SCOPE',notes='Incomplete measurement reconstruction is distinct from surrogate representation sensitivity.')
 refs.append(r);(D/'literature'/'VERIFIED_REFERENCE_RECORDS.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2),encoding='utf-8');pd.DataFrame(refs).to_csv(D/'LITERATURE_VERIFICATION.csv',index=False,encoding='utf-8-sig')
 entry=f"16. {r['authors'].replace(';',',')}. (2026). {r['title']}. Marine Structures 109, 104059. https://doi.org/{doi}."
 for name in ['MANUSCRIPT_REVISION_R1.md','VERIFIED_REFERENCES.md']:
  p=D/name;t=p.read_text(encoding='utf-8');t+='\n\n'+entry+'\n';p.write_text(t,encoding='utf-8')
 p=D/'MANUSCRIPT_REVISION_R1.md';t=p.read_text(encoding='utf-8');needle='For measured surfaces, a further issue arises before changing the model architecture.'
 t=t.replace(needle,'Incomplete measurement also requires explicit geometric assumptions: Plets et al. [16] reconstruct inaccessible portions of scanned tubular joints for FE modelling. This addresses completion of an incompletely measured structure, whereas the present intervention examines how a fixed surrogate responds to changing visible support and feature statistics. Neither approach makes the unseen surface experimentally measured.\n\n'+needle)
 t=t.replace('Historical development and exposed test identities were kept separate; the twelve exposed historical test groups and the external Aalborg sources were not used for new tuning in this study.','Historical development and exposed test identities were kept separate; exposed historical test identities and external Aalborg sources were not used for new tuning in this study.')
 t=t.replace('Symbols not defined','Symbols not defined')
 p.write_text(t,encoding='utf-8')
 p=D/'STATE_OF_THE_ART_COMPARISON.md';t=p.read_text(encoding='utf-8');t=t.replace('| PointNet and Point Transformer', '| Plets et al. 2026 [16] | Incomplete scan completion for FE | Explicit model-form assumptions for unseen surfaces |\n| PointNet and Point Transformer');p.write_text(t,encoding='utf-8')
print('References:',len(refs))
