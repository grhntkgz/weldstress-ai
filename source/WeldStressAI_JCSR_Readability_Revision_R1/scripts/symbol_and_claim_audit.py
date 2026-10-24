from pathlib import Path
import csv,json,re,collections,hashlib
D=Path(__file__).resolve().parents[1];B=Path(r'E:\welding\outputs\WeldStressAI_JCSR_FigureEnhancement_R1')
new=(D/'MANUSCRIPT_READABILITY_REVISED.md').read_text(encoding='utf-8');notes=(D/'SUPPLEMENTARY_READABILITY_METHOD_NOTES.md').read_text(encoding='utf-8')
symbols=[('i, j','Original surface-vertex indices','dimensionless','2.3, 4'),('N(i)','Accepted same-face 1 mm three-dimensional Euclidean chord neighborhood of vertex i','mm support','2.3 / Equation 1'),('a_j','Original T0 surface-area weight of neighbor j','mm²','2.3 / Equation 1'),('s_j','Nonnegative tensile maximum principal stress at j, recovered before averaging','MPa','2.3 / Equation 1'),('T2_i','Area-regularized numerical FE reference at query i','MPa','2.3 / Equation 1'),('p_i, y_i','Prediction and T2 numerical FE reference at original query i','MPa','4 / Equations 2–4'),('w_i','Original T0 area weight at query i','mm²','4 / Equations 2–4'),('r','Scalar response summarized across the eight factorial combinations','metric-dependent','Note A5'),('A, B, C','Centering, geometric-span and normal-statistic feature groups','channel groups','3.2'),('±1','Retained factorial coding used for contrast signs','dimensionless','Note A5'),('ΔIoU','IoU difference with the explicitly specified comparison direction','dimensionless','Tables 5–6'),('E','Young’s modulus, assumed as 210 GPa','GPa','2.2'),('ν','Poisson’s ratio, assumed as 0.30','dimensionless','2.2'),('UX, UY, UZ','Displacement components along canonical X, Y and Z','mm','Note A2'),('YMIN, YMAX','Minimum and maximum Y positions on an end cap','mm coordinates','Note A2'),('RMS','Root mean square reference stress magnitude used for validity of normalization','MPa','Note A7'),('SSE, SAE','Original-area-weighted sums of squared and absolute errors','weighted sums','Note A7'),('Q95','Own-field original-area-weighted 95th-percentile stress, not the quantile of pointwise error','MPa','4'),('X, Y, Z','Registered canonical coordinates; tensile loading along +X, profile direction Y','mm','2.1–2.2')]
with (D/'MATHEMATICAL_SYMBOL_REGISTER.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['symbol','meaning','units','definition_location']);w.writerows(symbols)
p=D/'ABBREVIATIONS_AND_NOMENCLATURE.md'
p.write_text(p.read_text(encoding='utf-8').split('\n## Mathematical symbols and retained technical labels')[0],encoding='utf-8')
with p.open('a',encoding='utf-8') as f:
 f.write('\n## Mathematical symbols and retained technical labels\n\n')
 for s,m,u,loc in symbols:f.write(f'- **{s}** — {m}. Units: {u}. Definition: {loc}.\n')
 f.write('\nSource identities such as G07-V1-S355-AW and opaque provenance keys identify existing artifacts; their labels are not new metrics. Organization names and abbreviations within the unchanged reference titles are preserved as bibliographic metadata.\n')

# Check claims as matched passages with comparison direction, not a bag of numeric tokens.
families=[
('abstract model order',['0.1391, 0.1740 and 0.1849','0.2570','full-observation training (N1)','mixed-observation training (N2)','visible-local geometric features (N3)']),
('oracle sensitivity',['changes L2 from 0.3330 to 0.1393','nondeployable','visible context fixed']),
('N3 deterioration direction',['L2 increases by 6.07–6.94%','High95 IoU improves by 0.0532–0.0625','absolute peak-amplitude error worsens']),
('adverse X and exception',['−0.0923','X23/FULL/20261021','+0.00158','Eleven of twelve']),
('extreme common threshold',['99th-percentile stress threshold reverses','every context and both seeds','0.1945%','0.03994']),
('regional trade-off',['19.1885 to 17.3934','17.7284 to 20.6722','7.3068 to 7.8045','No region improves across every plate/context combination']),
('geometry comparator scope',['all 78 source/seed/budget comparisons','not neural necessity','superiority to every geometric rule']),
('T2 sequence',['principal-value operation precedes averaging','0.0000001 mm','1 − 10⁻¹⁰','same face','Euclidean chord (straight-line)']),
('architecture and inputs',['nineteen inputs','encoder width 24','7228 trainable parameters','4096-point context','three fixed sixteen-neighbor sets','no query-to-query attention or pooling']),
('fixed evaluated support',['34,200 valid core queries','evaluated points and T2 targets remain unchanged','Original query ID 50815']),
('grouped evaluation',['one of the five groups is withheld','other four supply training data','leave-one-plate-out (LOPO)','not fresh independent generalization']),
('ranking versus amplitude',['each field uses its own threshold','differ from exactly 5%','does not guarantee correct stress amplitude','not an operational geometry-only threshold']),
]
alltext=new+'\n'+notes
out=[]
for family,anchors in families:
 absent=[a for a in anchors if a.lower() not in alltext.lower()]
 # Some semantic anchors are worded differently; flag rather than claim a missing exact phrase is proof of a changed finding.
 out.append({'claim_family':family,'exact_anchors_found':len(anchors)-len(absent),'anchors_expected':len(anchors),'missing_literal_anchors':absent,'review':'CHECK LITERAL WORDING' if absent else 'PASS'})
(D/'QA/CLAIM_CONTEXT_REVIEW.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=True,indent=2))
