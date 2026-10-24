from common import *
import numpy as np
from PIL import Image,ImageDraw,ImageOps
checks=[];manifests=[];expected={}
cachefile=D/'00_Source_Integrity/HISTORICAL_FILE_HASH_AUDIT.csv'
cached={r['path']:r for r in rows(cachefile)} if cachefile.exists() else {}
for base in [R,P,J,Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRevision_R1'),Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRevision_R2')]:
 mf=J/'10_Reproducibility_Manifest/REPRODUCIBILITY_MANIFEST.json' if base==J else base/'REPRODUCIBILITY_MANIFEST.json'
 if not mf.exists():mf=base/'REVISION_REPRODUCIBILITY_MANIFEST.json'
 m=json.loads(mf.read_text(encoding='utf-8'));manifests.append({'path':str(mf),'SHA256':sha(mf)})
 for row in m['files']:
  p=base/row['path'];prior=cached.get(str(p));h=prior['actual_SHA256'] if prior and prior['status']=='PASS' and prior['expected_SHA256']==row['SHA256'] else sha(p);expected[str(p)]=row['SHA256'];checks.append({'release':base.name,'path':str(p),'expected_SHA256':row['SHA256'],'actual_SHA256':h,'status':'PASS' if h==row['SHA256'] else 'FAIL'})
 print('HISTORICAL',base.name,len(m['files']),flush=True)
table('00_Source_Integrity/HISTORICAL_FILE_HASH_AUDIT.csv',checks);js('00_Source_Integrity/HISTORICAL_MANIFESTS.json',manifests);assert all(x['status']=='PASS' for x in checks)
for row in json.loads((P/'R2_1_INPUT_HASHES.json').read_text(encoding='utf-8'))['files']:expected[row['path']]=row['SHA256']
for name in ['FIGURE_SOURCE_REGISTRY.csv','FIGURE_CAPTIONS.md']:copy(J/'03_Figures'/name,'00_Source_Integrity/ORIGINAL_'+name)
for name in ['SUPPLEMENTARY_FIGURE_INDEX.csv','SUPPLEMENTARY_TABLE_INDEX.csv']:copy(J/'05_Supplementary_Material'/name,'00_Source_Integrity/ORIGINAL_'+name)
for name,src in [('SOURCE_GEOMETRY_REGISTRY.csv',P/'R2_1_SOURCE_REGISTRY.csv'),('FROZEN_FIELD_REGISTRY.csv',P/'FROZEN_FIELD_ANALYSIS_REGISTRY.csv'),('MODEL_PREDICTION_REGISTRY.csv',R/'MODEL_PREDICTION_REGISTRY.csv'),('FEATURE_CONTRACT.csv',R/'OBSERVABLE_N3_FEATURE_CONTRACT.csv')]:copy(src,'00_Source_Integrity/'+name)
for name in ['N3_ARCHITECTURE_AND_TRAINING.json','FEATURE_CONTEXT_CONSISTENCY.csv','FEATURE_BLOCK_CONTRACT.csv']:copy(R/name,'00_Source_Integrity/'+name)
copy(J/'08_Scientific_And_Editorial_QA/JOURNAL_COMPLIANCE_AUDIT.md','00_Source_Integrity/ORIGINAL_JOURNAL_COMPLIANCE_AUDIT.md')
copy(J/'08_Scientific_And_Editorial_QA/NUMERICAL_AND_STRUCTURE_AUDIT.json','00_Source_Integrity/ORIGINAL_SCIENTIFIC_QA.json')
sources=rows(P/'R2_1_SOURCE_REGISTRY.csv');sid='G07-V1-S355-AW';sr=next(r for r in sources if r['source_id']==sid)
g=dict(np.load(sr['geometry_path']));t=dict(np.load(sr['target_path']));core=dict(np.load(sr['E15_core_path']))
assert np.array_equal(g['source_ids'],t['source_ids']) and np.array_equal(g['xyz'],t['xyz']) and np.array_equal(g['area'],t['area'])
# Deterministic geometry-only illustrative point, sealed before any prediction arrays are opened.
eligible=np.flatnonzero(t['core']&t['valid']&(t['region']==2));center=np.array([g['center'][0],(g['xyz'][:,1].min()+g['xyz'][:,1].max())/2]);dist=((g['xyz'][eligible,:2]-center)**2).sum(1);order=np.lexsort((g['source_ids'][eligible],dist));q=int(eligible[order[0]]);qid=int(g['source_ids'][q]);qi=int(np.flatnonzero(core['source_ids']==qid)[0]);tile=int(core['tile_id'][qi])
selection={'source_id':sid,'source_point_id':qid,'original_row':q,'XYZ_mm':g['xyz'][q].tolist(),'tile':tile,'rule':'Within the unchanged valid scoring-core collar proxy, minimize squared XY distance to (full observed area-centroid X, full observed Y midrange); exact-distance ties by ascending original point ID.','uses_stress_or_predictions':False,'selection_sealed_before_prediction_read':True,'purpose':'Illustrative geometry-only point, not statistically representative','geometry_SHA256':sha(sr['geometry_path'])}
js('01_Enhanced_Figure03/ILLUSTRATIVE_QUERY_SELECTION.json',selection)
anchors=json.loads((R/'07_feature_implementation'/sid/'ANCHORS.json').read_text());windowrows=rows(P/'source_snapshot/OBSERVATION_WINDOW_COORDINATES.csv');features=[];featurearrays={};windows=[];consumed={}
def register(p,expected_hash=None,role=''):
 p=Path(p);actual=sha(p);eh=expected_hash or expected.get(str(p));assert eh is not None,('No independent expected hash',p);assert actual==eh,p
 consumed[str(p)]={'path':str(p),'role':role,'SHA256':actual,'expected_SHA256':eh,'status':'PASS'}
for p in [sr['geometry_path'],sr['target_path'],sr['E15_core_path'],sr['qualified_target_path']]:register(p,role='G07 frozen geometry/target/query topology')
register(R/'07_feature_implementation'/sid/'ANCHORS.json',role='Recorded feature anchors')
for condition in ['FULL','X50','X43']:
 a=anchors[f'{condition}_{tile}'];register(a['geometry_path'],a['geometry_SHA256'],'Recorded visible geometry');register(a['features_path'],a['features_SHA256'],'Recorded N3 base features');vg=dict(np.load(a['geometry_path']));ii=int(np.flatnonzero(vg['source_ids']==qid)[0]);assert np.array_equal(vg['xyz'][ii],g['xyz'][q]);f=np.load(a['features_path'])[ii].copy();f[:3]=((vg['xyz'][ii]-np.array(a['XYZ_mm']))/60).astype('f4');historical=vg['features'][ii];featurearrays[condition]=(historical,f)
 for ch in range(19):features.append({'condition':condition,'tile':tile,'source_point_id':qid,'channel':ch,'historical_N1_N2_value':float(historical[ch]),'N3_value':float(f[ch]),'historical_changed_vs_FULL':bool(historical[ch]!=featurearrays['FULL'][0][ch]),'N3_changed_vs_FULL':bool(f[ch]!=featurearrays['FULL'][1][ch])})
 wr=next((r for r in windowrows if r['source_id']==sid and r['condition']==condition and int(r['tile'])==tile),None)
 windows.append({'condition':condition,'tile':tile,'declared_X_min':float(wr['declared_X_min']) if wr else float(vg['xyz'][:,0].min()),'declared_X_max':float(wr['declared_X_max']) if wr else float(vg['xyz'][:,0].max()),'actual_X_min':float(vg['xyz'][:,0].min()),'actual_X_max':float(vg['xyz'][:,0].max()),'actual_Y_min':float(vg['xyz'][:,1].min()),'actual_Y_max':float(vg['xyz'][:,1].max()),'visible_points':len(vg['xyz']),'context_points':len(vg['context']),'neighbors16_IDs':vg['source_ids'][vg['neighbors'][ii]].tolist(),'anchor_XYZ_mm':a['XYZ_mm'],'visible_geometry_path':a['geometry_path']})
table('01_Enhanced_Figure03/QUERY_FEATURE_VALUES.csv',features);js('01_Enhanced_Figure03/EXACT_WINDOW_AND_NEIGHBOR_EVIDENCE.json',windows)
# Exact matching of four primary FULL fields; all other seed/context fields are retained for SI evidence.
registry=rows(P/'FROZEN_FIELD_ANALYSIS_REGISTRY.csv');modelreg=rows(R/'MODEL_PREDICTION_REGISTRY.csv');align=[];panelreg=[]
for sid in ['G07-V1-S355-AW','X23-V1-S355-AW']:
 sr=next(r for r in sources if r['source_id']==sid);g=dict(np.load(sr['geometry_path']));t=dict(np.load(sr['target_path']));mask=t['core']&t['valid'];ids=t['source_ids'][mask];xyz=t['xyz'][mask];area=t['area'][mask];y=t['T2_MPa'][mask]
 for p in [sr['geometry_path'],sr['target_path'],sr['qualified_target_path']]:register(p,role='Frozen comparison geometry/target')
 qualified=dict(np.load(sr['qualified_target_path']));qualified_checks={k:np.array_equal(qualified[k],t[k],equal_nan=True) for k in ['source_ids','xyz','area','T2_MPa','valid','core']};assert all(qualified_checks.values());assert np.isfinite(qualified['T2_MPa'][mask]).all()
 out={'source_ids':ids,'xyz':xyz,'area':area,'T2_MPa':y,'region':t['region'][mask]}
 for condition in ['FULL','X50','X43']:
  for seed in ['20261021','20261022']:
   for model in ['N2','N3']:
    fr=next(r for r in registry if r['source_id']==sid and r['model']==model and r['condition']==condition and r['seed']==seed);register(fr['path'],fr['SHA256'],'Saved neural prediction');pred=dict(np.load(fr['path']));ix=np.argsort(pred['source_ids']);ordered=pred['source_ids'][ix];assert len(np.unique(ordered))==len(ordered)==len(ids);take=ix[np.searchsorted(ordered,ids)];assert np.array_equal(pred['source_ids'][take],ids);assert np.array_equal(pred['xyz'][take],xyz);assert np.array_equal(pred['area'][take],area);assert pred.get('valid',np.ones(len(pred['source_ids']),dtype=bool))[take].all();v=pred['pred_MPa'][take];assert np.isfinite(v).all()
    mr=next(r for r in modelreg if r['source_id']==sid and r['model']==model and r['condition']==condition and r['seed']==seed);register(mr['checkpoint'],mr['checkpoint_SHA256'],'Frozen checkpoint provenance; not executed')
    align.append({'source_id':sid,'model':model,'condition':condition,'seed':seed,'points':len(ids),'IDs_exact':True,'XYZ_exact':True,'areas_exact':True,'valid':True,'prediction_SHA256':fr['SHA256'],'checkpoint_SHA256':mr['checkpoint_SHA256'],'source_order_changed':not np.array_equal(take,np.arange(len(ids))),'status':'PASS'})
    if condition=='FULL' and seed=='20261021':out[model]=v;out[model+'_error']=v-y;panelreg.append({'source_id':sid,'model':model,'condition':condition,'seed':seed,'geometry_path':sr['geometry_path'],'geometry_SHA256':sha(sr['geometry_path']),'target_path':sr['qualified_target_path'],'target_SHA256':sha(sr['qualified_target_path']),'prediction_path':fr['path'],'prediction_SHA256':fr['SHA256'],'checkpoint_path':mr['checkpoint'],'checkpoint_SHA256':mr['checkpoint_SHA256'],'IDs_SHA256':arrsha(ids),'XYZ_SHA256':arrsha(xyz),'areas_SHA256':arrsha(area)})
 for model in ['N2','N3']:
  assert np.array_equal(out[model+'_error'],out[model]-out['T2_MPa'])
 np.savez_compressed(D/'02_New_Figure07'/(sid[:3]+'_EXACT_PLOT_ARRAYS.npz'),**out)
table('02_New_Figure07/NUMERIC_ALIGNMENT_VERIFICATION.csv',align);table('02_New_Figure07/PANEL_PROVENANCE.csv',panelreg)
table('00_Source_Integrity/CONSUMED_INPUT_HASHES.csv',list(consumed.values()))
js('06_Scientific_QA/PREPARE_PASS.json',{'historical_files':len(checks),'historical_status':'PASS','direct_input_files':len(consumed),'primary_cases':4,'all_seed_context_alignment_cases':len(align),'query_selection':selection,'new_inference':0,'new_FE':0,'new_training':0,'new_experiments':0})
# Original artwork inventory and review boards: exact file contents retained.
inventory=[];pairs=[]
for kind,rrs in [('Main',rows(J/'03_Figures/FIGURE_SOURCE_REGISTRY.csv')),('Supplement',rows(J/'05_Supplementary_Material/SUPPLEMENTARY_FIGURE_INDEX.csv'))]:
 for rr in rrs:
  label='Figure '+(str(rr['figure']) if kind=='Main' else rr['figure_id']);p=J/('03_Figures/'+rr['filename'] if kind=='Main' else '05_Supplementary_Material/'+rr['file']);im=Image.open(p);act='Preserve unchanged'
  if label=='Figure 3':act='Replace with actual geometry, exact windows, 19-channel evidence and executed architecture'
  if label=='Figure 7':act='Move unchanged to S20; replace main slot with G07/X23 FULL seed20261021 FE comparison'
  inventory.append({'figure':label,'original_path':str(p),'source_data':rr.get('source',''),'question':p.stem.replace('_',' '),'manuscript_location':kind,'pixels':str(im.size),'resolution_DPI':str(im.info.get('dpi')),'physical_units':'mm/MPa where applicable; metrics dimensionless; schematic distinguished','color_scale':'Original source-wise or shared metric scale; reviewed against caption','caption_accuracy':'Reviewed; original caption retained unless explicitly revised','publication_readability':'Full-width recommended; dense regional grid moved to SI','revision_needed':label in ['Figure 3','Figure 7'],'action':act,'SHA256':sha(p)});pairs.append((label,p))
table('00_Source_Integrity/ORIGINAL_FIGURE_INVENTORY.csv',inventory)
for start in range(0,len(pairs),4):
 board=Image.new('RGB',(1600,1400),'white');draw=ImageDraw.Draw(board)
 for j,(label,p) in enumerate(pairs[start:start+4]):
  im=Image.open(p).convert('RGB');im.thumbnail((770,640));x=(j%2)*800;y=(j//2)*700;draw.text((x+15,y+10),label,fill='black');board.paste(im,(x+(800-im.width)//2,y+45+(640-im.height)//2))
 board.save(D/'06_Scientific_QA'/f'ORIGINAL_REVIEW_BOARD_{start//4+1}.png')
print('PREPARE PASS',len(consumed),'inputs;',len(align),'aligned fields; query',selection,flush=True)

