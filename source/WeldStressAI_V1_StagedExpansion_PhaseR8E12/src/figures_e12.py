from setup_e11r1 import *
import os
for k in ['TEMP','TMP','MPLCONFIGDIR']:os.environ[k]=str(R/'tmp')
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
OUT=R/'23_figures';OUT.mkdir(exist_ok=True);ledger=[]
plt.rcParams.update({'font.size':8,'figure.dpi':100,'savefig.dpi':135,'axes.spines.top':False,'axes.spines.right':False})
def save(fig,n,title,caption):
 stem=f'{n:02d}_'+title;fig.suptitle('R8-E12 | '+title.replace('_',' '));fig.tight_layout(rect=(0,0,1,.97));fig.savefig(OUT/(stem+'.png'));fig.savefig(OUT/(stem+'.pdf'));plt.close(fig);ledger.append(dict(number=n,title=title,PNG='23_figures/'+stem+'.png',PDF='23_figures/'+stem+'.pdf',caption=caption));print('FIGURE',n,title,flush=True)
def textfig(n,title,body,caption):
 f,a=plt.subplots(figsize=(10,5));a.axis('off');a.text(.02,.95,body,va='top',wrap=True,fontsize=11);save(f,n,title,caption)
def field(ax,x,t,v,title,label='MPa',cmap='viridis',limits=None):
 tri=mtri.Triangulation(x[:,0],x[:,1],t);tri.set_mask(~np.isfinite(v[t]).all(1));kw={} if limits is None else dict(vmin=limits[0],vmax=limits[1]);im=ax.tripcolor(tri,v,shading='gouraud',cmap=cmap,rasterized=True,**kw);ax.set(title=title,xlabel='X/mm',ylabel='Y/mm',aspect='equal');plt.colorbar(im,ax=ax,label=label,fraction=.03)
def main():
 final=read(R/'R8E12_FINAL_COUNTS.json');prov=rows(R/'SOURCE_PROVENANCE_REGISTRY.csv');receipt=read(R/'01_provenance/AUDIT_RECEIPT.json');queue=rows(R/'FROZEN_SELECTED_FIVE_SOURCES.csv');sids=[a['source_id'] for a in queue];old={a['source_id'] for a in rows(R/'VERIFIED_V1_SOURCE_REGISTRY.csv')};selected=set(sids);features=rows(R/'GEOMETRY_SELECTION_FEATURES.csv');remaining=set(read(R/'00_integrity/COHORT_RECONCILIATION.json')['remaining34']);pr={a['source_id']:a for a in prov};cost=rows(R/'FINAL_STORAGE_ACCOUNTING.csv');met=rows(R/'T2_NUMERICAL_METRICS.csv');qualified=[a['source_id'] for a in met if a['qualified']=='True'];cases={s:R/'cases'/s for s in sids};fields={s:np.load(cases[s]/'13_numerical_qualification/COMPARISON_FIELDS.npz') for s in qualified};tris={s:np.load(cases[s]/'01_frozen_protocol/source/triangles.npy') for s in qualified}
 for n,title,subset in [(1,'Eligible42_geometry_distribution',{a['source_id'] for a in features}),(2,'Existing8_geometry_distribution',old),(3,'Remaining34_geometry_distribution',remaining),(4,'Selected5_geometry_distribution',selected)]:
  fig,ax=plt.subplots(figsize=(10,5))
  for group,color in [('C','tab:blue'),('E','tab:orange'),('G','tab:green'),('H','tab:red'),('X','tab:purple')]:
   data=[a for a in features if a['source_id'] in subset and a['source_id'].startswith(group)];ax.scatter([float(a['relief_P95_mm']) for a in data],[float(a['roughness_residual_RMS_mm']) for a in data],c=color,label='Documentary plate '+group)
   for a in data:ax.annotate(a['source_id'][:3],(float(a['relief_P95_mm']),float(a['roughness_residual_RMS_mm'])),fontsize=6)
  ax.set(xlabel='Front-parent P95 relief/mm',ylabel='Fixed-filter residual RMS/mm');ax.legend(fontsize=7);save(fig,n,title,'Geometry-only descriptors; plate codes documentary, batch independence unresolved.')
 rank=rows(R/'FULL34_GEOMETRY_RANKING.csv');chosen=[a for a in rank if a['selected']=='True'];fig,ax=plt.subplots(figsize=(9,4));ax.bar([a['source_id'][:3] for a in chosen],[float(a['minimum_standardized_distance']) for a in chosen]);ax.set(xlabel='Frozen execution order',ylabel='Minimum standardized geometry distance');save(fig,5,'Selection_diversity','First objective prefers unrepresented documented plate, then max-min distance. No stress/AI features.')
 fig,ax=plt.subplots(figsize=(11,4));plates=sorted({a['confirmed_parent_plate'] for a in prov});xx=np.arange(len(plates));dev=[sum(a['confirmed_parent_plate']==p and a['population']=='DEVELOPMENT47' for a in prov) for p in plates];test=[sum(a['confirmed_parent_plate']==p and a['population']!='DEVELOPMENT47' for a in prov) for p in plates];ax.bar(xx,dev,label='Development');ax.bar(xx,test,bottom=dev,label='Exposed test provenance only');ax.set_xticks(xx,[p.rsplit('_',1)[1] for p in plates]);ax.set(xlabel='Documented plate code within S355MLO',ylabel='Documented coupon identifiers');ax.legend();save(fig,6,'Documented_provenance_relationships','Original metadata plus dissertation3.2.6; no target values from historical test.')
 fig,ax=plt.subplots(figsize=(13,7));
 for i,p in enumerate(plates):
  members=[a for a in prov if a['confirmed_parent_plate']==p];y=np.linspace(.1,.9,len(members));ax.scatter([i]*len(y),y,c=['tab:blue' if a['population']=='DEVELOPMENT47' else 'tab:red' for a in members]);ax.scatter(i,1.07,marker='s',s=90,c='black');ax.text(i,1.12,p.rsplit('_',1)[1],ha='center')
  for a,j in zip(members,y):ax.plot([i,i],[j,1.07],c='gray',lw=.25);ax.annotate(a['source_id'][:3],(i,j),xytext=(5,0),textcoords='offset points',fontsize=6)
 from matplotlib.lines import Line2D
 ax.legend(handles=[Line2D([],[],color='tab:blue',marker='o',ls='',label='Development source'),Line2D([],[],color='tab:red',marker='o',ls='',label='Exposed test: provenance only'),Line2D([],[],color='black',marker='s',ls='',label='Documented parent plate')],loc='upper center',ncol=3,frameon=False)
 ax.axis('off');save(fig,7,'Physical_dependency_graph','Five documented plate-code entities and59 coupon identifiers; blue development,red exposed-test provenance,black documented parent. No fabricated batch/session edges.')
 textfig(8,'Confirmed_and_unresolved_group_levels',f"Documented coupon identifiers:59 (47development +12exposedtest provenance)\nDocumented plate codes:5\nManufacturing batch identifiers:0\nPer-source scan session identifiers:0\nBetween-plate manufacturing dependence remains unresolved.\n47different source identities are not47independent plates.",'Counts refer to documentary entities, not independent laboratory reidentification.')
 pp=rows(R/'GEOMETRY_PAIRWISE_SCREEN.csv');names=sorted(a['source_id'] for a in rows(R/'GEOMETRY_DUPLICATE_SCREEN.csv'));index={s:i for i,s in enumerate(names)};a=np.full((47,47),np.nan)
 for p in pp:a[index[p['source_a']],index[p['source_b']]]=a[index[p['source_b']],index[p['source_a']]]=float(p['RMS_mm'])
 fig,ax=plt.subplots(figsize=(9,8));im=ax.imshow(a,cmap='magma_r');ax.set_xticks(range(47),[s[:3] for s in names],rotation=90,fontsize=5);ax.set_yticks(range(47),[s[:3] for s in names],fontsize=5);fig.colorbar(im,ax=ax,label='Best prespecified relief RMS/mm');save(fig,9,'Geometry_forensic_similarity','Discrete reflections/offsets only. High similarity flags possible dependency; low similarity never proves independence.')
 fig,ax=plt.subplots(figsize=(11,4));ax.bar(['Coupon ID','Plate code','Nominal t','Scan file/hash','Batch ID','Session ID','Acquisition time'],[59,59,59,59,0,0,0]);ax.set(ylabel='Sources with documentary evidence',ylim=(0,63));save(fig,10,'Provenance_evidence_completeness','ZIP timestamps are packaging metadata; not assigned as acquisition dates.')
 cadids=[s for s in sids if (cases[s]/'01_frozen_protocol/geometry/solid_source.npz').exists()];meshids=[s for s in sids if (cases[s]/'SELECTED_MESHES.json').exists() and len(read(cases[s]/'SELECTED_MESHES.json'))==2]
 for n,title in [(11,'Unchanged_measured_front_surfaces'),(12,'Standardized_planar_rear'),(13,'Source_CAD_fidelity')]:
  if not cadids:textfig(n,title,'NOT_EXECUTED: no qualified CAD artifacts.','No synthetic numerical field plotted.');continue
  fig,axes=plt.subplots(len(cadids),1,figsize=(11,2.5*len(cadids)),squeeze=False)
  for i,s in enumerate(cadids):
   c=cases[s];x=np.load(c/'01_frozen_protocol/source/xyz.npy');t=np.load(c/'01_frozen_protocol/source/triangles.npy');ax=axes[i,0]
   if n==11:field(ax,x,t,x[:,2],s[:3]+' source front','Z/mm')
   elif n==12:
    f=np.load(c/'01_frozen_protocol/geometry/solid_source.npz');j=len(f['y'])//2;ax.plot(f['x'],f['front'][:,j],label='Measured front representation');ax.plot(f['x'],f['back'][:,j],label='Assumed rear');ax.set(title=s[:3]+' Ymid section',xlabel='X/mm',ylabel='Z/mm');ax.legend()
   else:
    f=np.load(c/'05_CAD_fidelity'/(s+'.npz'));ax.hist(f['CAD_reverse_gap_mm'],bins=70);ax.axvline(.04,c='r',ls=':');ax.set(title=s[:3]+' reverse sameXY940800samples',xlabel='Gap/mm',ylabel='Count')
  save(fig,n,title,'Measured front preserved; planar rear is a computational assumption. Full forward/reverse numerical tables retained.')
 for n,title in [(14,'Actual_quadratic_M1_M2_meshes'),(15,'Achieved_near_weld_refinement'),(16,'Tet10_SICN'),(17,'Sampled_Jacobians')]:
  if not meshids:textfig(n,title,'NOT_EXECUTED: no qualified mesh pair.','No unexecuted mesh values invented.');continue
  fig,axes=plt.subplots(len(meshids),2 if n==14 else 1,figsize=(12,2.7*len(meshids)),squeeze=False)
  for i,s in enumerate(meshids):
   selectedmesh=read(cases[s]/'SELECTED_MESHES.json')
   if n==15:
    d=read(cases[s]/'10_mesh_hierarchy/PAIR_QUALIFICATION.json');axes[i,0].bar(['Median edge','P90 edge','Face density'],[d['median_edge_ratio'],d['P90_edge_ratio'],d['surface_density_ratio']]);axes[i,0].set(title=s[:3]+' M2/M1',ylabel='Ratio');continue
   for j,l in enumerate(['M1','M2']):
    f=Path(selectedmesh[l]['folder']);ax=axes[i,j if n==14 else 0]
    if n==14:
     m=np.load(f/'mesh.npz');p=np.load(f/'FULL_SOURCE_FIDELITY.npz');tri=m['tri6'][p['patch_labels']=='MEASURED_FRONT',:3];ax.triplot(m['xyz'][:,0],m['xyz'][:,1],tri,lw=.10,rasterized=True);ax.set(title=s[:3]+' '+l+' front corner display',aspect='equal',xlabel='X/mm',ylabel='Y/mm')
    else:
     g=np.load(f/'GLOBAL_QUALITY.npz');v=g['quality'] if n==16 else np.log10(g['min_Q1_J']);ax.hist(v,bins=100,histtype='step',label=l);ax.set(title=s[:3],xlabel='Minimum SICN' if n==16 else 'log10 minimum sampledJ/mm³');ax.legend()
  save(fig,n,title,'Actual retained quadratic mesh evidence.73-point sampled Jacobians do not constitute continuous global positivity proof.')
 repairs=rows(R/'ACTUAL_MOVED_NODES.csv');warn=rows(R/'NATIVE_SHAPE_WARNINGS.csv')
 if repairs:
  fig,axes=plt.subplots(1,2,figsize=(12,5))
  for k,s in enumerate(sorted({a['source_id'] for a in repairs})):
   rr=[a for a in repairs if a['source_id']==s];axes[0].scatter([float(a['old_X']) for a in rr],[float(a['old_Y']) for a in rr],color='C'+str(k),s=20,label=s[:3]);axes[1].scatter([s[:3]+a['level'] for a in rr],[float(a['displacement_mm']) for a in rr],color='C'+str(k),s=14)
  axes[0].set(xlabel='X/mm',ylabel='Y/mm',title='Actually moved interior midsides');axes[0].legend();axes[1].set(ylabel='Actual displacement/mm',title='Measured/external boundaries unchanged');save(fig,18,'Local_mesh_repair_evidence','Actual changed nodes only. Full old/new XYZ and candidate IDs in LOCAL_NODE_DISPLACEMENTS.csv; no physical surface edits.')
 else:textfig(18,'Local_mesh_repair_evidence','No actual local node movement. Full candidate counts retained.','No repair event invented.')
 if warn:
  fig,axes=plt.subplots(1,2,figsize=(12,5));im=axes[0].scatter([float(a['X']) for a in warn],[float(a['Y']) for a in warn],c=[float(a['Z']) for a in warn],s=25);fig.colorbar(im,ax=axes[0],label='Element corner-centroidZ/mm');axes[0].set(xlabel='X/mm',ylabel='Y/mm',title='Native warned-element locations');axes[1].scatter([a['source_id'][:3]+a['level'] for a in warn],[float(a['minSICN']) for a in warn]);axes[1].axhline(.02,c='r',ls=':');axes[1].set(ylabel='Independent element minimumSICN');save(fig,19,'Native_shape_warning_evidence','Actual element IDs/locations and expanded quality retained; warnings accepted under frozen policy, never suppressed.')
 else:textfig(19,'Native_shape_warning_evidence','No native warned-element locations.','No warning event invented.')
 eq=rows(R/'NATIVE_EQUILIBRIUM.csv');bv=rows(R/'STANDARDIZED_BVP_AUDIT.csv')
 portids=[s for s in sids if (cases[s]/'02_mesh_import/M2/BVP_ASSEMBLY.json').exists()]
 if portids:
  fig,axes=plt.subplots(len(portids),2,figsize=(12,3*len(portids)),squeeze=False)
  for i,s in enumerate(portids):
   c=cases[s];b=read(c/'02_mesh_import/M2/BVP_ASSEMBLY.json');m=np.load(Path(read(c/'SELECTED_MESHES.json')['M2']['folder'])/'mesh.npz');rr=rows(c/'02_mesh_import/M2/PORT_FACE_REGISTRY.csv');x=m['xyz'];origin=np.array(b['loadline_origin'])
   for j,p in enumerate(b['ports']):
    face=np.array([int(a['face_index']) for a in rr if a['patch']==p['patch']]);t=m['tri6'][face,:3];v=abs(np.c_[np.ones(len(x)),x[:,1]-origin[1],x[:,2]-origin[2]]@np.array(p['coefficients']));tri=mtri.Triangulation(x[:,1],x[:,2],t);im=axes[i,j].tripcolor(tri,v,shading='gouraud',rasterized=True);fig.colorbar(im,ax=axes[i,j],label='|X traction|/MPa');axes[i,j].set(title=s[:3]+' '+p['patch']+f" area={p['area_mm2']:.3f}mm²",xlabel='Y/mm',ylabel='Z/mm',aspect='equal')
  save(fig,20,'Standardized_load_ports','Actual quadratic native ports,53200N/port. Display uses corner projection of actual affine traction coefficients; integration uses full quadratic geometry. No loaded-face clamp.')
 else:textfig(20,'Standardized_load_ports','NOT_EXECUTED: no native BVP ports.','No load field invented.')
 if eq:
  fig,ax=plt.subplots(figsize=(12,4));labels=[a['source_id'][:3]+a['level'] for a in eq];ax.semilogy(labels,[max(float(a['force_residual_relative']),1e-16) for a in eq],'o-',label='Force/F');ax.semilogy(labels,[max(float(a['moment_residual_over_Ft']),1e-16) for a in eq],'s-',label='Moment/Ft');ax.axhline(1e-5,c='r',ls=':');ax.legend();save(fig,21,'Native_equilibrium','Actual completed solutions only; normalized signed global reaction audit.')
 else:textfig(21,'Native_equilibrium','NOT_EXECUTED: no completed native solution.','No equilibrium result invented.')
 for n,title,key in [(22,'Original_source_M1_T2','M1'),(23,'Original_source_M2_T2','M2'),(24,'Original_source_T2_difference','difference'),(26,'High95_overlap','high95')]:
  if not qualified:textfig(n,title,'NOT_EXECUTED: no qualified stress targets.','No stress field invented.');continue
  fig,axes=plt.subplots(len(qualified),1,figsize=(11,2.7*len(qualified)),squeeze=False)
  for i,s in enumerate(qualified):
   d=fields[s];mask=d['common'];v=d[key] if key in ['M1','M2'] else d['M2']-d['M1'] if key=='difference' else d['high_M1'].astype(float)+2*d['high_M2'];limits=None
   if key=='difference':m=max(float(abs(v[mask]).max()),1e-6);limits=(-m,m)
   elif key in ['M1','M2']:limits=(min(float(d['M1'][mask].min()),float(d['M2'][mask].min())),max(float(d['M1'][mask].max()),float(d['M2'][mask].max())))
   field(axes[i,0],d['xyz'],tris[s],np.where(mask,v,np.nan),s[:3],label='membership0/1/2/3' if key=='high95' else 'MPa',cmap='coolwarm' if key=='difference' else 'viridis',limits=limits)
  save(fig,n,title,'Original source IDs/coordinates/T0 areas; actual per-source halo/core masks are audited separately from full68457-point geometry. C16 queriedhalo39151; do not assume39200.1mm3D chord principal-before-average target.')
 for n,title in [(25,'Maximum_regularized_T2'),(27,'Regional_L2'),(28,'T2_core_coverage')]:
  if not met:textfig(n,title,'NOT_EXECUTED: no qualified numerical metrics.','No numerical values invented.');continue
  fig,ax=plt.subplots(figsize=(10,4));names=[a['source_id'][:3] for a in met]
  if n==25:ax.bar(names,[float(a['M2_max_T2_MPa']) for a in met]);ax.set_ylabel('M2 maximum T2/MPa')
  elif n==27:
   for i,a in enumerate(met):ax.bar(i-.15,float(a['whole_L2']),.3,color='tab:blue');ax.bar(i+.15,float(a['worst_regional_L2']),.3,color='tab:orange')
   ax.set_xticks(range(len(names)),names);ax.axhline(.02,ls=':',c='blue');ax.axhline(.03,ls=':',c='orange');ax.set_ylabel('Whole blue / worst region orange L2')
  else:ax.bar(names,[float(a['M2_mapping_coverage']) for a in met]);ax.axhline(.99,c='r',ls=':');ax.set(ylim=(0,1.05),ylabel='Mapped halo area fraction')
  save(fig,n,title,'Two-mesh numerical consistency, not asymptotic convergence or validated local physical notch stress.')
 fig,ax=plt.subplots(figsize=(9,4));ax.bar(['Previous8','New qualified','Cumulative'],[8,len(qualified),8+len(qualified)]);ax.set_ylabel('Qualified source identities');save(fig,29,'Qualified_cohort_progression','M1/M2 and crops of a source count once; identities do not imply independent plates.')
 for n,title,key in [(30,'Actual_cost_per_source','wall_components_s'),(31,'Actual_retained_storage','archive_GiB')]:
  fig,ax=plt.subplots(figsize=(10,4));ax.bar([a['source_id'][:3] for a in cost],[float(a[key]) for a in cost]);ax.set_ylabel('Controller wall seconds' if n==30 else 'Case archive/GiB');save(fig,n,title,'Includes actual failed candidates and I/O. Sampled resource maxima are not continuous peaks.')
 textfig(32,'Physical_dependency_uncertainty','Five documentary plate groups; shared manufacturing batch unknown.\nPer-source acquisition timestamps/session IDs unavailable.\nSame scan-file mappings are confirmed; shared grid alone is not a repeated-scan finding.\nHistorical exposed tests share all five development plate groups.','Distinct plate codes do not establish external or cross-batch independence.')
 textfig(33,'Future_grouped_split_feasibility','Future from-scratch plate-held-out design: five documentary plate groups.\nAll crops, M1/M2 and confirmed same-plate coupons remain in one fold.\nHistorical exposed12 tests remain quarantined.\nPlate grouping is documentary; manufacturing-batch independence is unresolved.\nNo folds trained/evaluated in R8-E12.','A proposed partition design is not independent generalization validation.')
 fore=rows(R/'REMAINING_COHORT_FORECAST.csv');fig,ax=plt.subplots(figsize=(11,4))
 if fore:ax.bar([a['scenario'] for a in fore],[float(a['additional_archive_GiB']) for a in fore]);ax.axhline(shutil.disk_usage(R).free/GiB-20,c='r',ls=':',label='Current space after reserve');ax.legend()
 ax.set_ylabel('Additional retained archives/GiB');save(fig,34,'Remaining_cohort_storage_forecast','Forecast is cohort-conditional engineering estimate; further production unauthorized.')
 textfig(35,'Numerical_production_decision',f"{final['campaign_status']}\nNew SOLVE invocations: {final['actual_native_SOLVE_invocations']}/10\nSuccessful native solutions: {final['successful_native_solutions']}\nQualified new targets: {final['new_qualified_targets']}/5\nCumulative qualified sources: {final['cumulative_qualified_targets']}\nCampaign stop: {final['campaign_stop']}",'Actual numerical outcome; no substitution or stress-informed source replacement.')
 textfig(36,'Scientific_readiness_decision','Documentary plate-grouped future experiment design is possible.\nPhysical independence across manufacturing batches remains unestablished.\nNo untouched external physically independent cohort established.\nNo AI training or inference; no physical stress/fatigue validation.\nOverall R8E12_PARTIAL if physical uncertainties remain.','Numerical target qualification and physical independence reported separately.')
 ledger.sort(key=lambda a:a['number']);assert [a['number'] for a in ledger]==list(range(1,37));table(R/'SCIENTIFIC_FIGURES.csv',ledger)
if __name__=='__main__':main()
