"""Targeted, documented display-only QA repairs; no predictions/metrics/model changes."""
from common_e13 import *
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from score_e13 import quantile
def main():
 verify_seal();archive=R/'21_reproducibility/visual_revision1';archive.mkdir(exist_ok=True);numbers=[1,8,9,13,21,22,23,24,25,26]
 for n in numbers:
  for p in (R/'14_figures').glob(f'{n:02d}_*'):shutil.copyfile(p,archive/p.name)
 plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
 def save(n,title,fig):
  fig.suptitle('R8-E13 | '+title,fontsize=13);fig.tight_layout(rect=(0,0,1,.97));base=next((R/'14_figures').glob(f'{n:02d}_*.png'));fig.savefig(base,dpi=150);fig.savefig(base.with_suffix('.pdf'));plt.close(fig);print('QA_REVISED',n,flush=True)
 fig,ax=plt.subplots(figsize=(10,3.8));ax.imshow(np.zeros((5,3)),vmin=0,vmax=1,cmap='Reds',aspect='auto');ax.set_xticks(range(3),['Source overlap','Plate overlap','Held-out minibatches']);ax.set_yticks(range(5),list('CEGHX'))
 for i in range(5):
  for j in range(3):ax.text(j,i,'0',ha='center',va='center')
 save(8,'Independent leakage checks',fig)
 fig,ax=plt.subplots(figsize=(12,4));ax.axis('off');lines=['Measured front only -> 19 geometry channels -> MLP encoder width 24','Vector attention: K16 + 16 anchors at 1 mm + 16 anchors at 3 mm','Learned scale mixture + mean of 4096 area-CDF context encodings','Residual MLP + LayerNorm -> scalar K -> x100 MPa; 7,228 parameters']
 for y,line in zip([.8,.55,.3,.05],lines):ax.text(.02,y,line,fontsize=12)
 save(9,'Frozen historical S1 architecture',fig)
 fig,ax=plt.subplots(figsize=(8,4));ax.imshow(np.ones((5,2)),vmin=0,vmax=1,cmap='Greens',aspect='auto');ax.set_xticks([0,1],['Seed 20261021','Seed 20261022']);ax.set_yticks(range(5),list('CEGHX'))
 for i in range(5):
  for j in range(2):ax.text(j,i,'80/80',ha='center',va='center',color='white')
 save(13,'Training completion matrix',fig)
 sources=sorted({a['source_id'] for a in rows(R/'PREDICTION_REGISTRY.csv')});data={s:dict(np.load(R/'01_dataset/targets'/(s+'.npz'))) for s in sources};pred={}
 for a in rows(R/'PREDICTION_REGISTRY.csv'):
  if a['model']=='N1_POINT_TRANSFORMER':pred[str(a['seed']),a['source_id']]=dict(np.load(a['path']))['pred_MPa']
 fig,axs=plt.subplots(5,3,figsize=(15,15))
 for ax,s in zip(axs.flat,sources):
  d=data[s];x=d['xyz'];sc=ax.scatter(x[:,0],x[:,1],c=x[:,2],s=2,cmap='viridis',rasterized=True);ax.set_title(s);ax.set_aspect('equal');ax.set_xlabel('X mm');ax.set_ylabel('Y mm');fig.colorbar(sc,ax=ax,label='Original front Z mm')
 for ax in list(axs.flat)[13:]:ax.axis('off')
 save(1,'Thirteen measured source geometries',fig)
 vmax=max(max(float(d['T2_MPa'][d['core']].max()) for d in data.values()),max(float(pred[seed,s][data[s]['core']].max()) for seed in ['20261021','20261022'] for s in sources));vmin=min(min(float(d['T2_MPa'][d['core']].min()) for d in data.values()),min(float(pred[seed,s][data[s]['core']].min()) for seed in ['20261021','20261022'] for s in sources));elim=max(float(np.max(abs(pred[seed,s][data[s]['core']]-data[s]['T2_MPa'][data[s]['core']]))) for seed in ['20261021','20261022'] for s in sources)
 for n,title,kind in [(21,'Reference and neural T2 fields','fields'),(22,'Signed prediction error','signed'),(23,'Absolute prediction error','absolute'),(24,'Reference High95 support','refhigh'),(25,'Predicted High95 support','predhigh'),(26,'High95 spatial overlap','overlap')]:
  cols=3 if kind=='fields' else (1 if kind=='refhigh' else 2);fig,axs=plt.subplots(13,cols,figsize=(5*cols,2.75*13),squeeze=False)
  for row,s in enumerate(sources):
   d=data[s];m=d['core']&d['valid'];x=d['xyz'][m];y=d['T2_MPa'][m];w=d['area'][m];hy=y>=quantile(y,w)
   for col in range(cols):
    seed=str(20261021+(max(0,col-1) if kind=='fields' else col));p=pred[seed,s][m] if kind!='refhigh' else y;hp=p>=quantile(p,w)
    if kind=='fields':v=y if col==0 else p;cmap='viridis';kw=dict(vmin=vmin,vmax=vmax);label='Reference T2 MPa' if col==0 else 'PT '+seed+' T2 MPa'
    elif kind=='signed':v=p-y;cmap='coolwarm';kw=dict(vmin=-elim,vmax=elim);label='Signed error MPa '+seed
    elif kind=='absolute':v=abs(p-y);cmap='magma';kw=dict(vmin=0,vmax=elim);label='Absolute error MPa '+seed
    elif kind=='refhigh':v=hy.astype(int);cmap='Greys';kw=dict(vmin=0,vmax=1);label='Reference High95 membership'
    elif kind=='predhigh':v=hp.astype(int);cmap='Greys';kw=dict(vmin=0,vmax=1);label='PT '+seed+' High95 membership'
    else:v=hy.astype(int)+2*hp.astype(int);cmap=matplotlib.colors.ListedColormap(['#eeeeee','#d94b3d','#3986c6','#4d9d46']);kw=dict(vmin=0,vmax=3);label='0 none / 1 FN / 2 FP / 3 overlap'
    ax=axs[row,col];sc=ax.scatter(x[:,0],x[:,1],c=v,s=3,cmap=cmap,rasterized=True,**kw);ax.set_title(s[:3]+' | '+label,fontsize=9);ax.set_aspect('equal');ax.set_xlabel('X mm');ax.set_ylabel('Y mm');fig.colorbar(sc,ax=ax,shrink=.7)
  save(n,title,fig)
 for name in ['HIGH95_SPATIAL_LOCALIZATION.md']:
  p=R/name;p.write_text(p.read_text(encoding='utf8').replace('Figures use every third core row for display; metrics use all original core rows.','Final map figures display all original core rows; metrics also use all original core rows. The initial fixed-stride thumbnails aliased the regular longitudinal grid; those versions are archived, and only display sampling was repaired.'),encoding='utf8')
 write(R/'21_reproducibility/VISUAL_LAYOUT_REPAIR.json',dict(UTC=now(),figures=numbers,reason='Remove overlapping labels and encoding artefacts; show every source/core point to avoid fixed-stride grid aliasing',training_changes=0,prediction_changes=0,metric_changes=0,prior_artifacts_archived=True))
if __name__=='__main__':main()
