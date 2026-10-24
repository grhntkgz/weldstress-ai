from pathlib import Path
import json,shutil
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.tri import Triangulation
from matplotlib.patches import Rectangle
from matplotlib.colors import ListedColormap, BoundaryNorm
D=Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRevision_R2');O=D.parent;R=O/'WeldStressAI_FinalResearch_PhaseR8E16';H=O/'WeldStressAI_PlateHeldOutAI_PhaseR8E13';P=O/'WeldStressAI_ManuscriptRevision_R1'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'legend.fontsize':8})
for f in (P/'figures'/'main').glob('*'):shutil.copy2(f,D/'figures'/'main'/f.name)
info=json.loads((D/'qa'/'SOURCE_SPATIAL_INPUTS.json').read_text());registry=pd.read_csv(R/'MODEL_PREDICTION_REGISTRY.csv',keep_default_na=False);captions=[]
def save(fig,path,caption,source,condition='X43',seed='both'):
 path=D/path;path.parent.mkdir(parents=True,exist_ok=True);fig.savefig(path.with_suffix('.png'),dpi=300,bbox_inches='tight');fig.savefig(path.with_suffix('.pdf'),bbox_inches='tight');plt.close(fig);captions.append(dict(path=str(path.with_suffix('.png')),PDF=str(path.with_suffix('.pdf')),source_id=source,condition=condition,seed=seed,caption=caption,diagnostic_scope='RETROSPECTIVE_FROZEN_OUTPUT_DESCRIPTIVE_DIAGNOSTIC'))
def load(sid):
 g=dict(np.load(info[sid]['geometry_path']));t=dict(np.load(info[sid]['target_path']));core=t['core']&t['valid'];x=g['xyz'];datum=info[sid]['datum'];height=(x[:,2]-datum['intercept_Z_mm']-datum['slope_X']*(x[:,0]-datum['origin_X_mm'])-datum['slope_Y']*(x[:,1]-datum['origin_Y_mm']))/np.sqrt(1+datum['slope_X']**2+datum['slope_Y']**2);return g,t,core,height
def q(v,w):ii=np.argsort(v,kind='stable');return np.interp(.95,np.cumsum(w[ii])/w.sum(),v[ii])
def boundaries(ax,g,t,core,proxy=False):
 x=g['xyz'];cx=x[core];ax.set(xlim=(x[:,0].min()-1,x[:,0].max()+1),ylim=(15,45),xlabel='Canonical X (mm)',ylabel='Profile Y (mm)',aspect='equal');ax.axvline(round(x[:,0].min(),3),ls='-',lw=1.2,color='#a52323');ax.axvline(round(x[:,0].max(),3),ls='-',lw=1.2,color='#a52323');ax.add_patch(Rectangle((cx[:,0].min(),cx[:,1].min()),np.ptp(cx[:,0]),np.ptp(cx[:,1]),fill=False,ls='--',lw=1,color='black'))
 if proxy:
  tr=Triangulation(x[:,0],x[:,1],g['triangles']);ax.tricontour(tr,(t['region']==1).astype(float),levels=[.5],colors=['#2b6a9c'],linewidths=.7);ax.tricontour(tr,(t['region']>0).astype(float),levels=[.5],colors=['#2b6a9c'],linewidths=.7,linestyles=':')
def scatter(ax,x,v,label,limits=None,cmap='viridis'):
 if 'region code' in label.lower():
  cm=ListedColormap(['#c9cdd1','#da9352','#5996b6']);z=ax.scatter(x[:,0],x[:,1],c=v,s=2,rasterized=True,cmap=cm,norm=BoundaryNorm([-.5,.5,1.5,2.5],3));plt.colorbar(z,ax=ax,shrink=.7,pad=.02,label=label,ticks=[0,1,2]);return z
 z=ax.scatter(x[:,0],x[:,1],c=v,s=2,rasterized=True,cmap=cmap,vmin=None if limits is None else limits[0],vmax=None if limits is None else limits[1]);plt.colorbar(z,ax=ax,shrink=.7,pad=.02,label=label);return z
# Correct R1's default 3-D plotting aspect by using physical axis spans explicitly.
sid='G07-V1-S355-AW';g,t,m,height=load(sid);x=g['xyz'];fig=plt.figure(figsize=(10,4));a=fig.add_subplot(121,projection='3d');a.scatter(*x[::8].T,c=x[::8,2],s=2,cmap='viridis');a.set_box_aspect(np.ptp(x,axis=0));a.set(xlim=(x[:,0].min(),x[:,0].max()),ylim=(16,44),zlim=(x[:,2].min(),x[:,2].max()),xlabel='X (mm)',ylabel='Y (mm)',zlabel='Z (mm)',title='(a) Processed measured front; true aspect');a.view_init(elev=25,azim=-65);a.set_zticks([]);a.set_zlabel('');a.set_xticks([130,150,170]);a.set_yticks([20,30,40]);a.set_xlabel('');a.set_ylabel('');a.text2D(.4,.04,'X (mm)',transform=a.transAxes,fontsize=9);a.text2D(.87,.16,'Y (mm)',transform=a.transAxes,fontsize=9);a.text2D(.04,.82,f'Z range {x[:,2].min():.2f} to {x[:,2].max():.2f} mm',transform=a.transAxes,fontsize=9);b=fig.add_subplot(122);scatter(b,x[m],t['T2_MPa'][m],'Numerical T2 (MPa)');boundaries(b,g,t,m);b.set_title('(b) Frozen FE numerical reference',fontsize=10);fig.tight_layout()
save(fig,'figures/main/Fig01_Geometry_and_reference','G07-V1-S355-AW processed measured front in canonical coordinates and its frozen numerical T2 reference. Geometry uses physical axis-span aspect ratios, with no vertical exaggeration. Red lines mark native loaded X-cap positions; black dashes mark the accepted core. No measured toe trajectory is asserted. The field is numerical, not experimental. FULL reference; neural seed is not applicable. Original point coordinates and target values are unchanged.','G07-V1-S355-AW','reference','NA')
# Main spatial association figure: all three mandatory sources, no invented toe marker.
fig,axs=plt.subplots(3,2,figsize=(10,8.3),layout='constrained')
for i,sid in enumerate(['G07-V1-S355-AW','X10-V1-S355-AW','X23-V1-S355-AW']):
 g,t,m,height=load(sid);x=g['xyz'];cx=x[m];y=t['T2_MPa'][m];w=t['area'][m];hy=y>=q(y,w)
 scatter(axs[i,0],x,height,'Normal relief (mm)');boundaries(axs[i,0],g,t,m,True);axs[i,0].set_title(sid.split('-')[0]+' measured shape and existing proxies')
 scatter(axs[i,1],cx,y,'Numerical T2 (MPa)');boundaries(axs[i,1],g,t,m,True);axs[i,1].scatter(cx[hy,0],cx[hy,1],s=1.2,c='#b30a79',rasterized=True);axs[i,1].set_title(sid.split('-')[0]+' reference with High95 in magenta')
save(fig,'figures/main/Fig08_Geometry_stress_association','G07, X10 and X23 processed measured front geometry and frozen numerical reference on identical canonical axes. Left: parent-plane-normal relief, in mm; right: T2 in MPa with reference High95 vertices in magenta. Blue solid and dotted contours delimit the existing height/collar proxies, not measured toe trajectories. Red X-cap lines are native loading boundaries; black dashed rectangles are evaluation cores. The display is planar XY without relief exaggeration. Reference fields have no observation condition or neural seed. This retrospective association diagnostic does not validate physical stress or identify a boundary cause.','G07;X10;X23','reference','NA')
# Plate contrast includes the adverse X group and both seeds, without pointwise CI.
plate=pd.read_csv(D/'R2_PLATE_HIGH95_COMPARISON.csv');ps=pd.read_csv(D/'PLATE_SEED_PAIRED_CONTRASTS.csv');fig,axs=plt.subplots(1,2,figsize=(10,4.3),layout='constrained');colors=['#2467a3','#c47826','#3e8e6c'];conditions=['FULL','X50','X43'];xx=np.arange(5)
for j,c in enumerate(conditions):
 z=plate[plate.condition==c].set_index('plate').loc[list('CEGHX')];pos=xx+(j-1)*.24
 for ax,metric in zip(axs,['delta_high95_IoU','delta_L2']):
  ax.bar(pos,z[metric],width=.22,color=colors[j],label=c)
  for seed,marker in [(20261021,'o'),(20261022,'x')]:
   zz=ps[(ps.condition==c)&(ps.seed==seed)].set_index('plate').loc[list('CEGHX')];ax.scatter(pos,zz[metric],marker=marker,c='black',s=15,zorder=4)
for ax in axs:ax.axhline(0,color='black',lw=.7);ax.set_xticks(xx,list('CEGHX'));ax.set_xlabel('Held-out documentary plate');ax.legend(ncol=3)
axs[0].set_ylabel('N3 minus N2 High95 area IoU');axs[1].set_ylabel('N3 minus N2 normalized L2')
save(fig,'PLATE_LOCALIZATION_CONTRAST_FIGURE','All five documentary plates and all three frozen observation conditions. Bars are N3-minus-N2 contrasts after source-within-plate averaging and arithmetic averaging of separately scored neural seeds. Black circles and crosses retain seeds 20261021 and 20261022, respectively; they are not confidence intervals. Positive IoU is favorable, while positive L2 is unfavorable. X localization deteriorates under all contexts and both seeds. Retrospective descriptive reaggregation; no new inference.','all13','FULL;X50;X43','20261021;20261022')
for ext in ['png','pdf']:shutil.copy2(D/('PLATE_LOCALIZATION_CONTRAST_FIGURE.'+ext),D/'figures'/'main'/('Fig09_Plate_localization_contrasts.'+ext))
# Remove copied, superseded main figure files only inside the new workspace.
for stem in ['Fig08_Matched_fields_and_error','Fig09_Accuracy_localization_tradeoff']:
 for ext in ['png','pdf']:
  p=D/'figures'/'main'/(stem+'.'+ext)
  if p.exists():p.unlink()
for sid in info:
 g,t,m,height=load(sid);x=g['xyz'];fig,axs=plt.subplots(1,3,figsize=(13,3.4),layout='constrained');scatter(axs[0],x,height,'Normal relief (mm)');scatter(axs[1],x[m],t['T2_MPa'][m],'T2 (MPa)');scatter(axs[2],x,t['region'],'Existing region code',limits=(0,2),cmap='tab10')
 for a in axs:boundaries(a,g,t,m,True)
 for a,ttl in zip(axs,['Processed measured shape','Frozen numerical T2 reference','0 parent; 1 height; 2 collar proxies']):a.set_title(ttl,fontsize=10)
 save(fig,'figures/supplementary/'+sid+'_geometry_reference',f'{sid}: original processed measured geometry, existing numerical T2 reference in MPa, and frozen geometry-only region codes on the same original coordinates. Relief is normal to the documented fitted parent plane, in mm. Blue contours are geometric proxies, not measured toe trajectories. Red lines are native X loading caps and black dashes denote core bounds. No neural seed/observation context applies. Retrospective descriptive association; no experimental stress validation.',sid,'reference','NA')
for sid in ['G07-V1-S355-AW','X10-V1-S355-AW','X23-V1-S355-AW']:
 g,t,m,height=load(sid);x=g['xyz'];cx=x[m];y=t['T2_MPa'][m];w=t['area'][m];hy=y>=q(y,w)
 for cond in ['FULL','X50','X43']:
  for seed in [20261021,20261022]:
   values=[]
   for model in ['N2','N3']:
    r=registry[(registry.source_id==sid)&(registry.model==model)&(registry.condition==cond)&(registry.seed.astype(str)==str(seed))].iloc[0];values.append(np.load(r.path)['pred_MPa'])
   lo=min(y.min(),*(v.min() for v in values));hi=max(y.max(),*(v.max() for v in values));lim=max(abs(v-y).max() for v in values);fig,axs=plt.subplots(4,3,figsize=(12,12),layout='constrained')
   # First row shows true 3-D aspect, existing proxies and an actual source section.
   ax=axs[0,0];ax.remove();a=fig.add_subplot(4,3,1,projection='3d');a.scatter(*x[::8].T,c=x[::8,2],s=1.8,cmap='viridis');a.set_box_aspect(np.ptp(x,axis=0));a.set(xlim=(x[:,0].min(),x[:,0].max()),ylim=(16,44),zlim=(x[:,2].min(),x[:,2].max()),xlabel='X (mm)',ylabel='Y (mm)',zlabel='Z (mm)',title='Measured front; physical aspect')
   a.set_zticks([]);a.set_zlabel('');a.text2D(.02,.88,f'Z range {x[:,2].min():.2f} to {x[:,2].max():.2f} mm',transform=a.transAxes,fontsize=8)
   scatter(axs[0,1],x,t['region'],'Frozen region code',limits=(0,2),cmap='tab10');boundaries(axs[0,1],g,t,m,True);axs[0,1].set_title('Frozen geometry proxies',fontsize=10)
   ym=np.unique(x[:,1])[np.argmin(abs(np.unique(x[:,1])-30))];section=np.isclose(x[:,1],ym,atol=1e-7);ix=np.argsort(x[section,0]);axs[0,2].plot(x[section,0][ix],height[section][ix],color='#236c94');axs[0,2].axhline(.5,color='gray',ls='--',lw=.7);axs[0,2].set(xlabel='X (mm)',ylabel='Parent-normal relief (mm)',title=f'Original transverse profile Y={ym:g} mm')
   for j,(v,ttl) in enumerate(zip([y]+values,['Reference T2','N2 prediction','N3 prediction'])):scatter(axs[1,j],cx,v,'T2 (MPa)',(lo,hi));boundaries(axs[1,j],g,t,m);axs[1,j].set_title(ttl)
   for j,(v,ttl) in enumerate(zip(values,['N2 minus reference','N3 minus reference'])):scatter(axs[2,j],cx,v-y,'Error (MPa)',(-lim,lim),'coolwarm');boundaries(axs[2,j],g,t,m);axs[2,j].set_title(ttl)
   # Original High95 support stays fixed. Mask differences are not used to create toe labels.
   h2=values[0]>=q(values[0],w);h3=values[1]>=q(values[1],w);category=np.zeros(len(cx));category[hy&h2&~h3]=1;category[hy&~h2&h3]=2;axs[2,2].scatter(cx[:,0],cx[:,1],s=.8,c='#dddddd',rasterized=True)
   for mask,col,lab in [(category==1,'#c33d3d','Reference-high lost by N3'),(category==2,'#287c42','Reference-high gained by N3')]:axs[2,2].scatter(cx[mask,0],cx[mask,1],s=2,c=col,label=lab,rasterized=True)
   boundaries(axs[2,2],g,t,m);axs[2,2].legend(fontsize=7);axs[2,2].set_title('Retrospective changed true-positive sets')
   for j,(mask,ttl) in enumerate(zip([hy,h2,h3],['Reference High95','N2 own-field High95','N3 own-field High95'])):
    axs[3,j].scatter(cx[:,0],cx[:,1],s=.8,c='#e0e0e0',rasterized=True);axs[3,j].scatter(cx[mask,0],cx[mask,1],s=2,c='#a01876',rasterized=True);boundaries(axs[3,j],g,t,m);axs[3,j].set_title(ttl)
   caption=f'{sid}, {cond}, seed {seed}. Actual processed measured front XYZ and one original Y≈30 mm transverse profile; physical 3-D aspect with no relief exaggeration. Frozen geometry regions are proxies, not documentary measured toe trajectories. T2 reference and stored N2/N3 predictions use common MPa limits; prediction-minus-reference errors use one zero-centered scale. Own-field High95 masks retain the original weighted-CDF thresholds. Red vertical lines show native loaded X caps, black dashes show the unchanged evaluation core. Changed true-positive sets are retrospective diagnostics. All stress fields are numerical, not experimental; no crack location or physically validated toe marker is shown.'
   save(fig,'figures/supplementary/'+sid+'_'+cond+'_s'+str(seed)+'_spatial',caption,sid,cond,str(seed))
(D/'R2_SPATIAL_FIGURE_REGISTRY.json').write_text(json.dumps(captions,indent=2))
print('FROZEN_DATA_FIGURE_PAIRS',len(captions))
