from common_e14 import *
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from metric_e14 import quantile
def raster(ax,x,values,cmap='viridis',vmin=None,vmax=None):
 ux,xi=np.unique(x[:,0],return_inverse=True);uy,yi=np.unique(x[:,1],return_inverse=True)
 if len(ux)*len(uy)==len(x) and len(np.unique(yi*len(ux)+xi))==len(x):
  a=np.full((len(uy),len(ux)),np.nan);a[yi,xi]=values;im=ax.imshow(a,origin='lower',extent=[ux.min(),ux.max(),uy.min(),uy.max()],aspect='equal',interpolation='nearest',cmap=cmap,vmin=vmin,vmax=vmax)
 else:im=ax.scatter(x[:,0],x[:,1],c=values,s=3,cmap=cmap,vmin=vmin,vmax=vmax,rasterized=True);ax.set_aspect('equal')
 ax.set_xlabel('X mm');ax.set_ylabel('Y mm');return im
def figures():
 plt.rcParams.update({'font.size':8,'axes.spines.top':False,'axes.spines.right':False});out=R/'18_figures';source=pd.read_csv(R/'SOURCE_CONTEXT_METRICS.csv');plate=pd.read_csv(R/'PLATE_CONTEXT_METRICS.csv');study=pd.read_csv(R/'SEED_CONTEXT_METRICS.csv');density=pd.read_csv(R/'OBSERVATION_CONTEXT_DENSITY.csv');sensitivity=pd.read_csv(R/'09_context_sensitivity/ALL_MODEL_SENSITIVITY.csv');freq=pd.read_csv(R/'N2_CONTEXT_FREQUENCIES.csv');history=pd.read_csv(R/'N2_TRAINING_LOSS_HISTORY.csv');old=pd.read_csv(R/'05_spatial_error_baseline/ORIGINAL_OOF_SPATIAL_DIAGNOSTICS.csv');geo=pd.read_csv(R/'GEOMETRY_DOMAIN_SHIFT.csv');registry=rows(R/'20_reproducibility/PREDICTION_REGISTRY.csv');sources=sorted(source.source_id.unique());provenance=[]
 def save(n,name,fig):
  fig.suptitle('R8-E14 | '+name,fontsize=12);fig.tight_layout(rect=(0,0,1,.96));p=out/f'{n:02d}_{name.replace(" ","_").replace("/","-")}';fig.savefig(p.with_suffix('.png'),dpi=150);fig.savefig(p.with_suffix('.pdf'));plt.close(fig);provenance.append(dict(number=n,title=name,kind='NEW_FROM_ACTUAL_ARRAYS',path=str(p.with_suffix('.png'))));print('FIGURE',n,name,flush=True)
 for n,oldnum,name in [(1,1,'Original thirteen measured geometries'),(2,2,'Documentary plate groups'),(3,17,'Verified original prediction accuracy'),(4,21,'Original reference and predicted T2'),(5,22,'Original signed stress error'),(6,23,'Original absolute stress error'),(10,27,'Original along weld profiles'),(11,28,'Original transverse profiles')]:
  p=next((H/'14_figures').glob(f'{oldnum:02d}_*.png'));dest=out/f'{n:02d}_{name.replace(" ","_")}.png';shutil.copyfile(p,dest);shutil.copyfile(p.with_suffix('.pdf'),dest.with_suffix('.pdf'));provenance.append(dict(number=n,title=name,kind='IMMUTABLE_R8E13_BASELINE_REUSED',path=str(dest),historical_path=str(p),historical_SHA256=sha(p)))
 data={s:dict(np.load(H/'01_dataset/targets'/(s+'.npz'))) for s in sources};pred={(a['model'],a['seed'],a['condition'],a['source_id']):dict(np.load(a['path']))['pred_MPa'] for a in registry};colors=['#1f77b4','#48a0d0','#c75b12','#ee9f54'];combos=[('N1','20261021'),('N1','20261022'),('N2','20261021'),('N2','20261022')]
 for number,name,which in [(7,'Original false positive High95 regions','FP'),(8,'Original false negative High95 regions','FN')]:
  fig,axs=plt.subplots(13,2,figsize=(10,31),squeeze=False)
  for row,s in enumerate(sources):
   d=data[s];m=d['core']&d['valid'];x=d['xyz'][m];w=d['area'][m];y=d['T2_MPa'][m];hy=y>=quantile(y,w);fold='F'+str('CEGHX'.index(s[0])+1)
   for col,seed in enumerate(['20261021','20261022']):
    p=dict(np.load(H/'06_predictions'/('N1_POINT_TRANSFORMER_'+fold+'_s'+seed+'_'+s+'.npz')))['pred_MPa'][m];hp=p>=quantile(p,w);mask=hp&~hy if which=='FP' else hy&~hp;im=raster(axs[row,col],x,mask.astype(int),'Reds',0,1);axs[row,col].set_title(s[:3]+' seed '+seed);fig.colorbar(im,ax=axs[row,col],shrink=.6,label=which+' membership')
  save(number,name,fig)
 fig,ax=plt.subplots(figsize=(12,4))
 for j,seed in enumerate([20261021,20261022]):
  ss=old[old.seed==seed].set_index('source_id');ax.bar(np.arange(13)+(j-.5)*.35,ss.reindex(sources).high95_centroid_distance_mm,.35,label=str(seed))
 ax.set_xticks(range(13),[s[:3] for s in sources]);ax.set_ylabel('Original High95 centroid displacement mm');ax.legend();save(9,'Original High95 centroid errors',fig)
 sid=sources[0];g=dict(np.load(H/'02_geometry'/(sid+'.npz')))
 for number,condition in [(12,'FULL'),(13,'X50'),(14,'X43')]:
  fig,axs=plt.subplots(1,2,figsize=(12,4))
  for ax,tile in zip(axs,[0,2]):
   a=density[(density.source_id==sid)&(density.condition==condition)&(density.tile==tile)].iloc[0];visible=(g['xyz'][:,0]>=a.actual_X_min-1e-8)&(g['xyz'][:,0]<=a.actual_X_max+1e-8);im=raster(ax,g['xyz'][visible],g['xyz'][visible,2]);ax.set_xlim(g['xyz'][:,0].min(),g['xyz'][:,0].max());ax.set_title(f'{sid[:3]} tile {tile}; X={a.actual_X_mm:.3f}mm; Y={a.actual_Y_mm:.3f}mm');fig.colorbar(im,ax=ax,label='Observed Z mm')
  save(number,'Observed '+condition+' geometry and clipped extent',fig)
 fig,axs=plt.subplots(1,2,figsize=(12,4));order=['FULL','X50','X43','D0'];axs[0].boxplot([density[density.condition==c].context_density_per_mm2 for c in order],tick_labels=order);axs[0].set_ylabel('4096 / observed surface area, mm^-2');axs[1].boxplot([density[density.condition==c].context_NN_median_mm for c in order],tick_labels=order);axs[1].set_ylabel('Selected context median nearest spacing mm');save(15,'Context sampling density controls',fig)
 fig,ax=plt.subplots(figsize=(8,4));ax.boxplot([density[density.condition==c].full_context_overlap/4096 for c in order],tick_labels=order);ax.set_ylabel('Fraction of context IDs shared with FULL');save(16,'Context point overlap',fig)
 ft=pd.read_csv(R/'04_feature_contract/FEATURE_CHANGES_BY_CHANNEL.csv');fig,ax=plt.subplots(figsize=(12,4))
 for condition in ['X50','X43']:
  z=ft[ft.condition==condition].groupby('channel').mean_absolute_change.mean();ax.plot(z.index,z.values,'o-',label=condition)
 ax.set_xlabel('Original feature channel');ax.set_ylabel('Mean absolute feature change, frozen mixed units');ax.legend();save(17,'Feature changes from visible geometry',fig)
 for number,name,value in [(18,'N1 context induced prediction shifts','mean_signed_prediction_shift_MPa'),(19,'N1 context induced normalized L2 changes','DELTA_L2'),(20,'N1 context induced High95 IoU changes','DELTA_IOU')]:
  fig,ax=plt.subplots(figsize=(11,4));n=sensitivity[sensitivity.model=='N1'];idx=np.arange(5)
  for j,condition in enumerate(['X50','X43','D0']):
   z=n[n.condition==condition].groupby(['plate','seed'])[value].mean().groupby('plate').mean().reindex(list('CEGHX'));ax.bar(idx+(j-1)*.25,z,.25,label=condition)
  ax.axhline(0,color='black',lw=.5);ax.set_xticks(idx,list('CEGHX'));ax.set_ylabel(value+'; mean of two separately scored seeds');ax.legend();save(number,name,fig)
 binned=pd.read_csv(R/'05_spatial_error_baseline/ERROR_DESCRIPTOR_BINS.csv');fig,ax=plt.subplots(figsize=(9,4))
 for model in ['N1','N2']:
  z=binned[(binned.model==model)&(binned.descriptor=='query_observation_X_boundary_distance_mm')&(binned.condition!='D0')];ax.scatter(z.mean_descriptor,z.MAE_MPa,s=4,alpha=.25,label=model)
 ax.set_xlabel('Query distance to observed X edge mm');ax.set_ylabel('Binned area-weighted MAE MPa');ax.legend();save(21,'Observation boundary distance and error',fig)
 fig,ax=plt.subplots(figsize=(10,4));bottom=np.zeros(10);runlabels=[]
 for condition in ['FULL','X50','X43']:
  z=freq[freq.context==condition].sort_values(['fold','seed']);ax.bar(range(10),z.fraction,bottom=bottom,label=condition);bottom+=z.fraction.to_numpy();runlabels=[r.fold+'\n'+str(r.seed)[-2:] for r in z.itertuples()]
 ax.set_xticks(range(10),runlabels);ax.set_ylabel('Actual training minibatch fraction');ax.legend();save(22,'N2 context frequencies',fig)
 fig,ax=plt.subplots(figsize=(11,4))
 for (fold,seed),z in history.groupby(['fold','seed']):ax.plot(z.epoch,z.weighted_MSE_K,label=fold+' '+str(seed))
 ax.set_yscale('log');ax.set_xlabel('Epoch');ax.set_ylabel('Importance-weighted mean squared K');ax.legend(ncol=5,fontsize=6);save(23,'N2 frozen epoch training losses',fig)
 def platebars(number,name,condition,value):
  fig,ax=plt.subplots(figsize=(10,4))
  for j,(model,seed) in enumerate(combos):
   z=plate[(plate.model==model)&(plate.seed.astype(str)==seed)&(plate.condition==condition)].set_index('plate').reindex(list('CEGHX'));ax.bar(np.arange(5)+(j-1.5)*.18,z[value],.18,label=model+' '+seed,color=colors[j])
  ax.set_xticks(range(5),list('CEGHX'));ax.set_ylabel(value);ax.legend(ncol=2);save(number,name,fig)
 platebars(24,'N1 and N2 FULL context accuracy','FULL','L2');platebars(25,'N1 and N2 X50 accuracy','X50','L2');platebars(26,'N1 and N2 X43 accuracy','X43','L2')
 for number,name,metric in [(27,'High95 spatial IoU by observation','equal_plate_high95_IoU'),(28,'High95 false negative area by observation','equal_plate_false_negative_area_mm2')]:
  fig,ax=plt.subplots(figsize=(10,4))
  for j,(model,seed) in enumerate(combos):
   z=study[(study.model==model)&(study.seed.astype(str)==seed)].set_index('condition').reindex(['FULL','X50','X43']);ax.bar(np.arange(3)+(j-1.5)*.18,z[metric],.18,label=model+' '+seed,color=colors[j])
  ax.set_xticks(range(3),['FULL','X50','X43']);ax.set_ylabel(metric);ax.legend(ncol=2);save(number,name,fig)
 fig,ax=plt.subplots(figsize=(12,4))
 for model in ['N1','N2']:
  for condition in ['FULL','X50','X43']:
   z=source[(source.model==model)&(source.condition==condition)].groupby('source_id').max_error_MPa.mean().reindex(sources);ax.plot(range(13),z,'o-',label=model+' '+condition)
 ax.axhline(0,color='grey',lw=.5);ax.set_xticks(range(13),[s[:3] for s in sources]);ax.set_ylabel('Mean-seed maximum T2 prediction error MPa');ax.legend(ncol=3);save(29,'Regularized stress peak amplitude bias',fig)
 for number,name,index in [(30,'Plate context sensitivity','plate'),(31,'Source context sensitivity','source_id')]:
  fig,ax=plt.subplots(figsize=(12,4));xx=list('CEGHX') if index=='plate' else sources
  for model in ['N1','N2']:
   for condition in ['X50','X43']:
    z=sensitivity[(sensitivity.model==model)&(sensitivity.condition==condition)].groupby(index).RMS_prediction_shift_MPa.mean().reindex(xx);ax.plot(range(len(xx)),z,'o-',label=model+' '+condition)
  ax.set_xticks(range(len(xx)),[s[:3] for s in xx]);ax.set_ylabel('Mean-seed RMS field shift from corresponding FULL, MPa');ax.legend(ncol=2);save(number,name,fig)
 fig,axs=plt.subplots(1,2,figsize=(12,4))
 for model in ['N1','N2']:
  for ax,metric in zip(axs,['equal_plate_L2','equal_plate_high95_IoU']):
   for seed in [20261021,20261022]:
    z=study[(study.model==model)&(study.seed==seed)].set_index('condition').reindex(['FULL','X50','X43']);ax.plot(range(3),z[metric],'o-',label=model+' '+str(seed));ax.set_xticks(range(3),['FULL','X50','X43']);ax.set_ylabel(metric)
 axs[0].legend(fontsize=7);save(32,'Seed variability and context outcomes',fig)
 fig,ax=plt.subplots(figsize=(8,5));des=geo.set_index('source_id')
 for model in ['N1','N2']:
  z=source[(source.model==model)&(source.condition=='X43')].groupby('source_id').L2.mean().reindex(sources);ax.scatter(des.reindex(sources).height_span_mm,z,label=model)
 ax.set_xlabel('Measured parent-relative vertical height span mm');ax.set_ylabel('Mean-seed X43 normalized L2');ax.legend();save(33,'Geometry error descriptive associations',fig)
 fig,ax=plt.subplots(figsize=(12,4));ax.plot(range(13),des.reindex(sources).historical_M1_M2_L2,'o-',label='M1-M2 numerical consistency')
 for model in ['N1','N2']:ax.plot(range(13),source[(source.model==model)&(source.condition=='FULL')].groupby('source_id').L2.mean().reindex(sources),'o-',label=model+' FULL')
 ax.set_yscale('log');ax.set_xticks(range(13),[s[:3] for s in sources]);ax.set_ylabel('Normalized L2; mesh discrepancy is not an error bound');ax.legend();save(34,'Numerical reference consistency and ML error',fig)
 fig,ax=plt.subplots(figsize=(8,5))
 for model,seed in combos:
  ss=sensitivity[(sensitivity.model==model)&(sensitivity.seed.astype(str)==seed)&sensitivity.condition.isin(['X50','X43'])];xx=ss.groupby(['condition','plate']).prediction_change_L2.mean().mean();yy=study[(study.model==model)&(study.seed.astype(str)==seed)&study.condition.isin(['X50','X43'])].equal_plate_L2.mean();ax.scatter(xx,yy,label=model+' '+seed,s=60)
 ax.set_xlabel('Mean restricted/FULL prediction-change L2');ax.set_ylabel('Mean restricted absolute target-error L2');ax.legend();save(35,'Robustness and absolute accuracy trade off',fig)
 from reports_e14 import decision
 result=decision(study);fig,ax=plt.subplots(figsize=(12,5));ax.axis('off');lines=[result,'Exploratory existing-plate methodological study; not a fresh outer test.','10 frozen N1 checkpoints; 10 fresh N2 fits; 13 sources; 5 documentary plate groups.']
 for a in study[study.condition.isin(['FULL','X50','X43'])].itertuples():lines.append(f'{a.model} {a.seed} {a.condition}: L2 {a.equal_plate_L2:.5f}, MAE {a.equal_plate_MAE_MPa:.3f} MPa, IoU {a.equal_plate_high95_IoU:.4f}')
 ax.text(.01,.98,'\n'.join(lines),va='top',fontsize=10);save(36,'Exploratory scientific decision',fig)
 # One source/seed panel set preserves all difficult cases and all primary conditions.
 supp=out/'source_maps';supp.mkdir(exist_ok=True);category_cmap=matplotlib.colors.ListedColormap(['#eeeeee','#d94b3d','#3986c6','#4d9d46'])
 for sid in sources:
  d=data[sid];m=d['core']&d['valid'];x=d['xyz'][m];y=d['T2_MPa'][m];w=d['area'][m];hy=y>=quantile(y,w)
  for seed in ['20261021','20261022']:
   vv=[pred[model,seed,c,sid] for model in ['N1','N2'] for c in ['FULL','X50','X43']];lo=min(float(y.min()),min(float(v.min()) for v in vv));hi=max(float(y.max()),max(float(v.max()) for v in vv));fig,axs=plt.subplots(3,4,figsize=(16,9),squeeze=False)
   for i,c in enumerate(['FULL','X50','X43']):
    for j,model in enumerate(['N1','N2']):
     p=pred[model,seed,c,sid];im=raster(axs[i,j],x,p,vmin=lo,vmax=hi);axs[i,j].set_title(model+' '+c+' T2 MPa');fig.colorbar(im,ax=axs[i,j],shrink=.7);hp=p>=quantile(p,w);im=raster(axs[i,j+2],x,hy.astype(int)+2*hp.astype(int),category_cmap,0,3);axs[i,j+2].set_title(model+' '+c+' High95: 0 none / 1 FN / 2 FP / 3 both');fig.colorbar(im,ax=axs[i,j+2],shrink=.7)
   fig.suptitle(sid+' | seed '+seed+' | same original V1 core; nearest-cell display only');fig.tight_layout(rect=(0,0,1,.96));p=supp/(sid+'_s'+seed);fig.savefig(p.with_suffix('.png'),dpi=140);fig.savefig(p.with_suffix('.pdf'));plt.close(fig)
 table(R/'20_reproducibility/FIGURE_PROVENANCE.csv',provenance);write(R/'20_reproducibility/FIGURES_COMPLETE.json',dict(UTC=now(),primary_pairs=36,supplemental_pairs=26,total_pairs=62,all_sources_and_seeds_displayed=True,raster_rule='All original XY point values on original rectangular grid, nearest-cell display if complete grid; otherwise all-point scatter. No stress recomputation or target interpolation.'))
if __name__=='__main__':figures()
