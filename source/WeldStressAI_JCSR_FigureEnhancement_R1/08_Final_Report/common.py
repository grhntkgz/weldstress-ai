from pathlib import Path
import hashlib,json,csv,shutil,datetime,re
D=Path(__file__).resolve().parents[1]
J=Path(r'E:\welding\outputs\WeldStressAI_JCSR_Submission_Final')
P=Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRobustness_R2_1')
R=Path(r'E:\welding\outputs\WeldStressAI_FinalResearch_PhaseR8E16')
for folder in ['00_Source_Integrity','01_Enhanced_Figure03','02_New_Figure07','03_Other_Figure_Updates','04_Supplementary_Update','05_Final_Manuscript','06_Scientific_QA','07_Updated_Submission_Package','08_Final_Report']:(D/folder).mkdir(exist_ok=True,parents=True)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def arrsha(a):return hashlib.sha256(a.tobytes(order='C')).hexdigest()
def write(p,s):
 p=D/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
def js(p,o):write(p,json.dumps(o,ensure_ascii=False,indent=2))
def rows(p):
 with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def table(p,rs):
 p=D/p;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',newline='',encoding='utf-8-sig') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
def copy(src,dest):
 dest=D/dest;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
