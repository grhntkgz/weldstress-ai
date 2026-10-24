"""Use the packaged rasterizer, substituting installed Word only for unavailable LibreOffice conversion."""
import importlib.util,subprocess,sys,os,json
from pathlib import Path
package=Path(r'C:\Users\grhnt.DESKTOP-KRBB26F\.codex\plugins\cache\openai-primary-runtime\documents\26.1022.11436\skills\documents\render_docx.py')
spec=importlib.util.spec_from_file_location('packaged_render_docx',package);renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
def word_to_pdf(doc_path,user_profile,convert_tmp_dir,stem,verbose):
 dest=str(Path(convert_tmp_dir)/(stem+'.pdf'))
 # Powershell literal strings safely escape only single quotes; no string-built file operations.
 a=str(Path(doc_path).resolve()).replace("'","''");b=dest.replace("'","''")
 script=f"$ErrorActionPreference='Stop'; $wordTask=New-Object -ComObject Word.Application; $wordTask.Visible=$false; $wordTask.DisplayAlerts=0; try {{ $docTask=$wordTask.Documents.Open('{a}',$false,$true); $docTask.ExportAsFixedFormat('{b}',17); $docTask.Close(0) }} finally {{ $wordTask.Quit() }}"
 proc=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',script],capture_output=True,text=True,timeout=120)
 if proc.returncode or not Path(dest).exists():raise RuntimeError('Native Word conversion failed: '+proc.stdout+proc.stderr)
 return dest,'Native Microsoft Word COM conversion; packaged Poppler rasterization; LibreOffice unavailable.'
renderer.convert_to_pdf=word_to_pdf
if __name__=='__main__':renderer.main()
