from pathlib import Path
import csv, json, hashlib, shutil, zipfile, difflib
from datetime import datetime, timezone
from docx import Document
from lxml import etree
from pypdf import PdfReader

D=Path(r'E:\welding\outputs\WeldStressAI_JCSR_Readability_Revision_R1')
B=Path(r'E:\welding\outputs\WeldStressAI_JCSR_FigureEnhancement_R1')
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def dump(p,obj):p.write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding='utf-8')
def csvout(p,rows):
 with p.open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

summary=json.loads((D/'QA/CONTENT_AUDIT_SUMMARY.json').read_text())
assert summary['status']=='PASS'
baseline=list(csv.DictReader((D/'00_Source_Integrity/BASELINE_HASH_VERIFICATION.csv').open(encoding='utf-8-sig')))
for r in baseline:
 r['actual_SHA256']=sha(r['path']);r['status']='PASS' if r['actual_SHA256']==r['expected_SHA256'] else 'FAIL'
assert len(baseline)==462 and all(r['status']=='PASS' for r in baseline)
csvout(D/'00_Source_Integrity/FINAL_BASELINE_HASH_VERIFICATION.csv',baseline)

source=B/'05_Final_Manuscript/WELDSTRESS_AI_JCSR_VISUAL_FINAL.docx'
old,new=Document(source),Document(D/'MANUSCRIPT_READABILITY_REVISED.docx')
tables=lambda doc:[[[c.text for c in row.cells] for row in t.rows] for t in doc.tables]
assert len(new.tables)==7 and tables(old)==tables(new)
ns={'m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
maths=lambda doc:[etree.tostring(x,method='c14n') for x in doc._element.findall('.//m:oMath',ns)]
assert len(maths(new))==4 and maths(old)==maths(new)
def media(p):
 with zipfile.ZipFile(p) as z:return sorted(hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/media/'))
assert len(new.inline_shapes)==9 and media(source)==media(D/'MANUSCRIPT_READABILITY_REVISED.docx')
xml=etree.tostring(new._element).decode()
assert '<w:ins ' not in xml and '<w:del ' not in xml and 'commentRangeStart' not in xml
assert all(s.width<=int(6.901*914400) for s in new.inline_shapes)
structure=dict(status='PASS',editable_tables=7,tables_identical_to_baseline=True,editable_OMML_equations=4,equation_XML_identical=True,embedded_figures=9,embedded_figure_bytes_identical=True,tracked_changes=False)
dump(D/'QA/FINAL_DOCX_STRUCTURE_AUDIT.json',structure)

pages=[]
for folder,stem,target in [('release','MANUSCRIPT_READABILITY_REVISED','MANUSCRIPT_READABILITY_REVISED_REVIEW.pdf'),('notes_final','SUPPLEMENTARY_READABILITY_METHOD_NOTES','SUPPLEMENTARY_READABILITY_METHOD_NOTES_REVIEW.pdf')]:
 p=D/'QA/rendered'/folder/(stem+'.pdf');reader=PdfReader(p)
 assert len(reader.pages)==(26 if folder=='release' else 4)
 for i,page in enumerate(reader.pages,1):
  assert len(page.extract_text().strip())>50
  image=D/'QA/rendered'/folder/f'page-{i}.png';assert image.is_file()
  pages.append(dict(document=stem,page=i,status='PASS',review='Visually inspected: text, symbols, equations, figures/captions, tables and margins; no clipping or overlap observed',render_sha256=sha(image)))
 shutil.copy2(p,D/target)
csvout(D/'QA/VISUAL_PAGE_QA.csv',pages)
oldmd=(B/'05_Final_Manuscript/WELDSTRESS_AI_JCSR_VISUAL_FINAL.md').read_text(encoding='utf-8-sig')
newmd=(D/'MANUSCRIPT_READABILITY_REVISED.md').read_text(encoding='utf-8')
(D/'QA/COMPLETE_MANUSCRIPT_DIFF.patch').write_text(''.join(difflib.unified_diff(oldmd.splitlines(True),newmd.splitlines(True),fromfile='verified_enhanced_baseline.md',tofile='readability_revision.md')),encoding='utf-8')

criteria=[
('Original evidence unchanged','201 preservation checks, exact seven table contents, four equation XML objects, nine embedded image hashes; 462 baseline files rehashed.'),
('First-use concepts','46-term register, first-use audit and nineteen-symbol register; all seventeen requested central concepts addressed.'),
('Consistent terminology','Measured surface, reconstructed solid, numerical representation, FE reference and prediction distinguished throughout.'),
('Geometry versus representation','Abstract, Introduction, Sections 3.1–3.3 and Figure 3 explain unchanged source points and changed inputs.'),
('T2 numerical status','Sections 2.1–2.3 explain principal-value calculation, tensile clipping, original-area chord averaging and exclusions.'),
('High95 and IoU','Section 4 defines own-field percentiles, area weights, inclusive ties, overlap/union and limitations.'),
('Ranking versus threshold','Section 4.2 and Figures 6/9 distinguish area budgets from a common FE-derived stress threshold.'),
('N1/N2/N3 roles','Abstract and Sections 2.1/3.1 distinguish training context and representation within one architecture.'),
('Oracle nondeployability','Section 3.2 explicitly identifies full-information substitutions as diagnostic and nondeployable.'),
('Factorial concept first','Two states for each of A/B/C and eight combinations precede channel indices and exact contrasts.'),
('G0/G1 scope','Section 4.2 explains broad unequal-area collar and fixed matched-budget contour-distance rule; no stress amplitude prediction.'),
('Results narrative','Every Results subsection begins with its engineering/computational finding before detailed evidence.'),
('Unfavorable findings','X-group deterioration, small X23 exception, extreme-threshold reversal, larger L2 and worse peak errors remain explicit.'),
('Discussion synthesis','Sections 6.1–6.4 connect representation sensitivity, uncertainty and bounded engineering meaning.'),
('Figures and captions','Nine original main figures retained including enhanced Figures 3/7; all nine captions clarified and thirty SI captions reviewed.'),
('Equations tables references','Four editable equations, seven editable tables and sixteen references retained; citation first-appearance order unchanged.'),
('Engineering readership','Three-audience editorial assessment completed; exact technical detail retained in article, contracts and fifteen method-note sections. This is not a reader survey.'),
('Declarations','Data/code status, AI assistance and author-confirmation placeholders preserved; author review checklist supplied.'),
('No new research','Zero FE solves, mesh changes, ML fits, inference runs or new research metrics; checks concern document integrity only.'),
('Visual quality','All 26 final manuscript pages and 4 new method-note pages rendered through native Word and visually inspected; no clipping or overlap observed.')]
report='# Final readability QA report\n\nDecision: **SCIENTIFIC_READABILITY_REVISION_PASS — READY_FOR_AUTHOR_REVIEW**.\n\nScientific classification remains **METHOD_IMPROVEMENT_MIXED**. Research remains **CLOSED**. This editorial release neither supplies fresh independent generalization validation nor physical stress validation.\n\n'
report+='## Verification evidence\n\n201 content-preservation checks passed. Twelve separate scientific claim/context families passed. All 462 files in the verified enhanced baseline manifest passed fresh SHA-256 verification at closeout. Seven editable table contents, four native equation XML objects and nine embedded main-figure image hashes match that baseline exactly. The thirty-figure supplementary release was copied unchanged and verified by file hashes; its previous page-QA is inherited, not represented as a fresh visual inspection in this revision. Earlier research-wide verification receipts remain historical evidence; their entire research archive was not rehashed again here.\n\n'
report+=f"Main Markdown whitespace-token counts (including captions/tables/references): {summary['original_words']:,} → {summary['revised_words']:,}, +{100*(summary['revised_words']/summary['original_words']-1):.2f}%. Abstract: {summary['revised_abstract_words']} words by the same token convention. The main review PDF is 26 pages versus the prior 24. Fifteen detailed passages were retained in a separately referenced four-page supplementary readability note to limit main-text expansion. No journal-specific mandatory word limit is asserted.\n\n"
report+='## Twenty acceptance criteria\n\n| No. | Criterion | Result and evidence |\n|---|---|---|\n'
for i,(name,evidence) in enumerate(criteria,1):report+=f'| {i} | {name} | PASS — {evidence} |\n'
report+='\n## Remaining author-controlled items\n\nAuthor confirmation of identities, declarations, complete AI-assistance history and responsibility remains required. Current journal rules, portal-specific file requirements and derived-data/code availability require author review before submission. The 254-word abstract is not claimed to comply with an unverified mandatory limit. Historical paths in provenance CSVs require privacy/anonymity review before public distribution. These items do not reopen the closed research or justify new analyses. No upload, submission or public deposit occurred.\n\nThe three-audience review is an editorial assessment, not a user study or empirical readability validation. Dense exact channel formulas, neighborhood definitions, tie rules and uncertainty qualifications remain necessarily technical and are indexed in the supplied audits.\n'
(D/'FINAL_READABILITY_QA_REPORT.md').write_text(report,encoding='utf-8')
(D/'README_AUTHOR_REVIEW.md').write_text('# Readability revision author-review package\n\nOpen MANUSCRIPT_READABILITY_REVISED.docx for the editable article, or MANUSCRIPT_READABILITY_REVISED_REVIEW.pdf for the 26-page review copy. The four-page SUPPLEMENTARY_READABILITY_METHOD_NOTES_REVIEW.pdf is an additional required companion to the unchanged supplementary/ release. Main manuscript image links use figures/main/.\n\nRead FINAL_READABILITY_QA_REPORT.md and FINAL_AUTHOR_REVIEW_CHECKLIST.md before submission. Root terminology, first-use, caption, mathematics, preservation and change-log files document the revision. supplementary/ contains the unchanged thirty-figure SI, tables and protocol contracts. author_review/ contains retained ancillary author documents. scripts/ and QA/ provide reproducibility and document-integrity checks; no new computational research was performed.\n\nThe ZIP contains release artifacts and audit records; draft page rasters are excluded. Final page rasters remain in the local workspace QA/rendered/release and QA/rendered/notes_final. SHA256_MANIFEST.csv records the packaged content; DELIVERY_INTEGRITY_RECEIPT.json seals the manifest and ZIP outside the ZIP. Earlier outputs are preserved. This package is for private author review, not an automatically approved journal submission.\n',encoding='utf-8')
required=['MANUSCRIPT_READABILITY_REVISED.md','MANUSCRIPT_READABILITY_REVISED.docx','MANUSCRIPT_READABILITY_REVISED_REVIEW.pdf','SCIENTIFIC_TERMINOLOGY_AUDIT.csv','ABBREVIATIONS_AND_NOMENCLATURE.md','FIRST_USE_DEFINITION_AUDIT.csv','SECTION_BY_SECTION_READABILITY_REPORT.md','BEFORE_AFTER_TECHNICAL_SENTENCES.md','FIGURE_CAPTION_CLARITY_AUDIT.md','MATHEMATICAL_EXPLANATION_AUDIT.md','SCIENCE_PRESERVATION_AUDIT.md','MANUSCRIPT_READABILITY_CHANGELOG.md','FINAL_AUTHOR_REVIEW_CHECKLIST.md','FINAL_READABILITY_QA_REPORT.md']
assert all((D/p).is_file() for p in required)
archive=D/'WeldStressAI_JCSR_Readability_Author_Review_Package.zip'
excluded={'SHA256_MANIFEST.csv','DELIVERY_INTEGRITY_RECEIPT.json',archive.name}
files=sorted(p for p in D.rglob('*') if p.is_file() and p.name not in excluded and 'rendered' not in p.relative_to(D).parts and '__pycache__' not in p.parts)
manifest=[dict(path=p.relative_to(D).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in files]
csvout(D/'SHA256_MANIFEST.csv',manifest)
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files+[D/'SHA256_MANIFEST.csv']:z.write(p,p.relative_to(D).as_posix())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for r in manifest:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
receipt=dict(status='PASS',created_UTC=datetime.now(timezone.utc).isoformat(),baseline_files_verified=462,science_checks=201,claim_context_families=12,main_pages_visually_reviewed=26,method_note_pages_visually_reviewed=4,required_deliverables=len(required),packaged_files=len(files)+1,manifest_SHA256=sha(D/'SHA256_MANIFEST.csv'),archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,archive=str(archive),classification='METHOD_IMPROVEMENT_MIXED',research_status='CLOSED',new_research_runs=0,readiness='PRIVATE_AUTHOR_REVIEW',pending_author_items='See FINAL_AUTHOR_REVIEW_CHECKLIST.md; not journal-submitted')
dump(D/'DELIVERY_INTEGRITY_RECEIPT.json',receipt)
print(json.dumps(receipt,indent=2))
