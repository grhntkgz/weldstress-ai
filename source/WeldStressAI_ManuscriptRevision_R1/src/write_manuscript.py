from pathlib import Path
import json,re
import pandas as pd
D=Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRevision_R1');S=D/'source_snapshot'
means=pd.read_csv(D/'MAIN_MODEL_METRICS.csv');seeds=pd.read_csv(D/'BOTH_SEED_METRICS.csv');plates=pd.read_csv(D/'ALL_PLATE_METRICS.csv');refs=json.loads((D/'literature'/'VERIFIED_REFERENCE_RECORDS.json').read_text(encoding='utf-8'));figs=json.loads((D/'figures'/'MAIN_FIGURE_REGISTRY.json').read_text());effects=pd.read_csv(S/'04_feature_mechanisms/EQUAL_PLATE_EFFECTS.csv');factor=pd.read_csv(S/'04_feature_mechanisms/FACTORIAL_METRIC_MEANS.csv');changes=pd.read_csv(S/'17_model_comparisons/PRIMARY_CONTRASTS.csv')
def mdtable(frame,cols,headers=None):
 rows=['| '+' | '.join(headers or cols)+' |','| '+' | '.join(['---']*len(cols))+' |']
 for _,r in frame.iterrows():
  values=[]
  for c in cols:
   x=r[c];values.append(f'{x:.4f}' if isinstance(x,(int,float)) else str(x))
  rows.append('| '+' | '.join(values)+' |')
 return '\n'.join(rows)
def fig(n):
 r=figs[n-1];return f"![Figure {n}]({r['path']})\n\nFigure {n}. {r['caption']}"
def refentry(r):
 vi=str(r.get('volume') or '');issue=str(r.get('issue') or '');pages=str(r.get('pages') or '')
 return f"{r['reference_id']}. {r['authors'].replace(';', ',')}. ({r['year']}). {r['title']}. {r['venue']} {vi}{'('+issue+')' if issue else ''}{', '+pages if pages else ''}. https://doi.org/{r['doi']}."
references='\n\n'.join(refentry(r) for r in refs)
table1=mdtable(means,['model','condition','L2','MAE_MPa','high95_IoU'],['Model','Observation','L2','MAE (MPa)','High95 IoU'])
table2=mdtable(changes.assign(L2_increase_percent=-changes.L2_reduction_percent),['condition','L2_increase_percent','IoU_difference','FN_area_change_percent','absolute_peak_error_change_percent','absolute_Q95_error_change_percent'],['Observation','L2 change (%)','IoU change','FN area change (%)','Peak error change (%)','Q95 error change (%)'])
table3=mdtable(seeds[seeds.model.isin(['N1','N2','N3'])].assign(seed=lambda z:z.seed.astype(int).astype(str)),['model','seed','condition','L2','MAE_MPa','high95_IoU'],['Model','Seed','Observation','L2','MAE (MPa)','High95 IoU'])
table4=mdtable(plates,['plate','N2_FULL','N3_FULL','N2_X43','N3_X43'],['Held-out plate','N2 FULL L2','N3 FULL L2','N2 X43 L2','N3 X43 L2'])
amplitudes=mdtable(means,['model','condition','false_negative_area_mm2','absolute_max_error_MPa','absolute_Q95_error_MPa'],['Model','Observation','FN area (mm²)','Absolute peak error (MPa)','Absolute Q95 error (MPa)'])
abstract='''Learning stress concentrations from scanned welds requires geometric representations that remain meaningful as the observed surface changes. We investigated how representation and observation context influence field accuracy, prediction stability and high-stress localization using thirteen processed weld-front geometries grouped by five documentary parent plates. References were area-regularized tensile maximum-principal-stress fields from previously qualified quadratic-tetrahedral finite element models with an assumed planar rear and standardized elastic loading. An eight-cell frozen-weight intervention separated coordinate-centering, span and normal-statistic blocks. A visible-local-geometry representation was subsequently assessed with the unchanged compact SurfacePT architecture, two fixed training seeds, leave-one-plate-out evaluation and a fixed XGBoost comparator. All conditions retained identical original evaluation points. For full observation, equal-plate normalized L2 was 0.1391 for the original neural model, 0.1740 for context-mixed training, 0.1849 for the visible-local representation and 0.2570 for XGBoost. Relative to context-mixed training, the visible-local representation increased L2 by 6.07–6.94% across observation conditions but increased High95 area intersection-over-union by 0.0532–0.0625 and reduced missed high-area by 14.12–16.40%. Field-maximum amplitude errors increased despite these localization gains. Full-information feature substitution substantially restored the original model's restricted-observation accuracy, identifying computational representation sensitivity without establishing a deployable oracle. The evidence supports a mixed accuracy–localization outcome, not universal model superiority. Repeated examination of the small cohort limits generalization claims, and the numerical targets do not establish experimental stress accuracy or fatigue life.'''
text=f'''# Geometry representation and observation context in learning stress fields from scanned welded joints

## Abstract

{abstract}

Keywords: scanned weld geometry; finite element reference; point-cloud learning; observation context; stress localization; plate-grouped evaluation.

## 1 Introduction

Measured weld surfaces contain reinforcement, misalignment and spatially varying transitions that influence local elastic stress. A learning system intended to use these surfaces must contend with two distinct uncertainties: the relationship between the reconstructed numerical model and the physical joint, and the relationship between its geometric inputs and its numerical predictions. Reducing surrogate error addresses the latter. It cannot, by itself, resolve incomplete surface measurement, uncertain reconstruction or differences between a standardized loading problem and an experimental fixture. This distinction is central when evaluating models intended to identify regions of elevated stress.

The geometry–mechanics connection is already well established in weld research. Ottersböck et al. [2] examined measured butt-weld topography and undercuts using local geometric characterization and numerical stress analysis. Hultgren et al. [3] considered scanning resolution in reconstructed weld models and fatigue assessment. Their work makes scan processing and resolution part of the engineering evidence, rather than neutral steps preceding analysis. Dänekas et al. [8] further show that toe-parameter extraction depends on point spacing, noise and the underlying profile. These findings motivate preserving the exact processed geometry and qualifying a defined numerical target before evaluating a surrogate. They do not validate the physical notch radii of the present reconstructions.

Machine learning of weld stress concentration also predates this study. Braun et al. [4] trained neural stress-concentration estimates from parametric FE analyses and applied them along measured butt-weld seams. Schubnell et al. [5] used profile-coordinate learning with FE-derived stress-concentration factors. Rohani Raftar et al. [6] combined digitized fillet-weld geometry, numerical sectional stresses and bagged trees. Consequently, neither learning from weld geometry nor combining scans, FE and machine learning constitutes the novelty claimed here. The present question concerns dense surface predictions and how their representation changes when the available observation window changes.

Adjacent computational-mechanics research demonstrates that learned stress fields are not restricted to welds. Nie et al. [9] predict two-dimensional elastic von Mises fields from geometry, loads and boundary conditions with convolutional networks. Park and Kang [10] combine point-set geometry encoding and operator learning for three-dimensional displacement and stress fields under variable loads. These are precedents for field surrogates, not direct benchmarks for this dataset: geometries, governing assumptions, stress quantities and evaluation designs differ. PointNet [11] and Point Transformer [12] provide relevant point-set architectures, but neither their original recognition results nor their names establish reliability of an engineering stress predictor.

For measured surfaces, a further issue arises before changing the model architecture. Cropping a scan can change the centroid, coordinate spans and normal statistics used to encode a point that is itself unchanged. A prediction difference can therefore reflect both unavailable geometry and altered numerical representation. Contextual pooling creates another dependency because a different visible surface produces a different encoded context even when local features remain nearly constant. Testing these effects requires identical evaluation support and explicit information contracts; a random split of surface points would not provide specimen-level evidence.

We ask: how do geometric feature representation and observation-context variation influence the accuracy, robustness and high-stress localization of machine-learning surrogates trained on three-dimensional scanned welded joints? Three connected analyses address this question. A fixed-weight factorial intervention probes global feature dependencies. A local representation tests whether removing reliance on unseen global statistics produces useful predictions. A fixed nonlinear tree comparator separates the observed neural result from the assumption that nonlinear local regression must perform similarly. Whole-field accuracy, same-point prediction stability and high-stress localization are evaluated separately, with both seeds and every documentary plate retained. This is a final exploratory analysis on previously examined groups, not fresh independent generalization validation.

## 2 Experimental geometry and numerical reference

### 2.1 Provenance and observational support

The source is the public repository of Dänekas [1]. Its processed scans are spatially aligned and smoothed; they are not equivalent to independently registered raw metrology. Thirteen accepted as-welded source identities are C02, C05, C16, E21, G04, G07, G08, G16, G25, H12, H19, X10 and X23, each with the suffix V1-S355-AW. Documentary parent-plate identifiers define groups C, E, G, H and X, containing respectively three, one, five, two and two sources. These groups are not independently certified production batches, and scan-session independence remains unresolved. Historical development and exposed test identities were kept separate; the twelve exposed historical test groups and the external Aalborg sources were not used for new tuning in this study.

Original point identities, XYZ coordinates, canonical triangles and their T0 vertex areas remain fixed. Each source contributes the same 34,200 valid core queries under every observation condition. The FULL condition uses the complete processed front; X50 and X43 retain their frozen restricted windows and context rules. These names denote existing geometric protocols, not new cropped targets. Five geometric query tiles have fixed ownership under the primary S0 inference policy. Queries are not discarded merely because the visible context becomes smaller, and predictions from different tiles are not averaged under S0. Full window definitions and original IDs are retained in the supplementary provenance files.

Figure 1 pairs the retained measured front with the numerical quantity to be predicted. G07 is the historical illustrative source and is also a difficult source for N3; it was not chosen after revision to display a favorable outcome. All-source tables are necessary because an individual stress map cannot represent the behavior of the five groups.

{fig(1)}

### 2.2 Standardized elastic problem

The reference uses the processed measured front and an idealized planar rear, determined from the documentary nominal thickness and the frozen parent-surface plane rule. Synthetic rear geometry is not described as scanned material. Standardized tension acts along canonical X with nominal reference stress 100 MPa, consistent end-traction resultants and the historical common-midline loading convention. The retained rigid-body gauge constraints and force/moment checks qualify that numerical boundary-value problem; they do not reproduce or validate the original fatigue-test fixture. Isotropic linear elasticity assumes Young's modulus 210 GPa and Poisson's ratio 0.30. These are modelling assumptions rather than measured specimen properties.

Historical ANSYS models employ quadratic Tet10 SOLID187 elements at mesh levels M1 and M2. The fine numerical reference is designated QUALIFIED_FINE_M2_V1_T2. Tensor recovery, source mapping and equilibrium checks are retained with the qualified packages. No FE solve, remeshing or target modification was performed for this manuscript revision.

### 2.3 Target operator and numerical qualification

At an original surface vertex, tensile maximum principal stress is first calculated and clipped below at zero. The T2 value is its T0-area-weighted average over original vertices on the same face within a three-dimensional Euclidean chord distance of 1 mm. The radius tolerance is 0.0000001 mm, and complete-weight coverage must be at least 1 − 10⁻¹⁰. The principal-value operation precedes averaging. Thus T2 is neither a geodesic surface average nor a principal value recovered from a previously averaged tensor. The core excludes unsupported boundary queries.

For vertex i and accepted neighborhood N(i), define a_j as original T0 area and s_j as nonnegative maximum principal stress. The operator is

T2_i = Σ[j in N(i)] a_j s_j / Σ[j in N(i)] a_j. (1)

The prescribed M1/M2 criteria are normalized whole-field L2 ≤ 0.020, worst proxy-region L2 ≤ 0.030, High95 area IoU ≥ 0.800 and mapping coverage ≥ 0.990. Across the thirteen targets, whole-field L2 ranges from 0.0017210 to 0.0066990; the largest regional disagreement is 0.0103491 and the smallest High95 IoU is 0.953628. Figure 2 includes every source. This establishes consistency between the retained mesh levels for this operator, not asymptotic convergence or experimental validation.

T2 must also be distinguished from stress measures used in standardized fatigue assessment. Qi et al. [7] specifically compare structural-stress approaches for idealized and as-built scanned welds, while Hobbacher [15] provides the established fatigue-assessment framework. The present area/chord operator is a declared numerical regularization; it is not asserted to implement a standardized structural-hotspot or effective-notch-stress method. No fatigue strength is inferred from its maximum.

{fig(2)}

## 3 Geometry representation and learning methods

### 3.1 Executed neural implementation and historical comparators

All neural variants use the executed compact SurfacePT forward override: nineteen inputs, width 24, one multiscale block, three fixed sixteen-neighbor sets, a 4096-point contextual sample and 7228 trainable parameters. A shared encoder feeds local geometric attention and a mean-pooled encoded context branch; scale contributions use learned softmax weights. Per-query layer normalization is used. The actual override has no query-to-query pooling. Therefore changing a query batch does not create a different physical observation context, apart from possible floating-point ordering effects. Figure 3 documents this implementation. It is inspired by point attention [12] and is not an exact reproduction of the original full Point Transformer.

N1 was trained on FULL observation. N2 uses the same architecture with an equal-probability FULL/X50/X43 context mixture. Their historical nineteen-channel representation includes XYZ relative to the visible centroid, visible-domain coordinate spans, normals, load direction, a front tag, local relief, local normal variation, geometric incident area and visible-global normal statistics. Coordinate scaling is fixed at 60 mm. Z-span information occurs in more than one channel. Consequently, the representation depends on the extent of the observation even when the original query point is retained.

### 3.2 Frozen-weight factorial intervention

The controlled blocks are A = channels 0–2 (centering), B = channels 6–8 and 18 (spans), and C = channels 16–17 (normal statistics). For every frozen checkpoint/source pair under X50 and X43, all eight combinations substitute selected blocks with exact-original-ID-matched FULL values. Weights, visible geometry, local neighbors, context IDs and queries remain fixed. The design contains 832 complete prediction fields. Its F000 and F111 endpoints reproduce the retained baseline and joint-oracle outputs exactly across 208 replay fields, with maximum discrepancy 0 MPa.

For a scalar response r at each of the eight cells, a contrast is the signed sum of cell responses divided by four. The sign is the product of the selected factors' ±1 levels. Main effects are mean high-minus-low contrasts; pair effects are half the corresponding difference-in-differences, and the triple effect is one quarter of its alternating difference. This convention is important when comparing magnitudes. Effects on a nonlinear metric do not form an additive physical variance decomposition.

Substituting FULL statistics deliberately uses information absent from a restricted observation. Such combinations can also be outside the training distribution. This intervention tests sensitivity of the executed computation, not a deployable method for recovering unseen geometry and not the mechanical effect of independently changing crown height or toe radius. FULL is an unchanged reused control.

### 3.3 Observable local representation

N3 replaces the historical global dependencies with an explicitly visible-geometry contract. Query coordinates are referenced to the registered geometric tile's XY center; the Z datum is the nearest currently visible XY vertex, with ties resolved by minimum original ID. Spans become spans of the visible sixteen-neighbor set; normal statistics become local population standard deviations. The repeated global Z span becomes local Z standard deviation divided by 60 mm. Height relief, oriented normals and incident-triangle areas use only visible surface data. The area channel is log(1 + area/1 mm²), without FE labels. Normals are oriented toward positive canonical Z, and the declared load direction remains [1, 0, 0]. The complete channel formulas accompany the paper.

Operational observability is conditional: the input workflow must provide registered canonical coordinates, the load axis, original IDs and the query plan. No independently calibrated physical Z origin is implied. N3 FULL uses anchor-specific feature views of the same complete geometry, whereas N2 FULL retains its historical centering. Their comparison therefore changes coordinate-frame support as well as feature locality. It is not a pure one-channel ablation or an architecture comparison.

A geometry-only audit distinguishes core-query agreement from agreement over all visible contextual vertices. Exact invariance is neither required nor assumed at crop boundaries, where neighborhoods and incident geometry change. Moreover, invariant local features do not make the model invariant because the pooled encoded context still depends on which surface is visible. A post-fit contextual feature audit was diagnostic and did not select or alter the trained contract.

{fig(3)}

### 3.4 Training and fixed tree baseline

N3 comprises five leave-one-plate-out folds at each of the fixed seeds 20261021 and 20261022. Each run starts from random initialization and uses eighty epochs. AdamW [14] has learning rate 0.001, weight decay 0.0001, a cosine minimum of 0.00001 and gradient-norm clipping at one. Targets are divided by 100 MPa. Each epoch visits every training source, samples 512 queries with replacement using original-area probabilities, and selects each observation condition with probability one third. The source loss multiplier is the number of training sources divided by four times the number from that source's training plate, giving equal expected training-plate weight. Only final-epoch checkpoints are evaluated; no held-out early stopping or better-seed selection is used.

B2 is a fixed XGBoost 3.0.2 baseline [13], using CPU histogram trees, 500 boosting rounds, maximum depth six, learning rate 0.05, subsampling 0.8, column subsampling 0.8, L2 tree regularization one, squared-error objective and seed 20261021. Five training-only fits use the same nineteen-channel N3 inputs. Per source and context, 1024 unique area-CDF midpoint queries define equal-area strata. Quadrature and hierarchical source/plate/context weights are normalized to mean one. The same source IDs are used across conditions without stress-guided selection. N3 and B2 differ in sampling budget, model capacity and optimization; their results do not isolate architecture independently of these differences. Historical B0 constant and B1 geometric Ridge results are retained for FULL only. Restricted B0/B1 results are unavailable, not zero-error controls.

## 4 Evaluation design and metrics

The held-out unit is the documentary parent plate, not a point or mesh node. All sources from a held-out plate are absent from its fitting data. The five outer groups had nevertheless been inspected during earlier development. Plate isolation protects against direct within-run training overlap but cannot erase adaptive cohort exposure. Accordingly, the analysis is exploratory method development on a reused cohort. Neither the number of points nor repeated contexts increases the number of independent production groups.

Let p_i and y_i denote prediction and T2 reference, and w_i the original T0 area. Whole-field error is

L2 = √(Σ_i w_i (p_i − y_i)² / Σ_i w_i y_i²). (2)

MAE = Σ_i w_i |p_i − y_i| / Σ_i w_i. (3)

RMSE = √(Σ_i w_i (p_i − y_i)² / Σ_i w_i). (4)

Bias is the weighted mean signed difference. Prediction stability is assessed separately by replacing the reference y in the change numerator with the same model's FULL prediction while retaining the frozen reference normalization. A stable prediction can be consistently inaccurate; stability is not substituted for accuracy.

High95 uses a separately calculated area-weighted 95th-percentile threshold for each field, obtained by stable value sorting and weighted-CDF interpolation. Membership includes values equal to the field's threshold. Area IoU is the weighted area of the intersection divided by that of the union. False-negative area is reference-high area outside prediction-high; false-positive area is prediction-high area outside reference-high. Precision and recall use predicted-high and reference-high areas as their respective denominators. The centroid-distance metric uses area-weighted centroids of the two high sets. This relative high-area definition does not measure agreement against a common absolute stress threshold.

Threshold ties require explicit care. For the constant baseline, every predicted value equals its own threshold, so the entire predicted field belongs to High95. It therefore has recall one and zero false-negative area while displaying IoU near 0.05 and poor field-amplitude accuracy. Zero missed area is not evidence that this predictor identifies a useful hotspot. Figure 7 omits the degenerate baseline from its curves, while its full numerical result remains in the tables.

Peak error is predicted field maximum minus reference field maximum; absolute peak error is the absolute value of that difference. Q95 error compares the two own-field weighted quantiles in the same way. Neither is the maximum absolute pointwise prediction error. The frozen parent/collar/weld proxy regions support regional L2 reporting but are not independently validated toe tracks.

For every metric, sources are averaged within each plate and the five plate means are then weighted equally. Neural results retain both seeds separately; their combined values are arithmetic means of metrics, not averaged prediction fields. No point-level confidence intervals are constructed. Comparisons are descriptive across five reused groups and two fixed seeds. The reporting classification requires joint accuracy, localization and amplitude safeguards; it is not a hypothesis test. Claim-level CSV provenance, independent macro reaggregation and the complete source-level results accompany this revision.

## 5 Results

### 5.1 Whole-field accuracy and observation sensitivity

Table 1 and Figure 5 retain every baseline and observation condition. For FULL, N1 attains L2 0.1391 and MAE 7.6981 MPa, compared with Ridge L2 0.2413 and MAE 12.7887 MPa. That advantage is observation-dependent: N1 L2 rises to 0.2930 under X50 and 0.3330 under X43. N2 remains between 0.1729 and 0.1740 across conditions. N3 is similarly close in aggregate, between 0.1841 and 0.1849, but has larger L2 than N2 in every condition. Similar condition means do not imply identical same-point predictions; the separate stability data remain supplementary.

Table 1. Equal-plate field accuracy and High95 localization. Neural entries average separately scored seeds. B0 and B1 have FULL results only.

{table1}

{fig(5)}

Historical inference controls distinguish representation effects from tile aggregation. In N1 X43, the joint FULL-statistic oracle changes L2 from 0.3329615 to 0.1392848. Uniform overlapping prediction instead changes the corresponding L2 by only −0.2713%, despite reducing the mean original-boundary jump error from 5.8674 to 1.8588 MPa. Thus the tested stitching intervention improves continuity without resolving the main whole-field discrepancy. FULL used a shared context and had no actual original tile seams; its historical cut-line diagnostic must not be interpreted as a physical inference seam. Oracle and overlap controls change different computational components and cannot be added into a unique causal budget.

### 5.2 Controlled representation effects

Figure 4 shows the three main feature-block contrasts. For N1 X43, span block B has L2 contrast −0.1298113, compared with −0.0508108 for centering and −0.0140170 for normal statistics. Under X50, B is again the largest of these contrasts, at −0.1003922. Under N2 the response is smaller and different in sign: X43 centering has contrast +0.0057097, spans +0.0036573 and normal statistics −0.0052623. The N2 X43 AB interaction is −0.0154021, demonstrating that individual main contrasts do not describe every joint intervention. All interactions and source dependencies are retained in the supporting tables.

{fig(4)}

These results support a computational mechanism for the previously observed N1 crop sensitivity. The model responds strongly to the supplied span-related statistics even when the visible neighborhoods and context sample are fixed. The experiment does not identify a missing physical surface variable, and favorable oracle scores do not establish usable partial-scan performance. The weaker and differently signed N2 effects also argue against treating one normalization explanation as universal across trained variants.

### 5.3 Localization and amplitude trade-offs

N3 improves High95 localization relative to N2 while worsening whole-field L2. For FULL, IoU increases from 0.5479 to 0.6011; for X43 it increases from 0.5279 to 0.5887. Corresponding missed high-area decreases from 12.9701 to 11.1392 mm² and from 13.7567 to 11.5456 mm². Across all conditions the relative missed-area reduction is 14.12–16.40%. Table 2 defines the sign of each contrast explicitly; Figure 7 shows overlap, missed area and peak-amplitude error together.

Table 2. N3 relative to N2. Positive L2 and amplitude-error changes indicate degradation; positive IoU and negative missed-area changes indicate improvement. Changes use separately scored seed means, not individual-field ensembles.

{table2}

{fig(7)}

The amplitude safeguards prevent equating better overlap with accurate local stress magnitude. N3 FULL absolute peak error is 11.6419 MPa versus 10.1082 MPa for N2; under X43 the values are 11.9200 and 10.1096 MPa. Thus absolute peak error increases by 15.17–17.91% across conditions, whereas absolute Q95 error decreases by 9.68–27.02%. These are different amplitude questions. Both remain necessary because a relative High95 set can move into better alignment even if predicted maxima are too large or too small.

Against fixed B2, N3 has lower L2 and higher IoU: FULL L2 is 0.1849 versus 0.2570, and X43 L2 is 0.1841 versus 0.2570. However, B2 FULL L2 also exceeds historical Ridge L2 0.2413. This is evidence about these fixed estimators and their declared training budgets, not universal neural superiority or proof that adding nonlinear complexity improves every metric.

### 5.4 Seed, plate and spatial variability

Table 3 retains the complete two-seed neural comparison and Figure 6 displays seed and plate variability. N1 X43 L2 is 0.4656 for seed 20261021 and 0.2003 for seed 20261022; the mean alone would conceal this difference. N3 X43 L2 is 0.1859 and 0.1824 for the same seeds. This smaller observed difference does not estimate a population distribution over random initialization from only two draws.

Table 3. Every neural seed and observation condition, with equal-plate metrics. No seed was selected or discarded.

{table3}

{fig(6)}

Table 4 shows every documentary plate. At FULL, N3 L2 exceeds N2 on C, E, G and X, with a modest decrease on H. Under X43 it decreases on C, E and H but increases on G and X. The X-plate discrepancy therefore remains visible despite N3's favorable aggregate localization. The largest individual N3 plate/condition/seed L2 is G/FULL/20261022, 0.2362; the largest source row is G07/FULL/20261022, 0.2729. These are maxima over the released comparison, not omitted outliers or new validation failures.

Table 4. Plate-specific accuracy using both-seed metric means. E has one source; no independent manufacturing-batch interpretation is assigned to the group labels.

{table4}

Figure 8 shows the retained G07 example on matched original coordinates. Shared prediction/reference color limits and a zero-centered signed-error scale reveal both overprediction and underprediction. The map is a qualitative spatial illustration; the all-source metrics, both seeds and difficult plates determine the conclusions. It does not visually validate physical stress or accurately identify a physical fatigue crack-initiation site.

{fig(8)}

### 5.5 Joint interpretation

Figure 9 summarizes the central outcome. N3's 6.07–6.94% L2 increase fails the whole-field improvement requirement, and its peak-amplitude degradation fails the amplitude safeguard. Its IoU improvement nevertheless exceeds the frozen threshold for a meaningful localization benefit. The prescribed descriptive classification therefore remains METHOD_IMPROVEMENT_MIXED. The category records conflicting numerical outcomes; it is not evidence that the method is suitable for physical engineering acceptance.

{fig(9)}

## 6 Discussion

### 6.1 What the controlled interventions establish

The main mechanistic result concerns representation rather than mechanics. In the frozen network, a subset of global channels can produce a large change while the queried measured points and visible context are retained. This makes feature construction an explicit component of the learned mapping. A cropped input is not simply a complete input with some points removed if normalization statistics also change. The factorial design quantifies this dependence and its interactions without training a different network for each intervention.

There are limits to that interpretation. FULL-derived substitutions are deliberate diagnostic interventions that can form feature combinations unlike those encountered during fitting. Their favorable numerical behavior does not prove that the network recovered physically meaningful remote geometry, that true information loss is negligible, or that a missing global descriptor can be measured in deployment. The effects quantify the chosen computation and scalar response, not an additive division into physical roughness, crown and toe mechanisms. N2's different block response is further evidence that learned weights and training context jointly govern sensitivity.

The constructive N3 test addresses another question: whether a fully specified visible-local input contract improves the practical predictor. It removes dependence on unseen FULL statistics but changes the anchoring frame and local information support. Context pooling remains observation-dependent. The modest aggregate stability and improved High95 overlap are therefore compatible with worse L2 and worse peak amplitudes. Observability, invariance and predictive usefulness are separate properties; satisfying the first does not guarantee the other two.

### 6.2 Position relative to earlier research

Earlier studies already establish important parts of the overall scan-to-stress workflow [2–6]. The distinction here is the controlled evaluation of representation under changing observation context, with predictions retained on the same original surface and aggregated by documentary plate. Dense area-weighted field accuracy is evaluated alongside relative high-area localization and amplitudes. The contribution is this explicit diagnosis and the mixed constructive result, rather than a claim that scanned geometry, point-set networks or FE-trained weld prediction are new individually.

Comparison with general field-surrogate studies [9,10] should likewise remain methodological. The present fixed elastic problem does not demonstrate variable-load operator learning. Its processed front and idealized rear define only one numerical model family. Nor is the implemented SurfacePT interchangeable with the full recognition architectures [11,12]. Reproducibility requires the executed forward override, geometric support and input formulas, not merely an architecture label. The fixed XGBoost comparison is useful because it prevents treating nonlinear local regression as an untested explanation of the neural result; different training budgets prohibit a capacity-matched architectural conclusion.

### 6.3 Engineering meaning of a localization gain

An engineer may use a spatial surrogate to prioritize regions for closer numerical inspection. Relative high-area overlap is relevant to that limited task, but it does not set an allowable stress or certify a safe region. Independently calculated percentile thresholds can reward spatial ranking while masking amplitude bias. The constant baseline gives an extreme illustration: its zero missed area is obtained by labeling everything high. Reporting IoU, missed area, peak and quantile amplitude errors together prevents that degeneracy from becoming a positive claim.

Likewise, a visually smooth stitched field is not necessarily a more accurate field. The retained overlap control greatly reduces a boundary-jump diagnostic while barely changing the whole-field score. This argues for reporting continuity as a separate numerical property. Neither the present maps nor the frozen proxy regions are physically validated weld-toe trajectories. A prediction of the regularized numerical field cannot be substituted for a validated notch-stress analysis, grinding design or fatigue-life assessment.

### 6.4 Scope of reproducibility and uncertainty

The evidence permits traceable computational statements within the frozen cohort. Original IDs, geometry areas, target operators, model checkpoints and complete results are retained; the revision independently reaggregates published source-level metrics. Documentary plate grouping reduces direct dependence between fitting and evaluation compared with point-level splitting. It does not establish five independent manufacturing batches or undo the repeated use of these groups during development. Reporting every plate and both fixed seeds is therefore more appropriate than constructing narrow confidence intervals from many surface points.

The remaining uncertainty has several sources that should not be conflated. M1/M2 discrepancies describe numerical mesh sensitivity of the declared operator. Differences across seeds and groups describe the observed learner/cohort variation. Processed-scan smoothing, unresolved raw registration and the assumed rear contribute geometric/model-form uncertainty not calibrated by those discrepancies. No probabilistic coverage guarantee is assigned to the resulting field. Public artifact deposition and fresh independent evaluation would be separate author-controlled work, not an implied outcome of this revision.

## 7 Study limitations

The dataset comprises thirteen numerical source identities from five documentary groups, all previously examined. Production-batch and scan-session independence are uncertified. Raw-scan registration remains unresolved, and processed scans have already been aligned and smoothed. The rear surface, material constants and standardized loading are assumptions. Two-level FE consistency is not asymptotic convergence, exact notch-radius metrology or experimental stress validation.

N3 requires registered coordinates and a declared query plan; arbitrary unregistered scans are outside the demonstrated input contract. Local features and pooled context can change near observation boundaries. N2–N3 differences include coordinate-frame support, and B2–N3 comparisons have unequal sampling budgets and learning mechanisms. Two seeds provide limited evidence about initialization variability. Own-percentile High95 metrics do not establish absolute peak accuracy, and proxy regions are not independent toe measurements.

No welding residual stresses, plasticity, crack growth, fatigue-life prediction or experimental stress measurements are included. No fresh independent cohort or external validation was performed. Numerical stress localization is not physical fatigue-critical-site validation, and the present results do not authorize industrial deployment or an optimization campaign.

## 8 Conclusions

Frozen-weight interventions show that observation-dependent global geometric representation substantially influences the original neural model's restricted-context predictions. For N1 X43, replacing the full global block changes L2 from 0.3330 to 0.1393 with the visible context held fixed. This diagnostic is nondeployable and does not isolate physical information loss.

The visible-local representation produces a mixed numerical result. Relative to N2, N3 increases whole-field L2 by 6.07–6.94%, improves High95 IoU by 0.0532–0.0625 and reduces missed high-area by 14.12–16.40%. Absolute peak-amplitude error worsens. N3 is therefore not universally superior, despite outperforming the fixed XGBoost comparator on the reported field and localization metrics.

Both seeds, all documentary plates and the difficult G and X results remain part of the evidence. The classification METHOD_IMPROVEMENT_MIXED distinguishes localization improvement from field-accuracy improvement. The study supports a reproducible account of representation/context sensitivity within a standardized numerical weld model family; it does not establish fresh independent generalization, physical weld stress accuracy or fatigue life.

## Data availability

The original scans and experimental metadata are available from Dänekas [1], version 1.0, DOI 10.25835/0dojws6u, under CC BY 4.0. T2 fields, planar-rear geometries, FE results and learned predictions are derived project artifacts and must not be attributed to the repository as measured stresses. Their local provenance is recorded in QUALIFIED13_SOURCE_REGISTRY.csv and MODEL_PREDICTION_REGISTRY.csv in the preserved release. This revision includes supporting CSV tables, figure sources and hash audits. The derived target/model package has not been publicly deposited and has no asserted public DOI. Author-managed curation, third-party licensing checks and a persistent archive remain necessary before a public-data availability claim can be finalized.

## Code availability

Executed research code, frozen configuration hashes and checkpoint paths remain in the immutable research release. The retained environment uses CPU PyTorch 2.6.0; B2 uses XGBoost 3.0.2, scikit-learn 1.6.1 and NumPy 2.2.6 in its separate environment. Revision scripts generate tables, figures and documents from released artifacts without fitting or inference. A public code repository has not been created. Local provenance and the reproducibility manifest support auditability, but do not substitute for a publicly installable research package.

## References

{references}
'''
text=text.replace("while retaining the frozen reference normalization", "and normalizing by the same model's area-weighted FULL prediction norm")
# Number main figures by first manuscript appearance, retaining original figure provenance.
for a,b in [('Figure 4','Figure TEMP'),('Figure 5','Figure 4'),('Figure TEMP','Figure 5'),('Fig04_','FigTEMP_'),('Fig05_','Fig04_'),('FigTEMP_','Fig05_')]:text=text.replace(a,b)
(D/'MANUSCRIPT_REVISION_R1.md').write_text(text,encoding='utf-8')
(D/'ABSTRACT_AND_HIGHLIGHTS.md').write_text('# Abstract\n\n'+abstract+'\n\n# Highlights\n\n- Fixed-point interventions expose observation-dependent representation sensitivity.\n- All comparisons preserve the original area-weighted numerical target and query support.\n- Visible-local features improve high-area overlap but worsen whole-field and peak errors.\n- Two fixed seeds and every documentary plate are reported without favorable selection.\n- Findings concern numerical surrogates on a reused cohort, not validated physical stress.\n',encoding='utf-8')
(D/'VERIFIED_REFERENCES.md').write_text('# Verified references\n\nFocused primary-source review, checked 23 October 2026. Publisher abstracts, original-author records and Crossref metadata are distinguished in LITERATURE_VERIFICATION.csv; abstract-only access is not represented as full-text review.\n\n'+references+'\n\n## Verification notes\n\nNie et al. is cited by its 2020 issue year (first online 2019). Dänekas et al. toe-algorithm paper uses the 2025 issue year despite a 2024 DOI. PointNet author order is corrected from the original-author record. Point Transformer DOI 10.1109/ICCV48922.2021.01595 was verified by exact title; a candidate ending 01600 resolved to a different paper and was rejected. Schubnell et al. is a proceedings contribution in Procedia Structural Integrity, not presented as an independent journal benchmark. AdamW uses the original-author DOI with its stated ICLR 2019 venue. The direct-point-cloud cruciform conference lead seen only in a secondary index was not relied upon. No exhaustive-review or priority claim is made.\n',encoding='utf-8')
(D/'MAIN_RESULTS_TABLES.md').write_text('# Main results and complete amplitude tables\n\n## Table 1\n\n'+table1+'\n\n## Table 2\n\n'+table2+'\n\n## Table 3 Both fixed seeds\n\n'+table3+'\n\n## Table 4 All plates\n\n'+table4+'\n\n## Supplementary amplitude and missed-area table\n\n'+amplitudes+'\n\nFN areas and amplitude errors use their own original-area weights. Constant-field zero FN results from ties, not useful localization. Peak errors compare field maxima, not maximum pointwise errors. Neural means average metrics, not fields. Exact unrounded values and all additional metrics remain in MAIN_MODEL_METRICS.csv and BOTH_SEED_METRICS.csv.\n',encoding='utf-8')
print(json.dumps({'manuscript_words':len(text.split()),'references':len(refs),'main_figures':len(figs)}))
