from common_e16 import *
import re,numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
def polish(text):
 lines=[];references=False
 for line in text.splitlines():
  if line.startswith('## References'):references=True
  if references or line.startswith('|'):lines.append(line);continue
  line=line.replace('L 20.','L2 0.').replace('L 2 ','L2 ').replace('High 95','High95').replace('asmethod','as method');line=re.sub(r'\b(is|for|from|at|by|of|as)(?=(?:N[123]\b|B[012]\b|[CEGHX]\d{2}|[CEGHX]/|METHOD_))',r'\1 ',line);line=re.sub(r'\bblock([ABC])\b',r'block \1',line)
  protected=[]
  def hide(m):protected.append(m.group());return chr(0xe000+len(protected)-1)
  line=re.sub(r'https?://\S+|(?:[A-Z]:/|[A-Z]:\\)\S+|(?:DOI)?10\.\d{4,9}/\S+|\b[A-Za-z0-9]+_[A-Za-z0-9_./:-]+|\b(?:N[123]|B[012]|T[02]|S[01]|M[12]|X50|X43|L2|R2|Q95|High95|SOLID187|Tet10|F[01]{3}|F[1-5]|[CEGHX]\d{2}(?:-V1-S355-AW)?)\b',hide,line)
  line=re.sub(r'(?<=\d)[eE](?=[+-]?\d)',lambda m:'\uefff',line);line=re.sub(r'(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])',' ',line);line=line.replace('\uefff','e');line=re.sub(r',(?=[A-Za-z0-9])',', ',line)
  for i,value in enumerate(protected):line=line.replace(chr(0xe000+i),value)
  line=line.replace('3 D','3D')
  lines.append(line)
 return '\n'.join(lines)+'\n'
def main():
 revision=R/'20_manuscript/revisions';revision.mkdir(exist_ok=True);audit=[]
 for name in ['WELDSTRESS_AI_Q1_MANUSCRIPT_DRAFT.md','ABSTRACT.md']:
  p=R/'20_manuscript'/name;old=p.read_text(encoding='utf8');backup=revision/('PRE_EDITORIAL_'+name)
  if not backup.exists():backup.write_text(old,encoding='utf8')
  new=polish(old);p.write_text(new,encoding='utf8');audit.append(dict(path=str(p),before_SHA256=sha(backup),after_SHA256=sha(p),scope='spacing and metric typography only; numeric tables untouched'))
 # Strengthen the requested synthesis figure with actual released results; no experiment is rerun.
 figpath=R/'19_scientific_figures/35_Final_research_findings';rev=R/'19_scientific_figures/revisions';rev.mkdir(exist_ok=True)
 for ext in ['png','pdf']:
  p=figpath.with_suffix('.'+ext);b=rev/('35_PRE_EDITORIAL.'+ext)
  if not b.exists():shutil.copyfile(p,b)
 m=pd.read_csv(R/'17_model_comparisons/TWO_SEED_METRIC_MEANS.csv');get=lambda model,c:m[(m.model==model)&(m.condition==c)].iloc[0];a=get('N2','FULL');b=get('N3','FULL');c=get('N2','X43');d=get('N3','X43');xgb=get('B2_GEOMETRY_XGBOOST','FULL');decision=read(R/'21_reports/SCIENTIFIC_DECISION.json')['scientific_result'];lines=[decision,f'FULL L2: N2 {a.L2:.4f}, N3 {b.L2:.4f}; High95 IoU: {a.high95_IoU:.4f} versus {b.high95_IoU:.4f}',f'X43 L2: N2 {c.L2:.4f}, N3 {d.L2:.4f}; High95 IoU: {c.high95_IoU:.4f} versus {d.high95_IoU:.4f}',f'Fixed XGBoost FULL L2 {xgb.L2:.4f}; N3 {b.L2:.4f} (different training budgets).','13 sources, five documentary plates; 10 N3 fits and 5 tree fits; no model search.','Research closed. External generalization and physical stress validation NOT ESTABLISHED.'];plt.rcParams.update({'font.size':10,'savefig.facecolor':'white','figure.dpi':110});f,ax=plt.subplots(figsize=(10,5.8),layout='constrained');f.suptitle('35. Final research findings',fontsize=13);ax.axis('off')
 for i,line in enumerate(lines):ax.text(.02,.94-i*.92/len(lines),line,ha='left',va='top',fontsize=11,wrap=True,transform=ax.transAxes)
 f.savefig(figpath.with_suffix('.png'),dpi=170);f.savefig(figpath.with_suffix('.pdf'));plt.close(f);figs=rows(R/'SCIENTIFIC_FIGURES.csv')
 for a in figs:
  if a['number']=='35':a.update(source_artifact='21_reports/SCIENTIFIC_DECISION.json;17_model_comparisons/TWO_SEED_METRIC_MEANS.csv',caption='Decision follows sealed rules; numerical accuracy/localization tradeoffs remain explicit. Neural values are means of separately scored seed metrics, not ensemble fields.')
 # Contrast repair for numerical annotations on dark heatmap cells.
 matrixpath=R/'19_scientific_figures/32_Model_comparison_decision_matrix'
 for ext in ['png','pdf']:
  dest=rev/('32_PRE_EDITORIAL.'+ext)
  if not dest.exists():shutil.copyfile(matrixpath.with_suffix('.'+ext),dest)
 frame=m.pivot(index='model',columns='condition',values='L2').reindex(columns=['FULL','X50','X43']);f,ax=plt.subplots(figsize=(10,5.8),layout='constrained');f.suptitle('32. Model comparison decision matrix',fontsize=13);im=ax.imshow(np.ma.masked_invalid(frame.values),aspect='auto',cmap='viridis_r');ax.set(yticks=range(len(frame)),yticklabels=frame.index,xticks=range(3),xticklabels=frame.columns)
 for i in range(len(frame)):
  for j in range(3):
   value=frame.iloc[i,j];rgba=im.cmap(im.norm(value)) if np.isfinite(value) else (1,1,1,1);lum=.2126*rgba[0]+.7152*rgba[1]+.0722*rgba[2];ax.text(j,i,'NOT EVALUATED' if not np.isfinite(value) else f'{value:.4f}',ha='center',va='center',color='white' if lum<.45 else 'black',fontsize=8)
 f.colorbar(im,ax=ax,label='Equal-plate normalized L2');f.savefig(matrixpath.with_suffix('.png'),dpi=170);f.savefig(matrixpath.with_suffix('.pdf'));plt.close(f)
 table(R/'SCIENTIFIC_FIGURES.csv',figs);table(R/'20_manuscript/EDITORIAL_REVISION_AUDIT.csv',audit);write(R/'20_manuscript/EDITORIAL_REVISION.json',dict(UTC=now(),passed=True,scientific_results_changed=False,fit_or_inference_repeated=False,prior_revisions_retained=True,abstract_words=len((R/'20_manuscript/ABSTRACT.md').read_text(encoding='utf8').split())));print('EDITORIAL_RELEASE_COMPLETE',flush=True)
if __name__=='__main__':main()
