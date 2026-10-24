from pathlib import Path
import json,hashlib,csv,shutil
import numpy as np,pandas as pd
D=Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRevision_R2');O=D.parent;R=O/'WeldStressAI_FinalResearch_PhaseR8E16';P=O/'WeldStressAI_ManuscriptRevision_R1';H=O/'WeldStressAI_PlateHeldOutAI_PhaseR8E13'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
audit=[]
for root,manifestname,label in [(R,'REPRODUCIBILITY_MANIFEST.json','R8E16'),(P,'REVISION_REPRODUCIBILITY_MANIFEST.json','R1')]:
 manifest=json.loads((root/manifestname).read_text());index={r['path']:r for r in manifest['files']};files=[p for p in root.iterdir() if p.is_file() and p.suffix in ['.md','.csv','.json','.docx'] and p.name not in ['XGBOOST_SAMPLE_IDS.csv',manifestname,'DELIVERY_VERIFICATION.json']]
 if label=='R1':files+=list((root/'figures').rglob('*.png'))+list((root/'figures').rglob('*.pdf'))+list((root/'literature').glob('*.json'))
 else:
  for folder in ['17_model_comparisons','20_manuscript','18_independent_verification']:
   files += [p for p in (root/folder).iterdir() if p.is_file() and p.suffix in ['.csv','.md','.json']]
 for p in sorted(set(files)):
  rel=p.relative_to(root).as_posix();expected=index[rel]['SHA256'];h=sha(p);assert h==expected,(label,rel);dest=D/'source_snapshot'/label/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);audit.append(dict(label=label,path=str(p),relative_path=rel,SHA256=h,status='PASS'))
 shutil.copy2(root/manifestname,D/'source_snapshot'/label/manifestname)
pd.DataFrame(audit).to_csv(D/'qa'/'INITIAL_SOURCE_INTEGRITY.csv',index=False)
shutil.copy2(Path(r'C:\Users\grhnt.DESKTOP-KRBB26F\.codex\attachments\7ff52253-fe45-49fd-be93-e9c34c03c1f3\Pasted text.txt'),D/'source_snapshot'/'R2_REQUEST.txt')
summary=[]
for sid in ['G07-V1-S355-AW','X10-V1-S355-AW','X23-V1-S355-AW']:
 g=dict(np.load(H/'02_geometry'/(sid+'.npz')));t=dict(np.load(H/'01_dataset/targets'/(sid+'.npz')));reg=pd.read_csv(R/'QUALIFIED13_SOURCE_REGISTRY.csv');row=reg[reg.source_id==sid].iloc[0];package=Path(row.qualified_M2_target_path).parent
 summary.append(dict(source=sid,geometry_keys={k:list(v.shape) for k,v in g.items()},target_keys={k:list(v.shape) for k,v in t.items()},geometry_bounds=[g['xyz'].min(0).tolist(),g['xyz'].max(0).tolist()],region_counts={int(k):int((t['region']==k).sum()) for k in np.unique(t['region'])},package=str(package),package_files=[str(p) for p in package.iterdir() if p.suffix.lower() in ['.json','.csv','.md']],release_workspace=row.release_workspace))
(D/'qa'/'SPATIAL_INPUT_DISCOVERY.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
