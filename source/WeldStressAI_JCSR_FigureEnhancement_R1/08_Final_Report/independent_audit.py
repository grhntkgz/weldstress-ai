from common import *
import numpy as np

checks=[]
def check(name,ok,detail=''):
 checks.append({'check':name,'pass':bool(ok),'detail':detail})
 if not ok:raise AssertionError(name+': '+detail)
for r in rows(D/'00_Source_Integrity/CONSUMED_INPUT_HASHES.csv'):
 check('Fresh input SHA256 '+r['path'],sha(r['path'])==r['expected_SHA256'])
for r in json.loads((D/'00_Source_Integrity/HISTORICAL_MANIFESTS.json').read_text(encoding='utf-8')):
 check('Historical manifest unchanged '+r['path'],sha(r['path'])==r['SHA256'])
source=rows(P/'R2_1_SOURCE_REGISTRY.csv');fr=rows(P/'FROZEN_FIELD_ANALYSIS_REGISTRY.csv')
models=rows(R/'MODEL_PREDICTION_REGISTRY.csv');ancillary=[]
for sid in ['G07','X23']:
 sr=next(r for r in source if r['source_id'].startswith(sid));t=dict(np.load(sr['target_path']));g=dict(np.load(sr['geometry_path']));m=t['valid']&t['core'];a=dict(np.load(D/'02_New_Figure07'/(sid+'_EXACT_PLOT_ARRAYS.npz')))
 for key in ['source_ids','xyz','area','T2_MPa','region']:check(sid+' exact original '+key,np.array_equal(a[key],t[key][m]))
 check(sid+' unique original scoring support',len(np.unique(a['source_ids']))==34200)
 for model in ['N1','N2','N3']:
  r=next(r for r in models if r['source_id']==sr['source_id'] and r['model']==model and r['condition']=='FULL' and r['seed']=='20261021')
  pp=dict(np.load(r['path']));lookup={int(k):j for j,k in enumerate(pp['source_ids'])};ix=np.array([lookup[int(k)] for k in a['source_ids']])
  check(sid+model+' original geometry match',np.array_equal(pp['xyz'][ix],a['xyz']))
  check(sid+model+' original areas match',np.array_equal(pp['area'][ix],a['area']))
  check(sid+model+' frozen prediction hash',sha(r['path'])==r['SHA256'])
  ancillary.append({'source_id':sr['source_id'],'model':model,'condition':'FULL','seed':20261021,'path':r['path'],'SHA256':r['SHA256'],'role':'N1 inspected ancillary evidence; only N2/N3 displayed' if model=='N1' else 'Displayed frozen field'})
  if model!='N1':
   check(sid+model+' exact saved prediction',np.array_equal(a[model],pp['pred_MPa'][ix]))
   check(sid+model+' exact signed subtraction',np.array_equal(a[model+'_error'],pp['pred_MPa'][ix]-t['T2_MPa'][m]))
 tri=np.load(D/'02_New_Figure07'/(sid+'_ORIGINAL_CORE_TRIANGLES.npy'))
 lookup={int(k):j for j,k in enumerate(a['source_ids'])};ix=np.array([lookup.get(int(k),-1) for k in g['source_ids']]);original=ix[g['triangles']];original=original[(original>=0).all(axis=1)]
 check(sid+' unchanged original triangle connectivity',np.array_equal(tri,original))
 check(sid+' every scoring vertex in original triangles',len(np.unique(tri))==len(a['source_ids']))
 scale=next(r for r in rows(D/'02_New_Figure07/EXACT_COLOR_SCALES.csv') if r['source_id']==sid)
 joint=np.concatenate([a['T2_MPa'],a['N2'],a['N3']]);er=np.concatenate([a['N2_error'],a['N3_error']])
 check(sid+' shared exact unclipped stress extrema',float(scale['stress_min_MPa'])==joint.min() and float(scale['stress_max_MPa'])==joint.max())
 check(sid+' symmetric shared error extrema',float(scale['error_min_MPa'])==-abs(er).max() and float(scale['error_max_MPa'])==abs(er).max() and float(scale['error_center_MPa'])==0)
 for r in rows(D/'02_New_Figure07/PLOTTED_ARRAY_HASHES.csv'):
  if r['source_id']!=sid:continue
  k={'Frozen FE T2':'T2_MPa','Saved N2':'N2','Saved N3':'N3','N2 signed error':'N2_error','N3 signed error':'N3_error'}[r['panel']]
  check(sid+' plotted vertex field '+r['panel'],r['values_SHA256']==arrsha(a[k]) and r['IDs_SHA256']==arrsha(a['source_ids']))

# Recompute the geometry-only selection; use no prediction magnitude or error.
sr=next(r for r in source if r['source_id'].startswith('G07'));g=dict(np.load(sr['geometry_path']));t=dict(np.load(sr['target_path']));valid=t['valid']&t['core']&(t['region']==2)
sel=json.loads((D/'01_Enhanced_Figure03/ILLUSTRATIVE_QUERY_SELECTION.json').read_text(encoding='utf-8'))
centroid=np.average(g['xyz'][:,0],weights=g['area']);ymid=(g['xyz'][:,1].min()+g['xyz'][:,1].max())/2
candidates=np.flatnonzero(valid);distance=(g['xyz'][candidates,0]-centroid)**2+(g['xyz'][candidates,1]-ymid)**2;chosen=candidates[np.lexsort((g['source_ids'][candidates],distance))[0]]
check('Geometry-only query selection reproduced',int(g['source_ids'][chosen])==sel['source_point_id'])
fc=rows(D/'01_Enhanced_Figure03/QUERY_FEATURE_VALUES.csv')
for cond in ['X50','X43']:
 changed=[int(r['channel']) for r in fc if r['condition']==cond and r['historical_changed_vs_FULL']=='True']
 check(cond+' historical changed-channel annotation',changed==[0,1,2,6,16,17])
 check(cond+' N3 local invariance at illustrative query',not any(r['N3_changed_vs_FULL']=='True' for r in fc if r['condition']==cond))
for n in [1,2,4,5,6,8,9]:
 for p in (J/'03_Figures').glob(f'Fig{n:02d}_*'):
  check('Preserved main artwork '+p.name,sha(p)==sha(D/'05_Final_Manuscript/figures/main'/p.name))
for r in rows(J/'05_Supplementary_Material/SUPPLEMENTARY_FIGURE_INDEX.csv'):
 check('Preserved original SI '+r['figure_id'],sha(D/'04_Supplementary_Update'/r['file'])==r['SHA256'])
si=rows(D/'04_Supplementary_Update/SUPPLEMENTARY_FIGURE_INDEX.csv')
check('Thirty sequential SI identities',[r['figure_id'] for r in si]==['S'+str(i) for i in range(1,31)])
check('Unchanged regional figure moved to S20',sha(J/'03_Figures/Fig07_Regional_errors.png')==sha(D/'04_Supplementary_Update/figures/Figure_S20.png'))
for r in si:check('SI source hash '+r['figure_id'],sha(D/'04_Supplementary_Update'/r['file'])==r['SHA256'])
old=(J/'01_Main_Manuscript/WELDSTRESS_AI_JCSR_MAIN_MANUSCRIPT.md').read_text(encoding='utf-8');new=(D/'05_Final_Manuscript/WELDSTRESS_AI_JCSR_VISUAL_FINAL.md').read_text(encoding='utf-8')
check('Original editable numerical tables unchanged',[x for x in old.splitlines() if x.startswith('|')]==[x for x in new.splitlines() if x.startswith('|')])
check('References unchanged',old[old.index('## References'):]==new[new.index('## References'):])
check('Abstract unchanged',old[old.index('## Abstract'):old.index('## 1')]==new[new.index('## Abstract'):new.index('## 1')])
check('Nine main embedded images',len(re.findall(r'^!\[Figure [1-9]\]',new,re.M))==9)
table('06_Scientific_QA/INDEPENDENT_NUMERIC_AUDIT.csv',checks)
table('00_Source_Integrity/ANCILLARY_N1_N2_N3_FIELD_INSPECTION.csv',ancillary)
js('06_Scientific_QA/INDEPENDENT_NUMERIC_AUDIT.json',{'status':'PASS','checks':len(checks),'new_FE_training_inference':0,'note':'Separate reread and reconstruction of panel inputs; no model execution or new scientific metric.'})
print('INDEPENDENT AUDIT PASS',len(checks))
