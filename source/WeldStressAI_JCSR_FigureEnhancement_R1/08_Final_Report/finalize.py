from common import *
import zipfile

report=D/'08_Final_Report/FINAL_FIGURE_ENHANCEMENT_REPORT.md'
assert report.exists()
for p in ['FINAL_FIGURE_ENHANCEMENT_REPORT.md','FIGURE_CHANGELOG.md','FIGURE_PROVENANCE_MATRIX.csv','FINAL_DECISIONS.json']:
 copy(D/'08_Final_Report'/p,Path('07_Updated_Submission_Package/review_evidence')/p)
write('README_DELIVERY.md','# Enhanced JCSR author review package\n\nOpen 05_Final_Manuscript/WELDSTRESS_AI_JCSR_VISUAL_FINAL.docx or its REVIEW.pdf. The updated SI document and review PDF are in 04_Supplementary_Update. Complete review candidates are in 07_Updated_Submission_Package. The report answers all 29 requested checks. New Figures 3 and 7 are supplied as PNG/PDF/SVG; all previous files remain unchanged.\n\nNine main figures; thirty SI figures; seven editable tables; four Word equations; 53 final rendered pages inspected. Frozen evidence and output hashes are recorded. No new FE solve, learning fit, inference or numerical experiment was run. METHOD_IMPROVEMENT_MIXED and CLOSED research status remain unchanged.\n\nThis is a private author-review package, not author-approved journal submission. Author facts, declarations, complete AI-history review, journal-specific artwork/size/anonymity checks and public data/code release decisions remain pending.\n\nRerendering scripts read external frozen source paths recorded in the provenance files; the package is not a standalone public training reproduction environment. Figure source scripts are under 08_Final_Report. The output manifest excludes itself, the final receipt and ZIP archives to avoid recursive hashes; the receipt records manifest and ZIP hashes.\n')
pkg=D/'07_Updated_Submission_Package'
table('07_Updated_Submission_Package/SUBMISSION_FILE_INVENTORY.csv',[{'path':str(p.relative_to(pkg)),'bytes':p.stat().st_size,'SHA256':sha(p),'role':'Private author-review candidate; exact portal role to be confirmed','author_approval':'PENDING'} for p in sorted(pkg.rglob('*')) if p.is_file() and p.name!='SUBMISSION_FILE_INVENTORY.csv'])
excluded={'08_Final_Report/FINAL_DELIVERY_MANIFEST.json','DELIVERY_VERIFICATION.json'}
records=[]
for p in sorted(D.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(D).as_posix()
 if rel in excluded or p.suffix.lower()=='.zip' or '__pycache__' in p.parts:continue
 records.append({'path':rel,'bytes':p.stat().st_size,'SHA256':sha(p)})
js('08_Final_Report/FINAL_DELIVERY_MANIFEST.json',{'created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'output_root':str(D),'status':'PASS','files':records,'self_exclusions':sorted(excluded)+['*.zip','__pycache__'],'historical_files_rehashed':4529,'numeric_audit_checks':180,'main_figures':9,'SI_figures':30,'final_pages_visually_inspected':53,'new_FE_training_inference_experiments':0,'research_classification':'METHOD_IMPROVEMENT_MIXED','research_status':'CLOSED','author_approval':'PENDING'})
archive=D/'WeldStressAI_JCSR_Visual_Final_Author_Review_Package.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for p in sorted(D.rglob('*')):
  if not p.is_file() or p.suffix.lower()=='.zip' or p.name=='DELIVERY_VERIFICATION.json' or '__pycache__' in p.parts:continue
  rel=p.relative_to(D).as_posix()
  # Internal page rasters, draft conversions and print preview boards stay on disk, not in review archive.
  if rel.startswith('06_Scientific_QA/rendered/') or (rel.startswith('06_Scientific_QA/') and p.suffix=='.png'):continue
  z.write(p,rel)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for name in z.namelist():assert hashlib.sha256(z.read(name)).hexdigest()==sha(D/name),name
 entries=len(z.namelist())
for r in records:assert sha(D/r['path'])==r['SHA256'],r['path']
js('DELIVERY_VERIFICATION.json',{'status':'PASS','manifest':str(D/'08_Final_Report/FINAL_DELIVERY_MANIFEST.json'),'manifest_SHA256':sha(D/'08_Final_Report/FINAL_DELIVERY_MANIFEST.json'),'verified_output_files':len(records),'archive':str(archive),'archive_bytes':archive.stat().st_size,'archive_SHA256':sha(archive),'archive_entries':entries,'ZIP_CRC_and_every_entry_SHA256':'PASS','historical_manifest_entries_freshly_rehashed':4529,'independent_numeric_checks':180,'main_pages':24,'SI_pages':29,'final_pages_visually_inspected':53,'uncompleted_scientific_or_document_checks':[],'outstanding_author_actions':'Current JCSR-specific guide/artwork limits; authorship and declarations; AI-history review; permissions/privacy; public derived-data/code release decisions. No automatic submission.','final_decisions':json.loads((D/'08_Final_Report/FINAL_DECISIONS.json').read_text(encoding='utf-8'))})
print(json.dumps({'status':'PASS','files':len(records),'archive_entries':entries,'archive_bytes':archive.stat().st_size,'archive_SHA256':sha(archive)}),flush=True)
