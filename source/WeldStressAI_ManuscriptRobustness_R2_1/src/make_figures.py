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
for f in (P/'figures'/'main').glob('*'):shutil.copy2(f,D/'figures'/'main'/f.name)
def save(fig,name,caption):
 path=D/name;fig.savefig(path.with_suffix('.png'),dpi=300,bbox_inches='tight');fig.savefig(path.with_suffix('.pdf'),bbox_inches='tight');plt.close(fig);captions.append(dict(path=str(path.relative_to(D).with_suffix('.png')),caption=caption,scope='RETROSPECTIVE_EXPLORATORY_FROZEN_OUTPUTS',physical_validation=False))
rank=pd.read_csv(D/'THRESHOLD_ROBUSTNESS_MACRO.csv');common=pd.read_csv(D/'REFERENCE_THRESHOLD_MACRO.csv');rs=pd.read_csv(D/'THRESHOLD_ROBUSTNESS_MACRO_SEED.csv');cs=pd.read_csv(D/'REFERENCE_THRESHOLD_MACRO_SEED.csv')
fig,axs=plt.subplots(2,3,figsize=(8.5,6.0),layout='constrained')
for i,(tab,seeds,title) in enumerate([(rank[rank.scheme=='RANK_BUDGET'],rs[rs.scheme=='RANK_BUDGET'],'Matched rank budget'),(common,cs,'Common FE threshold diagnostic')]):
 for j,cond in enumerate(conds):
  ax=axs[i,j]
  for model in models:
   z=tab[(tab.model==model)&(tab.condition==cond)].sort_values('budget');ax.plot(z.budget*100,z.IoU,'o-',c=colors[model],lw=1.2,ms=4,label=model)
   for seed,marker in [(20261021,'o'),(20261022,'x')]:
    a=seeds[(seeds.model==model)&(seeds.condition==cond)&(seeds.seed.astype(str)==str(seed))].sort_values('budget');ax.scatter(a.budget*100,a.IoU,s=14,marker=marker,color=colors[model],alpha=.5)
  ax.set(title=cond+' — '+title,xlabel='Reference upper-area level (%)',ylabel='Area IoU',xticks=[1,5,10],ylim=(0,.8));ax.set_title(cond+'\n'+title,fontsize=10)
axs[0,0].legend(ncol=3,loc='lower right',fontsize=8)
save(fig,'figures/main/Fig06_Threshold_robustness','Retrospective all-thirteen-source, equal-five-plate IoU for N1/N2/N3 at 1%, 5% and 10%, under FULL/X50/X43. Lines average separately scored seeds; faint circles/crosses retain 20261021/20261022, not confidence intervals. Top: equal-area rank masks from unchanged saved numerical fields. Bottom: the same FE-derived MPa threshold applied to both fields, diagnostic only and unavailable to an operational held-out predictor. The processed measured front, assumed rear and numerical T2 reference remain unchanged; no physical toe label is used. IoU and area percentages are dimensionless.')
for ext in ['png','pdf']:(D/'figures'/'main'/('Fig06_Localization_and_amplitude.'+ext)).unlink(missing_ok=True)
# All plate/seed evidence, not just the equal-plate macro.
ps=pd.read_csv(D/'THRESHOLD_ROBUSTNESS_PLATE_SEED.csv');pm=pd.read_csv(D/'THRESHOLD_ROBUSTNESS_PLATE.csv');fig,axs=plt.subplots(3,3,figsize=(9,7.5),layout='constrained')
for i,cond in enumerate(conds):
 for j,b in enumerate(budgets):
  ax=axs[i,j]
  for k,model in enumerate(models):
   z=pm[(pm.model==model)&(pm.condition==cond)&(pm.budget==b)&(pm.scheme=='RANK_BUDGET')].set_index('plate').loc[list('CEGHX')];pos=np.arange(5)+(k-1)*.18;ax.scatter(pos,z.IoU,s=20,c=colors[model],label=model)
   for seed,mark in [(20261021,'o'),(20261022,'x')]:
    z=ps[(ps.model==model)&(ps.condition==cond)&(ps.budget==b)&(ps.scheme=='RANK_BUDGET')&(ps.seed.astype(str)==str(seed))].set_index('plate').loc[list('CEGHX')];ax.scatter(pos,z.IoU,s=12,c=colors[model],marker=mark,alpha=.45)
  ax.set(title=f'{cond} — top {b*100:g}%',xticks=np.arange(5),xticklabels=list('CEGHX'),ylim=(0,1),ylabel='Rank-budget area IoU')
axs[0,0].legend(ncol=3,fontsize=7)
save(fig,'figures/supplementary/Figure_A_All_plate_thresholds','Retrospective N1/N2/N3 rank-budget IoU on every documentary plate, context and 1/5/10% level. Large dots are source-within-plate then two-seed metric means; faint circles/crosses retain both seeds. No point-level confidence interval is constructed. All thirteen original processed measured fronts and original-area numerical T2 references are retained. This panel reports numerical localization, not physical toe validation.')
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
# Specific sealed FULL geometry comparator; no hidden restricted-view reuse.
gc=pd.read_csv(D/'G1_GEOMETRY_MACRO.csv');g0=pd.read_csv(D/'G0_COLLAR_MACRO.csv');comp=pd.read_csv(D/'NEURAL_VERSUS_GEOMETRY_PLATE.csv');fig,axs=plt.subplots(1,2,figsize=(8.5,4.1),layout='constrained')
for model in models:
 z=rank[(rank.model==model)&(rank.condition=='FULL')&(rank.scheme=='RANK_BUDGET')].sort_values('budget');axs[0].plot(z.budget*100,z.IoU,'o-',color=colors[model],label=model,lw=1.2,ms=4)
axs[0].plot(gc.budget*100,gc.IoU,'s--',c=colors['G1_GEOMETRY_TRANSITION_RANKING'],label='G1 matched area',lw=1.2,ms=4);axs[0].plot(g0.budget*100,g0.IoU,'^:',c=colors['G0_EXISTING_COLLAR_MASK'],label='G0 unequal area',lw=1.2,ms=4);axs[0].set(xlabel='Reference upper-area level (%)',ylabel='FULL area IoU',xticks=[1,5,10],ylim=(0,.85));axs[0].legend(fontsize=7,ncol=2)
for k,b in enumerate(budgets):
 z=comp[(comp.model=='N3')&(comp.geometry_model=='G1_GEOMETRY_TRANSITION_RANKING')&(comp.budget==b)].set_index('plate').loc[list('CEGHX')];axs[1].bar(np.arange(5)+(k-1)*.24,z.delta_IoU,width=.22,color=['#2676a8','#c27c2b','#9b3d79'][k],label=f'{b*100:g}%')
axs[1].axhline(0,c='black',lw=.7);axs[1].set(xticks=np.arange(5),xticklabels=list('CEGHX'),xlabel='Documentary held-out plate',ylabel='FULL N3 minus G1 area IoU');axs[1].legend(ncol=3,fontsize=8)
save(fig,'figures/main/Fig09_Geometry_comparator','Retrospective FULL-only numerical localization comparison on all thirteen processed measured fronts. G1 ranks exact XY distance to the sealed height-proxy transition and uses the same 1/5/10% area budgets as N1/N2/N3. G0 marks the unchanged broad collar (9.56% mean core coverage), so its area is unequal and its IoU is not a matched-budget comparison. Left: equal-plate metric means; right: N3-minus-G1 contrasts on all five plates, averaging separately scored seeds 20261021/20261022. Geometry masks predict no stress amplitude and are not validated toe curves. Restricted comparisons are unavailable because the baseline plane/labels require full-source geometry. Numerical T2 is not measured stress.')
for ext in ['png','pdf']:(D/'figures'/'main'/('Fig09_Plate_localization_contrasts.'+ext)).unlink(missing_ok=True)
sources=pd.read_csv(D/'R2_1_SOURCE_REGISTRY.csv');fields=pd.read_csv(D/'FROZEN_FIELD_ANALYSIS_REGISTRY.csv',keep_default_na=False)
def data(sid):
 sr=sources[sources.source_id==sid].iloc[0];g=dict(np.load(sr.geometry_path));t=dict(np.load(sr.target_path));m=t['core']&t['valid'];return g,t,m,t['xyz'][m]
def field(sid,model,cond,seed):
 r=fields[(fields.source_id==sid)&(fields.model==model)&(fields.condition==cond)&(fields.seed.astype(str)==str(seed))].iloc[0];return np.load(r.path)['pred_MPa'],dict(np.load(D/'qa'/'masks'/(r.field_id+'.npz')))
def bounds(ax,g,x):
 ax.set(xlim=(g['xyz'][:,0].min()-1,g['xyz'][:,0].max()+1),ylim=(15,45),aspect='equal',xlabel='Canonical X (mm)',ylabel='Profile Y (mm)');ax.axvline(g['xyz'][:,0].min(),color='#9f3c2f',lw=.7);ax.axvline(g['xyz'][:,0].max(),color='#9f3c2f',lw=.7);ax.add_patch(Rectangle((x[:,0].min(),x[:,1].min()),np.ptp(x[:,0]),np.ptp(x[:,1]),fill=False,ls='--',lw=.7,color='black'))
def maskplot(ax,g,x,mask,title):
 ax.scatter(x[:,0],x[:,1],s=.5,c='#dedede',rasterized=True);ax.scatter(x[mask,0],x[mask,1],s=1.2,c='#71386b',rasterized=True);bounds(ax,g,x);ax.set_title(title,fontsize=9)
for frac in budgets:
 code=f'{int(frac*100):02d}'
 for seed in [20261021,20261022]:
  fig,axs=plt.subplots(3,5,figsize=(15,7.7),layout='constrained')
  for i,sid in enumerate(['G07-V1-S355-AW','X10-V1-S355-AW','X23-V1-S355-AW']):
   g,t,m,x=data(sid);_,a=field(sid,'N2','FULL',seed);_,b=field(sid,'N3','FULL',seed);geo=np.load(D/'geometry_only'/(sid+'.npz'))
   # Use stored score and the sealed primary rank rule only for display of already evaluated masks.
   from metric_contract import budget
   gm,_=budget(geo['score'][m],t['area'][m],t['source_ids'][m],frac)
   for j,(mask,title) in enumerate(zip([a['ref_rank_'+code],t['region'][m]==2,gm,a['pred_rank_'+code],b['pred_rank_'+code]],['FE top-area','G0 FULL collar (unequal)','G1 FULL geometry rank','N2 FULL rank','N3 FULL rank'])):maskplot(axs[i,j],g,x,mask,sid[:3]+' / '+title)
  save(fig,f'figures/supplementary/Figure_B_FULL_masks_top{code}_seed{seed}',f'Retrospective original-coordinate masks for G07, X10 and X23; FULL, seed {seed}, upper-area level {frac*100:g}%. Reference and N2/N3 masks use the sealed same-area rank rule. G1 uses FULL measured geometry and frozen parent-plane contour proximity only; G0 marks its entire broad collar and has unequal area. Red lines are actual loaded X-cap locations and black dashed bounds are scoring cores. XY aspect is equal with no relief exaggeration. These are numerical/geometry masks, not measured toe or crack labels; G0/G1 do not predict MPa.')
for sid in ['X10-V1-S355-AW','X23-V1-S355-AW']:
 g,t,m,x=data(sid);y=t['T2_MPa'][m]
 for cond in ['FULL','X43']:
  for seed in [20261021,20261022]:
   n2,a=field(sid,'N2',cond,seed);n3,b=field(sid,'N3',cond,seed);lo=min(y.min(),n2.min(),n3.min());hi=max(y.max(),n2.max(),n3.max());err=max(abs(n2-y).max(),abs(n3-y).max());fig,axs=plt.subplots(3,3,figsize=(10,9.1),layout='constrained')
   for j,(v,title) in enumerate(zip([y,n2,n3],['Frozen FE T2','Frozen N2','Frozen N3'])):
    sc=axs[0,j].scatter(x[:,0],x[:,1],c=v,vmin=lo,vmax=hi,cmap='viridis',s=1,rasterized=True);plt.colorbar(sc,ax=axs[0,j],shrink=.7,label='T2 (MPa)');bounds(axs[0,j],g,x);axs[0,j].set_title(title)
   for j,(v,title) in enumerate([(n2-y,'N2 minus FE'),(n3-y,'N3 minus FE')]):
    sc=axs[1,j].scatter(x[:,0],x[:,1],c=v,vmin=-err,vmax=err,cmap='coolwarm',s=1,rasterized=True);plt.colorbar(sc,ax=axs[1,j],shrink=.7,label='Error (MPa)');bounds(axs[1,j],g,x);axs[1,j].set_title(title)
   maskplot(axs[1,2],g,x,t['region'][m]==2,'Original collar proxy')
   for j,(mm,title) in enumerate([(a['ref_rank_05'],'FE top 5% area'),(a['pred_rank_05'],'N2 top 5% area'),(b['pred_rank_05'],'N3 top 5% area')]):maskplot(axs[2,j],g,x,mm,title)
   save(fig,f'figures/supplementary/Figure_D_{sid[:3]}_{cond}_s{seed}',f'Retrospective {sid}, {cond}, seed {seed}. Original core coordinates, frozen FE T2 and stored N2/N3 predictions share MPa limits; signed prediction-minus-FE errors share a symmetric zero-centered MPa scale. Original broad collar and sealed rank-budget top-5% masks are shown separately. Red X-cap locations and black core bounds are distinct. Observation edges are outside the core by more than 1 mm and are documented per query ownership in the boundary table, not replaced by core lines. The front is processed measured geometry, the stress reference numerical; no authenticated measured toe trajectory or crack marker is available. Equal XY physical aspect; no altered field values.')
(D/'R2_1_FIGURE_REGISTRY.json').write_text(json.dumps(captions,indent=2),encoding='utf-8');print('R2_1_NEW_FIGURE_PAIRS',len(captions),flush=True)
