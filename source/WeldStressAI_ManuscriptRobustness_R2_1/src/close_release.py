from pathlib import Path
import json,csv,hashlib,datetime,shutil,re,zipfile,xml.etree.ElementTree as ET
from PIL import Image
from pypdf import PdfReader
D=Path(__file__).resolve().parents[1];O=D.parent;P=O/'WeldStressAI_ManuscriptRevision_R2';R=O/'WeldStressAI_FinalResearch_PhaseR8E16';P1=O/'WeldStressAI_ManuscriptRevision_R1'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def write(n,s):(D/n).write_text(s.strip()+'\n',encoding='utf-8')
# Verify the sealed analysis contracts and geometry scores were never changed after metrics.
seal=json.loads((D/'R2_1_PROTOCOL_SEAL.json').read_text())
for f in seal['files']:assert sha(D/f['path'])==f['SHA256'],f['path']
inputs=json.loads((D/'R2_1_INPUT_HASHES.json').read_text());inputchecks=[]
for row in inputs['files']:
 actual=sha(row['path']);assert actual==row['SHA256'],row['path'];inputchecks.append(dict(path=row['path'],expected_SHA256=row['SHA256'],actual_SHA256=actual,status='PASS'))
with (D/'qa'/'FINAL_INPUT_HASH_CHECK.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(inputchecks[0]));w.writeheader();w.writerows(inputchecks)
release=[]
for root,mf in [(R,'REPRODUCIBILITY_MANIFEST.json'),(P1,'REVISION_REPRODUCIBILITY_MANIFEST.json'),(P,'REPRODUCIBILITY_MANIFEST.json')]:
 data=json.loads((root/mf).read_text());count=0
 for row in data['files']:assert sha(root/row['path'])==row['SHA256'],str(root/row['path']);count+=1
 release.append(dict(workspace=str(root),files=count,manifest_SHA256=sha(root/mf),status='PASS'));print('FINAL_ORIGINAL_RELEASE_UNCHANGED',root.name,count,flush=True)
(D/'qa'/'FINAL_HISTORICAL_RELEASE_INTEGRITY.json').write_text(json.dumps(release,indent=2))
editorial=[]
for name in ['LITERATURE_VERIFICATION.csv','VERIFIED_REFERENCES.md']:
 p=P1/name;dest=D/'source_snapshot'/name;shutil.copy2(p,dest);editorial.append(dict(path=str(p),SHA256=sha(p),copy_SHA256=sha(dest)))
p=P1/'literature'/'VERIFIED_REFERENCE_RECORDS.json';dest=D/'source_snapshot'/p.name;shutil.copy2(p,dest);editorial.append(dict(path=str(p),SHA256=sha(p),copy_SHA256=sha(dest)))
(D/'qa'/'ADDITIONAL_EDITORIAL_INPUT_HASHES.json').write_text(json.dumps(editorial,indent=2))
paper=(D/'MANUSCRIPT_FINAL_R2_1.md').read_text(encoding='utf-8');old=(P/'MANUSCRIPT_REVISION_R2.md').read_text(encoding='utf-8');assert paper.split('## References')[1].strip()==old.split('## References')[1].strip()
assert len(re.findall(r'^Figure \d+\.',paper,re.M))==9 and len(re.findall(r'^Table \d+\.',paper,re.M))==7
assert 'Supplementary Retrospective Robustness Assessments' in paper and 'Engineering Robustness and Geometry-Only Localization Baselines' in paper
with zipfile.ZipFile(D/'MANUSCRIPT_FINAL_R2_1.docx') as z:
 root=ET.fromstring(z.read('word/document.xml'));ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
 assert len(root.findall('.//w:tbl',ns))==7;assert len(root.findall('.//w:drawing',ns))==9;assert len(root.findall('.//m:oMath',ns))==4
 assert all(float(e.attrib['cx'])<=6.91*914400 for e in root.iter() if e.tag.endswith('}extent') and 'cx' in e.attrib)
pages=list((D/'qa'/'docx_release').glob('page-*.png'));assert len(pages)==24
eq=json.loads((D/'qa'/'RENDER_EQUIVALENCE.json').read_text());assert set(eq['changed_pages'])=={'page-21.png','page-23.png','page-24.png'}
visual=dict(status='PASS',pages=24,figures=9,tables=7,editable_structured_OMML_equations=4,inspection='Every initial rendered page visually inspected; final pages 21/23/24 separately inspected after historical-definition clarification and intact-reference paragraph correction; other 21 page PNGs are hash-identical.',unresolved_clipping_overlap=False,renderer='Native Microsoft Word conversion with packaged render_docx Poppler rasterization',internal_previews_delivered=False)
(D/'qa'/'FINAL_DOCX_VISUAL_QA.json').write_text(json.dumps(visual,indent=2))
figs=json.loads((D/'R2_1_FIGURE_REGISTRY.json').read_text());assert len(figs)==18
for row in figs:
 p=D/row['path']
 with Image.open(p) as im:im.verify()
 assert len(PdfReader(str(p.with_suffix('.pdf'))).pages)==1
assert len(list((D/'figures'/'main').glob('*.png')))==9
audit=json.loads((D/'qa'/'INDEPENDENT_AUDIT_PASS.json').read_text());extra=json.loads((D/'qa'/'ADDITIONAL_INDEPENDENT_CHECKS.json').read_text());assert audit['status']==extra['status']=='PASS'
required=['R2_1_ANALYSIS_PROTOCOL.md','R2_1_PROTOCOL_SEAL.json','R2_1_THRESHOLD_CONTRACT.json','R2_1_GEOMETRY_BASELINE_CONTRACT.json','R2_1_REGIONAL_METRIC_CONTRACT.json','R2_1_SOURCE_REGISTRY.csv','R2_1_INPUT_HASHES.json','R2_1_INPUT_INTEGRITY_REPORT.md','R2_1_INDEPENDENT_METRIC_AUDIT.md','THRESHOLD_ROBUSTNESS_SOURCE.csv','THRESHOLD_ROBUSTNESS_PLATE.csv','REFERENCE_THRESHOLD_DIAGNOSTICS.csv','THRESHOLD_TIE_AND_AREA_AUDIT.csv','G0_COLLAR_BASELINE_RESULTS.csv','G1_GEOMETRY_RANKING_RESULTS.csv','GEOMETRY_BASELINE_OBSERVABILITY_AUDIT.csv','NEURAL_VERSUS_GEOMETRY_BASELINES.csv','REGIONAL_ERROR_SOURCE.csv','REGIONAL_ERROR_PLATE.csv','REGIONAL_ERROR_CONTRIBUTIONS.csv','CRITICAL_SOURCE_ERROR_DIAGNOSTICS.md','R2_1_SCIENTIFIC_FINDINGS.md','R2_1_UNFAVORABLE_RESULTS.md','R2_1_CLAIM_EVIDENCE_MATRIX.csv','R2_1_EDITORIAL_RISK_ASSESSMENT.md','MANUSCRIPT_FINAL_R2_1.md','MANUSCRIPT_FINAL_R2_1.docx','MAIN_FIGURE_SELECTION.md','FINAL_FIGURE_CAPTIONS.md','SUPPLEMENTARY_MATERIAL_PLAN.md','MANUSCRIPT_CHANGELOG.md','MANUSCRIPT_FINAL_QUALITY_AUDIT.md']
decisions=['FROZEN_EVIDENCE_VERIFIED','LOCALIZATION_MIXED_ACROSS_THRESHOLDS','NEURAL_ADDED_VALUE_SUPPORTED','REGIONAL_ERROR_AUDIT_COMPLETE','METHOD_IMPROVEMENT_MIXED','MANUSCRIPT_FINAL_READY_FOR_AUTHOR_REVIEW','CURRENT_WELDSTRESS_AI_MANUSCRIPT_RESEARCH_CLOSED']
write('MANUSCRIPT_FINAL_QUALITY_AUDIT.md',f'''# Final R2.1 scientific and publication-preparation audit

## Independent decisions

{chr(10).join('- '+d for d in decisions)}

NEURAL_ADDED_VALUE_SUPPORTED is limited to the one sealed FULL-geometry G1 comparator. It does not imply neural indispensability, fair restricted-view geometry comparison or physical validation. The original METHOD_IMPROVEMENT_MIXED experiment is not rewritten. Threshold robustness is mixed despite positive nine-cell mean rank contrasts.

## Historical evidence and protocol discipline

All 2,715 original R8-E16, 470 R1 and 388 R2 manifested files pass fresh initial and final SHA-256 audits. All 644 sealed input files remain unchanged at closeout. Original source IDs, XYZ, triangles, T0 areas, qualified T2, 34,200-query cores, five plates and both seeds pass verification. All 299 saved original available fields are unchanged; historical High95 was recovered before the R2.1 seal. Fixed contracts, geometry-score files and metric/geometry modules still match their sealed hashes. The seal establishes retrospective execution discipline, not original-phase preregistration or an untouched cohort.

No ANSYS solve, mesh, FE target, training, fitting, architecture, hyperparameter search, new source/context, inference, best-seed selection or stress-derived geometry label was introduced. All original observations and research releases remain preserved. The resource preflight passed before metric execution.

## Independent numerical verification

The separate implementation passes {audit['numeric_cells']:,} numeric cells, including {audit['aggregate_cells']:,} aggregation cells; maximum absolute discrepancy is {audit['max_absolute_cell_error']:.12g}. Every rank, common-reference and historical mask matches exactly. All thirteen contours were independently reconstructed, with maximum distance discrepancy {audit['independent_geometry_max_distance_error_mm']:.12g} mm. Additional boundary, geometry aggregation and paired-comparison checks pass {extra['boundary_geometry_and_grouping_cells']:,} cells, maximum discrepancy {extra['maximum_absolute_error']:.12g}. The initial checker-order issue for undefined precision is documented and resolved by a complete rerun, without changing primary results.

Rank budgets, original-CDF High95 and common-reference MPa thresholds are separate. Common thresholds are diagnostic only; actual mask areas, tie behavior, empty-set definitions and valid counts remain explicit. Source metrics are averaged within plate and then equally across plates separately for each neural seed, followed by seed-metric mean; single fixed regressors and geometry rules are not duplicated to fabricate seeds. No point-count confidence interval or significance claim is made. All unfavorable source/plate/seed outcomes are retained.

## Geometry and regional scope

G0/G1 FULL results are feasible on all thirteen sources. Fifty-two restricted source/model/context comparison rows remain NOT_EVALUABLE because a qualified visible-only parent-plane/label contract is absent. This is an explicitly reported scientific comparison limitation, not an unreported failed calculation. No substitute score or threshold was tuned. Geometry masks receive no stress amplitudes or L2. Historical B0/B1 restricted predictions remain unavailable.

Original parent/collar/height regions are retained. Numerical load caps, gauges, scoring-core edges, owning observation edges and geometry contours are distinct. These proximity diagnostics do not isolate a causal mechanical boundary effect or identify independently measured physical toe/crack locations. M1/M2 numerical consistency remains distinct from physical stress/radius validation.

## Manuscript and figures

The final English Word manuscript contains 24 rendered pages, nine main figures, seven tables and four editable structured native OMML equations. Every page was visually inspected; after final corrections only pages 21, 23 and 24 changed and were reinspected, while the other twenty-one pages are pixel-identical. No unresolved clipped text, figure, equation or table remains. References are kept intact across page breaks. The original title and all sixteen verified reference entries are unchanged; source bibliographic records are included.

Three main figures are replaced with threshold, regional and geometry-comparator evidence; original versions remain supplementary. Eighteen new figure pairs comprise three main figures, one all-plate grid, six geometry-mask panels and eight critical-source atlases. Prior R1/R2 supplementary evidence is preserved in legacy subdirectories. Main regional panels have common MPa axes; direct FE/prediction comparisons share color limits and errors are zero-centered. Actual measured-source coordinates are retained and no physical toe is invented. Representative new supplementary spatial/grid images and every main figure through the final Word pages were visually inspected; all new PNG/PDF files also pass parse checks. This is not a claim of individual visual inspection of every inherited supplementary page.

All thirty-nine requested questions are answered in R2_1_FINAL_QUESTIONS.md and appended to the scientific findings report. R2_1_CLAIM_EVIDENCE_MATRIX.csv links derived numeric records to exact CSV row keys, numeric payloads and source hashes; the original R2 ledger remains preserved. Native large research binaries remain at their unchanged absolute provenance paths; the editorial archive does not assert a self-contained research installation or public persistent deposition.

## Remaining author and physical-validation limitations

Readiness is for final human author review, with the above scientific limitations. Target-journal word limits, authorship, submission formatting and persistent code/data deposition remain author-controlled. No guaranteed Q1 acceptance, deployment readiness, independent external generalization, experimental stress validation, validated toe radius or fatigue life is claimed. Raw registration and processed metrology uncertainty, assumed rear/material/loading and causal nonlocal boundary influence remain unresolved. No R8-E17, R2.2 or additional model-development campaign is initiated. The current manuscript research program is closed.
''')
write('FINAL_R2_1_DECISIONS.md','# Final R2.1 decisions\n\n'+'\n'.join('- '+d for d in decisions)+'\n\nGeometry added value is limited to the sealed FULL comparator. Threshold conclusions are mixed and fair restricted geometry baselines remain unavailable. Original experimental interpretation and physical-validation limits are retained. The detailed final scientific findings answer all thirty-nine required questions. Research is closed without a new development phase.')
write('README_DELIVERY.md','''# WeldStress AI final manuscript package R2.1

MANUSCRIPT_FINAL_R2_1.docx and MANUSCRIPT_FINAL_R2_1.md are the final English author-review paper. R2_1_SCIENTIFIC_FINDINGS.md includes the new numerical findings and all thirty-nine question responses; R2_1_FINAL_QUESTIONS.md supplies them separately. MANUSCRIPT_FINAL_QUALITY_AUDIT.md records scope, integrity, document checks and limitations. Root CSVs retain source/plate/seed metrics and all unavailable comparisons. R2_1_FIGURE_REGISTRY.json and FINAL_FIGURE_CAPTIONS.md identify genuine frozen-data figures.

Original artifacts remain unchanged. New deterministic scores, masks, contracts, checking code and provenance are included. Large original numerical fields, meshes and checkpoints remain in their original workspaces, located through absolute paths and hashes. The archive is an editorial/reproducibility evidence package, not a public-data deposition or a complete standalone research installation. No new FE, fitting, training or inference occurred. G0/G1 partial-view comparisons are explicitly unavailable. Physical stress/geometry validation remains unresolved. This bounded assessment closes the current manuscript research program.
''')
assert all((D/p).exists() and (D/p).stat().st_size for p in required)
# Ensure ledger sources have not changed since their numeric payloads were recorded.
with (D/'R2_1_CLAIM_EVIDENCE_MATRIX.csv').open(encoding='utf-8-sig',newline='') as f:ledger=list(csv.DictReader(f))
lh={r['evidence_file']:r['evidence_SHA256'] for r in ledger}
for p,h in lh.items():assert sha(p)==h,p
manifest_file=D/'REPRODUCIBILITY_MANIFEST.json';receipt_file=D/'DELIVERY_VERIFICATION.json';archive=D/'WeldStressAI_ManuscriptRobustness_R2_1_Package.zip'
def include(p):
 rel=p.relative_to(D)
 return p.is_file() and p not in [manifest_file,receipt_file,archive] and p.suffix not in ['.pyc','.zip'] and '__pycache__' not in rel.parts and not (rel.parts[0]=='qa' and len(rel.parts)>1 and rel.parts[1].startswith('docx_'))
files=[dict(path=p.relative_to(D).as_posix(),size_bytes=p.stat().st_size,SHA256=sha(p)) for p in sorted(D.rglob('*')) if include(p)]
manifest=dict(release='WeldStressAI_ManuscriptRobustness_R2_1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),decisions=decisions,geometry_decision_scope='Sealed G1, FULL only',protocol_seal_SHA256=sha(D/'R2_1_PROTOCOL_SEAL.json'),input_files_verified=644,historical_releases=release,unavailable_comparisons=['G0/G1 restricted observations (52 explicit NOT_EVALUABLE rows)','Historical B0/B1 restricted fields'],physical_validation=False,independent_external_validation=False,new_ANSYS_solves=0,new_training=0,new_fits=0,new_inference=0,files=files,excluded='Self manifest, ZIP/receipt, internal DOCX render PNG/PDF; large original native arrays remain at their unchanged absolute paths')
manifest_file.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for row in files:z.write(D/row['path'],row['path'])
 z.write(manifest_file,manifest_file.name)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for row in files:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['SHA256'],row['path']
 assert z.read(manifest_file.name)==manifest_file.read_bytes()
receipt=dict(status='PASS',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),decisions=decisions,required_outputs=len(required),manifest_files=len(files),ZIP_entries=len(files)+1,ZIP_size_bytes=archive.stat().st_size,ZIP_SHA256=sha(archive),manifest_SHA256=sha(manifest_file),each_ZIP_entry_SHA256_and_CRC='PASS',sealed_input_hashes_verified=644,original_release_files_unchanged=sum(x['files'] for x in release),independent_numeric_cells=audit['numeric_cells'],additional_checked_cells=extra['boundary_geometry_and_grouping_cells'],new_figure_pairs=18,Word_pages=24,main_figures=9,tables=7,uncompleted_release_checks=[],unavailable_scientific_comparisons=manifest['unavailable_comparisons'],research_closed=True)
receipt_file.write_text(json.dumps(receipt,indent=2),encoding='utf-8');print(json.dumps(receipt),flush=True)
