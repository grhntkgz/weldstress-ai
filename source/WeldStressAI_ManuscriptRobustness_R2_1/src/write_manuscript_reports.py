from pathlib import Path
import json,re,shutil,hashlib
import pandas as pd,numpy as np
D=Path(__file__).resolve().parents[1];O=D.parent;P=O/'WeldStressAI_ManuscriptRevision_R2';R=O/'WeldStressAI_FinalResearch_PhaseR8E16'
def write(n,s):(D/n).write_text(s.strip()+'\n',encoding='utf-8')
def table(df,cols):
 z=df[cols].copy()
 for c in z:
  if pd.api.types.is_float_dtype(z[c]):z[c]=z[c].map(lambda v:f'{v:.6f}' if pd.notna(v) else 'undefined')
 return '| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'+'\n'.join('| '+' | '.join(str(x) for x in row)+' |' for row in z.itertuples(index=False,name=None))
audit=json.loads((D/'qa'/'INDEPENDENT_AUDIT_PASS.json').read_text());extra=json.loads((D/'qa'/'ADDITIONAL_INDEPENDENT_CHECKS.json').read_text());assert audit['status']==extra['status']=='PASS'
macro=pd.read_csv(D/'THRESHOLD_ROBUSTNESS_MACRO.csv');macro=macro[macro.scheme=='RANK_BUDGET'];common=pd.read_csv(D/'REFERENCE_THRESHOLD_MACRO.csv');plate=pd.read_csv(D/'THRESHOLD_ROBUSTNESS_PLATE.csv');plate=plate[plate.scheme=='RANK_BUDGET'];region=pd.read_csv(D/'REGIONAL_ERROR_MACRO.csv');g0=pd.read_csv(D/'G0_COLLAR_MACRO.csv');g1=pd.read_csv(D/'G1_GEOMETRY_MACRO.csv');geometry=pd.read_csv(D/'NEURAL_VERSUS_GEOMETRY_BASELINES.csv');seed=pd.read_csv(D/'THRESHOLD_ROBUSTNESS_MACRO_SEED.csv');seed=seed[seed.scheme=='RANK_BUDGET']
contrasts=[]
for c in ['FULL','X50','X43']:
 for b in [.01,.05,.10]:
  z=macro[(macro.condition==c)&(macro.budget==b)].set_index('model');q=common[(common.condition==c)&(common.budget==b)].set_index('model');contrasts.append(dict(condition=c,budget=b,N1_rank_IoU=z.loc['N1','IoU'],N2_rank_IoU=z.loc['N2','IoU'],N3_rank_IoU=z.loc['N3','IoU'],rank_delta_N3_N2=z.loc['N3','IoU']-z.loc['N2','IoU'],common_N2_IoU=q.loc['N2','IoU'],common_N3_IoU=q.loc['N3','IoU'],common_delta_N3_N2=q.loc['N3','IoU']-q.loc['N2','IoU']))
ct=pd.DataFrame(contrasts);ct.to_csv(D/'N3_N2_THRESHOLD_SUMMARY.csv',index=False)
for filename,frame in [('THRESHOLD_ROBUSTNESS',plate),('REFERENCE_THRESHOLD',pd.read_csv(D/'REFERENCE_THRESHOLD_PLATE.csv'))]:
 z=frame[frame.model.isin(['N2','N3'])].pivot(index=['plate','condition','budget'],columns='model',values='IoU');z['delta_IoU']=z.N3-z.N2;z.reset_index().to_csv(D/(filename+'_N3_MINUS_N2_PLATE.csv'),index=False)
for filename in ['THRESHOLD_ROBUSTNESS','REFERENCE_THRESHOLD']:
 a=pd.read_csv(D/(filename+'_MACRO_SEED.csv'));a=a[(a.model.isin(['N2','N3']))&(a.scheme!='HISTORICAL_HIGH95')];z=a.pivot(index=['seed','condition','budget'],columns='model',values='IoU');z['delta_IoU']=z.N3-z.N2;z.reset_index().to_csv(D/(filename+'_N3_MINUS_N2_MACRO_SEED.csv'),index=False)
intro='All R2.1 findings below are retrospective exploratory descriptions of frozen numerical fields on the previously examined cohort. No new solve, mesh, target, training, fitting or inference was performed. The original METHOD_IMPROVEMENT_MIXED decision is preserved.\n\n'
findings='''# R2.1 scientific findings and closure

'''+intro+'''## Threshold robustness

N3-minus-N2 equal-plate rank IoU is positive in all nine context/budget means, but the 1% FULL gain is only 0.000702 and changes sign between the two seeds. The 5% gains remain about 0.0531–0.0625, while 10% gains shrink to 0.0054–0.0211. Plate signs are heterogeneous: at 1%, E and G are adverse in every context; at 10%, E is adverse in every context and C is adverse in restricted contexts. These are not uniformly robust plate-level improvements.

'''+table(ct,['condition','budget','N1_rank_IoU','N2_rank_IoU','N3_rank_IoU','rank_delta_N3_N2','common_delta_N3_N2'])+'''

The X plate remains adverse at 5% rank budgets in all contexts, with approximately −0.01920 FULL, −0.07845 X50 and −0.09240 X43. It is not uniformly adverse under other definitions: 10% rank contrasts become positive in all contexts, while 1% restricted-view contrasts become positive and FULL remains negative. At the common FE-derived 5% threshold, all five mean plate contrasts favor N3, including X (+0.03752, +0.00802 and +0.01844). At the common 1% threshold N3 loses to N2 in all contexts and both seeds; macro IoU differences are −0.06607, −0.05010 and −0.03894 under FULL/X50/X43. Thus relative ranking, threshold classification and field amplitude are distinct outcomes. Common thresholds are REFERENCE_THRESHOLD_DIAGNOSTIC_ONLY; their held-out FE values are unavailable operationally.

Under FULL at the reference 99th percentile, N3 selects only 0.1945% of core area and achieves recall 0.03994, despite a nominal reference high area of about 1%. This is a numerical amplitude-sensitive failure, not a physical allowable-stress determination. N1 FULL rank IoU remains the largest of the neural models at all three budgets, while common-threshold top-5% N3 IoU narrowly exceeds N1; model order can depend on the diagnostic.

## Area quotas and ties

The closest-prefix rule retains whole original-area vertices and breaks exact score ties by increasing original ID. Across nonconstant scores the maximum area-fraction deviation is 1.83511e−5, or 0.00183511 percentage points. Neural source-level 5% rank-versus-historical IoU differs by at most 0.00090120; macro differences are below 0.00015. These differences do not explain the large common-threshold reversals. Original High95 is exactly recovered separately. The constant baseline's rank mask is arbitrary ID ordering without stress information; its historical own-CDF mask still marks the entire core. It must not be interpreted as a meaningful learned ranking.

## Geometry-only comparator

G0 covers an equal-plate mean 9.5632% of the core (source range 5.3699–11.2712%). Its 5% reference capture is 87.3770% on average, with source range 64.8981–100%; its precision is 0.487918 and IoU 0.461345. At 1% it captures 98.7110% but precision is only 0.109405; at 10% capture falls to 66.1879%. Recall alone cannot establish usefulness, and G0 marks an unequal area compared with budgeted neural masks.

The sealed G1 geometry rule is feasible for all thirteen sources, each having two contour components. Its FULL IoUs are 0.000000, 0.032933 and 0.156313 for 1/5/10%; N3 gives 0.140055, 0.601118 and 0.605041. All 78 N3 source/seed/budget comparisons against G1 are favorable, as are all fifteen two-seed plate/budget means. This supports NEURAL_ADDED_VALUE_SUPPORTED over this specific fixed FULL geometry ranking, not over every possible geometric or mechanics-based method. A narrow distance band around the 0.5 mm relief contour does not capture the observed numerical high sets well, despite their broad-collar association. The contour is not a validated toe curve; its weak performance cannot prove that neural architecture is indispensable.

G0/G1 partial-observation comparisons are NOT_EVALUABLE: the existing labels depend on a FULL-source fitted parent plane, without a previously qualified strictly visible replacement. No hidden full-source labels or post-result alternative fit is introduced. This is an explicit information-contract limitation, not evidence of poor restricted geometry-only performance. The comparison is valid under FULL only. Geometry masks have no assigned MPa and no L2.

## Regional error and boundaries

The original height proxy occupies 80.9572% of core area on average, collar 9.5632% and parent 9.4796%. Height therefore contributes the largest macro weighted squared error for each neural model/context, although collar pointwise MAE can be larger. N3's height-region SSE share is 46.72–52.93%; its parent share is 24.57–29.09%. These are mean source error shares, not pooled physical specimen fractions.

N3 FULL collar MAE improves from N2's 19.18849 to 17.39336 MPa, and improves in every two-seed mean plate under FULL. Parent MAE simultaneously worsens from 17.72843 to 20.67217 MPa; height MAE rises from 7.30678 to 7.80455 MPa. At X50 collar MAE worsens slightly (16.69736 to 16.85945 MPa), whereas at X43 it improves slightly (17.06290 to 16.88939 MPa). No geometric region improves under N3 in every plate/context cell. The whole-field and transition-region rankings are therefore different.

X10 and X23 exhibit stronger parent underprediction in N3, with height-region overprediction and source-dependent collar behavior. X10 FULL N3 parent bias is −22.7763 MPa and height bias +10.0016 MPa; X23 values are −19.5558 and +4.7699 MPa. Under X43 both continue parent underprediction. Collar MAE can improve while relative top-5% overlap worsens, because local stress amplitude errors and within-region ordering are different questions. These are observed numerical patterns, not a causal physical-defect explanation.

The within-1-mm core X-edge area is about 5.4–5.8% for critical sources. N3's error share there is about 10–12%, but it remains a minority of total error. Native loading caps/gauges and owning observation edges are distinct: no evaluated query is within 1 mm of those native caps or gauges or owning observation X edges; the minimum owning observation-edge distance is 11.00001 mm. Proximity to a scoring edge does not establish traction causation. The R2 direct-cap separation and unresolved nonlocal boundary influence remain unchanged.

## Decisions

- FROZEN_EVIDENCE_VERIFIED
- LOCALIZATION_MIXED_ACROSS_THRESHOLDS
- NEURAL_ADDED_VALUE_SUPPORTED — restricted to the sealed FULL geometry comparator
- REGIONAL_ERROR_AUDIT_COMPLETE
- METHOD_IMPROVEMENT_MIXED — original experiment unchanged
- MANUSCRIPT_FINAL_READY_FOR_AUTHOR_REVIEW — subject to the final render/integrity receipt
- CURRENT_WELDSTRESS_AI_MANUSCRIPT_RESEARCH_CLOSED

The remaining physical validation, registration, rear-surface, fixture and independent-cohort limitations are not resolved by these diagnostics. No R8-E17, R2.2 or further model-development phase is initiated.
'''
write('R2_1_SCIENTIFIC_FINDINGS.md',findings)
write('R2_1_UNFAVORABLE_RESULTS.md','''# Unfavorable and unavailable R2.1 findings

'''+intro+'''N3's top-1% rank gain is seed dependent and nearly zero under FULL. Its common FE 99th-percentile IoU is below N2 in every context and both seeds. E/G remain adverse at 1% rank; E and restricted C are adverse at 10%. X remains adverse at 5% rank, with a definition-dependent reversal elsewhere. Historical N3 L2 and peak-amplitude degradation remain unchanged. Parent MAE worsens in aggregate under N3 at every context; collar MAE does not improve at X50, and no region improves across all plates/contexts. Stronger source-specific parent underprediction persists in X10/X23. These results qualify practical robustness despite favorable FULL neural-versus-G1 comparisons.

G1 has zero 1% IoU and low 5% IoU on this fixed contour rule. Its weakness does not establish superiority over every geometric alternative. G0 recall requires unequal broad area and must not be presented as a fair equal-budget success. Fair partial-view geometry baselines are unavailable because no qualified visible-only parent-plane contract exists; all 52 restricted source/model rows are explicitly NOT_EVALUABLE rather than fabricated scores. B0/B1 restricted predictions remain historically unavailable. Empty common-threshold masks have undefined precision/centroid, with valid group counts retained; they are not zero-error predictions.

The independent checker initially used the wrong order for means containing undefined precision, then was corrected to the sealed per-seed hierarchy; the initial discrepancy and complete successful recheck are retained under qa. No scientific threshold, primary metric or prediction was changed. Physical toe/peak-stress validation and causal boundary attribution remain unresolved.
''')
write('R2_1_INPUT_INTEGRITY_REPORT.md','''# Input integrity

The original R8-E16 release (2,715 manifested files), R1 (470) and R2 (388) pass fresh full SHA-256 checks. The sealed input registry records 644 directly consumed original artifacts with expected hashes. Thirteen original/qualified target packages retain exact point IDs, XYZ, areas and T2; original triangle areas and geometry-region rules were independently reconstructed. All 299 saved prediction fields match their original registry hashes and exact 34,200-query supports. Original tile ownership and visible/context IDs are verified for 130 restricted source/context/tile views; each owns unchanged queries and 4,096 unique context IDs. All original historical High95 source metrics are reproduced before R2.1 execution.

The five documentary plates and both neural seeds remain fixed. B0/B1 FULL source arrays are projected to the unchanged original core by exact original indices; no new predictions are computed. R2 boundary records are reused as frozen records, distinct from new mechanical sensitivity verification. No missing prescribed source or original available prediction was replaced. G0/G1 partial-view observability is explicitly unavailable, not an input-file loss.

R2_1_INPUT_HASHES.json, R2_1_SOURCE_REGISTRY.csv, the protocol seal and qa full-integrity/ownership/High95 files provide detailed provenance. File integrity does not imply physical model validity.
''')
write('R2_1_INDEPENDENT_METRIC_AUDIT.md',f'''# Independent R2.1 numerical audit

The separate checking implementation passes {audit['numeric_cells']:,} numerical cells including {audit['aggregate_cells']:,} aggregation cells, with maximum absolute discrepancy {audit['max_absolute_cell_error']:.12g}. Every rank, common-threshold and historical mask is exactly identical to the primary implementation. Python sorting, cumulative/bisect quota selection and separate percentile interpolation check the NumPy primary rule; dot-product set arithmetic and math.fsum weighted errors independently check localization and regions. Explicit source/plate/seed loops preserve the sealed hierarchy.

All thirteen G1 contours and scores were independently reconstructed from mesh-edge intersections; maximum distance difference is {audit['independent_geometry_max_distance_error_mm']:.12g} mm. Stored geometry score membership is independently ranked, with no stress input. An additional {extra['boundary_geometry_and_grouping_cells']:,} cells independently check nonexclusive native/core/observation boundary strata, geometry baseline aggregations and paired contrasts; maximum discrepancy {extra['maximum_absolute_error']:.12g}.

The first checker failed macro precision with undefined empty-mask values because it reversed seed/plate averaging order. The correction affects the checker only; the sealed primary outputs remain unchanged. The full successful rerun and initial failure record are retained. Valid-source and valid-plate counts accompany partially undefined precision/centroid diagnostics. Historical High95 remains a separate exact control. No claim of independent external validation follows from this arithmetic audit.
''')
critical=pd.read_csv(D/'REGIONAL_ERROR_SOURCE.csv');critical=critical[critical.source_id.str[:3].isin(['G07','X10','X23'])&critical.model.isin(['N2','N3'])];cp=critical.groupby(['source_id','model','condition','region'])[['MAE_MPa','bias_MPa','SSE_share']].mean().reset_index()
write('CRITICAL_SOURCE_ERROR_DIAGNOSTICS.md','# Critical-source retrospective error diagnostics\n\n'+intro+'The following are means of separately scored seeds; the original seed rows remain in REGIONAL_ERROR_SOURCE.csv and CRITICAL_SOURCE_SIGNED_ERROR_REGIONS.csv. These diagnostics identify numerical patterns without a causal physical-defect explanation. Actual maps preserve both seeds and FULL/X43; the R2 historical atlas retains all contexts.\n\n'+table(cp,['source_id','model','condition','region','MAE_MPa','bias_MPa','SSE_share'])+'\n\nG07 remains a difficult source and its N3 height-region weighted SSE is among the largest retained values. X10 shows substantially stronger parent underprediction and height overprediction under N3; X23 shares parent underprediction but has different collar and maximum-amplitude behavior. Core-edge error enrichment does not demonstrate FE-boundary causation. See BOUNDARY_ERROR_STRATA_SOURCE.csv for all five distinct nonexclusive strata and original owning observation edges. No measured toe/crack location is asserted.')
write('R2_1_EDITORIAL_RISK_ASSESSMENT.md','''# Final editorial risks

The manuscript must distinguish rank-budget overlap from common-reference-threshold amplitude classification. The latter uses held-out FE thresholds and is diagnostic only. Strong 5% results must not conceal weak or seed-dependent 1% results or adverse plates. G1 is one fixed geometry-only rule; its poor outcome does not make Point Transformer architecture indispensable. G0's broad-area recall must remain tied to its area cost. Restricted geometry baselines and historically unavailable B0/B1 restricted fields must stay unavailable.

The cohort is reused, small and grouped by documentary plates, not certified independent production batches. No point-count confidence intervals or significance claims are justified. Processed front metrology, assumed rear, material, thickness and loading remain model inputs; numerical qualification is not experimental toe/radius/stress validation. Undefined precision/centroid values must retain denominators. Main-text conclusions and abstract must include threshold/seed/region dependence. Public deposition and target-journal formatting are separate author responsibilities; author-review readiness does not guarantee acceptance.
''')
# Preserve replaced figures and earlier detailed evidence without modifying old workspaces.
for folder,sourcefolder in [('legacy_R2',P/'figures'/'supplementary'),('legacy_R1',P/'source_snapshot'/'R1'/'figures'/'supplementary')]:
 out=D/'figures'/'supplementary'/folder;out.mkdir(parents=True,exist_ok=True)
 for f in sourcefolder.glob('*'):
  if f.is_file():shutil.copy2(f,out/f.name)
for stem in ['Fig06_Localization_and_amplitude','Fig07_Seeds_and_plate_variability','Fig09_Plate_localization_contrasts']:
 for ext in ['png','pdf']:shutil.copy2(P/'figures'/'main'/(stem+'.'+ext),D/'figures'/'supplementary'/('R2_'+stem+'.'+ext))
# Retain R2 text, revise only interpretation and add the bounded assessment.
paper=(P/'MANUSCRIPT_REVISION_R2.md').read_text(encoding='utf-8');paper=paper.replace('The evidence supports a mixed accuracy–localization outcome, not universal model superiority.','Retrospective 1%, 5% and 10% area budgets reveal seed- and plate-dependent localization; applying a common FE-derived 99th-percentile threshold reverses the N3/N2 comparison in every context. Under full geometry, N3 exceeds one fixed transition-distance ranking at all budgets, while regional errors expose competing collar and parent behavior. The evidence supports a mixed accuracy–localization outcome, not universal model superiority.')
anchor='## 2 Experimental geometry and numerical reference';paper=paper.replace(anchor,'A useful spatial predictor should also be compared with simple geometry-only transition identification. Concentration of numerical high area within a broad collar does not show whether learned predictions add information beyond that mask, and relative percentile ranking does not establish absolute stress-threshold accuracy. A bounded retrospective assessment addresses these questions on the unchanged released fields, without training or selecting a new model.\n\n'+anchor)
methods='''### 4.2 Supplementary Retrospective Robustness Assessments

After R2 closure, a separate retrospective protocol was sealed before new metrics were examined. It retains all original sources, five documentary groups, two neural seeds and FULL/X50/X43 saved predictions. Rank-budget masks select the upper 1%, 5% and 10% of original T0 area. Scores are ordered descending, exact ties by increasing original ID; the cumulative-area prefix closest to the requested quota is chosen, including the crossing vertex if equally close. Achieved areas are reported because vertices carry finite area. Original own-field interpolated-CDF High95 remains an unchanged separate control. Constant-field budget masks use arbitrary ID ties and are not informative stress rankings.

A separate common-threshold diagnostic derives each 99th, 95th or 90th percentile in MPa from the frozen FE reference and applies that same threshold to reference and prediction. This tests amplitude-sensitive classification, not matched area. Held-out FE thresholds are unavailable operationally, so all such results are diagnostic only. Empty predicted sets have undefined precision and centroid, zero recall and IoU against a nonempty reference; valid-source/plate counts remain explicit. No physical allowable stress is introduced.

G0 marks the original broad collar without changing its 0.5 mm height and 2 mm XY rules. G1 scores negative exact XY distance to the piecewise-linear 0.5 mm parent-normal-relief contour on original triangles. Edge intersections are linearly interpolated, every connected component is retained, and the same rank-area budgets are applied. No stress magnitude, error or reference mask enters score construction, and no score or contour parameter is tuned. Both geometry rules are evaluated under FULL only: their original parent plane/labels depend on the complete source, and no qualified visible-only replacement rule exists. Restricted comparator rows are explicitly unavailable, rather than given hidden full-source information. G0 has unequal area; neither geometry rule predicts MPa or receives L2.

Regional MAE, RMSE, signed bias, absolute-error Q95, reference statistics and weighted squared/absolute-error shares use the unchanged parent/collar/height labels. Regional normalized L2 is undefined if reference RMS is at most 1e−6 MPa. Nonexclusive 1 mm strata distinguish core X/Y edges, native loaded caps, three-dimensional gauge proximity and each query's owning observation X edges. These are descriptive associations, not causal boundary interventions. Metrics are computed per source, averaged within plate, equally across plates for each seed, then across separately scored seeds. Undefined metrics retain valid counts. A separate implementation checks masks, thresholds, contour scores, weighted errors and aggregation. All new diagnostics are retrospective exploratory analyses on a repeatedly examined cohort, not newly independent validation.

'''
paper=paper.replace('## 5 Results',methods+'## 5 Results')
figreg=json.loads((D/'R2_1_FIGURE_REGISTRY.json').read_text());newcaps={6:figreg[0]['caption'],7:next(r['caption'] for r in figreg if 'Fig07_' in r['path']),9:next(r['caption'] for r in figreg if 'Fig09_' in r['path'])}
for n,oldname,newname in [(6,'Fig06_Localization_and_amplitude','Fig06_Threshold_robustness'),(7,'Fig07_Seeds_and_plate_variability','Fig07_Regional_errors'),(9,'Fig09_Plate_localization_contrasts','Fig09_Geometry_comparator')]:
 paper=paper.replace(oldname+'.png',newname+'.png');paper=re.sub(r'^Figure '+str(n)+r'\..+$','Figure '+str(n)+'. '+newcaps[n],paper,flags=re.M)
paper=paper.replace('Table 2 defines the sign of each contrast explicitly; Figure 6 shows overlap, missed area and peak-amplitude error together.','Table 2 defines the sign of each historical contrast explicitly; the preserved R2 supplementary figure shows overlap, missed area and peak-amplitude error together. Figure 6 extends the assessment to alternative area budgets and common reference thresholds, interpreted in Section 5.7.')
paper=paper.replace('Table 3 retains the complete two-seed neural comparison and Figure 7 displays seed and plate variability.','Table 3 retains the complete two-seed neural comparison, and the preserved R2 supplementary figure displays historical seed and plate variability. Figure 7 provides the retrospective regional MAE comparison discussed in Section 5.7.')
paper=paper.replace('Table 5 includes all plate/context contrasts and Figure 9 retains both seeds.','Table 5 includes all historical plate/context contrasts; both seeds remain in the supporting contrast tables and preserved R2 supplementary figure. Figure 9 adds the FULL geometry-only comparator.')
paper=paper.replace('Figure 9 exposes both this aggregate trade-off and the adverse X-plate exception.','Table 5 and the retained R2 supplementary contrast figure expose the adverse X-plate exception. Figure 9 addresses the separate FULL geometry-comparator question.')
t6='| Context | Area (%) | N1 rank IoU | N2 rank IoU | N3 rank IoU | Common ΔN3−N2 |\n| --- | --- | --- | --- | --- | --- |\n'
for r in ct.itertuples():t6+=f'| {r.condition} | {r.budget*100:g} | {r.N1_rank_IoU:.4f} | {r.N2_rank_IoU:.4f} | {r.N3_rank_IoU:.4f} | {r.common_delta_N3_N2:+.4f} |\n'
t7='| Area (%) | G1 rank IoU | N2 rank IoU | N3 rank IoU | G0 unequal IoU |\n| --- | --- | --- | --- | --- |\n'
for b in [.01,.05,.10]:
 z=ct[(ct.condition=='FULL')&(ct.budget==b)].iloc[0];t7+=f'| {b*100:g} | {g1[g1.budget==b].iloc[0].IoU:.4f} | {z.N2_rank_IoU:.4f} | {z.N3_rank_IoU:.4f} | {g0[g0.budget==b].iloc[0].IoU:.4f} |\n'
results='''### 5.7 Engineering Robustness and Geometry-Only Localization Baselines

Table 6 and Figure 6 show positive mean N3-minus-N2 rank IoU contrasts in all nine context/budget cells, but this does not establish uniform robustness. At 1%, FULL improves by only 0.000702; its seed contrasts are +0.036345 and −0.034941, with negative second-seed contrasts also under both restricted contexts. At 10%, mean gains shrink to 0.0054–0.0211; the second-seed X43 contrast is −0.001514. At plate level, E/G are adverse at 1% in every context, and E plus restricted C are adverse at 10%. The 5% historical and area-budget findings agree closely: neural source IoU differs by at most 0.0009012 and macro IoU by less than 0.00015. Finite-area quota deviations are at most 0.001835 percentage points for nonconstant scores.

Table 6. Retrospective equal-plate, separately scored two-seed IoU at fixed area levels. Rank masks use separately matched area budgets. The final column instead applies the common FE-derived numerical threshold and reports its N3-minus-N2 contrast; it is diagnostic only and does not have matched predicted area.

'''+t6+'''
The common 99th-percentile threshold reverses the N3/N2 result in all contexts and both seeds: mean IoU contrasts are −0.06607, −0.05010 and −0.03894 for FULL/X50/X43. FULL N3 high-area coverage is only 0.1945% of the core, with recall 0.03994 against the approximately 1% reference set. Common 95th-percentile contrasts instead favor N3 on every mean plate, including X. X therefore remains adverse at 5% rank, but becomes favorable at 10% rank and at the common 95th-percentile threshold. Its restricted 1% rank contrast also becomes positive. These definition-dependent changes prohibit a general statement that X always deteriorates or that relative localization guarantees amplitude accuracy.

G0's broad collar covers 9.5632% of core area on average, ranging from 5.3699% to 11.2712% across sources. It captures 98.7110%, 87.3770% and 66.1879% of the 1%, 5% and 10% reference sets, respectively. At 5%, precision is 0.487918 and IoU 0.461345; high recall is purchased with unequal area. The original High95 capture differs slightly from this rank-budget control and remains unchanged in R2.

Table 7 and Figure 9 show that the single sealed G1 distance ranking is substantially weaker than the learned FULL fields. All thirteen contours are feasible with two components each, and no component is selected by stress. N3 exceeds G1 in all 78 source/seed/budget comparisons and all fifteen plate/budget means. This establishes added numerical localization information over this specific FULL geometry rule. It does not establish neural necessity, superiority to all geometric methods, or a fair partial-view comparison. G1's weak 1% result also shows that the broad collar association cannot be replaced by assuming exact correspondence to its height-contour edge.

Table 7. FULL-only retrospective comparator. G1, N2 and N3 have matched area budgets. G0 retains its entire broad collar at every reference level and therefore has unequal area. Both neural seeds and all five plates are included.

'''+t7+'''
Regional errors in Figure 7 separate local error magnitude from total contributions. The height proxy occupies 80.96% of core area and has the largest macro squared-error share in every neural model/context; this need not mean it has the largest regional MAE. For N3 its height share is 46.72–52.93%, while parent share is 24.57–29.09%. Under FULL, N3 collar MAE improves from 19.1885 to 17.3934 MPa in aggregate and improves on all five mean plates, but parent MAE worsens from 17.7284 to 20.6722 MPa and height MAE from 7.3068 to 7.8045 MPa. Collar MAE worsens slightly at X50 and improves slightly at X43. No region improves across every plate/context combination.

X10 and X23 illustrate that worse top-area overlap can coexist with improved collar MAE. N3 has stronger parent underprediction and source-dependent height/collar behavior; FULL parent biases are −22.7763 and −19.5558 MPa, respectively. Within 1 mm of critical-source core X edges, about 5.4–5.8% of area contributes roughly 10–12% of N3 squared error, still a minority. No evaluated query is within 1 mm of a native loaded cap, gauge or its owning observation X edge. Those boundaries remain distinct from the scoring core and geometric collar. The observed error redistribution does not establish boundary causation or a physical defect mechanism. Complete source/plate/seed grids and critical-source masks are supplementary.

'''
paper=paper.replace('## 6 Discussion',results+'## 6 Discussion')
paper=paper.replace('### 6.4 Scope of reproducibility and uncertainty','''The bounded robustness assessment narrows practical interpretation further. A learned field can improve relative top-5% overlap while underestimating the extreme FE-threshold class, and while increasing errors in the parent region. Neither one percentile nor one regional MAE is a complete engineering utility criterion. The simple G1 rule performs worse under matched FULL budgets, supporting additional numerical localization information beyond proximity to that fixed transition contour. Its poor performance does not establish that every useful geometric rule requires a neural architecture. G0 already identifies a broad informative region at a larger area cost. No visible-only geometric baseline is established for the restricted contexts.

The representation/context sensitivity result remains intact, but independent utility is not universal across plates, thresholds or amplitudes. Post-development geometry and threshold diagnostics strengthen traceability rather than create new independent observations. The small reused cohort and the assumed mechanical problem still limit generalization and physical interpretation.

### 6.4 Scope of reproducibility and uncertainty''')
paper=paper.replace('## 8 Conclusions','Retrospective threshold selection was fixed at 1%, 5% and 10% before metric inspection. Nevertheless these are exploratory post-development diagnostics. The full-source parent-plane dependency prevents a fair restricted-view geometry comparator here. A weak single distance rule cannot establish neural necessity, and undefined empty-mask precision must not be treated as zero error.\n\n## 8 Conclusions')
paper=paper.replace('## Data availability','''The final retrospective assessment finds that mean rank gains are threshold-, seed- and plate-dependent; common extreme FE thresholds can reverse N3's apparent advantage. Under FULL, N3 adds numerical localization information over the one fixed area-matched geometric transition ranking, while regional errors expose competing improvements and deterioration. These findings qualify practical utility without rewriting METHOD_IMPROVEMENT_MIXED. The current manuscript research program is closed after this bounded assessment; no further model development or independent validation is asserted.

## Data availability''')
paper=paper.replace('Both high-area misses and false positives increase in X across contexts and seeds,','Under the historical High95 definition, both high-area misses and false positives increase in X across contexts and seeds,')
write('MANUSCRIPT_FINAL_R2_1.md',paper)
for name in ['build_docx.py','render_docx_word.py']:
 s=(P/'src'/name).read_text(encoding='utf-8').replace('WeldStressAI_ManuscriptRevision_R2','WeldStressAI_ManuscriptRobustness_R2_1').replace('MANUSCRIPT_REVISION_R2','MANUSCRIPT_FINAL_R2_1').replace('manuscript revision R2','manuscript revision R2.1')
 (D/'src'/name).write_text(s,encoding='utf-8')
captions=re.findall(r'^Figure \d+\..+$',paper,re.M)
write('FINAL_FIGURE_CAPTIONS.md','# Final figure captions\n\n'+'\n\n'.join(captions)+'\n\n## New supplementary figures\n\n'+'\n\n'.join(r['path']+'\n\n'+r['caption'] for r in figreg if 'supplementary' in r['path']))
write('MAIN_FIGURE_SELECTION.md','''# Final main figure selection

Nine main figures are retained. Figures 1–5 and 8 preserve the verified R2 geometry/reference, FE qualification, executed network, field comparison, factorial effects and actual geometry association. Figures 6, 7 and 9 replace redundant historical presentations with threshold robustness, all-plate regional MAE and the FULL geometry comparator. Their complete historical versions are retained as R2-prefixed supplementary PNG/PDF files. No difficult plate, source or seed is dropped.

New supplementary Figure A retains all plates, contexts, budgets and both seeds for N1/N2/N3. Figure B supplies G07/X10/X23 FULL reference/G0/G1/N2/N3 masks at all budgets and both seeds (six figure pairs). Figure D supplies X10/X23 FE/N2/N3 fields, centered errors and rank/collar masks under FULL/X43 and both seeds (eight pairs). Historical R1 and R2 supplementary figures are preserved in legacy subdirectories. Direct field comparisons share stress limits; errors are zero-centered. No physical toe curve is invented.
''')
write('SUPPLEMENTARY_MATERIAL_PLAN.md','''# Final supplementary material

Root CSVs retain all source, plate, seed, budget, common-threshold, achieved-area/tie, geometry, regional and boundary outcomes. Undefined precision/centroid fields retain valid group counts. Unavailable restricted geometry cases are explicit, rather than omitted or filled with hidden full-source scores. The 299-field analysis registry and sealed 644-input registry locate original immutable arrays and provenance.

New figure pairs: one all-plate threshold grid, six FULL geometry-mask comparisons and eight critical-source field/error/mask atlases, plus three revised main figures. Previous main figures moved to supplementary, and historical R1/R2 supplementary artwork is preserved under legacy directories. All additional results are retrospective exploratory; no neural/FE execution or new target is performed. Native meshes, checkpoints and large fields remain in their recorded immutable original workspaces; the editorial archive does not claim to be a self-contained research installation or public persistent deposition.
''')
write('MANUSCRIPT_CHANGELOG.md','''# Final R2.1 manuscript changes

Retained title, sixteen verified references, original R2 numerical results and scientific limitations. Added motivation for utility beyond broad transition identification and a sealed retrospective-methods subsection. Added Engineering Robustness and Geometry-Only Localization Baselines with complete macro threshold/comparator tables, adverse common-extreme-threshold results, seed/plate heterogeneity, unavailable partial-view geometry comparisons and regional redistribution. Replaced three main figures while retaining nine total and preserving old figures in supplementary material. Abstract, discussion, limitations and conclusions explicitly qualify practical utility and close the program. Original METHOD_IMPROVEMENT_MIXED is unchanged.
''')
print('MANUSCRIPT_AND_FOCUSED_REPORTS_WRITTEN',len(paper.split()),'words',flush=True)
