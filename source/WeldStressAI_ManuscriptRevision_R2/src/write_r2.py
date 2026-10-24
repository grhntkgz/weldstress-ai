"""Editorial synthesis of immutable numerical evidence; no model execution."""
from pathlib import Path
import pandas as pd,numpy as np,json,re,shutil,hashlib
D=Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRevision_R2');P=D.parent/'WeldStressAI_ManuscriptRevision_R1';R=D.parent/'WeldStressAI_FinalResearch_PhaseR8E16'
plate=pd.read_csv(D/'R2_PLATE_HIGH95_COMPARISON.csv');source=pd.read_csv(D/'R2_SOURCE_HIGH95_COMPARISON.csv');seed=pd.read_csv(D/'PLATE_SEED_PAIRED_CONTRASTS.csv');sp=pd.read_csv(D/'R2_GEOMETRY_STRESS_SPATIAL_AUDIT.csv');fields=pd.read_csv(D/'SEED_SPECIFIC_LOCALIZATION_RESULTS.csv')
def write(name,s): (D/name).write_text(s.strip()+'\n',encoding='utf-8')
def md(frame,cols):
 z=frame[cols].copy()
 for c in z:
  if pd.api.types.is_float_dtype(z[c]):z[c]=z[c].map(lambda v:f'{v:.8f}')
 return '| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in z.itertuples(index=False,name=None))
px=plate[plate.plate=='X'];sx=source[source.plate=='X'];xs=seed[seed.plate=='X'];crit=sp[sp.source_id.str[:3].isin(['G07','X10','X23'])]
intro='This is a retrospective descriptive audit of frozen R8-E16 outputs. No new FE solve, meshing, target calculation, model fitting or inference was performed. All contexts, both seeds, all thirteen sources and five documentary plates are retained. It is not preregistered independent validation.\n\n'
xtext='# X plate N2 versus N3 diagnostic\n\n'+intro+'''The adverse X-plate result is reproduced in all three contexts and both separately scored seeds. The X43 two-seed mean IoU contrast is −0.0922588286212. C, E, G and H have positive mean contrasts in each context; X alone has negative mean contrasts in each context. This statement concerns the released cohort and does not establish a population effect.

## Two-seed means

'''+md(px,['condition','high95_IoU_N2','high95_IoU_N3','delta_high95_IoU','L2_N2','L2_N3','delta_false_negative_area_mm2','delta_false_positive_area_mm2'])+'\n\n## Separate seeds\n\n'+md(xs,['seed','condition','delta_high95_IoU','delta_L2','delta_false_negative_area_mm2','delta_false_positive_area_mm2'])+'\n\n## Source contributions\n\n'+md(sx,['source_id','condition','delta_high95_IoU','delta_false_negative_area_mm2','delta_false_positive_area_mm2','delta_absolute_max_error_MPa','delta_absolute_Q95_error_MPa'])+'''

Both X10 and X23 contribute materially. X10 has the larger IoU loss under FULL; X23 is marginally larger under X50 and larger under X43 (−0.09773421 versus −0.08678345). Thus X23 contributes about 53% of the X43 mean loss under equal source weights, not a universal dominance across contexts. Neither source was excluded. At the finer source/seed/context level, eleven of twelve contrasts are adverse; X23/FULL/seed 20261021 has a small favorable IoU contrast of approximately +0.00158. Plate-level consistency must not be misreported as universal source-level seed deterioration.

False-negative and false-positive areas both increase: under X43 the plate means rise by 3.27469382 and 3.27011193 mm², respectively. N3 misses more of the reference high set while also marking other regions high. Own-field percentile thresholds constrain each mask to roughly 5% area, making nearly balanced FN and FP changes unsurprising. This is not only an amplitude change, and no unique physical defect is identified.

Mask changes are spatially nonuniform. Under X43 the reference-to-predicted high-area centroid distance improves for X10 (1.88236 to 0.59020 mm) despite worse IoU, but worsens for X23 (5.89213 to 8.42571 mm). A single centroid cannot represent overlap of separated bands. Peak-amplitude error increases for X10 by 8.07845 MPa and decreases for X23 by 7.74976 MPa under X43. No uniform peak-bias or rigid-shift mechanism explains both sources. Signed-error maps and all own-threshold masks are supplied for every context and seed in the eighteen critical-source atlases.

Reference High95 is wholly in X10's existing collar proxy and 99.82784% in X23's collar proxy. These geometric associations do not establish measured weld-toe trajectories, a crack-initiation location or a physical explanation of the learner's error. The numerical reference itself incorporates assumed rear geometry and standardized loading. Physical defect causation and nonlocal boundary influence remain unresolved.
'''
write('R2_X_PLATE_DIAGNOSTIC.md',xtext);write('X_PLATE_N2_N3_COMPARISON.md',xtext)
toe='# Weld toe evidence classification\n\n'+intro+'''All thirteen sources support GEOMETRIC_PROXY_ASSOCIATION_ONLY. The overall decision is SPATIAL_ASSOCIATION_PARTIAL. Original processed XYZ, identifiers, triangles and T0 areas are documented measured geometry; this does not independently validate processed notch radii. Original IDs/XYZ/areas exactly match both the canonical target and qualified M2 package. Recomputed triangle-lumped areas agree within 1e−10 mm².

The original dataset contains averaged notch radius/angle descriptors, not XYZ toe curves registered to these numerical fields. The 56 retained documentary rows include repeats and are not 56 independent toe measurements. The historical Phase 5C algorithmic candidates cover C02, C03 and C19, with only C02 in this cohort; they lack expert confirmation and qualified mechanical-frame registration. Other historical trajectories and E13 pilot tracks cannot be transferred to these thirteen sources. No authenticated measured toe trajectory is available for G07, X10 or X23, or for the complete qualified cohort. No retrospective toe curve was invented from stress peaks.

The frozen geometry-only regions reproduce exactly with zero label mismatches: parent-normal relief at least 0.5 mm defines code 1; outside it, an XY distance at most 2 mm to a code-1 vertex defines code 2; all remaining vertices are code 0. They are height/collar/parent proxies, not independently measured weld toes. Parent-normal relief uses the existing fitted parent plane and its normal normalization.

The retrospective reference High95 area fractions are 64.92141–100% in the collar, 0–35.07859% in the parent proxy and 0% in the height-defined crown across all thirteen sources. This supports association with a broad existing transition proxy, not a precise physical toe, a geometric discontinuity, or a universal surface-gradient mechanism. X23's High95 mean slope is lower than its remainder mean; slope alone is not a sufficient general explanation.

SPATIAL_LABEL_EVIDENCE_REGISTRY.csv records DOCUMENTED_MEASURED_GEOMETRY, EXISTING_GEOMETRY_DERIVED_PROXY and NOT_AVAILABLE separately. No RETROSPECTIVE_GEOMETRIC_ESTIMATE trajectory was constructed. Documentary mean descriptors are explicitly distinct from spatial toe labels. R2_GEOMETRY_STRESS_SPATIAL_AUDIT.csv reports every source and REFERENCE_HIGH95_BY_EXISTING_REGION.csv every existing region.
'''
write('R2_WELD_TOE_EVIDENCE_CLASSIFICATION.md',toe)
bc='# Boundary condition interpretation\n\n'+intro+'''Canonical X is the numerical tensile direction. The measured full front spans approximately 60 mm in X and 28 mm in Y. Y is the retained longitudinal profile convention; independent raw-scan physical-frame calibration remains unresolved. The evaluation core is a numerical scoring subset, approximately 38 by 22 mm with 34,200 points, not a physical cut or traction boundary.

The existing native M2 records apply affine X tractions on the actual XMIN/XMAX end caps. Their force/moment construction uses the basis [1, Y−Yline, Z−Zline] and the historical common load line. Nominal stress is 100 MPa; each cap's axial resultant magnitude is 53,200 N for the 19 by 28 mm nominal section. Local traction is not necessarily uniformly 100 MPa. No new boundary formulation was introduced.

Six scalar gauge constraints act at three nodes on the left cap: left rear YMIN UX/UY/UZ, left rear YMAX UX/UZ, and left front YMIN UX. These are the documented rigid-body gauges, not a claimed experimental full-face clamp. All six DOFs and coordinates were checked against actual selected quadratic M2 mesh nodes for every source. All six nodes of each loaded quadratic face were used to verify its cap X position. The original mesh SHA-256 matches the released qualified registry. ACTUAL_NATIVE_MESH_BOUNDARIES.csv and copied BVP/port/gauge records provide the native provenance.

For G07 the actual caps are X=124.975 and 184.975 mm, with load-line Y=30 mm and Z=−9.7317923979 mm. Gauges occur at (124.975,16,−19.0155376856), (124.975,44,−18.9791606574) and (124.975,16,−0.05) mm. These rear/front gauge coordinates must not be confused with the plotted measured front alone.

## Critical-source distances

'''+md(crit,['source_id','high95_min_X_port_distance_mm','high95_min_gauge_distance_mm','high95_min_core_X_edge_distance_mm','high95_fraction_within_1mm_core_X_edge'])+'''

No accepted reference High95 area lies within 1 mm of the actual loaded X caps in any source. G07, X10 and X23 minimum cap distances are 12.4000, 11.0500 and 12.9000 mm. Thus the visible core bands do not directly coincide with loaded faces or gauge nodes. This geometric finding does not prove mechanical independence from those boundaries.

X10's reference High95 reaches the scoring core X edge, with 34.44284% of its high area within 1 mm of that edge. This is an evaluation-support limitation, not direct overlap with a physical loaded end. G07 and X23 have no high area within 1 mm of their core X edges. Every source's distances and area fractions are retained in the all-source spatial table.

Only one standardized frozen boundary-value family is available here. Nonlocal influence of affine traction, gauges, truncation and assumed rear completion cannot be separated causally from geometry with these records alone. No new boundary-sensitivity solve is authorized. The physical origin of the bands therefore remains unresolved. Neither “boundary artifact” nor “physically validated toe hotspot” is justified. The narrower supported conclusion is spatial association with the independently defined existing broad collar proxy.
'''
write('R2_BOUNDARY_CONDITION_INTERPRETATION.md',bc)
# Revise the existing paper; preserve all original numerical tables and verified references.
paper=(P/'MANUSCRIPT_REVISION_R1.md').read_text(encoding='utf-8')
paper=paper.replace('The evidence supports a mixed accuracy–localization outcome, not universal model superiority.','The aggregate localization gain is not uniform: X-plate High95 IoU decreases by 0.0190, 0.0785 and 0.0923 under FULL, X50 and X43, respectively, with adverse contrasts under both seeds. A retrospective geometry audit supports association with broad existing transition proxies, without registered measured toe trajectories or a resolved physical explanation. The evidence supports a mixed accuracy–localization outcome, not universal model superiority.')
anchor='## 2 Experimental geometry and numerical reference'
paper=paper.replace(anchor,'Actual available geometry, numerical feature representation and numerical stress are distinct information levels. Processed measured XYZ supplies observed surface evidence. The input construction transforms that geometry into coordinate, span, normal and context channels. The standardized FE problem supplies a derived stress field that the learner approximates; changing the second level does not change the original measured query coordinates or experimentally manipulate physical stress.\n\n'+anchor)
anchor='### 2.3 Target operator and numerical qualification'
paper=paper.replace(anchor,'''The full measured front spans approximately 60 mm along X and 28 mm along Y; Y follows the retained longitudinal profile convention. Affine end-cap X tractions satisfy the existing axial force and moment construction about the common load line. At nominal thickness 19 mm, each cap carries 53,200 N in magnitude; local traction can differ from 100 MPa. Six scalar rigid-body gauges act at three left-cap nodes: rear YMIN UX/UY/UZ, rear YMAX UX/UZ and front YMIN UX. Native M2 quadratic-face and gauge-node coordinates were retrospectively checked for all sources. These numerical constraints are not an experimental fixture reconstruction. The approximately 38 by 22 mm core is only an evaluation mask, not an FE load boundary. Figure 1 distinguishes the actual cap positions from that core.

'''+anchor)
anchor='## 5 Results'
paper=paper.replace(anchor,'''### 4.1 Retrospective editorial spatial audit

Revision R2 reads only frozen original fields and geometry. All 156 N2/N3 source–seed–context fields retain exact original point IDs, XYZ and areas; 1,560 source-metric cells reproduce the released results within 1e−9. Original triangle-lumped T0 areas and target-package correspondence were checked. Source metrics are averaged within plate, followed by equal-plate aggregation and the mean of separately scored seeds; no seed fields are ensembled. These are retrospective descriptive checks, not new independent validation experiments.

The existing geometry labels were reconstructed without using stress: parent-normal relief ≥0.5 mm defines the height proxy; other vertices within 2 mm in XY of a height-proxy vertex define the collar; the remainder defines parent. All original labels reproduce exactly. Area fractions of the unchanged reference High95 set and distances to actual cap/gauge locations describe associations only. Documentary mean toe descriptors and unreviewed historical candidate curves do not supply authenticated toe trajectories registered to this qualified cohort. No stress-derived toe marker was introduced.

'''+anchor)
start=paper.index('Figure 8 shows the retained G07 example');end=paper.index('## 6 Discussion',start)
tab='| Held-out plate | FULL ΔIoU | X50 ΔIoU | X43 ΔIoU |\n| --- | --- | --- | --- |\n'
for p in 'CEGHX':tab+='| '+p+' | '+' | '.join(f'{plate[(plate.plate==p)&(plate.condition==c)].iloc[0].delta_high95_IoU:+.4f}' for c in ['FULL','X50','X43'])+' |\n'
new='''### 5.5 Plate-Specific Hotspot Localization and Spatial Interpretation

N3's aggregate High95 gain does not extend to every documentary plate. Table 5 includes all plate/context contrasts and Figure 9 retains both seeds. C, E, G and H have positive two-seed means under all three conditions. X has negative contrasts: −0.01902766 for FULL, −0.07849776 for X50 and −0.09225883 for X43. Each X contrast remains negative under both seeds; the X43 seed-specific changes are −0.08265160 and −0.10186606. X whole-field L2 simultaneously increases from 0.1655 to 0.2064 for FULL and from 0.1541 to 0.2051 for X43.

Table 5. Complete plate-specific N3-minus-N2 High95 area-IoU contrasts. Sources are averaged within each plate and separately scored seed metrics are averaged. Positive values favor N3. These retrospective descriptive contrasts do not imply statistical independence of points.

'''+tab+'''
Both X sources contribute. Under X43, X10 and X23 IoU contrasts are −0.08678345 and −0.09773421; X23 contributes slightly more, whereas X10 contributes more under FULL. Eleven of twelve X source/seed/context contrasts are adverse; X23/FULL/20261021 instead improves slightly (+0.00158). For the X plate, false-negative and false-positive areas rise by 3.27469 and 3.27011 mm² under X43. N3 misses more reference high area and predicts other locations high. This is not a universal rigid displacement: X10's high-area centroid distance improves from 1.88236 to 0.59020 mm despite worse overlap, whereas X23's worsens from 5.89213 to 8.42571 mm. Absolute peak error increases by 8.07845 MPa for X10 but decreases by 7.74976 MPa for X23. A common physical-defect explanation is not established.

Figure 8 places the processed measured shapes and reference fields in the same canonical frame. Across all thirteen sources, 64.92–100% of reference High95 area lies in the existing 2 mm collar proxy, 0–35.08% in its parent complement, and none in the height-defined crown. The association is therefore with a broad geometry-only transition proxy. No authenticated measured toe trajectory registered to these fields is available, and the collar must not be renamed a physically validated weld toe. Local gradient association is source dependent; it does not identify one general mechanism.

![Figure 8](figures/main/Fig08_Geometry_stress_association.png)

Figure 8. Retrospective G07, X10 and X23 processed measured geometry and frozen numerical T2 reference on original canonical XY coordinates. Relief is parent-normal height in mm; reference stress is T2 in MPa, with High95 in magenta. Color limits are source-specific, so cross-source stress ranking should use tables. Blue solid/dotted contours delimit existing height/collar proxies, not measured toe curves. Red lines mark actual loaded X caps and black dashed rectangles mark scoring cores. These reference-only panels have no neural seed or observation restriction; stress is numerical, not experimental. Planar axes use equal physical scale, without relief exaggeration.

The actual reference High95 bands do not directly overlap loaded caps: minimum distances for G07, X10 and X23 are 12.4000, 11.0500 and 12.9000 mm. All thirteen sources have zero reference high area within 1 mm of a loaded cap. X10 nevertheless reaches the evaluation-core X edge, with 34.44% of its high area within 1 mm of that edge; this edge is not a physical FE boundary. A single frozen boundary-value family cannot separate nonlocal effects of loading, gauges, truncation or assumed rear geometry. Neither a boundary-artifact explanation nor physical toe-hotspot validation follows. The engineering classification is geometric-proxy association only, with the physical mechanism unresolved.

The supplementary critical-source atlas includes G07, X10 and X23 for every context and both seeds: actual 3D front geometry at physical aspect, an original transverse profile, existing proxy regions, FE reference, N2/N3 fields, signed errors and own-field High95 masks. Reference/prediction limits are shared within each comparison and errors use one zero-centered scale. All thirteen sources also have geometry/reference overlays and quantitative spatial records; the selected illustrations do not replace all-source evidence.

### 5.6 Joint interpretation

N3's 6.07–6.94% L2 increase fails the whole-field improvement requirement and its peak-amplitude deterioration fails the amplitude safeguard. Aggregate IoU improvement still exceeds the frozen meaningful-localization threshold. METHOD_IMPROVEMENT_MIXED therefore remains unchanged. Figure 9 exposes both this aggregate trade-off and the adverse X-plate exception. The classification is a descriptive computational result, not physical engineering acceptance.

![Figure 9](figures/main/Fig09_Plate_localization_contrasts.png)

Figure 9. Retrospective N3-minus-N2 contrasts on all thirteen processed measured fronts, grouped by all five documentary plates and FULL/X50/X43. Bars average source metrics within plate and separately scored seeds; circles/crosses denote seeds 20261021/20261022 and are not confidence intervals. IoU is dimensionless High95 area overlap; L2 is dimensionless whole-field error against numerical T2. Positive IoU favors N3, whereas positive L2 is unfavorable. No physical toe labels or experimental stress are depicted.

'''
paper=paper[:start]+new+paper[end:]
paper=paper.replace('### 6.4 Scope of reproducibility and uncertainty','''The X-group audit shows why aggregate localization cannot stand in for engineering transferability. Both high-area misses and false positives increase in X across contexts and seeds, while source-level peak and centroid behavior differ. The observed surface, its numerical feature encoding and its standardized numerical reference remain separate. Feature changes on identical XYZ can alter the learned ranking without identifying a changed physical notch or a true fatigue-critical location.

The broad collar association supplies limited geometric support, but no registered independent toe trajectory establishes exact physical correspondence. Actual cap coordinates exclude direct coincidence of the accepted high bands with end loading; they do not exclude nonlocal boundary influence. The assumed planar rear, affine loading and processed front jointly define the numerical problem. Future inspection-oriented use would require independently registered geometry, an appropriate mechanical reference and independent group evaluation. The present audit does not establish readiness for inspection acceptance or grinding decisions.

### 6.4 Scope of reproducibility and uncertainty''')
paper=paper.replace('Both seeds, all documentary plates and the difficult G and X results remain part of the evidence.','Both seeds, all documentary plates and the difficult G and X results remain part of the evidence. X High95 overlap deteriorates under every context and both seeds, including a two-seed X43 IoU contrast of −0.0923. Numerical high regions associate with existing broad collar proxies, but authenticated measured toe trajectories and a causal separation of geometry from nonlocal boundary influence remain unavailable.')
extra={1:' Actual 3D axis spans use physical aspect without vertical exaggeration; red cap lines and black core bounds are distinct. Reference only; seed and observation restriction are not applicable; no registered measured toe curve is shown.',2:' Cohort: all thirteen processed measured fronts; full-domain FE reference, without a neural seed. L2 and IoU are dimensionless; regions are geometric proxies, not measured toes.',3:' Schematic for all thirteen processed measured fronts and both neural seeds, applicable to FULL/X50/X43. Channels are numerical representations of measured geometry, not experimental stress or measured toe curves.',4:' Cohort: all thirteen processed measured fronts; neural seeds 20261021/20261022. L2 is dimensionless and MAE is MPa against numerical T2; no physical toe label is used.',5:' Cohort: all thirteen processed measured fronts, seeds 20261021/20261022, restricted X50/X43 contexts. Contrasts are dimensionless numerical metric changes; no physical toe marker is asserted.',6:' Cohort: all thirteen processed measured fronts, FULL/X50/X43 and both neural seeds. IoU is dimensionless, missed area is mm² and maximum-amplitude error is MPa against numerical T2; no measured toe trajectory is asserted.',7:' Cohort: all thirteen processed measured fronts. L2 is dimensionless error against numerical T2; no experimental stress or authenticated physical toe labels are shown.'}
for n,tail in extra.items():paper=re.sub(r'(^Figure '+str(n)+r'\..+)$',lambda m:m.group(0)+tail,paper,flags=re.M)
write('MANUSCRIPT_REVISION_R2.md',paper)
# Use the existing paper's visual and equation implementation.
for name in ['build_docx.py','render_docx_word.py']:
 text=(P/'src'/name).read_text(encoding='utf-8').replace('WeldStressAI_ManuscriptRevision_R1','WeldStressAI_ManuscriptRevision_R2').replace('MANUSCRIPT_REVISION_R1','MANUSCRIPT_REVISION_R2').replace('manuscript revision R1','manuscript revision R2')
 (D/'src'/name).write_text(text,encoding='utf-8')
# Ledger: retain original claims and append every numeric cell of new comparison/spatial evidence.
ledger=pd.read_csv(P/'CLAIM_EVIDENCE_AUDIT.csv',keep_default_na=False).to_dict('records')
for fname,keys in [('R2_PLATE_HIGH95_COMPARISON.csv',['plate','condition']),('R2_SOURCE_HIGH95_COMPARISON.csv',['source_id','condition']),('PLATE_SEED_PAIRED_CONTRASTS.csv',['seed','plate','condition']),('R2_GEOMETRY_STRESS_SPATIAL_AUDIT.csv',['source_id'])]:
 z=pd.read_csv(D/fname)
 for _,row in z.iterrows():
  for c in z.select_dtypes(include='number'):
   if c in keys:continue
   ledger.append(dict(claim_id=f'R2_{len(ledger)+1:05d}',claim=f'{c}: '+', '.join(str(row[k]) for k in keys),evidence_file=str(D/fname),row_key=';'.join(f'{k}={row[k]}' for k in keys),column=c,verified_value=row[c],unit='as explicitly named in CSV column',derivation='Retrospective frozen-output recomputation; original field metric replay within 1e-9',manuscript_location='Section 5.5 and associated technical reports/tables',evidence_level='RETROSPECTIVE_NUMERICAL_DESCRIPTION',status='PASS'))
pd.DataFrame(ledger).to_csv(D/'R2_CLAIM_EVIDENCE_MATRIX.csv',index=False)
write('R2_MANUSCRIPT_CHANGELOG.md','''# Revision R2 changelog

The title, sixteen verified references, frozen research decision, original model comparisons, both seeds, all sources and evaluation definitions are retained. Abstract and conclusions now explicitly disclose adverse X localization. Methods distinguish native end caps from the scoring core and document the retrospective existing-data audit. Results add the required Plate-Specific Hotspot Localization and Spatial Interpretation subsection, complete plate IoU table, both X sources and seed contrasts, mask/amplitude diagnostics and physical-interpretation limits. Discussion separates observed geometry, feature encoding and numerical stress.

Nine main figures are retained. Figures 1, 8 and 9 are revised/replaced to establish physical aspect, actual geometry/reference association and all-plate localization contrasts. Figures 2–7 are inherited unchanged. Thirty-one supplementary figure pairs document all thirteen geometries and eighteen critical-source/context/seed atlases. Original R1 figures remain preserved in source_snapshot/R1. All new spatial/aggregate diagnostics are retrospective; no new research results were generated by fitting, inference or FE execution.
''')
write('R2_SUPPLEMENTARY_MATERIAL_PLAN.md','''# Supplementary evidence supplied with R2

All thirteen sources have geometry/reference/region overlays (thirteen PNG/PDF pairs). G07, X10 and X23 each have FULL/X50/X43 × both seeds comparison atlases (eighteen PNG/PDF pairs), with actual coordinates, physical 3D aspect, matched T2 limits, centered error scales and original High95 masks. R2_SPATIAL_FIGURE_REGISTRY.json records exact identities and captions.

Source, plate, seed, mask-hash, region and native-boundary CSV tables are included at the root. Documentary mean toe descriptors, metadata provenance and historical unreviewed candidates are supplied under source_snapshot. They are not qualified physical toe curves. R1's unchanged supplementary figures and literature verification records are preserved in source_snapshot/R1. Native research binaries remain in the immutable research workspaces; the manuscript archive does not duplicate them. Absolute provenance paths and SHA-256 checks locate those original artifacts. Public persistent deposition remains author work and is not asserted here.
''')
print('MANUSCRIPT_WORDS',len(paper.split()),'CLAIM_ROWS',len(ledger),flush=True)
