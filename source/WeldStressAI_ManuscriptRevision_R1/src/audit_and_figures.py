from pathlib import Path
import csv,json,hashlib,shutil
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image,ImageDraw
D=Path(r'E:\welding\outputs\WeldStressAI_ManuscriptRevision_R1');S=D/'source_snapshot';F=D/'figures'/'main'
def read(p):return pd.read_csv(S/p)
means=read('17_model_comparisons/TWO_SEED_METRIC_MEANS.csv');seeds=read('17_model_comparisons/SEED_METRICS.csv');plates=read('15_plate_metrics/ALL_MODEL_PLATE_L2.csv');q=read('QUALIFIED13_SOURCE_REGISTRY.csv');effects=read('04_feature_mechanisms/EQUAL_PLATE_EFFECTS.csv');contrasts=read('17_model_comparisons/PRIMARY_CONTRASTS.csv')
audit=[]
def claim(id,description,path,key,col,value,formula='exact released CSV cell',unit='dimensionless',where='Results tables and figures'):
 audit.append(dict(claim_id=id,claim=description,evidence_file=str(S/path),row_key=key,column=col,verified_value=value,unit=unit,derivation=formula,manuscript_location=where,evidence_level='NUMERICAL_RELEASE',status='PASS'))
for frame,path,keys,cols,prefix in [(means,'17_model_comparisons/TWO_SEED_METRIC_MEANS.csv',['model','condition'],['L2','MAE_MPa','high95_IoU','false_negative_area_mm2','absolute_max_error_MPa','absolute_Q95_error_MPa'],'M'),(seeds,'17_model_comparisons/SEED_METRICS.csv',['model','seed','condition'],['L2','MAE_MPa','high95_IoU'],'S'),(effects,'04_feature_mechanisms/EQUAL_PLATE_EFFECTS.csv',['model','condition','effect'],['L2','high95_IoU'],'F'),(contrasts,'17_model_comparisons/PRIMARY_CONTRASTS.csv',['condition'],[c for c in contrasts if c!='condition'],'D')]:
 for i,row in frame.iterrows():
  for col in cols:claim(f'{prefix}{i+1:03}_{col}',f'{col} for '+', '.join(str(row[k]) for k in keys),path,';'.join(f'{k}={row[k]}' for k in keys),col,float(row[col]),unit='MPa' if col.endswith('MPa') else 'mm2' if 'mm2' in col else '%' if 'percent' in col else 'dimensionless')
for col,op in [('T2_L2','min'),('T2_L2','max'),('T2_worst_regional_L2','max'),('T2_high95_IoU','min'),('mapping_coverage','min')]:
 claim('Q_'+op+'_'+col,f'{op} {col} across all thirteen sources','QUALIFIED13_SOURCE_REGISTRY.csv','all13',col,float(getattr(q[col],op)()),op+' across all source rows')
for i,row in q.iterrows():
 for col in ['T2_L2','T2_worst_regional_L2','T2_high95_IoU','mapping_coverage']:claim(f'Q{i:02}_{col}',col,'QUALIFIED13_SOURCE_REGISTRY.csv',row['source_id'],col,float(row[col]))
for i,row in plates.iterrows():
 for col in plates:
  if col!='plate':claim(f'P{i}_{col}','Plate-specific L2','15_plate_metrics/ALL_MODEL_PLATE_L2.csv',row['plate'],col,float(row[col]))
# Independently check macro aggregation from the released source-level metrics.
source=read('SOURCE_LEVEL_METRICS.csv');checks=[]
for _,r in seeds.iterrows():
 mask=(source.model==r.model)&(source.condition==r.condition)
 if str(r.seed)!='NA' and not pd.isna(r.seed):mask &= source.seed.astype(str).str.replace('.0','',regex=False)==str(r.seed).replace('.0','')
 x=source[mask]
 for metric in ['L2','MAE_MPa','high95_IoU']:
  if len(x):
   v=x.groupby('plate')[metric].mean().mean();err=abs(v-r[metric]);checks.append(dict(model=r.model,seed=r.seed,condition=r.condition,metric=metric,recomputed=v,released=r[metric],absolute_error=err,status='PASS' if err<1e-10 else 'FAIL'))
pd.DataFrame(checks).to_csv(D/'qa'/'MACRO_REAGGREGATION_AUDIT.csv',index=False);assert checks and all(x['status']=='PASS' for x in checks)
for _,r in means[means.model.isin(['N1','N2','N3'])].iterrows():
 x=seeds[(seeds.model==r.model)&(seeds.condition==r.condition)];assert len(x)==2
 for c in ['L2','MAE_MPa','high95_IoU']:assert abs(x[c].mean()-r[c])<1e-12
for _,r in contrasts.iterrows():
 a=means[(means.model=='N2')&(means.condition==r.condition)].iloc[0];b=means[(means.model=='N3')&(means.condition==r.condition)].iloc[0]
 assert abs((1-b.L2/a.L2)*100-r.L2_reduction_percent)<1e-10
 assert abs(b.high95_IoU-a.high95_IoU-r.IoU_difference)<1e-12
pd.DataFrame(audit).to_csv(D/'CLAIM_EVIDENCE_AUDIT.csv',index=False,encoding='utf-8-sig')
means.to_csv(D/'MAIN_MODEL_METRICS.csv',index=False);seeds.to_csv(D/'BOTH_SEED_METRICS.csv',index=False);plates.to_csv(D/'ALL_PLATE_METRICS.csv',index=False)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'axes.labelsize':10,'legend.fontsize':8})
figindex=read('SCIENTIFIC_FIGURES.csv');originals=S/'19_scientific_figures'
selected=[]
def save(fig,n,name,orig,caption,reason):
 stem=f'Fig{n:02}_{name}';fig.savefig(F/(stem+'.png'),dpi=300,bbox_inches='tight');fig.savefig(F/(stem+'.pdf'),bbox_inches='tight');plt.close(fig)
 selected.append(dict(number=n,name=name,path='figures/main/'+stem+'.png',PDF='figures/main/'+stem+'.pdf',original_numbers=orig,original_files='; '.join(str(figindex[figindex.number==int(i)].iloc[0].PNG) for i in orig.split(',')),caption=caption,justification=reason))
def show_original(ax,num,title):
 row=figindex[figindex.number==num].iloc[0];im=Image.open(originals/Path(row.PNG).name);ax.imshow(im);ax.axis('off');ax.set_title(title,fontsize=10,pad=4)
fig,axs=plt.subplots(1,2,figsize=(10,4.4));show_original(axs[0],1,'(a) Published processed front surface');show_original(axs[1],5,'(b) Qualified regularized numerical reference')
save(fig,1,'Geometry_and_reference','1,5','Published processed front geometry and regularized tensile maximum-principal-stress reference for G07. Original XYZ and T0 areas are unchanged. The front is measured and processed; the planar rear and elastic boundary-value problem are numerical assumptions. Display subsampling affects illustration only. Stress is T2 in MPa, not measured stress.','Establishes measured input and the numerical quantity learned; G07 is the retained historical illustration, not a newly selected favorable source.')
fig,axs=plt.subplots(1,2,figsize=(10,4));axs[0].plot(q.T2_L2,np.arange(13),'o',label='Whole field');axs[0].plot(q.T2_worst_regional_L2,np.arange(13),'s',label='Worst proxy region');axs[0].axvline(.02,color='k',ls='--',lw=.8,label='Whole-field limit');axs[0].axvline(.03,color='gray',ls=':',label='Regional limit');axs[0].set_yticks(np.arange(13),q.source_id.str.split('-').str[0]);axs[0].set_xlabel('M1/M2 normalized L2');axs[0].legend();axs[1].scatter(q.T2_high95_IoU,np.arange(13));axs[1].axvline(.8,color='k',ls='--');axs[1].set_xlim(.78,1);axs[1].set_xlabel('M1/M2 High95 area IoU');axs[1].set_yticks(np.arange(13),q.source_id.str.split('-').str[0]);fig.tight_layout()
save(fig,2,'FE_reference_qualification','4','Two-level M1/M2 numerical consistency on every accepted source, using identical original-point areas and T2 fields. Dashed limits are the frozen whole-field and High95 criteria; the dotted limit is the regional criterion. Native M1/M2 mesh images are retained as Supplementary Figure S04. Two-level agreement does not establish asymptotic convergence or physical stress accuracy.','Replaces unreadably small five-source mesh montage in the main text with complete thirteen-source qualification; native evidence remains supplementary.')
fig,ax=plt.subplots(figsize=(10,4.6));ax.set_xlim(0,10);ax.set_ylim(0,5);ax.axis('off')
boxes=[(.1,3.2,2.4,1.2,'Registered visible geometry\nFULL / X50 / X43\nFixed original query plan'),(3.1,3.2,2.6,1.2,'19 observable channels\nLocal coordinates / spans\nNormals / relief / areas'),(6.3,3.2,3.4,1.2,'Shared encoder width 24\nThree 16-neighbor sets\nLearned scale attention'),(3.1,.7,2.6,1.2,'4096 visible context points\nMean encoded context'),(6.3,.7,3.4,1.2,'Query + local + context\nPer-query LayerNorm\nScalar T2 / 100 MPa')]
for x,y,w,h,t in boxes:ax.add_patch(plt.Rectangle((x,y),w,h,fc='#f2f4f6',ec='#34536b'));ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=9)
for a,b in [((2.5,3.8),(3.1,3.8)),((5.7,3.8),(6.3,3.8)),((4.4,3.2),(4.4,1.9)),((5.7,1.3),(6.3,1.3)),((8,3.2),(8,1.9))]:ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='->',color='black'))
ax.text(.1,.3,'Executed compact SurfacePT: one block; 7228 parameters; no query-to-query pooling.\nN1/N2 retain historical global channels. N3 requires registered coordinates and a declared query plan.',fontsize=9)
save(fig,3,'Representation_and_executed_network','7,14,15,17','Executed compact SurfacePT and N3 information contract. Visible geometry supplies local features and a 4096-point contextual branch. FULL and restricted observations use the same original evaluation points; only available contextual geometry changes. The actual override has no query-to-query pooling. This is an implementation schematic, not a reproduction of the full published Point Transformer.','Replaces text-only network and observability panels with a readable factual schematic of the executed implementation.')
fig,axs=plt.subplots(1,2,figsize=(10,3.7));colors=['#1764ab','#ce6a19','#23854b','#8c4d9d']
for (model,cond),color in zip([('N1','X43'),('N1','X50'),('N2','X43'),('N2','X50')],colors):
 x=effects[(effects.model==model)&(effects.condition==cond)&effects.effect.isin(['A','B','C'])].set_index('effect').loc[['A','B','C']]
 for ax,metric in zip(axs,['L2','high95_IoU']):ax.plot(np.arange(3),x[metric].to_numpy(),'o-',color=color,label=f'{model} {cond}');ax.axhline(0,color='gray',lw=.6);ax.set_xlabel('Substituted feature block');ax.set_xticks(np.arange(3),['A','B','C'])
axs[0].set_ylabel('Main contrast in normalized L2');axs[1].set_ylabel('Main contrast in High95 area IoU');axs[0].legend(ncol=2);fig.tight_layout()
save(fig,4,'Controlled_factorial_effects','9,10,11','Frozen-weight main contrasts for centering (A), spans including repeated Z span (B), and normal statistics (C), averaged equally by plate and then across both seeds. Contrasts use the complete eight-cell design; negative L2 and positive IoU changes indicate better agreement. Substituted full-information features are nondeployable diagnostic inputs. All pair and triple interactions are supplementary.','Shows the controlled mechanism without treating oracle features as deployable predictions or attributing physical causality.')
models=['B0_CONSTANT','B1_GEOMETRY_RIDGE','B2_GEOMETRY_XGBOOST','N1','N2','N3'];conds=['FULL','X50','X43'];short={'B0_CONSTANT':'Constant','B1_GEOMETRY_RIDGE':'Ridge','B2_GEOMETRY_XGBOOST':'XGBoost','N1':'N1','N2':'N2','N3':'N3'}
fig,axs=plt.subplots(1,2,figsize=(10,4))
for model in models:
 x=means[means.model==model].set_index('condition').reindex(conds)
 for ax,m in zip(axs,['L2','MAE_MPa']):ax.plot(conds,x[m],'o-',label=short[model],ms=4)
axs[0].set_ylabel('Area-normalized L2');axs[1].set_ylabel('Area-weighted MAE (MPa)');axs[0].legend(ncol=2);fig.tight_layout()
save(fig,5,'Whole_field_comparison','19,32','Whole-field normalized L2 and MAE under fixed full and restricted observation conditions. Neural points are arithmetic means of independently evaluated seed metrics; they are not field ensembles. Sources are averaged within plates and then equally across five plates. Constant and Ridge have FULL results only; no restricted baseline values are interpolated.','Displays all baselines and unfavorable N3 accuracy outcomes, separating whole-field accuracy from localization.')
fig,axs=plt.subplots(1,2,figsize=(10,4))
for model in ['N1','N2','N3']:
 for seed,style in [(20261021,'-'),(20261022,'--')]:
  x=seeds[(seeds.model==model)&(seeds.seed.astype(str).str.startswith(str(seed)))].set_index('condition').reindex(conds);axs[0].plot(conds,x.L2,'o'+style,label=f'{model} {str(seed)[-2:]}',ms=3)
for model in ['N1','N2','N3','B2_GEOMETRY_XGBOOST']:axs[1].plot(plates.plate,plates[model+'_X43'],'o-',label=short[model],ms=4)
axs[0].set_ylabel('Normalized L2 by seed');axs[0].legend(ncol=2);axs[1].set_ylabel('X43 normalized L2 by held-out plate');axs[1].legend();fig.tight_layout()
save(fig,6,'Seeds_and_plate_variability','20,21,23','Both fixed neural seeds (labels 21 and 22 denote 20261021 and 20261022) and every held-out documentary plate under X43. Plate values average both neural seed metrics; XGBoost has one fixed seed. Connecting lines aid comparison and imply no continuous plate ordering. The complete source and three-condition tables accompany the paper.','Prevents selective presentation of seeds or plates; full-condition seed instability of N1 remains visible.')
fig,axs=plt.subplots(1,3,figsize=(12,3.6))
for model in ['B1_GEOMETRY_RIDGE','B2_GEOMETRY_XGBOOST','N1','N2','N3']:
 x=means[means.model==model].set_index('condition').reindex(conds)
 for ax,m in zip(axs,['high95_IoU','false_negative_area_mm2','absolute_max_error_MPa']):ax.plot(conds,x[m],'o-',label=short[model],ms=3)
for ax,label in zip(axs,['High95 area IoU','Missed High95 area (mm²)','Absolute field-maximum error (MPa)']):ax.set_ylabel(label)
axs[0].legend(ncol=2);fig.tight_layout()
save(fig,7,'Localization_and_amplitude','24,25,28','High95 overlap, missed reference high-area, and absolute error in field maximum. Each field defines its own area-weighted 95th-percentile threshold. Constant-field ties yield zero missed area while declaring the entire surface high; this degenerate baseline is tabulated but omitted from these curves. A maximum-amplitude error is not the maximum absolute pointwise error. Q95 amplitude errors are reported in Table 3 and Supplementary Figure S28.','Pairs overlap with missed area and peak-amplitude safeguards; removes misleading visual credit for constant-baseline zero false negatives without suppressing its numerical result.')
R=Path(r'E:\welding\outputs\WeldStressAI_FinalResearch_PhaseR8E16');O=R.parent;sid='G07-V1-S355-AW'
corefile=O/'WeldStressAI_InferenceMechanisms_PhaseR8E15'/'02_source_geometry'/sid/'CORE.npz';targetfile=O/'WeldStressAI_PlateHeldOutAI_PhaseR8E13'/'01_dataset'/'targets'/(sid+'.npz')
reg=read('MODEL_PREDICTION_REGISTRY.csv');row=reg[(reg.model=='N3')&(reg.condition=='X43')&(reg.source_id==sid)&(reg.seed.astype(str).str.startswith('20261021'))].iloc[0];predfile=Path(row.path)
assert hashlib.sha256(predfile.read_bytes()).hexdigest()==row.SHA256
core=np.load(corefile);target=np.load(targetfile);pred=np.load(predfile)['pred_MPa'];xyz=core['xyz'];y=target['T2_MPa'][core['query_original_rows']];assert pred.shape==y.shape==(34200,)
extras=[]
for p in [corefile,targetfile,predfile]:extras.append(dict(path=str(p),SHA256=hashlib.sha256(p.read_bytes()).hexdigest(),purpose='Read-only redraw of existing matched fields'))
pd.DataFrame(extras).to_csv(D/'qa'/'SPATIAL_FIGURE_INPUT_HASHES.csv',index=False)
fig,axs=plt.subplots(1,3,figsize=(12,4.1),layout='constrained');lo=min(y.min(),pred.min());hi=max(y.max(),pred.max());limit=float(abs(pred-y).max())
for ax,v,title in zip(axs,[y,pred,pred-y],['FE numerical T2 reference','N3 X43 prediction','Prediction minus reference']):
 signed=ax is axs[2];im=ax.scatter(xyz[:,0],xyz[:,1],c=v,s=1.7,rasterized=True,cmap='coolwarm' if signed else 'viridis',vmin=-limit if signed else lo,vmax=limit if signed else hi);ax.set(title=title,xlabel='X (mm)',ylabel='Y (mm)',aspect='equal');fig.colorbar(im,ax=ax,shrink=.8,label='Error (MPa)' if signed else 'T2 (MPa)')
save(fig,8,'Matched_fields_and_error','26,27','Matched G07 reference and N3 X43 prediction for seed 20261021, followed by signed prediction-minus-reference error on original coordinates. The two stress maps retain shared limits in MPa; the error map retains a zero-centered diverging scale. This historical example was retained before editorial selection, is not the best N3 source, and does not replace all-source quantitative reporting.','Direct spatial evidence, including conspicuous local overprediction and underprediction; no new inference or fabricated FE data.')
fig,axs=plt.subplots(1,2,figsize=(10,3.6));x=np.arange(3);axs[0].bar(x,-contrasts.L2_reduction_percent,color='#a53e37');axs[0].set_ylabel('N3 vs N2 increase in L2 (%)');axs[1].bar(x,contrasts.IoU_difference,color='#287a6b');axs[1].set_ylabel('N3 minus N2 High95 area IoU')
for ax in axs:ax.set_xticks(x,contrasts.condition);ax.axhline(0,color='black',lw=.7)
fig.tight_layout();save(fig,9,'Accuracy_localization_tradeoff','35','Paired N3–N2 trade-off under every observation condition, using means of separately scored seeds. Whole-field L2 increases by 6.07–6.94%, while High95 IoU increases by 0.0532–0.0625. Missed high-area decreases, but field-maximum amplitude error increases. The frozen classification remains METHOD_IMPROVEMENT_MIXED, a descriptive research decision rather than a statistical significance test.','States the central negative and positive result together, without a universal-superiority claim.')
(D/'figures'/'MAIN_FIGURE_REGISTRY.json').write_text(json.dumps(selected,indent=2),encoding='utf-8')
for _,r in figindex.iterrows():
 for ext in ['PNG','PDF']:
  p=originals/Path(r[ext]).name;shutil.copy2(p,D/'figures'/'supplementary'/f'S{int(r.number):02}_{p.name}')
# Contact sheets retain full source images, not image edits.
for batch in range(3):
 items=selected[batch*3:batch*3+3];sheet=Image.new('RGB',(1500,items.__len__()*530),'white');draw=ImageDraw.Draw(sheet)
 for i,item in enumerate(items):
  im=Image.open(D/item['path']);im.thumbnail((1450,490));sheet.paste(im,((1500-im.width)//2,i*530+25));draw.text((15,i*530+5),f"Figure {item['number']}: {item['name']}",fill='black')
 sheet.save(D/'qa'/f'MAIN_CONTACT_{batch+1}.png')
print(json.dumps({'claims':len(audit),'macro_checks':len(checks),'figures':len(selected),'qualified_sources':len(q),'M1M2_bounds':[q.T2_L2.min(),q.T2_L2.max()]}))
