from common_e15 import *
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
 df=pd.read_csv(R/'SOURCE_LEVEL_FIELD_METRICS.csv');means=pd.read_csv(R/'15_plate_level_metrics/ARITHMETIC_SEED_METRIC_MEANS.csv');var=pd.read_csv(R/'CONTEXT_PREDICTION_VARIATION.csv');matches=pd.read_csv(R/'BOUNDARY_INTERIOR_MATCHED_COMPARISONS.csv');features=pd.read_csv(R/'FEATURE_NORMALIZATION_DIFFERENCES.csv');overlap=pd.read_csv(R/'07_same_point_contexts/CONTEXT_POINT_OVERLAP.csv');dist=pd.read_csv(R/'12_tile_boundary_analysis/JUMP_DISTANCE_BINS.csv');sid='G07-V1-S355-AW';core=dict(np.load(R/'02_source_geometry'/sid/'CORE.npz'));xyz=core['xyz'];adj=dict(np.load(R/'02_source_geometry'/sid/'ADJACENCY.npz'));ij=adj['pairs'];cross=(adj['tile_id'][ij[:,0]]!=adj['tile_id'][ij[:,1]])&adj['x_axis_edge'];mid=(xyz[ij[:,0]]+xyz[ij[:,1]])/2;reg=[];plt.rcParams.update({'font.size':10,'axes.grid':False,'figure.dpi':120})
 def data(policy='S0',condition='X43',model='N1'):
  a=df[(df.model==model)&(df.seed==20261021)&(df.source_id==sid)&(df.condition==condition)&(df.policy==policy)].iloc[0];return dict(np.load(a.path))
 def start(n,title):
  fig,ax=plt.subplots(figsize=(11,6),layout='constrained');fig.suptitle(str(n)+'. '+title,fontsize=13);return fig,ax
 def save(fig,n,title):
  path=R/'19_figures'/(f'{n:02d}_'+title.replace(' ','_').replace('/','_'));fig.savefig(path.with_suffix('.png'),dpi=160);fig.savefig(path.with_suffix('.pdf'));plt.close(fig);reg.append(dict(number=n,title=title,PNG=str(path.with_suffix('.png')),PDF=str(path.with_suffix('.pdf')),actual_executed_data=True))
 def mapplot(n,title,values,xy=xyz[:,:2],label='MPa',cmap='viridis'):
  fig,ax=start(n,title);limit=max(float(np.max(abs(values))),1e-12);bounds=dict(vmin=-limit,vmax=limit) if cmap=='coolwarm' else {};z=ax.scatter(xy[:,0],xy[:,1],c=values,s=3,cmap=cmap,rasterized=True,**bounds);fig.colorbar(z,ax=ax,label=label);ax.set(xlabel='X (mm)',ylabel='Y (mm)',aspect='equal');save(fig,n,title)
 def grouped(n,title,frame,x,y,group,label):
  fig,ax=start(n,title)
  for name,ss in frame.groupby(group):
   s=ss.groupby(x)[y].mean();ax.plot(s.index.astype(str),s.values,'o-',label=str(name))
  ax.set(xlabel=x,ylabel=label)
  if x=='source_id':ax.tick_params(axis='x',rotation=60,labelsize=7)
  ax.legend(fontsize=8,ncol=2);save(fig,n,title)
 fig,axes=plt.subplots(3,5,figsize=(16,10),layout='constrained');fig.suptitle('1. Thirteen unchanged measured front surfaces; Z in mm')
 for ax,a in zip(axes.flat,rows(R/'SOURCE_CORE_REGISTRY.csv')):
  g=dict(np.load(a['source_geometry_path']));ind=np.arange(0,len(g['xyz']),8);sc=ax.scatter(g['xyz'][ind,0],g['xyz'][ind,1],c=g['xyz'][ind,2],s=2,rasterized=True);cb=fig.colorbar(sc,ax=ax,shrink=.65);cb.set_label('Z mm',fontsize=7);cb.ax.tick_params(labelsize=7);ax.set_title(a['source_id'],fontsize=9);ax.set_aspect('equal');ax.set_xlabel('X mm');ax.set_ylabel('Y mm')
 for ax in axes.flat[13:]:ax.set_visible(False)
 save(fig,1,'Qualified measured surfaces')
 fig,ax=start(2,'Documentary parent plates');counts=pd.Series([a['source_id'][0] for a in rows(R/'SOURCE_CORE_REGISTRY.csv')]).value_counts().sort_index();ax.bar(counts.index,counts.values);ax.set(xlabel='Documentary plate (batch independence unresolved)',ylabel='Qualified sources');save(fig,2,'Documentary plate groups')
 grouped(3,'Historical field accuracy',means[means.policy=='S0'].assign(series=lambda d:d.model), 'condition','L2','series','Equal-plate normalized L2; mean of seed metrics')
 grouped(4,'Historical High95 localization',means[means.policy=='S0'],'condition','high95_IoU','model','Area High95 IoU; mean of seed metrics')
 mapplot(5,'Original restricted hard tile ownership',core['tile_id'],label='Original restricted tile ID',cmap='tab10')
 fig,ax=start(6,'Matched points and visible contexts: G07 X43 tile 2');g=dict(np.load(H/'02_geometry'/(sid+'.npz')));old=dict(np.load(J/'07_context_geometry'/sid/'X43_2.npz'));new=dict(np.load(R/'02_source_geometry'/sid/'X43_SHIFT_2.npz'));ax.scatter(g['xyz'][::30,0],g['xyz'][::30,1],s=2,color='lightgray');sel=core['tile_id']==2;ax.scatter(xyz[sel][::20,0],xyz[sel][::20,1],s=6,label='identical query points')
 for a,color,label in [(old,'tab:blue','A original'),(new,'tab:orange','B shifted +2 mm')]:
  lo=a['xyz'][:,0].min();hi=a['xyz'][:,0].max();ax.axvline(lo,color=color,label=label);ax.axvline(hi,color=color)
 ax.set(xlabel='X (mm)',ylabel='Y (mm)');ax.legend();save(fig,6,'Matched original point contexts')
 grouped(7,'Actual selected context ID overlap',overlap,'condition','context_Jaccard','plate','Context-ID Jaccard A versus shifted B')
 p0=data();ps=data('SHIFT');delta=ps['pred_MPa']-p0['pred_MPa'];mapplot(8,'Same-point shifted-context difference N1 X43 G07',delta,label='Shift minus original (MPa)',cmap='coolwarm')
 grouped(9,'Context disagreement by observation',var[var.policy=='SHIFT'],'condition','RMS_difference_MPa','model','Original-area-weighted RMS change (MPa)')
 grouped(10,'Context disagreement by plate',var[(var.policy=='SHIFT')&(var.condition=='X43')],'plate','RMS_difference_MPa','model','Source-mean paired RMS change (MPa)')
 fig,ax=start(11,'Nineteen-channel visibility contract');contract=pd.read_csv(R/'FEATURE_DEPENDENCY_CONTRACT.csv');ax.imshow(np.vstack([contract.local.astype(int),contract.visible_global.astype(int),contract.oracle_replace.astype(int)]),aspect='auto',vmin=0,vmax=1,cmap='Blues');ax.set(yticks=[0,1,2],yticklabels=['local support','visible global','oracle replaced'],xticks=np.arange(19),xticklabels=np.arange(19),xlabel='Channel index');save(fig,11,'Feature visibility contract')
 grouped(12,'Centered coordinate feature changes',features[features.channel.isin([0,1,2])],'channel','RMS_change','condition','Feature RMS change (dimensionless)')
 grouped(13,'Height representation changes',features[features.channel.isin([2,8,13,18])],'channel','RMS_change','condition','RMS feature change; channel13 is mm, others /60mm')
 grouped(14,'Matched-point feature changes',features,'channel','RMS_change','condition','Per-window RMS feature change (channel-specific units)')
 fig,ax=start(15,'Full versus restricted feature representation');detail=pd.read_csv(R/'FEATURE_NORMALIZATION_VALUES.csv');ss=detail[(detail.source_id==sid)&(detail.condition=='X43')&(detail.channel==0)];ax.scatter(ss.full_normalized,ss.visible_normalized,s=3);v=[min(ss.full_normalized.min(),ss.visible_normalized.min()),max(ss.full_normalized.max(),ss.visible_normalized.max())];ax.plot(v,v,'k--');ax.set(xlabel='FULL centered X /60mm',ylabel='Visible X43 centered X /60mm');save(fig,15,'Full versus restricted representation')
 oracle=data('ORACLE');mapplot(16,'Oracle global-feature block diagnostic N1 X43 G07',oracle['pred_MPa']-p0['pred_MPa'],label='Oracle minus NORM-V prediction (MPa)',cmap='coolwarm')
 fig=plt.figure(figsize=(11,6),layout='constrained');ax=fig.add_subplot(111,projection='3d');idx=np.arange(0,len(xyz),15);ax.scatter(*xyz[idx].T,c=core['tile_id'][idx],s=2,cmap='tab10');ax.scatter(*mid[cross][::4].T,c='black',s=4);ax.set(xlabel='X mm',ylabel='Y mm',zlabel='Z mm');fig.suptitle('17. Actual restricted tile boundaries on measured surface');save(fig,17,'Actual tile boundaries in 3D')
 horizontal=adj['x_axis_edge'];pv=p0['pred_MPa'];yv=p0['reference_MPa'];dp=pv[ij[:,1]]-pv[ij[:,0]];dy=yv[ij[:,1]]-yv[ij[:,0]];mapplot(18,'Adjacent predicted X-edge jumps N1 X43 G07',abs(dp[horizontal]),mid[horizontal,:2],label='Absolute predicted jump (MPa)')
 mapplot(19,'Unchanged FE reference X-edge jumps G07',abs(dy[horizontal]),mid[horizontal,:2],label='Absolute reference jump (MPa)')
 fig,ax=start(20,'Boundary versus geometry-matched interior');s=matches[(matches.policy=='S0')&(matches.condition=='X43')];ax.boxplot([s[s.model==m][k] for m in ['N1','N2'] for k in ['mean_boundary_jump_error_MPa','mean_matched_interior_jump_error_MPa']],tick_labels=['N1 seam','N1 interior','N2 seam','N2 interior']);ax.set_ylabel('Mean jump error per source/seed (MPa)');save(fig,20,'Boundary versus matched interior')
 mapplot(21,'Signed excess adjacent jump N1 X43 G07',abs(dp[horizontal])-abs(dy[horizontal]),mid[horizontal,:2],label='Abs(pred jump) minus abs(T2 jump) MPa',cmap='coolwarm')
 grouped(22,'Jump error versus geometric boundary distance',dist[(dist.policy=='S0')&(dist.condition=='X43')],'distance_lower_mm','mean_jump_error_MPa','model','Mean X-edge jump error (MPa)')
 critical=pd.read_csv(R/'12_tile_boundary_analysis/CRITICAL_BOUNDARY_COORDINATES.csv');grouped(23,'Worst original boundary discontinuity',critical[(critical.policy=='S0')&(critical.condition=='X43')],'source_id','jump_error_MPa','model','Maximum boundary jump error (MPa)')
 grouped(24,'Prediction jump by observation width',matches[matches.policy=='S0'],'condition','mean_boundary_pred_jump_MPa','model','Original seam/proxy-line mean predicted jump (MPa)')
 a=df[(df.model=='N1')&(df.seed==20261021)&(df.source_id==sid)&(df.condition=='X43')&(df.policy=='S1')].iloc[0];raw=dict(np.load(a.raw_path));ll=raw['core_position'];cnt=np.bincount(ll,minlength=len(xyz));mu=np.bincount(ll,weights=raw['pred_MPa'],minlength=len(xyz))/cnt;std=np.sqrt(np.maximum(0,np.bincount(ll,weights=raw['pred_MPa']**2,minlength=len(xyz))/cnt-mu**2));mapplot(25,'Raw overlap disagreement N1 X43 G07',std,label='Within-point raw prediction std (MPa)')
 for number,policy,title in [(26,'S1','Uniform overlap weights'),(27,'S2','Geometric partition of unity weights')]:
  wpath=R/'13_stitching_interventions'/(Path(a.raw_path).stem+'_'+policy+'_WEIGHTS.npz');ww=dict(np.load(wpath));fig,ax=start(number,title);yy=xyz[ll,1];pick=yy==yy.min()
  for tile in np.unique(raw['tile_id']):
   z=pick&(raw['tile_id']==tile);order=np.argsort(xyz[ll[z],0]);ax.plot(xyz[ll[z],0][order],ww['weight'][z][order],label='tile '+str(tile))
  ax.set(xlabel='Original query X (mm), first core Y row',ylabel='Normalized contributor weight');ax.legend(ncol=5);save(fig,number,title)
 for number,pols,title in [(28,['S0','S1'],'Historical versus uniform stitching'),(29,['S1','S2'],'Uniform versus geometric stitching')]:
  ss=means[(means.condition=='X43')&means.policy.isin(pols)].assign(series=lambda d:d.model+' '+d.policy);grouped(number,title,ss,'policy','L2','model','Equal-plate L2; mean seed metrics')
 s=matches[matches.condition=='X43'].merge(df,on=['model','seed','source_id','plate','condition','policy','fold'],suffixes=('','_field'));fig,ax=start(30,'Continuity and numerical field accuracy')
 for name,ss in s[s.policy.isin(['S0','S1','S2'])].groupby(['model','policy']):ax.scatter(ss.mean_boundary_jump_error_MPa,ss.L2,s=18,label=' '.join(name))
 ax.set(xlabel='Mean original-boundary jump error (MPa)',ylabel='Source normalized L2');ax.legend(ncol=3,fontsize=8);save(fig,30,'Continuity versus T2 accuracy')
 grouped(31,'High95 localization by stitching policy',means[(means.condition=='X43')&means.policy.isin(['S0','S1','S2'])],'policy','high95_IoU','model','Equal-plate High95 IoU; mean seed metrics')
 absolute=pd.read_csv(R/'16_high95_localization/ABSOLUTE_AMPLITUDE_SEED_MACROS.csv');grouped(32,'Peak stress amplitude preservation',absolute[(absolute.condition=='X43')&absolute.policy.isin(['S0','S1','S2'])],'policy','absolute_peak_error_MPa','model','Equal-plate mean absolute peak error (MPa)');grouped(33,'False-negative hotspot area',means[(means.condition=='X43')&means.policy.isin(['S0','S1','S2'])],'policy','high95_FN_area_mm2','model','Mean original T0 FN area (mm2)')
 ss=df[(df.condition=='X43')&df.policy.isin(['S0','S2'])].pivot_table(index='source_id',columns=['model','policy'],values='L2');fig,ax=start(34,'Source heterogeneity S2 minus S0');v=np.column_stack([ss[(m,'S2')]-ss[(m,'S0')] for m in ['N1','N2']]);z=ax.imshow(v,aspect='auto',cmap='coolwarm');ax.set(yticks=np.arange(len(ss)),yticklabels=ss.index,xticks=[0,1],xticklabels=['N1','N2']);fig.colorbar(z,ax=ax,label='L2 change (negative improves)');save(fig,34,'Source plate heterogeneity')
 evidence=pd.read_csv(R/'MECHANISM_EVIDENCE_MATRIX.csv');fig,ax=start(35,'Mechanism evidence classification');ax.axis('off');tbl=ax.table(cellText=evidence[['mechanism','classification']].values,colLabels=['Mechanism','Permitted evidence class'],cellLoc='left',loc='center',colWidths=[.45,.55]);tbl.auto_set_font_size(False);tbl.set_fontsize(8);tbl.scale(1,2.5);save(fig,35,'Mechanism evidence matrix')
 grouped(36,'Controlled block and residual context sensitivity',var[var.condition=='X43'].assign(series=lambda d:d.model+' '+d.policy),'policy','RMS_difference_MPa','model','Paired area-weighted RMS change (MPa)')
 costs=pd.read_csv(R/'RESOURCE_ACCOUNTING.csv');grouped(37,'Actual sequential inference costs',costs,'stage','elapsed_s','model','Mean worker elapsed time (s)')
 fig,ax=start(38,'Future inference design: separately authorized tests');ax.axis('off');lines=['Freeze context/normalization contract before new cohort access.','Test any retained stitching policy jointly on continuity, L2, High95 and peak bias.','Keep N1/N2 and both seeds; no policy winner selected by exposed plates.','Test representation blocks separately with design-defined physical datums.','Use unused documented parent plates and recorded acquisition sessions.','This audit changes no weights and establishes no physical stress validation.'];ax.text(.03,.9,'\n\n'.join(lines),va='top',fontsize=12,transform=ax.transAxes);save(fig,38,'Future inference design requirements')
 table(R/'19_figures/FIGURE_REGISTRY.csv',reg);write(R/'19_figures/FIGURES_COMPLETE.json',dict(UTC=now(),pairs=len(reg),passed=len(reg)==38));print('FIGURES_COMPLETE',len(reg),flush=True)
if __name__=='__main__':main()
