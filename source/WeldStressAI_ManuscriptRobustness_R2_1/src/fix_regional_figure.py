from pathlib import Path
import json,shutil
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
D=Path(__file__).resolve().parents[1];P=D.parent/'WeldStressAI_ManuscriptRevision_R2'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'legend.fontsize':8})
colors={'N1':'#2676a8','N2':'#c27c2b','N3':'#9b3d79','G1_GEOMETRY_TRANSITION_RANKING':'#596c38','G0_EXISTING_COLLAR_MASK':'#73787c'};models=['N1','N2','N3'];conds=['FULL','X50','X43'];budgets=[.01,.05,.10];captions=[]

def save(fig,name,caption):
 path=D/name;fig.savefig(path.with_suffix('.png'),dpi=300,bbox_inches='tight');fig.savefig(path.with_suffix('.pdf'),bbox_inches='tight');plt.close(fig);captions.append(dict(path=str(path.relative_to(D).with_suffix('.png')),caption=caption,scope='RETROSPECTIVE_EXPLORATORY_FROZEN_OUTPUTS',physical_validation=False))
# Regional MAE in physical MPa; plate means, all regions and contexts.
rp=pd.read_csv(D/'REGIONAL_ERROR_PLATE.csv');fig,axs=plt.subplots(3,3,figsize=(8.5,7.2),sharey=True,layout='constrained')
for i,region in enumerate(['PARENT','COLLAR','HEIGHT_REGION']):
 for j,cond in enumerate(conds):
  ax=axs[i,j]
  for k,model in enumerate(models):
   z=rp[(rp.model==model)&(rp.condition==cond)&(rp.region==region)].set_index('plate').loc[list('CEGHX')];ax.bar(np.arange(5)+(k-1)*.24,z.MAE_MPa,width=.22,color=colors[model],label=model)
  ax.set(title=cond+' / '+region.replace('_',' '),xticks=np.arange(5),xticklabels=list('CEGHX'),ylabel='Regional MAE (MPa)',ylim=(0,None));ax.set_title(cond+' / '+region.replace('_',' '),fontsize=10)
fig.legend(*axs[0,0].get_legend_handles_labels(),ncol=3,loc='upper center',bbox_to_anchor=(.5,1.04),frameon=False)
save(fig,'figures/main/Fig07_Regional_errors','Retrospective regional MAE in MPa for N1/N2/N3 on all thirteen processed measured fronts, five documentary plates and FULL/X50/X43. Bars average source metrics within plate and separately scored neural seeds 20261021/20261022. Parent, collar and height labels are unchanged geometry-derived proxies, not independent measured toes. Stress errors are relative to numerical T2; bar heights are not area shares or normalized L2. Source/seed values and error contributions remain in supporting CSVs.')
for ext in ['png','pdf']:(D/'figures'/'main'/('Fig07_Seeds_and_plate_variability.'+ext)).unlink(missing_ok=True)
