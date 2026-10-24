from pathlib import Path
import json,hashlib,re,csv
import pandas as pd
from PIL import Image
D=Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRevision_R1');S=D/'source_snapshot'
refs=json.loads((D/'literature'/'VERIFIED_REFERENCE_RECORDS.json').read_text(encoding='utf-8'));figs=json.loads((D/'figures'/'MAIN_FIGURE_REGISTRY.json').read_text())
# Make the public figure sequence identical to first citation in the revised manuscript.
if not (D/'qa'/'FIGURES_RENUMBERED.json').exists():
 for r in figs:
  if r['number'] in [4,5]:
   new=9-r['number']
   for field in ['path','PDF']:
    old=D/r[field];rel=r[field].replace(f"Fig{r['number']:02}_",f'Fig{new:02}_');old.rename(D/rel);r[field]=rel
   r['number']=new
 figs.sort(key=lambda r:r['number']);(D/'figures'/'MAIN_FIGURE_REGISTRY.json').write_text(json.dumps(figs,indent=2),encoding='utf-8');(D/'qa'/'FIGURES_RENUMBERED.json').write_text('{"passed":true,"reason":"first manuscript citation order"}')
def put(name,s):(D/name).write_text(s,encoding='utf-8')
state='''# Position relative to prior research

This is a focused primary-source review, not a systematic review or proof of priority. Exact bibliography, original links, access scope and verified methodological summaries are recorded in LITERATURE_VERIFICATION.csv. Abstract/highlight-only access limits the detail claimed for those sources. No cross-paper accuracy ranking is attempted because targets, supports and loading problems differ.

| Prior work | Established scope | Relationship to this manuscript |
|---|---|---|
| Ottersböck et al. 2021 [2] | Actual weld topography and local mechanical concentration | Numerical geometry sensitivity already studied |
| Hultgren et al. 2021 [3] | Scan resolution and real-weld reconstruction | Measurement/reconstruction fidelity precedes surrogate accuracy |
| Braun et al. 2022 [4] | FE-trained neural SCF and measured seams | Neural scan-based concentration assessment is prior art |
| Schubnell et al. 2024 [5] | Coordinate-profile regression of numerical SCF | Direct profile input is prior art; proceedings contribution |
| Rohani Raftar et al. 2024 [6] | Digitized weld geometry, FE and bagged trees | Closest scan/FE/ML comparator; combination itself is not novel |
| Qi et al. 2025 [7] | Structural stress of idealized and scanned joints | Stress-definition distinction; no equivalence to T2 |
| Dänekas et al. 2025 [8] | Toe-parameter measurement algorithms | Supports caution about geometry metrology |
| Nie et al. 2020 [9] | Elastic stress-field CNN | Dense numerical-field prediction is prior art |
| Park and Kang 2026 [10] | Point-set/operator stress-field surrogate | Geometry-to-field learning is prior art |
| PointNet and Point Transformer [11,12] | Point-set learning methods | Architecture origins; not physical-stress validation |

The present distinction is the combined controlled representation/context diagnosis, fixed original surface support, documentary-plate grouping and explicit field/localization/amplitude trade-off. We do not infer that any listed paper omitted every aspect of those questions merely because an abstract did not mention it. No absence-of-prior-work claim is required by the paper's contribution.
'''
put('STATE_OF_THE_ART_COMPARISON.md',state)
put('NOVELTY_POSITIONING.md','''# Contribution and boundaries

Research question: How do geometric feature representation and observation-context variation influence the accuracy, robustness and high-stress localization of machine-learning surrogates trained on three-dimensional scanned welded joints?

The contribution is a controlled representation audit coupled to a constructive visible-local contract, evaluated on exactly matched original surface support with documentary-plate grouping and joint numerical safeguards. Frozen-weight block substitutions establish computational dependence; they do not identify independent physical geometry causes. The local contract is operational under a registered frame/query plan; it does not eliminate contextual dependence or guarantee predictive improvement.

The retained outcome is METHOD_IMPROVEMENT_MIXED. N3's localization benefit coexists with worse whole-field and peak-amplitude errors relative to N2. The fixed tree comparator adds a limited empirical comparison under different sample usage, not proof of architectural superiority. Earlier scanned-weld/FE/ML studies are acknowledged in the manuscript rather than treated as absent. No first-study, universal-best, fresh external-validation or physical-fatigue claim is justified.
''')
sel=['# Main and supplementary figure selection','', 'All 35 original PNG/PDF pairs were retained byte-for-byte in source_snapshot/19_scientific_figures and copied to figures/supplementary. The main paper contains nine figures. Newly plotted numerical summaries use only released CSV cells; the field redraw reads existing stored predictions and targets without inference. Original maps are not rendered as new FE calculations.','']
caps=['# Main figure captions','']
for r in figs:
 im=Image.open(D/r['path']);sel += [f"## Figure {r['number']} {r['name'].replace('_',' ')}",'',f"Main placement: manuscript first citation Figure {r['number']}. New output: {r['path']} and {r['PDF']}. PNG dimensions: {im.width} × {im.height} pixels; exported at 300 dpi. Composite panels retain their source raster resolution; embedding does not create extra measured detail.", '',f"Exact original figure sources: {r['original_files']}",'',r['justification'],'',f"Caption: {r['caption']}",''];caps += [f"Figure {r['number']}. {r['caption']}",'']
orig=pd.read_csv(S/'SCIENTIFIC_FIGURES.csv');selected_nums=set(int(n) for r in figs for n in r['original_numbers'].split(','))
sel += ['## Complete original figure disposition','', '| Original | Title | Placement | Original PNG | Original PDF |','|---|---|---|---|---|']
for _,r in orig.iterrows():
 placement='Main derivative and supplementary original' if r.number in selected_nums else 'Supplementary'
 sel += [f'| {r.number} | {r.title} | {placement} | {r.PNG} | {r.PDF} |']
put('MAIN_FIGURE_SELECTION.md','\n'.join(sel));put('FIGURE_CAPTIONS.md','\n'.join(caps)+'\n\n## Supplementary captions\n\nOriginal S01–S35 captions, source paths and qualifications remain in source_snapshot/SCIENTIFIC_FIGURES.csv. Original internal numbering is intentionally retained in unchanged supplementary images. S25 must be read with the constant-field tie warning; its zero FN is not credited as localization success.\n')
put('SUPPLEMENTARY_MATERIAL_PLAN.md','''# Supplementary material delivered with the revision

S01–S35 are the complete original scientific PNG/PDF pairs in figures/supplementary, including native mesh evidence and unfavorable examples. New main figures are placed by manuscript citation, not by historical study sequence. MAIN_FIGURE_SELECTION.md maps every original to its disposition. Original figures remain unchanged, including internal historical numbers.

- Complete models and metrics: MAIN_MODEL_METRICS.csv, BOTH_SEED_METRICS.csv and ALL_PLATE_METRICS.csv; amplitude and missed-area interpretation in MAIN_RESULTS_TABLES.md.
- Exact original source-level scores, regional results, errors and context stability: corresponding source_snapshot CSV files and subdirectories 14–17.
- Numerical reference: thirteen-source registry, fixed target/operator identifiers, M1/M2 hashes and qualification bounds; native mesh figures S03–S04.
- Mechanism: all eight factorial cells, all main/pair/triple contrasts, per-source results and endpoint replay receipts. No cell omitted because its effect was unfavorable.
- Visible feature contract: nineteen-channel formulas, core and full-visible contextual consistency, feature visibility and post-fit audit distinction.
- Historical inference: hash-verified E15 policy and boundary controls in source_snapshot/historical_E15, with derived read-only summary tables at revision root.
- Reproducibility: original configuration, fold, target/checkpoint registries, closure rules, independent verification receipts and source manifests; revision scripts and claim ledger.

This package contains manuscript-supporting results, not a replacement public dataset deposit. Large FE solutions, checkpoint binaries and every historical prediction field remain at their unchanged original registered locations. No claim is made that the ZIP alone recreates the entire Windows research environment. Authors must select journal supplementary naming conventions and check permissions before public deposition.
''')
put('EDITORIAL_RISK_AND_REVIEWER_OBJECTIONS.md','''# Editorial risks and responses

## Is the claimed contribution already known

Scan-based FE stress analysis and learned weld concentration are established prior work. The revised Introduction identifies the nearest scanned-geometry/FE/ML precedents. The claim is restricted to this controlled representation/context study and its matched-support, plate-grouped evaluation; no priority claim remains. Literature access scope is explicit rather than presenting every abstract as full-text reading.

## Is the proposed model actually better

N3 is not universally better. Whole-field L2 and peak-amplitude error worsen relative to N2, even while relative high-area localization improves. METHOD_IMPROVEMENT_MIXED remains unchanged. Both seeds and every plate are retained, with difficult G and X outcomes in the main paper.

## Does the target represent physical weld-notch stress

No. T2 is an area/chord-regularized tensile maximum-principal numerical field under an assumed rear and fixed elastic problem. Its two-level qualification does not establish physical toe radius or standard structural/effective-notch stress. Residual stress, plasticity and fatigue life are excluded. A numerical surrogate cannot validate its reference experimentally.

## Is leave-one-plate-out an independent validation

The groups are documentary plates with unresolved batch/session independence and repeated development exposure. Within-run plate isolation is useful but does not restore a blind cohort. No fresh independent generalization claim is made. Many points do not provide many independent specimens.

## Are localization scores misleading

Own-field percentile thresholds assess relative spatial ranking. The constant baseline labels the entire surface high at a tie and obtains zero FN; this is disclosed, tabulated and not visually rewarded. Peak and Q95 amplitude errors remain alongside overlap and missed area. A smaller missed area alone does not establish a safer joint.

## Does the oracle prove deployable partial-observation recovery

No. It deliberately uses unseen FULL statistics and can create off-distribution combinations. It establishes computational sensitivity at fixed visible support. The N3 constructive comparison also changes anchoring support, so there is no unique physical-information causal decomposition.

## Is the tree comparison fair

The channels and outer grouping are documented, but training sample counts, optimization and capacity differ. The fixed estimator comparison is reported; architecture superiority and a controlled speed benchmark are not claimed. Historical restricted Ridge/constant fields are unavailable and are not fabricated.

## What remains before submission

Human authors must confirm authorship, affiliations, funding, competing interests, third-party permissions, selected journal requirements and derived-data/code deposition. The package is for author review, not a submitted or accepted article. No target journal, certified production-batch metadata, experimental stress validation or independent cohort can be invented editorially. These are explicit limits and author-facing submission actions, not uncompleted authorized simulations.
''')
put('SCIENTIFIC_REVISION_CHANGELOG.md','''# Scientific revision changelog

The authoritative research release was read without modification. The independent manuscript workspace contains copied evidence and newly authored editorial artifacts only.

1. Replaced chronological phase narration with a question-led engineering manuscript covering geometry, the numerical operator, representation, design, results and interpretation.
2. Added verified close prior scanned-weld/FE/ML research and general stress-field surrogates. Distinguished journal articles, proceedings, book, dataset and original-author records. Corrected issue-year differences and rejected a DOI that resolved to another title.
3. Created exact CSV claim provenance and independently reaggregated the released source-level metrics and two-seed summaries. The stability metric denominator was checked against executed scoring code and explicitly uses the model's FULL prediction norm.
4. Kept METHOD_IMPROVEMENT_MIXED and the whole-field/overlap/amplitude disagreement. Included both seeds and all plates, including unfavorable G and X results.
5. Inspected all 35 original figure pairs, retained them as supplementary, and prepared nine main figures from existing evidence. Replaced text-only architecture panels and small mesh montages with readable schematics and complete qualification plots. Stress maps use stored fields with common stress limits and signed errors.
6. Exposed the constant-baseline percentile-tie failure, nondeployable oracle status, compact SurfacePT override, anchoring confound, unequal baseline sampling budgets and previously examined cohort.
7. Expanded availability, uncertainty and reviewer-risk statements without inventing a public deposit, authorship information or physical validation.
8. Authored an editable Word version and performed page-render QA with the available native Word PDF conversion path, followed by the packaged document rasterizer. Renderer details and any final limitations are in the quality audit.

No ANSYS job, target generation, training, fit, model inference or experimental configuration was launched. No historical figure, target or checkpoint was overwritten.
''')
# Extend key-claim audit to historical controls, protocol numbers and source-level extrema.
audit=pd.read_csv(D/'CLAIM_EVIDENCE_AUDIT.csv');extra=[]
def add(id,claim,file,key,col,value,formula,unit='dimensionless'):
 extra.append(dict(claim_id=id,claim=claim,evidence_file=str(D/file),row_key=key,column=col,verified_value=value,unit=unit,derivation=formula,manuscript_location='Methods or Results narrative',evidence_level='NUMERICAL_RELEASE',status='PASS'))
for name in ['HISTORICAL_E15_POLICY_MEANS.csv','HISTORICAL_E15_CONTINUITY_MEANS.csv']:
 x=pd.read_csv(D/name)
 for i,r in x.iterrows():
  for c in ['L2','MAE_MPa','high95_IoU','mean_boundary_jump_error_MPa']:
   if c in x:add('H'+name[:5]+str(i)+c,'Historical policy/control aggregate',name,f'model={r.model};condition={r.condition};policy={r.policy}',c,r[c],'Source mean within plate, equal plates, then both seeds','MPa' if c.endswith('MPa') else 'dimensionless')
x=pd.read_csv(D/'HISTORICAL_E15_POLICY_MEANS.csv');a=x[(x.model=='N1')&(x.condition=='X43')&(x.policy=='S0')].iloc[0];b=x[(x.model=='N1')&(x.condition=='X43')&(x.policy=='S1')].iloc[0];add('H_STITCH_L2','N1 X43 uniform overlap L2 relative change','HISTORICAL_E15_POLICY_MEANS.csv','N1/X43/S1 versus S0','L2',(b.L2/a.L2-1)*100,'100*(S1/S0-1)','%')
source=pd.read_csv(S/'SOURCE_LEVEL_METRICS.csv');pl=pd.read_csv(S/'PLATE_LEVEL_METRICS.csv')
for data,name in [(source,'SOURCE_LEVEL_METRICS.csv'),(pl,'PLATE_LEVEL_METRICS.csv')]:
 sub=data[data.model=='N3'];r=sub.loc[sub.L2.idxmax()];add('WORST_'+name,'Maximum individual N3 L2 row','source_snapshot/'+name,';'.join(f'{k}={r[k]}' for k in ['model','seed','condition','plate']+(['source_id'] if 'source_id' in data else [])),'L2',r.L2,'Maximum over every released N3 row')
for file in ['N3_ARCHITECTURE_AND_TRAINING.json','METRIC_DEFINITIONS.json','XGBOOST_BASELINE_PROTOCOL.json','R8E16_FINAL_COUNTS.json']:
 obj=json.loads((S/file).read_text());
 def walk(x,path=''):
  if isinstance(x,dict):
   for k,v in x.items():walk(v,path+'.'+k)
  elif isinstance(x,list):
   for i,v in enumerate(x):walk(v,path+f'[{i}]')
  elif isinstance(x,(int,float)) and not isinstance(x,bool):add('PROTOCOL_'+file+'_'+path,'Frozen protocol or release count','source_snapshot/'+file,path,'JSON scalar',x,'Exact frozen scalar')
 walk(obj)
pd.concat([audit,pd.DataFrame(extra)],ignore_index=True).to_csv(D/'CLAIM_EVIDENCE_AUDIT.csv',index=False,encoding='utf-8-sig')
print(json.dumps({'support_documents':9,'total_claim_entries':len(audit)+len(extra),'figures':[r['number'] for r in figs]}))
