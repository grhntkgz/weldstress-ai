"""Close an editorial-only release with fresh consumed-input hashes and ZIP checks."""
from pathlib import Path
import json,csv,hashlib,zipfile,re,datetime,xml.etree.ElementTree as ET
from PIL import Image
from pypdf import PdfReader
D=Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRevision_R2');P=D.parent/'WeldStressAI_ManuscriptRevision_R1'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
checks={}
for filename in ['CONSUMED_SPATIAL_INPUT_HASHES.csv','ADDITIONAL_GEOMETRY_METADATA_HASHES.csv']:
 for row in read(D/'qa'/filename):
  p=Path(row['path']);actual=sha(p);assert actual==row['SHA256'],str(p);checks[str(p)]={'path':str(p),'SHA256':actual,'status':'PASS'}
with (D/'qa'/'FINAL_CONSUMED_INPUT_SHA256_CHECK.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['path','SHA256','status']);w.writeheader();w.writerows(checks.values())
paper=(D/'MANUSCRIPT_REVISION_R2.md').read_text(encoding='utf-8');old=(P/'MANUSCRIPT_REVISION_R1.md').read_text(encoding='utf-8');assert paper.split('## References')[1]==old.split('## References')[1]
assert 'Plate-Specific Hotspot Localization and Spatial Interpretation' in paper
paths=re.findall(r'!\[.+?\]\((.+?)\)',paper);assert len(paths)==9 and all((D/p).exists() for p in paths)
assert len(list((D/'figures'/'main').glob('*.png')))==9
assert len(list((D/'figures'/'supplementary').glob('*.png')))==31
figures=[]
for root in [D/'figures',D]:
 candidates=list(root.rglob('*.png')) if root!=D else [D/'PLATE_LOCALIZATION_CONTRAST_FIGURE.png']
 for p in candidates:
  with Image.open(p) as im:im.verify()
  pdf=p.with_suffix('.pdf');assert pdf.exists() and len(PdfReader(str(pdf)).pages)==1;figures.append(str(p.relative_to(D)))
with zipfile.ZipFile(D/'MANUSCRIPT_REVISION_R2.docx') as z:
 xml=z.read('word/document.xml');node=ET.fromstring(xml);ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
 assert len(node.findall('.//w:tbl',ns))==5
 assert len(node.findall('.//m:oMath',ns))==4
 assert len(node.findall('.//w:drawing',ns))==9
pages=sorted((D/'qa'/'docx_release').glob('page-*.png'));assert len(pages)==20
render=json.loads((D/'qa'/'RENDER_PAGE_EQUIVALENCE.json').read_text());assert render['changed_pages']==['page-3.png']
visual=dict(status='PASS',pages=20,visual_inspection='All twenty page images inspected; final page 3 re-inspected after figure-label correction; other nineteen final page PNG hashes identical to inspected render.',equations='Four editable native OMML equations',tables=5,main_figures=9,clipping_overlap='No unresolved clipping or overlap in final manuscript render',renderer='Native Microsoft Word conversion and packaged render_docx Poppler rasterizer',figure_pairs_checked=len(figures))
(D/'qa'/'FINAL_DOCUMENT_QA.json').write_text(json.dumps(visual,indent=2))
releases=json.loads((D/'qa'/'RELEASE_INTEGRITY_PASS.json').read_text());ind=json.loads((D/'qa'/'INDEPENDENT_R2_REAUDIT.json').read_text())
assert all(releases[n]['status']=='PASS' for n in ['WeldStressAI_ManuscriptRevision_R1','WeldStressAI_FinalResearch_PhaseR8E16']);assert ind['status']=='PASS'
decisions=['R2_EVIDENCE_VERIFIED','SPATIAL_ASSOCIATION_PARTIAL','X_GROUP_AUDIT_COMPLETE','MANUSCRIPT_R2_READY_FOR_AUTHOR_REVIEW','R8_E16_RESEARCH_REMAINS_CLOSED']
audit=f'''# Final R2 scientific quality audit

## Independent decisions

{chr(10).join('- '+d for d in decisions)}

The original scientific classification remains METHOD_IMPROVEMENT_MIXED. Evidence integrity and engineering interpretation are separate: a passing hash or arithmetic audit does not validate physical stress, toe location, notch radius or fatigue performance.

## Evidence and arithmetic checks

Fresh full original release checks pass for all 470 manifested R1 files and all 2,715 manifested R8-E16 files. The manifest hashes remain {releases['WeldStressAI_ManuscriptRevision_R1']['manifest_SHA256']} and {releases['WeldStressAI_FinalResearch_PhaseR8E16']['manifest_SHA256']}, respectively. Initial and final full-release receipts are retained under qa. At closeout, {len(checks)} unique consumed spatial/metadata/native-mesh files were rehashed against their original expected hashes, all passing. Archive-extracted metadata matches the preserved original CSV archive members.

All thirteen original geometry/target packages retain exact point IDs, XYZ and T0 areas. Canonical triangles reproduce lumped original areas within 1e−10 mm²; all frozen region labels reconstruct without mismatch. Each source retains 34,200 core queries. All 156 N2/N3 fields retain unchanged support and original High95 thresholds. Direct field replay checks 1,560 original metric cells; independent original-CSV reaggregation checks 1,080 cells with maximum absolute discrepancy {ind['maximum_absolute_metric_error']:.17g}. All fifteen released plate comparisons and all six N2/N3 macro rows agree. Both seeds, all three contexts and all five groups are retained. No point-level independence or confidence interval is asserted.

## Adverse results and spatial interpretation

X mean IoU contrasts are −0.01902766 FULL, −0.07849776 X50 and −0.09225883 X43; all six plate/seed/context contrasts are adverse. Eleven of twelve source/seed/context X contrasts are adverse; the small X23/FULL/20261021 favorable exception is disclosed. N3 whole-field and peak-amplitude deterioration remains visible. X10 and X23 source-dependent amplitude/centroid differences prohibit a uniform physical-defect explanation.

Every source is classified GEOMETRIC_PROXY_ASSOCIATION_ONLY. Original processed measured fronts, documentary mean toe descriptors and existing geometric proxies are distinguished. No authenticated measured toe trajectory in the qualified frame was found; unreviewed historical candidates were not promoted to toe truth. No curve was extracted from stress maxima. Native loading-cap and gauge coordinates were verified against all thirteen selected M2 meshes, while the evaluation core is distinguished from a physical FE boundary. Direct high-area/cap coincidence is absent; causal nonlocal boundary influence remains unresolved. The physical meaning of the bands is not experimentally established.

## Manuscript and figures

The English manuscript has twenty rendered pages, nine embedded main figures, five tables and four editable native OMML equations. All twenty page PNGs were visually inspected. After correcting compressed 3D axis labels, final page 3 was reinspected and the other nineteen pages are pixel-identical to the inspected render. No unresolved clipped equation, table, caption or image remains. Table 3 continues across pages with a repeated header. Nine main figure pairs, thirty-one retrospective supplementary spatial pairs and the root plate-comparison pair pass image/PDF readability checks. Physical plot aspect is declared, direct prediction/reference scales match, and error scales are zero-centered. Captions retain identity/context/seed/unit/numerical-field and proxy limitations. The sixteen verified R1 references are text-identical. R2_CLAIM_EVIDENCE_MATRIX.csv retains original claim links and adds new comparison/spatial cells with explicit retrospective provenance.

## Scope and remaining limitations

No new FE solve, meshing, geometry reconstruction for analysis, target calculation, training, fitting, fine-tuning or inference was performed. R8-E16 and R1 remain unchanged. Every added numerical/spatial diagnostic is retrospective, without new source selection, changed core, new context or seed selection. Fresh independent generalization and physical stress validation remain unavailable, as do authenticated spatial toe truth and causal boundary attribution. These limitations are explicit findings rather than omitted checks. Public deposition, authorship and journal-specific editorial review remain author responsibilities; acceptance or deployment readiness is not guaranteed. No additional research phase is opened.
'''
(D/'R2_FINAL_SCIENTIFIC_QUALITY_AUDIT.md').write_text(audit,encoding='utf-8')
required=['MANUSCRIPT_REVISION_R2.md','MANUSCRIPT_REVISION_R2.docx','R2_ENGINEERING_REVIEW_REPORT.md','R2_PLATE_HIGH95_COMPARISON.csv','R2_SOURCE_HIGH95_COMPARISON.csv','R2_X_PLATE_DIAGNOSTIC.md','R2_GEOMETRY_STRESS_SPATIAL_AUDIT.csv','R2_WELD_TOE_EVIDENCE_CLASSIFICATION.md','R2_BOUNDARY_CONDITION_INTERPRETATION.md','R2_MAIN_FIGURE_SELECTION.md','R2_REVISED_FIGURE_CAPTIONS.md','R2_CLAIM_EVIDENCE_MATRIX.csv','R2_MANUSCRIPT_CHANGELOG.md','R2_SUPPLEMENTARY_MATERIAL_PLAN.md','R2_FINAL_SCIENTIFIC_QUALITY_AUDIT.md','PLATE_LEVEL_HIGH95_REAUDIT.csv','SOURCE_LEVEL_HIGH95_REAUDIT.csv','X_PLATE_N2_N3_COMPARISON.md','SEED_SPECIFIC_LOCALIZATION_RESULTS.csv','PLATE_LOCALIZATION_CONTRAST_FIGURE.png','PLATE_LOCALIZATION_CONTRAST_FIGURE.pdf']
assert all((D/p).is_file() and (D/p).stat().st_size>0 for p in required)
# Internal render PDFs/PNGs are deliberately omitted from the manuscript delivery.
def eligible(p):
 rel=p.relative_to(D)
 if rel.parts[0]=='qa' and len(rel.parts)>1 and rel.parts[1].startswith('docx_'):return False
 return p.is_file() and p.suffix.lower() not in ['.zip','.pyc'] and p.name not in ['REPRODUCIBILITY_MANIFEST.json','DELIVERY_VERIFICATION.json'] and '__pycache__' not in rel.parts
files=[dict(path=p.relative_to(D).as_posix(),size_bytes=p.stat().st_size,SHA256=sha(p)) for p in sorted(D.rglob('*')) if eligible(p)]
manifest=dict(release='WeldStressAI_ManuscriptRevision_R2',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),decisions=decisions,research_decision='METHOD_IMPROVEMENT_MIXED',scope='Editorial revision and retrospective frozen-output diagnostics only',original_release_integrity=releases,consumed_inputs_check='qa/FINAL_CONSUMED_INPUT_SHA256_CHECK.csv',files=files,excluded='Self manifest, final ZIP/receipt and internal DOCX render intermediates; native research binaries stay unchanged at their recorded absolute paths.')
mp=D/'REPRODUCIBILITY_MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
archive=D/'WeldStressAI_ManuscriptRevision_R2_Package.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for row in files:z.write(D/row['path'],row['path'])
 z.write(mp,mp.name)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for row in files:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['SHA256']
 assert z.read(mp.name)==mp.read_bytes()
receipt=dict(status='PASS',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),decisions=decisions,required_outputs=len(required),manifest_files=len(files),ZIP_entries=len(files)+1,ZIP_size_bytes=archive.stat().st_size,ZIP_SHA256=sha(archive),manifest_SHA256=sha(mp),CRC_and_each_entry_SHA256='PASS',all_original_release_hashes='PASS',consumed_inputs_verified=len(checks),manuscript_pages=20,uncompleted_requested_release_checks=[],scientific_limits=['No fresh independent generalization validation','No physical toe/stress validation','Causal boundary-versus-geometry mechanism unresolved'],new_research_execution=False)
(D/'DELIVERY_VERIFICATION.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8');print(json.dumps(receipt),flush=True)
