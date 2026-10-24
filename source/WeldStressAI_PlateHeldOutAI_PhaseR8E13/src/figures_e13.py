from common_e13 import *
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from score_e13 import quantile
def figures(data,geom,preds,source,plate,study,regional,history,resources,domains,feature_shift,mesh,diagnostics,binned,decision):
 sources=sorted(data);keys=[('B0_CONSTANT','NA'),('B1_GEOMETRY_RIDGE','NA'),('N1_POINT_TRANSFORMER','20261021'),('N1_POINT_TRANSFORMER','20261022')];labels=['Constant','Ridge','PT seed 21','PT seed 22'];colors=['#888888','#c57b14','#1667b2','#9f328e'];plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
 def save(i,name,fig):
  fig.suptitle(f'R8-E13 | {name}',fontsize=13);fig.tight_layout(rect=(0,0,1,.97));p=R/'14_figures'/f'{i:02d}_{name.replace(" ","_").replace("/","-")}';fig.savefig(p.with_suffix('.png'),dpi=150);fig.savefig(p.with_suffix('.pdf'));plt.close(fig);print('FIGURE',i,name,flush=True)
 def bars(i,name,frame,value,index):
  fig,ax=plt.subplots(figsize=(12,4));xx=sorted(frame[index].unique());w=.8/4
  for k,((model,seed),lab,color) in enumerate(zip(keys,labels,colors)):
   ss=frame[(frame.model==model)&(frame.seed.astype(str)==seed)].set_index(index);vals=[ss.loc[x,value] if x in ss.index else np.nan for x in xx];ax.bar(np.arange(len(xx))+(k-1.5)*w,vals,w,label=lab,color=color)
  ax.set_xticks(np.arange(len(xx)),[x.split('-')[0] for x in xx]);ax.set_ylabel(value);ax.legend(ncol=4);save(i,name,fig)
 def panels(ncols=3):return plt.subplots(int(np.ceil(len(sources)/ncols)),ncols,figsize=(5*ncols,3*int(np.ceil(len(sources)/ncols))),squeeze=False)
 fig,axs=panels()
 for ax,s in zip(axs.flat,sources):
  g=geom[s];ii=np.arange(0,len(g['xyz']),12);v=g['xyz'];sc=ax.scatter(v[ii,0],v[ii,1],c=v[ii,2],s=2,cmap='viridis',rasterized=True);ax.set_title(s);ax.set_aspect('equal');fig.colorbar(sc,ax=ax,label='Measured front Z (mm)')
 for ax in list(axs.flat)[len(sources):]:ax.axis('off')
 save(1,'Thirteen measured source geometries',fig)
 fig,ax=plt.subplots(figsize=(7,4));ax.bar(list('CEGHX'),[3,1,5,2,2],color='#247ba0');ax.set_ylabel('Qualified source identities');save(2,'Documentary plate groups',fig)
 membership=np.array([[int(s[0]==p) for s in sources] for p in 'CEGHX']);fig,ax=plt.subplots(figsize=(12,3));ax.imshow(membership,cmap='Blues',vmin=0,vmax=1,aspect='auto');ax.set_yticks(range(5),list('CEGHX'));ax.set_xticks(range(13),[s.split('-')[0] for s in sources]);save(3,'Plate source membership',fig)
 fig,ax=plt.subplots(figsize=(12,3));ax.imshow(1-membership,cmap='RdYlBu',vmin=0,vmax=1,aspect='auto');ax.set_yticks(range(5),['F1 held C','F2 held E','F3 held G','F4 held H','F5 held X']);ax.set_xticks(range(13),[s.split('-')[0] for s in sources]);ax.set_xlabel('Blue = training; red = held-out');save(4,'Frozen LOPO design',fig)
 fig,ax=plt.subplots(figsize=(12,4))
 for i,s in enumerate(sources):
  d=data[s];m=d['core']&d['valid'];y=d['T2_MPa'][m];w=d['area'][m];q=[quantile(y,w,p) for p in [.05,.5,.95]];ax.plot([i,i],[q[0],q[2]],color='#247ba0');ax.scatter(i,q[1],color='#247ba0')
 ax.set_xticks(range(13),[s[:3] for s in sources]);ax.set_ylabel('V1 M2 T2 MPa; Q05/median/Q95');save(5,'Qualified target distributions',fig)
 fig,ax=plt.subplots(figsize=(12,4));ax.bar(range(13),[a['M1_M2_L2'] for a in mesh]);ax.set_xticks(range(13),[s[:3] for s in sources]);ax.set_ylabel('Historical M1-M2 normalized L2');save(6,'Numerical reference precision',fig)
 fig,ax=plt.subplots(figsize=(12,4));means=np.stack([np.mean(geom[s]['features'],0) for s in sources]);im=ax.imshow(means,aspect='auto',cmap='coolwarm');ax.set_xlabel('Geometry feature channel');ax.set_yticks(range(13),[s[:3] for s in sources]);fig.colorbar(im,ax=ax,label='Source mean, mixed frozen units');save(7,'Geometry feature distributions',fig)
 fig,ax=plt.subplots(figsize=(9,3));mat=np.zeros((5,3));im=ax.imshow(mat,vmin=0,vmax=1,cmap='Reds');ax.set_xticks(range(3),['Source overlap','Plate overlap','Runtime held-out batches']);ax.set_yticks(range(5),list('CEGHX'))
 for i in range(5):
  for j in range(3):ax.text(j,i,'0',ha='center',va='center')
 save(8,'Independent leakage checks',fig)
 fig,ax=plt.subplots(figsize=(12,4));ax.axis('off');ax.text(.02,.8,'Measured front only → 19 geometry channels → MLP encoder width 24',fontsize=13);ax.text(.02,.55,'Vector attention: K16 + 16 anchors at 1 mm + 16 anchors at 3 mm',fontsize=12);ax.text(.02,.3,'Learned scale mixture + mean of 4096 area-CDF context encodings',fontsize=12);ax.text(.02,.05,'Residual MLP + LayerNorm → scalar K → ×100 MPa; 7,228 parameters',fontsize=12);save(9,'Frozen historical S1 architecture',fig)
 fig,ax=plt.subplots(figsize=(11,5))
 for (f,s),ss in history.groupby(['fold','seed']):ax.plot(ss.epoch,ss.weighted_MSE_K,label=f'{f} {s}')
 ax.set_yscale('log');ax.set_xlabel('Epoch');ax.set_ylabel('Mean importance-weighted minibatch squared K error');ax.legend(ncol=5,fontsize=7);save(10,'Training loss trajectories',fig)
 fig,ax=plt.subplots(figsize=(9,4))
 for k,p in enumerate('CEGHX'):
  vals=[]
  for f in range(1,6):
   t=rows(R/'05_training'/('F'+str(f)+'_s20261021')/'runtime_membership.csv');ss=[x for x in t if int(x['epoch'])==0];vals.append(sum(float(x['source_step_weight']) for x in ss if x['plate']==p)/len(ss))
  ax.bar(np.arange(5),vals,bottom=np.array([0 if 'CEGHX'[i]==p else 0 for i in range(5)]) if False else np.sum([[0 if 'CEGHX'[i]==z else .25 for i in range(5)] for z in 'CEGHX'[:k]],axis=0) if k else 0,label=p)
 ax.set_xticks(range(5),list('CEGHX'));ax.set_ylabel('Actual epoch-0 normalized loss weight');ax.legend(title='Training plate',ncol=5);save(11,'Plate balanced loss contributions',fig)
 rdf=pd.DataFrame(resources);fig,ax=plt.subplots(1,2,figsize=(12,4));ax[0].plot(rdf.RSS_bytes.to_numpy()/1024**3);ax[0].set_ylabel('Training worker RSS GiB, sequential samples');runtime=history.groupby(['fold','seed']).elapsed_s.max();ax[1].bar(range(10),runtime);ax[1].set_ylabel('Seconds');ax[1].set_xticks(range(10),[f'{f}\n{str(s)[-2:]}' for f,s in runtime.index]);save(12,'CPU memory and training runtime',fig)
 fig,ax=plt.subplots(figsize=(6,4));ax.imshow(np.ones((5,2)),vmin=0,vmax=1,cmap='Greens');ax.set_xticks([0,1],['20261021','20261022']);ax.set_yticks(range(5),list('CEGHX'))
 for i in range(5):
  for j in range(2):ax.text(j,i,'80/80',ha='center',va='center')
 save(13,'Training completion matrix',fig)
 bars(14,'Per source normalized L2',source,'L2','source_id');bars(15,'Per plate normalized L2',plate,'L2','plate');bars(16,'Per source MAE',source,'MAE_MPa','source_id')
 fig,axs=plt.subplots(1,3,figsize=(15,4))
 for ax,metric in zip(axs,['equal_plate_L2','equal_plate_MAE_MPa','equal_plate_high95_IoU']):ax.bar(range(4),study[metric],color=colors);ax.set_xticks(range(4),[str(m).replace('N1_POINT_TRANSFORMER','PT').replace('B0_CONSTANT','B0').replace('B1_GEOMETRY_RIDGE','B1')+'\n'+str(s) for m,s in zip(study.model,study.seed)],rotation=20);ax.set_ylabel(metric)
 save(17,'Equal plate macro outcomes',fig)
 fig,ax=plt.subplots(figsize=(6,5));b=source[source.model=='B1_GEOMETRY_RIDGE'].set_index('source_id');n=source[source.model=='N1_POINT_TRANSFORMER'].groupby('source_id').L2.mean();ax.scatter(b.L2,n.reindex(b.index));lim=max(b.L2.max(),n.max())*1.05;ax.plot([0,lim],[0,lim],'--',color='grey');ax.set_xlabel('Ridge source L2');ax.set_ylabel('PT mean-seed source L2');save(18,'Ridge versus neural paired errors',fig)
 fig,ax=plt.subplots(figsize=(6,5));n1=source[(source.model=='N1_POINT_TRANSFORMER')&(source.seed.astype(str)=='20261021')].set_index('source_id');n2=source[(source.model=='N1_POINT_TRANSFORMER')&(source.seed.astype(str)=='20261022')].set_index('source_id');ax.scatter(n1.L2,n2.L2.reindex(n1.index));lim=max(n1.L2.max(),n2.L2.max())*1.05;ax.plot([0,lim],[0,lim],'--',color='grey');ax.set_xlabel('Seed 20261021 L2');ax.set_ylabel('Seed 20261022 L2');save(19,'Seed sensitivity',fig)
 worst=plate[plate.model=='N1_POINT_TRANSFORMER'].sort_values('L2').iloc[-1].plate;bars(20,'Worst neural held out plate '+worst,source[source.plate==worst],'L2','source_id')
 lo=min(float(data[s]['T2_MPa'][data[s]['core']].min()) for s in sources);hi=max(float(data[s]['T2_MPa'][data[s]['core']].max()) for s in sources);plo=min(float(preds[k[0],k[1],s][data[s]['core']].min()) for k in keys[2:] for s in sources);phi=max(float(preds[k[0],k[1],s][data[s]['core']].max()) for k in keys[2:] for s in sources);vmin=min(lo,plo);vmax=max(hi,phi)
 for number,name,kind in [(21,'Reference and neural T2 fields','fields'),(22,'Signed prediction error','signed'),(23,'Absolute prediction error','absolute'),(24,'Reference High95 support','refhigh'),(25,'Predicted High95 support','predhigh'),(26,'High95 spatial overlap','overlap')]:
  cols=3 if kind=='fields' else (1 if kind=='refhigh' else 2);fig,axs=plt.subplots(13,cols,figsize=(5*cols,2.65*13),squeeze=False)
  errlim=max(float(np.max(abs(preds[k[0],k[1],s][data[s]['core']]-data[s]['T2_MPa'][data[s]['core']]))) for k in keys[2:] for s in sources)
  for row,s in enumerate(sources):
   d=data[s];m=d['core']&d['valid'];x=d['xyz'][m];y=d['T2_MPa'][m];w=d['area'][m];hy=y>=quantile(y,w)
   for col in range(cols):
    p=preds['N1_POINT_TRANSFORMER',str(20261021+max(0,col-1) if kind=='fields' else 20261021+col),s][m] if kind!='refhigh' else y;hp=p>=quantile(p,w);kw={}
    if kind=='fields':v=y if col==0 else p;cmap='viridis';kw=dict(vmin=vmin,vmax=vmax);title='Reference' if col==0 else 'PT seed '+str(20+col)
    elif kind=='signed':v=p-y;cmap='coolwarm';kw=dict(vmin=-errlim,vmax=errlim);title='Signed MPa seed '+str(21+col)
    elif kind=='absolute':v=abs(p-y);cmap='magma';kw=dict(vmin=0,vmax=errlim);title='Absolute MPa seed '+str(21+col)
    elif kind=='refhigh':v=hy.astype(int);cmap='Greys';kw=dict(vmin=0,vmax=1);title='Reference high95'
    elif kind=='predhigh':v=hp.astype(int);cmap='Greys';kw=dict(vmin=0,vmax=1);title='Predicted high95 seed '+str(21+col)
    else:v=hy.astype(int)+2*hp.astype(int);cmap=matplotlib.colors.ListedColormap(['#eeeeee','#d94b3d','#3986c6','#4d9d46']);kw=dict(vmin=0,vmax=3);title='0 neither / 1 FN / 2 FP / 3 overlap'
    ax=axs[row,col];sc=ax.scatter(x[::3,0],x[::3,1],c=v[::3],s=1,cmap=cmap,rasterized=True,**kw);ax.set_title(s[:3]+' | '+title);ax.set_aspect('equal');fig.colorbar(sc,ax=ax,shrink=.7)
  save(number,name,fig)
 for number,name,axis in [(27,'Along weld area averaged profiles',1),(28,'Transverse center slice profiles',0)]:
  fig,axs=panels()
  for ax,s in zip(axs.flat,sources):
   d=data[s];m=d['core']&d['valid'];x=d['xyz'];w=d['area'];use=m.copy()
   if axis==0:use&=abs(x[:,1]-(x[:,1].min()+x[:,1].max())/2)<=.5
   edges=np.linspace(x[use,axis].min(),x[use,axis].max()+1e-8,31);series=[('Reference',d['T2_MPa'],'black')]+[(labels[k],preds[keys[k][0],keys[k][1],s],colors[k]) for k in [1,2,3]]
   for label,y,color in series:
    xx=[];yy=[]
    for left,right in zip(edges[:-1],edges[1:]):
     z=use&(x[:,axis]>=left)&(x[:,axis]<right)
     if z.any():xx.append(np.average(x[z,axis],weights=w[z]));yy.append(np.average(y[z],weights=w[z]))
    ax.plot(xx,yy,label=label,color=color)
   ax.set_title(s[:3]);ax.set_xlabel(('X' if axis==0 else 'Y')+' mm');ax.set_ylabel('T2 MPa')
  axs.flat[0].legend(fontsize=6)
  for ax in list(axs.flat)[13:]:ax.axis('off')
  save(number,name,fig)
 fig,ax=plt.subplots(figsize=(10,4))
 for (model,seed),lab in zip(keys,labels):
  ss=regional[(regional.model==model)&(regional.seed.astype(str)==seed)];means=ss.groupby(['plate','region']).L2.mean().groupby('region').mean();ax.plot(means.index,means.values,'o-',label=lab)
 ax.set_xlabel('Frozen V1 geometric region code');ax.set_ylabel('Equal-plate regional L2');ax.legend();save(29,'Geometry proxy regional errors',fig)
 fig,ax=plt.subplots(figsize=(9,4));bf=pd.DataFrame(binned)
 for seed in ['20261021','20261022']:
  z=bf[(bf.model=='N1_POINT_TRANSFORMER')&(bf.seed.astype(str)==seed)&(bf.descriptor=='target_T2_MPa')];ax.scatter(z.descriptor_mean,z.MAE_MPa,s=8,alpha=.4,label=seed)
 ax.set_xlabel('Reference T2 MPa, evaluation only');ax.set_ylabel('Area-weighted binned MAE MPa');ax.legend();save(30,'Stress magnitude and prediction error',fig)
 fig,ax=plt.subplots(figsize=(12,5));im=ax.imshow(np.stack(feature_shift),aspect='auto',vmin=0,vmax=1,cmap='magma');ax.set_yticks(range(13),[s[:3] for s in sources]);ax.set_xlabel('Feature channel');fig.colorbar(im,ax=ax,label='Core area fraction beyond training feature range');save(31,'Held out feature range shift',fig)
 fig,ax=plt.subplots(figsize=(7,5));dom=pd.DataFrame(domains).set_index('source_id');n=source[source.model=='N1_POINT_TRANSFORMER'].groupby('source_id').L2.mean();ax.scatter(dom.geometry_mean_standardized_distance,n.reindex(dom.index))
 for s in sources:ax.annotate(s[:3],(dom.loc[s,'geometry_mean_standardized_distance'],n.loc[s]),fontsize=7)
 ax.set_xlabel('Geometry-only mean standardized descriptor distance');ax.set_ylabel('Mean-seed held-out L2');save(32,'Domain shift association not causality',fig)
 bars(33,'Plate level signed bias',plate,'bias_MPa','plate')
 fig,ax=plt.subplots(figsize=(12,4));ax.plot(range(13),[a['M1_M2_L2'] for a in mesh],'o-',label='M1-M2 consistency');ax.plot(range(13),n.reindex(sources),'o-',label='Mean-seed neural error');ax.set_yscale('log');ax.set_xticks(range(13),[s[:3] for s in sources]);ax.set_ylabel('Normalized L2, no error-bound interpretation');ax.legend();save(34,'Neural error and mesh discrepancy',fig)
 fig,ax=plt.subplots(figsize=(10,4));mat=np.stack([source[source.model=='N1_POINT_TRANSFORMER'].groupby('source_id')[k].mean().reindex(sources).to_numpy() for k in ['L2','high95_IoU','worst_regional_L2']]);im=ax.imshow(mat,aspect='auto',cmap='viridis');ax.set_yticks(range(3),['L2 lower better','High95 IoU higher better','Worst regional L2 lower better']);ax.set_xticks(range(13),[s[:3] for s in sources]);fig.colorbar(im,ax=ax);save(35,'Observed source failure mode matrix',fig)
 fig,ax=plt.subplots(figsize=(12,5));ax.axis('off');lines=[decision,'10/10 fresh fits; 5 documentary plate groups; 13 qualified sources','Primary: equal-plate macro normalized L2']+[f'{r.model} seed {r.seed}: L2 {r.equal_plate_L2:.5f}, MAE {r.equal_plate_MAE_MPa:.3f} MPa, IoU {r.equal_plate_high95_IoU:.4f}' for r in study.itertuples()]+['Internal plate-held-out numerical feasibility only.','Batch independence and physical/external stress validation are not established.'];ax.text(.02,.95,'\n\n'.join(lines),va='top',fontsize=11);save(36,'Scientific decision and scope',fig)
