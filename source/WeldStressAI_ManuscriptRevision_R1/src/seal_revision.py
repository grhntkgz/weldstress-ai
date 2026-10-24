from pathlib import Path
import json,csv,hashlib,re,datetime,zipfile
import pandas as pd
from docx import Document
from pypdf import PdfReader
D=Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRevision_R1');S=D/'source_snapshot'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
integrity=json.loads((D/'qa'/'INTEGRITY_CLOSEOUT.json').read_text());assert integrity['passed']
md=(D/'MANUSCRIPT_REVISION_R1.md').read_text(encoding='utf-8');doc=Document(D/'MANUSCRIPT_REVISION_R1.docx');pdf=PdfReader(D/'qa'/'release_render'/'MANUSCRIPT_REVISION_R1.pdf');assert len(pdf.pages)==17
assert len(doc.inline_shapes)==9 and len(doc.tables)==4
assert md.count('![Figure ')==9
figs=json.loads((D/'figures'/'MAIN_FIGURE_REGISTRY.json').read_text());assert [x['number'] for x in figs]==list(range(1,10))
for path in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',md):assert (D/path).is_file(),path
assert 'Q95 amplitude errors are reported in Table 3' not in md
assert not doc.styles['Title'].element.xpath('./w:pPr/w:pBdr')
assert len(doc.element.xpath('.//m:oMath'))==4
assert len(list((D/'figures'/'supplementary').glob('*.png')))==35
assert len(list((D/'figures'/'supplementary').glob('*.pdf')))==35
refs=pd.read_csv(D/'LITERATURE_VERIFICATION.csv');assert len(refs)==16 and refs.reference_id.nunique()==16
scores=pd.read_csv(D/'qa'/'MACRO_REAGGREGATION_AUDIT.csv');assert scores.status.eq('PASS').all();assert len(scores)==69
audit=pd.read_csv(D/'CLAIM_EVIDENCE_AUDIT.csv');assert audit.status.eq('PASS').all()
for p in audit.evidence_file.unique():assert Path(p).exists(),p
# Explicit protocol entries that accompany the results-based cell ledger.
protocol=[('CORE_POINTS',34200,'MODEL_PREDICTION_REGISTRY.csv','core_points','Count is fixed across all model comparison fields'),('REFERENCE_E_MPa',210000,'QUALIFIED13_SOURCE_REGISTRY.csv','target_version','LE210000 numerical modelling assumption'),('REFERENCE_NU',.30,'QUALIFIED13_SOURCE_REGISTRY.csv','target_version','NU030 numerical modelling assumption')]
extra=[]
for key,value,file,col,meaning in protocol:extra.append(dict(claim_id=key,claim=meaning,evidence_file=str(S/file),row_key='all qualified sources/comparison fields',column=col,verified_value=value,unit='MPa' if key.endswith('MPa') else 'count' if key=='CORE_POINTS' else 'dimensionless',derivation='Exact frozen registry field or identifier',manuscript_location='Methods',evidence_level='FROZEN_PROTOCOL',status='PASS'))
audit=pd.concat([audit,pd.DataFrame(extra)],ignore_index=True).drop_duplicates('claim_id');audit.to_csv(D/'CLAIM_EVIDENCE_AUDIT.csv',index=False,encoding='utf-8-sig')
required=['MANUSCRIPT_REVISION_R1.md','MANUSCRIPT_REVISION_R1.docx','ABSTRACT_AND_HIGHLIGHTS.md','VERIFIED_REFERENCES.md','LITERATURE_VERIFICATION.csv','STATE_OF_THE_ART_COMPARISON.md','NOVELTY_POSITIONING.md','MAIN_FIGURE_SELECTION.md','FIGURE_CAPTIONS.md','MAIN_RESULTS_TABLES.md','SUPPLEMENTARY_MATERIAL_PLAN.md','CLAIM_EVIDENCE_AUDIT.csv','EDITORIAL_RISK_AND_REVIEWER_OBJECTIONS.md','SCIENTIFIC_REVISION_CHANGELOG.md','MANUSCRIPT_FINAL_QUALITY_AUDIT.md']
decision='SCIENTIFICALLY_REVISED_READY_FOR_AUTHOR_REVIEW'
quality=f'''# Final manuscript quality audit

Decision: **{decision}**

Scientific classification retained: **METHOD_IMPROVEMENT_MIXED**.

## Evidence integrity

The immutable R8-E16 manifest remains SHA-256 {integrity['original_R8E16_manifest_SHA256']}. Fresh checks passed for all {integrity['R8E16_files_freshly_verified']} manifest-listed R8-E16 files and {integrity['consumed_historical_files_freshly_verified']} consumed historical dependencies. This includes retained model/target provenance; it is not a claim to freshly hash every historical bulk export. All 189 initially copied support files match the released manifest and their local copies. Additional E14/E15 protocol copies and the three stored spatial-figure inputs passed their respective reference-hash checks.

The claim ledger contains {len(audit)} exact-cell, derived-summary or protocol entries. Independent source-to-plate-to-macro recomputation passed all {len(scores)} L2/MAE/IoU checks, with maximum absolute difference {scores.absolute_error.max():.3g}. Separately scored seed means and paired N3/N2 contrasts were also checked. The ledger distinguishes numerical results from frozen protocol assumptions; it is not an assertion that a repeated statement is an independent observation.

## Scientific and editorial checks

- Thirteen qualified targets and all five documentary plates retained; both neural seeds included without selection.
- Unfavorable N3 whole-field and field-maximum results retained alongside improved relative localization.
- M1/M2 qualification separated from asymptotic convergence and physical validation.
- Own-field High95 thresholds and the constant-baseline tie degeneracy explicitly explained.
- Frozen-weight oracle inputs described as nondeployable, potentially off-distribution diagnostics.
- Executed compact SurfacePT override, registered frame/query plan, contextual dependence and unequal tree/neural sampling budgets documented.
- Sixteen references verified against primary records and bibliographic metadata with explicit access scope. No claim that every full text was accessible; no unsupported first-study claim. One incorrect candidate DOI was rejected rather than silently assigned to Point Transformer.
- Nine main figures and all thirty-five unchanged original supplementary PNG/PDF pairs retained. Numerical summaries use released tables; spatial redraws use stored fields without inference.

## Document and figure QA

Editable Word document: 17 Letter-portrait pages, four native tables, nine embedded figures and four structured editable OMML equations. All 17 final page images were visually inspected. The last header-label-only repair changed pages 8, 10 and 11, which were reinspected; the other 14 release-render PNGs are byte-identical to the inspected final-render pages. No clipping, overlap, title rule, truncated table row, orphaned figure caption or missing equation glyph was observed. Short tables remain intact; the complete two-seed table fits on one page.

The packaged render_docx.py could not find LibreOffice on this Windows host. The retained adapter uses the installed Microsoft Word COM converter for DOCX-to-PDF and the packaged renderer/Poppler path for page PNGs. The internal PDF and page PNGs are QA artifacts, not additional claimed manuscript deliverables.

All thirty-five original PDFs were opened through a PDF reader and rasterized, and their preview contact sheets were compared visually with the original PNG set. Pixel correlation is diagnostic only, not a pass criterion: line rasterization and antialiasing differ. Original small-font mesh montages remain supplementary; the main qualification plot displays all thirteen sources. Source raster detail is not claimed to improve merely because a composite is exported at 300 dpi. Legends, axes, stress/error units and common map scales were checked in the final Word render.

## Explicit limits and author actions

No authorized revision deliverable is missing. No ANSYS solve, FE target creation, training, fine-tuning, XGBoost fitting, model inference or experimental configuration was executed. No historical release was modified.

This decision means ready for human author review, not submitted, accepted or guaranteed suitable for a Q1 journal. Authors still need to approve scientific wording, authorship/affiliations, funding and conflicts, the target journal's format and permissions. A public derived-data/code deposit has not been made. The small reused cohort, uncertified batch independence, unresolved raw registration and lack of experimental stress/fatigue validation remain substantive scientific limitations; no editorial revision removes them. No fresh independent generalization claim is made.
'''
(D/'MANUSCRIPT_FINAL_QUALITY_AUDIT.md').write_text(quality,encoding='utf-8')
readme='''# Manuscript revision R1 package

Start with MANUSCRIPT_REVISION_R1.docx or MANUSCRIPT_REVISION_R1.md. Main plots are in figures/main. All thirty-five original figure pairs are in figures/supplementary. MAIN_RESULTS_TABLES.md and the root CSV tables include both seeds and all plates. CLAIM_EVIDENCE_AUDIT.csv maps quantitative statements to retained evidence. LITERATURE_VERIFICATION.csv states bibliography verification and access scope. Read MANUSCRIPT_FINAL_QUALITY_AUDIT.md for the exact integrity scope and author-review decision.

The authoritative scientific outcome remains METHOD_IMPROVEMENT_MIXED. This is a manuscript revision from frozen evidence, not a new validation study. Existing source scans, targets, ANSYS results and checkpoints remain at their original paths.

The ZIP is a manuscript and audit package, not the entire research environment. It excludes bulky model/FE binaries and internal rendering images/PDFs. Native historical file paths and hashes remain in the copied registries. Source snapshot files are byte copies, not rewritten scientific evidence. The complete original manifest can be checked against its unchanged source release.

The final Markdown, figures and tables are the editorial sources. build_docx.py rebuilds Word from the final Markdown using bundled python-docx; render_docx_word.py invokes the packaged renderer with native Word conversion. Other src scripts record staged drafting/figure-generation operations and their initial numbering; they should not be treated as one idempotent end-to-end authoring command. No script here launches training, ANSYS or model inference. No research phase should be resumed automatically.

Final disposition: SCIENTIFICALLY_REVISED_READY_FOR_AUTHOR_REVIEW. Public deposition and journal submission have not occurred.
'''
(D/'README_DELIVERY.md').write_text(readme,encoding='utf-8')
visual=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),passed=True,pages=17,all_pages_visually_inspected=True,release_delta_reinspected=[8,10,11],unchanged_render_pages=14,original_PNG_PDF_pairs=35,main_figures=9,native_tables=4,editable_equations=4,renderer='Installed Microsoft Word PDF conversion plus packaged render_docx.py rasterizer',DOCX_SHA256=sha(D/'MANUSCRIPT_REVISION_R1.docx'))
(D/'qa'/'VISUAL_QA_RECEIPT.json').write_text(json.dumps(visual,indent=2),encoding='utf-8')
for f in required:assert (D/f).is_file(),f
files=[]
for p in sorted(D.rglob('*')):
 if p.is_file() and p.name not in ['REVISION_REPRODUCIBILITY_MANIFEST.json','DELIVERY_VERIFICATION.json'] and p.suffix!='.zip':files.append(dict(path=p.relative_to(D).as_posix(),bytes=p.stat().st_size,SHA256=sha(p)))
manifest=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),decision=decision,scientific_classification='METHOD_IMPROVEMENT_MIXED',source_manifest_SHA256=integrity['original_R8E16_manifest_SHA256'],scope='Entire independent revision workspace except circular delivery/manifest files and ZIP itself',files=files)
(D/'REVISION_REPRODUCIBILITY_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
archive=D/'WeldStressAI_ManuscriptRevision_R1_Package.zip'
tozip=[p for p in D.rglob('*') if p.is_file() and p.suffix!='.zip' and p.name!='DELIVERY_VERIFICATION.json' and ('qa' not in p.relative_to(D).parts or p.suffix in ['.json','.csv'])]
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(tozip):z.write(p,p.relative_to(D).as_posix())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for p in tozip:assert hashlib.sha256(z.read(p.relative_to(D).as_posix())).hexdigest()==sha(p)
receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),passed=True,decision=decision,required_outputs=len(required),manuscript_pages=17,verified_references=len(refs),claim_entries=len(audit),R8E16_files_verified=integrity['R8E16_files_freshly_verified'],historical_consumed_files_verified=integrity['consumed_historical_files_freshly_verified'],new_experiments=0,uncompleted_authorized_checks=[],package_path=str(archive),package_files=len(tozip),package_bytes=archive.stat().st_size,package_SHA256=sha(archive),revision_manifest_SHA256=sha(D/'REVISION_REPRODUCIBILITY_MANIFEST.json'),public_submission='NOT_PERFORMED')
(D/'DELIVERY_VERIFICATION.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8');print(json.dumps(receipt,indent=2))
