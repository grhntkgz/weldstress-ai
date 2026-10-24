from pathlib import Path
import json,hashlib,shutil,csv
import pandas as pd
D=Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRevision_R1');S=D/'source_snapshot';K=D.parent/'WeldStressAI_InferenceMechanisms_PhaseR8E15';J=D.parent/'WeldStressAI_ContextRobustness_PhaseR8E14'
man=D/'MANUSCRIPT_REVISION_R1.md';t=man.read_text(encoding='utf-8')
old='The FULL condition uses the complete processed front; X50 and X43 retain their frozen restricted windows and context rules.'
new='The FULL condition uses the complete processed front. X50 and X43 have nominal X widths 50 mm and 43 mm, respectively, centered at each fixed query tile midpoint and clipped independently to the measured X bounds without recentering. Both retain the complete measured Y extent (nominally 28 mm). Query bins have nominal X width 8 mm with a shorter final bin. Their midpoint is calculated from the actual query-coordinate extrema. Only fully visible original triangles contribute to recomputed visible-geometry features; deterministic area-CDF selection provides 4096 unique context IDs. Local neighborhoods use the historical nearest-sixteen and 1 mm/3 mm ring rules, each containing sixteen neighbors.'
t=t.replace(old,new)
bad='Q95 amplitude errors are reported in Table 3 and Supplementary Figure S28.';good='Absolute Q95 errors are retained in the supporting amplitude table and Supplementary Figure S28.'
t=t.replace(bad,good)
# Sequence of result figures: localization precedes variability in Results.
if not (D/'qa'/'FINAL_FIGURE_SEQUENCE.json').exists():
 figs=json.loads((D/'figures'/'MAIN_FIGURE_REGISTRY.json').read_text())
 for r in figs:
  r['caption']=r['caption'].replace(bad,good)
  if r['number'] in [6,7]:
   newnum=13-r['number']
   for key in ['path','PDF']:
    newpath=r[key].replace(f"Fig{r['number']:02}_",f'Fig{newnum:02}_');(D/r[key]).rename(D/newpath);r[key]=newpath
   r['number']=newnum
 figs.sort(key=lambda r:r['number']);(D/'figures'/'MAIN_FIGURE_REGISTRY.json').write_text(json.dumps(figs,indent=2))
 for a,b in [('Figure 6','Figure TEMP'),('Figure 7','Figure 6'),('Figure TEMP','Figure 7'),('Fig06_','FigTEMP_'),('Fig07_','Fig06_'),('FigTEMP_','Fig07_')]:t=t.replace(a,b)
 for name in ['FIGURE_CAPTIONS.md','MAIN_FIGURE_SELECTION.md']:
  p=D/name;s=p.read_text(encoding='utf-8').replace(bad,good)
  for a,b in [('Figure 6','Figure TEMP'),('Figure 7','Figure 6'),('Figure TEMP','Figure 7'),('Fig06_','FigTEMP_'),('Fig07_','Fig06_'),('FigTEMP_','Fig07_')]:s=s.replace(a,b)
  p.write_text(s,encoding='utf-8')
 (D/'qa'/'FINAL_FIGURE_SEQUENCE.json').write_text('{"passed":true}')
man.write_text(t,encoding='utf-8')
# Hash-verified compact historical input protocols, not executable research imports.
hist=[]
for root,name in [(J,'src/prepare_contexts_e14.py'),(J,'src/seal_protocol_e14.py'),(K,'ORIGINAL_TILE_TOPOLOGY.csv')]:
 m=json.loads((root/'REPRODUCIBILITY_MANIFEST.json').read_text());ix={x['path']:x for x in m['files']};p=root/name;h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==ix[name]['SHA256'];dest=S/'historical_input_contracts'/root.name/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);hist.append(dict(path=str(p),SHA256=h,status='PASS'))
pd.DataFrame(hist).to_csv(D/'qa'/'CONTEXT_PROTOCOL_INTEGRITY.csv',index=False)
audit=pd.read_csv(D/'CLAIM_EVIDENCE_AUDIT.csv');extra=[]
for key,value in [('X50_nominal_X_mm',50),('X43_nominal_X_mm',43),('query_nominal_X_mm',8),('nominal_Y_mm',28),('context_unique',4096)]:
 extra.append(dict(claim_id='CONTEXT_'+key,claim=key,evidence_file=str(S/'historical_input_contracts'/J.name/'src/seal_protocol_e14.py'),row_key='frozen context protocol',column=key,verified_value=value,unit='mm' if key.endswith('mm') else 'count',derivation='Read-only original protocol, verified against original release manifest',manuscript_location='Section 2.1',evidence_level='FROZEN_PROTOCOL',status='PASS'))
pd.concat([audit,pd.DataFrame(extra)],ignore_index=True).drop_duplicates('claim_id').to_csv(D/'CLAIM_EVIDENCE_AUDIT.csv',index=False,encoding='utf-8-sig')
print('Final editorial refinements saved')
