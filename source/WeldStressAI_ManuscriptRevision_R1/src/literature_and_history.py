from pathlib import Path
import json,csv,urllib.request,hashlib,shutil
import pandas as pd
D=Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRevision_R1');S=D/'source_snapshot'
records=json.loads((D/'literature'/'CROSSREF_SUMMARY.json').read_text(encoding='utf-8'))
# A guessed candidate DOI resolved to another work. It is explicitly rejected.
rejected=[r for r in records if r['doi']=='10.1109/ICCV48922.2021.01600'];(D/'literature'/'REJECTED_DOI_CANDIDATES.json').write_text(json.dumps(rejected,indent=2),encoding='utf-8')
records=[r for r in records if r['doi'] not in ['10.1109/ICCV48922.2021.01600','10.1016/j.jcsr.2017.08.009']]
for doi in ['10.1016/j.jcsr.2024.109112','10.1109/ICCV48922.2021.01595']:
 with urllib.request.urlopen('https://api.crossref.org/works/'+doi,timeout=30) as f:data=json.load(f)
 (D/'literature'/('crossref_'+doi.replace('/','_')+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');m=data['message']
 records.append(dict(doi=doi,title=m['title'][0],authors='; '.join((a.get('given','')+' '+a.get('family','')).strip() for a in m['author']),year=m['published']['date-parts'][0][0],venue=m.get('container-title',[''])[0],type=m['type'],volume=m.get('volume',''),issue=m.get('issue',''),pages=m.get('page',m.get('article-number','')),URL=m['URL'],status='CROSSREF_METADATA_VERIFIED'))
assert 'Point Transformer'==records[-1]['title']
contributions={
'10.1016/j.engstruct.2021.112266':('https://www.sciencedirect.com/science/article/pii/S0141029621004168','publisher abstract and article preview','Measured butt-weld topography, undercuts and local stress concentration; no learned field surrogate claimed.'),
'10.3390/met11050822':('https://www.mdpi.com/2075-4701/11/5/822','publisher numerical-method section and abstract','Scanning resolution and reconstructed real-weld FE stresses are linked to fatigue assessment.'),
'10.3390/app12126089':('https://tore.tuhh.de/bitstream/11420/12976/1/applsci-12-06089-v2.pdf','author institutional full-text repository and publisher metadata','Parametric FE-trained neural SCF estimates are applied statistically along laser-measured butt-weld seams.'),
'10.1016/j.prostr.2024.03.014':('https://www.sciencedirect.com/science/article/pii/S2452321624002312','publisher abstract; conference proceedings article','Modified PointNet++ and 2DLaserNet regress SCFs from synthetic weld-profile coordinates with FE labels.'),
'10.1016/j.jcsr.2024.108745':('https://www.sciencedirect.com/science/article/pii/S0143974X24002955','publisher abstract and author institutional metadata','Bagged trees use digitized T-joint geometry and FE sectional stresses; close real-scan/FE/ML precedent.'),
'10.1016/j.jcsr.2025.109724':('https://www.sciencedirect.com/science/article/pii/S0143974X2500402X','publisher title, metadata and highlights only','Idealized and as-built scanned B-spline models are compared using structural-stress approaches.'),
'10.1115/1.4044097':('https://doi.org/10.1115/1.4044097','publisher abstract and issue metadata','CNNs map two-dimensional cantilever geometry, loads and constraints to elastic von Mises fields.'),
'10.1016/j.neunet.2026.108560':('https://www.sciencedirect.com/science/article/pii/S0893608026000237','publisher abstract and article preview','PointNet/DeepONet predicts three-dimensional displacement and von Mises fields under variable loads.'),
'10.1109/CVPR.2017.16':('https://arxiv.org/abs/1612.00593','original authors arXiv record plus Crossref conference record','Point-set classification and segmentation architecture; foundational method, not weld-stress evidence.'),
'10.1145/2939672.2939785':('https://arxiv.org/abs/1603.02754','original authors arXiv record and linked ACM DOI','Scalable gradient tree boosting; algorithmic citation for the fixed nonlinear baseline.'),
'10.1007/978-3-319-23757-2':('https://link.springer.com/book/10.1007/978-3-319-23757-2','publisher second-edition book record and contents','Fatigue-assessment reference; T2 is not asserted to reproduce its standardized stress methods.'),
'10.1016/j.jcsr.2024.109112':('https://www.sciencedirect.com/science/article/pii/S0143974X2400662X','publisher abstract and original author-hosted article','Toe-radius and angle extraction depend on shape, spacing and noise; metrological caution.'),
'10.1109/ICCV48922.2021.01595':('https://arxiv.org/abs/2012.09164','original authors arXiv record and Crossref ICCV metadata','Point attention for recognition and segmentation; executed SurfacePT is a compact adaptation.')}
for r in records:
 u,scope,c=contributions[r['doi']];r.update(primary_URL=u,access_scope=scope,contribution=c,accessed='2026-10-23',verification='VERIFIED_WITH_STATED_ACCESS_SCOPE',notes='')
 if r['doi']=='10.1115/1.4044097':r['year']=2020;r['notes']='Issue year 2020; first online 2019. Publisher issue date used.'
 if r['doi']=='10.1016/j.jcsr.2024.109112':r['year']=2025;r['notes']='Issue year 2025; online/copyright 2024 and DOI suffix 2024.'
 if r['doi']=='10.1109/CVPR.2017.16':r['authors']='Charles R. Qi; Hao Su; Kaichun Mo; Leonidas J. Guibas';r['notes']='Author name order corrected from original-author record; Crossref transposes names.'
 if r['doi']=='10.1145/2939672.2939785':r['title']='XGBoost: A Scalable Tree Boosting System';r['notes']='Full subtitle from original-author arXiv record; Crossref title abbreviated.'
records.append(dict(doi='10.25835/0dojws6u',title='Research Data on Fatigue Tests of As-Welded, Deep-Rolled, and HFMI-Treated Joints',authors='Christian Dänekas',year=2025,venue='LUIS',type='dataset',volume='version 1.0',issue='',pages='',URL='https://doi.org/10.25835/0dojws6u',primary_URL='https://data.uni-hannover.de/dataset/research-data-repository-deep-rolling',access_scope='publisher record and frozen repository metadata',contribution='Aligned and smoothed weld scans, experimental metadata and specimen mapping; T2 is a derived numerical target.',accessed='2026-10-23',verification='VERIFIED_WITH_STATED_ACCESS_SCOPE',notes='CC BY 4.0; metadata updated in 2026.'))
records.append(dict(doi='10.48550/arXiv.1711.05101',title='Decoupled Weight Decay Regularization',authors='Ilya Loshchilov; Frank Hutter',year=2019,venue='ICLR 2019; original-author arXiv v3',type='conference-paper/author-preprint',volume='',issue='',pages='',URL='https://doi.org/10.48550/arXiv.1711.05101',primary_URL='https://arxiv.org/abs/1711.05101',access_scope='original-author record, v3 and stated ICLR venue',contribution='Decoupled weight decay for adaptive optimizers; methodological citation for AdamW.',accessed='2026-10-23',verification='VERIFIED_WITH_STATED_ACCESS_SCOPE',notes='arXiv identifier DOI is not a journal DOI.'))
order=['10.25835/0dojws6u','10.1016/j.engstruct.2021.112266','10.3390/met11050822','10.3390/app12126089','10.1016/j.prostr.2024.03.014','10.1016/j.jcsr.2024.108745','10.1016/j.jcsr.2025.109724','10.1016/j.jcsr.2024.109112','10.1115/1.4044097','10.1016/j.neunet.2026.108560','10.1109/CVPR.2017.16','10.1109/ICCV48922.2021.01595','10.1145/2939672.2939785','10.48550/arXiv.1711.05101','10.1007/978-3-319-23757-2']
records=sorted(records,key=lambda r:order.index(r['doi']))
for i,r in enumerate(records,1):r['reference_id']=i
pd.DataFrame(records).to_csv(D/'LITERATURE_VERIFICATION.csv',index=False,encoding='utf-8-sig');(D/'literature'/'VERIFIED_REFERENCE_RECORDS.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
K=Path(r'E:\welding\outputs\WeldStressAI_InferenceMechanisms_PhaseR8E15');m=json.loads((K/'REPRODUCIBILITY_MANIFEST.json').read_text());ix={r['path']:r for r in m['files']};hist=[]
for name in ['PLATE_LEVEL_FIELD_METRICS.csv','STITCHING_CONTINUITY_METRICS.csv','CONTEXT_PREDICTION_VARIATION.csv','R8E15_MASTER_REPORT.md','ORIGINAL_TILE_TOPOLOGY.csv','FROZEN_DIAGNOSTIC_PARAMETERS.json','MECHANISM_EVIDENCE_MATRIX.csv']:
 p=K/name;h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==ix[name]['SHA256'];dest=S/'historical_E15'/name;dest.parent.mkdir(exist_ok=True);shutil.copy2(p,dest);hist.append(dict(path=str(p),SHA256=h,status='PASS'))
pd.DataFrame(hist).to_csv(D/'qa'/'E15_SOURCE_INTEGRITY.csv',index=False)
v=pd.read_csv(S/'historical_E15/PLATE_LEVEL_FIELD_METRICS.csv');out=v.groupby(['model','condition','policy'],as_index=False).mean(numeric_only=True);out.to_csv(D/'HISTORICAL_E15_POLICY_MEANS.csv',index=False)
v=pd.read_csv(S/'historical_E15/STITCHING_CONTINUITY_METRICS.csv');out=v.groupby(['model','condition','policy','seed','plate'],as_index=False).mean(numeric_only=True).groupby(['model','condition','policy'],as_index=False).mean(numeric_only=True);out.to_csv(D/'HISTORICAL_E15_CONTINUITY_MEANS.csv',index=False)
print(json.dumps({'verified_references':len(records),'E15_hashes':len(hist),'PointTransformer':records[11]},indent=2))
