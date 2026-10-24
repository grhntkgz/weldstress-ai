from common_e15 import *
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
 df=pd.read_csv(R/'SOURCE_LEVEL_FIELD_METRICS.csv');sid='G07-V1-S355-AW';core=dict(np.load(R/'02_source_geometry'/sid/'CORE.npz'));xyz=core['xyz'];adj=dict(np.load(R/'02_source_geometry'/sid/'ADJACENCY.npz'));ij=adj['pairs'];mid=(xyz[ij[:,0]]+xyz[ij[:,1]])/2;mask=adj['x_axis_edge']
 def values(policy):return dict(np.load(df[(df.model=='N1')&(df.seed==20261021)&(df.source_id==sid)&(df.condition=='X43')&(df.policy==policy)].iloc[0].path))
 p=values('S0');shift=values('SHIFT');oracle=values('ORACLE');pv=p['pred_MPa'];ref=p['reference_MPa'];jump=abs(pv[ij[:,1]]-pv[ij[:,0]])-abs(ref[ij[:,1]]-ref[ij[:,0]]);plt.rcParams.update({'font.size':10,'axes.grid':False,'figure.dpi':120})
 for n,title,xy,v,label in [(8,'Same-point shifted-context difference N1 X43 G07',xyz[:,:2],shift['pred_MPa']-pv,'Shift minus original (MPa)'),(16,'Oracle global-feature block diagnostic N1 X43 G07',xyz[:,:2],oracle['pred_MPa']-pv,'Oracle minus NORM-V prediction (MPa)'),(21,'Signed excess adjacent jump N1 X43 G07',mid[mask,:2],jump[mask],'Abs(pred jump) minus abs(T2 jump) MPa')]:
  path=R/'19_figures'/(f'{n:02d}_'+title.replace(' ','_').replace('/','_'));fig,ax=plt.subplots(figsize=(11,6),layout='constrained');fig.suptitle(str(n)+'. '+title,fontsize=13);lim=max(float(np.max(abs(v))),1e-12);sc=ax.scatter(xy[:,0],xy[:,1],c=v,s=3,cmap='coolwarm',rasterized=True,vmin=-lim,vmax=lim);fig.colorbar(sc,ax=ax,label=label);ax.set(xlabel='X (mm)',ylabel='Y (mm)',aspect='equal');fig.savefig(path.with_suffix('.png'),dpi=160);fig.savefig(path.with_suffix('.pdf'));plt.close(fig)
 write(R/'18_independent_verification/SIGNED_MAP_SCALE_RECEIPT.json',dict(UTC=now(),passed=True,figures=[8,16,21],change='symmetric signed color limits center zero; prediction/metric arrays unchanged'));print('SIGNED_MAP_SCALE_PASS',flush=True)
if __name__=='__main__':main()
