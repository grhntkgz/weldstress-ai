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
