"""Scientific figures from actual completed artifacts only. No reference-label substitution."""
from setup_e11r1 import *
import os
os.environ['MPLCONFIGDIR']=str(R/'tmp')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
OUT=R/'23_figures';OUT.mkdir(exist_ok=True);ledger=[]
plt.rcParams.update({'font.size':9,'figure.dpi':110,'savefig.dpi':150,'axes.spines.top':False,'axes.spines.right':False})
def save(fig,name,caption,scope='ACTUAL_R8E11R1_NUMERICAL_EVIDENCE'):
 n=len(ledger)+1;stem=f'{n:02d}_'+name;fig.suptitle('R8-E11-R1 | '+name.replace('_',' '),fontsize=13);fig.tight_layout(rect=(0,0,1,.97));fig.savefig(OUT/(stem+'.png'));fig.savefig(OUT/(stem+'.pdf'));plt.close(fig);ledger.append(dict(number=n,title=name,PNG='23_figures/'+stem+'.png',PDF='23_figures/'+stem+'.pdf',caption=caption,scope=scope));print('FIGURE',n,name,flush=True)
def draw(ax,x,t,v,title,label='MPa',limits=None,cmap='viridis'):
 tr=mtri.Triangulation(x[:,0],x[:,1],t);tr.set_mask(~np.isfinite(v[t]).all(1));kw={} if limits is None else dict(vmin=limits[0],vmax=limits[1]);im=ax.tripcolor(tr,v,shading='gouraud',cmap=cmap,rasterized=True,**kw);ax.set(title=title,xlabel='GlobalX(mm)',ylabel='GlobalY(mm)');ax.set_aspect('equal');plt.colorbar(im,ax=ax,label=label,fraction=.035)
def main():
 final=read(R/'R8E11R1_FINAL_COUNTS.json');queue=rows(R/'FROZEN_SELECTED_FIVE_SOURCES.csv');sids=final['selected_sources'];cases={s:R/'cases'/s for s in sids};qualified=[a['source_id'] for a in rows(R/'NEW_QUALIFIED_V1_TARGET_REGISTRY.csv')];a=read(R/'RESOURCE_BUDGET_AMENDMENT.json');live=read(R/'LIVE_RESOURCE_MEASUREMENT.json')
 fig,ax=plt.subplots(figsize=(10,5));ax.axis('off');ax.text(.03,.96,'Frozen queue: '+' → '.join(s[:3] for s in sids)+'\n\nHistorical stop:16GiB cap <17.259678GiB forecast\nProspective amendment:24GiB; scientific protocol unchanged\nNew source targets qualified: '+str(len(qualified))+'/5\nActual native SOLVEs: '+str(final['actual_native_SOLVE_invocations'])+'/10\nCumulative qualified identities: '+str(final['cumulative_qualified_targets'])+'\n\n'+final['campaign_status'],va='top',fontsize=13);save(fig,'Amendment_and_actual_campaign','Historical resource stop retained; selection never rerun.','PROTOCOL_AND_ACTUAL_COUNTS')
 fig,axes=plt.subplots(1,2,figsize=(11,4));com=rows(R/'STORAGE_FORECAST_COMPONENTS.csv');bottom=0.
 for z in com:
  axes[0].bar(['Conservative peak'],[float(z['GiB'])],bottom=bottom,label=z['component']);bottom+=float(z['GiB'])
 axes[0].axhline(16,color='red',ls=':',label='Historical cap16GiB');axes[0].axhline(24,color='black',ls='--',label='Amended cap24GiB');axes[0].set_ylabel('GiB');axes[0].legend(fontsize=6,loc='upper left',bbox_to_anchor=(1.02,1));axes[1].bar(['Live free','After forecast','Reserve'],[live['E_free_GiB'],a['expected_remaining_free_disk_GiB'],20]);axes[1].set_ylabel('GiB');save(fig,'Resource_forecast_and_disk_reserve','Forecast is engineering allowance,not an observed peak.','RESOURCE_PREFLIGHT')
 cadids=[s for s in sids if (cases[s]/'01_frozen_protocol/geometry/solid_source.npz').exists()]
 if cadids:
  fig,axes=plt.subplots(len(cadids),2,figsize=(12,3.2*len(cadids)),squeeze=False)
  for row,s in enumerate(cadids):
   c=cases[s];src=np.load(c/'01_frozen_protocol/geometry/solid_source.npz');p=np.load(c/'01_frozen_protocol/source/xyz.npy');t=np.load(c/'01_frozen_protocol/source/triangles.npy');draw(axes[row,0],p,t,p[:,2],s[:3]+' unchanged measured front','Z(mm)');j=len(src['y'])//2;axes[row,1].plot(src['x'],src['front'][:,j],label='Measured-front CAD');axes[row,1].plot(src['x'],src['back'][:,j],label='Assumed planar rear');axes[row,1].set(xlabel='X(mm)',ylabel='Z(mm)',title='Ymid transverse section');axes[row,1].legend()
  save(fig,'Measured_front_and_assumed_rear','Actual original XYZ; rear andclosures are synthetic computational regions,not scans.')
  fig,axes=plt.subplots(len(cadids),2,figsize=(12,3*len(cadids)),squeeze=False)
  for row,s in enumerate(cadids):
   c=cases[s];arr=np.load(c/'05_CAD_fidelity'/(s+'.npz'));p=np.load(c/'01_frozen_protocol/source/xyz.npy');t=np.load(c/'01_frozen_protocol/source/triangles.npy');draw(axes[row,0],p,t,arr['source_forward_gap_mm'],s[:3]+' source→CAD gap','mm');axes[row,1].hist(arr['CAD_reverse_gap_mm'],bins=80);axes[row,1].axvline(.04,c='red',ls=':');axes[row,1].set(xlabel='Reverse same-XY gap(mm)',ylabel='Samples',title='Actual940800-point reverse audit')
  save(fig,'Full_source_CAD_fidelity','Source IDs/XYZ/triangles preserved. Reverse closest-T0 distance is separately recorded; acceptance uses frozen same-XY definition.')
 meshids=[s for s in sids if (cases[s]/'SELECTED_MESHES.json').exists() and len(read(cases[s]/'SELECTED_MESHES.json'))==2]
 if meshids:
  fig,axes=plt.subplots(len(meshids),2,figsize=(12,3*len(meshids)),squeeze=False)
  for i,s in enumerate(meshids):
   sel=read(cases[s]/'SELECTED_MESHES.json')
   for ax,l in zip(axes[i],['M1','M2']):
    f=Path(sel[l]['folder']);m=np.load(f/'mesh.npz');ff=np.load(f/'FULL_SOURCE_FIDELITY.npz');take=ff['patch_labels']=='MEASURED_FRONT';faces=m['tri6'][take,:3];ax.triplot(m['xyz'][:,0],m['xyz'][:,1],faces,lw=.12);ax.set(title=s[:3]+' '+l+' actual front mesh',xlabel='X(mm)',ylabel='Y(mm)');ax.set_aspect('equal')
  save(fig,'M1_M2_surface_meshes','Display uses corner-edge projection; actual quadratic geometry is independently audited at high-order samples.')
  fig,axes=plt.subplots(len(meshids),2,figsize=(12,3*len(meshids)),squeeze=False)
  for i,s in enumerate(meshids):
   sel=read(cases[s]/'SELECTED_MESHES.json')
   for l in ['M1','M2']:
    f=Path(sel[l]['folder']);g=np.load(f/'GLOBAL_QUALITY.npz');axes[i,0].hist(g['quality'],bins=100,histtype='step',label=l);axes[i,1].hist(np.log10(g['min_Q1_J']),bins=100,histtype='step',label=l)
   axes[i,0].axvline(.02,c='red',ls=':');axes[i,0].set(title=s[:3]+' independent whole-mesh SICN',xlabel='Minimum SICN per element');axes[i,0].legend();axes[i,1].set(title='73sample minimumJ',xlabel='log10(min sampledJacobian/mm³)');axes[i,1].legend()
  save(fig,'Quadratic_quality_and_Jacobians','Finite samples support numerical acceptance; no whole-element continuous positivity proof is inferred.')
  hh=[read(cases[s]/'10_mesh_hierarchy/PAIR_QUALIFICATION.json') for s in meshids if (cases[s]/'10_mesh_hierarchy/PAIR_QUALIFICATION.json').exists()]
  if hh:
   fig,axes=plt.subplots(1,2,figsize=(11,4));x=np.arange(len(hh));axes[0].bar(x-.17,[v['median_edge_ratio'] for v in hh],.34,label='Median');axes[0].bar(x+.17,[v['P90_edge_ratio'] for v in hh],.34,label='P90');axes[0].axhline(.98,c='red',ls=':');axes[0].set_xticks(x,[v['source_id'][:3] for v in hh]);axes[0].set_ylabel('Achieved M2/M1 edge ratio');axes[0].legend();axes[1].bar([v['source_id'][:3] for v in hh],[v['surface_density_ratio'] for v in hh]);axes[1].axhline(1,c='red',ls=':');axes[1].set_ylabel('M2/M1 surface density');save(fig,'Achieved_refinement','Actual geometry-based refinement,not just nominal settings.')
 if qualified:
  data={s:np.load(cases[s]/'13_numerical_qualification/COMPARISON_FIELDS.npz') for s in qualified};tri={s:np.load(cases[s]/'01_frozen_protocol/source/triangles.npy') for s in qualified}
  fig,axes=plt.subplots(len(qualified),3,figsize=(15,3.2*len(qualified)),squeeze=False)
  for i,s in enumerate(qualified):
   f=data[s];common=f['common'];lim=(0,max(f['M1'][common].max(),f['M2'][common].max()))
   for j,l in enumerate(['M1','M2']):v=np.where(common,f[l],np.nan);draw(axes[i,j],f['xyz'],tri[s],v,s[:3]+' '+l+' T2','MPa',lim)
   v=np.where(common,f['M2']-f['M1'],np.nan);d=max(abs(v[common]).max(),1e-6);draw(axes[i,2],f['xyz'],tri[s],v,'M2−M1 T2','MPa',(-d,d),'coolwarm')
  save(fig,'Original_source_T2_M1_M2_and_differences','Identical original IDs/XYZ/T0area/core; frozen1mm3Dchord principal-before-average target.')
  fig,axes=plt.subplots(len(qualified),2,figsize=(12,3.2*len(qualified)),squeeze=False)
  for i,s in enumerate(qualified):
   f=np.load(cases[s]/'10_source_mapping/M2/SOURCE_MAPPING.npz');v=np.where(f['valid'],f['sigma1_tensile'],np.nan);draw(axes[i,0],f['xyz'],tri[s],v,s[:3]+' mapped tensile principal stress');u=np.linalg.norm(f['FE_displacement'],axis=1);u[~f['valid']]=np.nan;draw(axes[i,1],f['xyz'],tri[s],u,'Mapped native displacement magnitude','mm')
  save(fig,'Actual_principal_stress_and_displacement','Actual native displacement-based isoparametric source recovery; not nearest-node labels and not AI.')
  fig,axes=plt.subplots(len(qualified),2,figsize=(12,3*len(qualified)),squeeze=False)
  for i,s in enumerate(qualified):
   f=data[s];common=f['common'];v=np.where(common,f['high_M1'].astype(float)+2*f['high_M2'].astype(float),np.nan);draw(axes[i,0],f['xyz'],tri[s],v,s[:3]+' high95 membership','0none/1M1/2M2/3both',(0,3),'viridis');v=np.where(common,f['region'].astype(float),np.nan);draw(axes[i,1],f['xyz'],tri[s],v,'Frozen geometry-only regions','regioncode')
  save(fig,'High95_overlap_and_fixed_regions','High95 thresholds use frozen interpolated area-weightedCDF. Proxy regions are not independently validated toe tracks.')
  fig=plt.figure(figsize=(12,3.8*len(qualified)));critical=[]
  for i,s in enumerate(qualified,1):
   f=data[s];valid=f['common'];ix=np.flatnonzero(valid);k=ix[np.argmax(f['M2'][valid])];p=f['xyz'][valid][::3];v=f['M2'][valid][::3];ax=fig.add_subplot(len(qualified),1,i,projection='3d');im=ax.scatter(*p.T,c=v,s=1,cmap='inferno');ax.scatter(*f['xyz'][k],c='cyan',s=35);ax.set(title=s[:3]+' M2 T2 on actual measured coordinates',xlabel='X(mm)',ylabel='Y(mm)',zlabel='Z(mm)');ax.set_box_aspect((60,28,7));fig.colorbar(im,ax=ax,label='MPa',shrink=.6);critical.append(dict(source_id=s,point_id=int(f['source_ids'][k]),X_mm=float(f['xyz'][k,0]),Y_mm=float(f['xyz'][k,1]),Z_mm=float(f['xyz'][k,2]),M2_T2_MPa=float(f['M2'][k]),K_T2=float(f['M2'][k]/100),interpretation='Regularizednumericalmaximum;notphysicalnotchstress'))
  save(fig,'Three_dimensional_T2_and_critical_regions','Display decimation only; critical point taken from full qualified source core.');table(R/'CRITICAL_T2_COORDINATES.csv',critical)
  met=rows(R/'T2_NUMERICAL_METRICS.csv');fig,axes=plt.subplots(1,3,figsize=(14,4));x=np.arange(len(met));names=[a['source_id'][:3] for a in met];axes[0].bar(x-.16,[float(a['whole_L2']) for a in met],.32,label='Whole');axes[0].bar(x+.16,[float(a['worst_regional_L2']) for a in met],.32,label='Worstregion');axes[0].axhline(.02,c='black',ls=':',label='Wholelimit');axes[0].axhline(.03,c='red',ls=':',label='Regionlimit');axes[0].set_xticks(x,names);axes[0].legend(fontsize=7);axes[1].bar(names,[float(a['high95_area_IoU']) for a in met]);axes[1].axhline(.8,c='red',ls=':');axes[1].set(title='High95 areaIoU',ylim=(0,1));axes[2].bar(names,[float(a['M2_max_T2_MPa']) for a in met]);axes[2].set(title='Maximum regularized M2T2',ylabel='MPa');save(fig,'Numerical_target_qualification','Whole<=.020,worstregion<=.030,IoU>=.800; this is two-mesh consistency,not physicalvalidation.')
  eq=rows(R/'NATIVE_EQUILIBRIUM.csv');fig,axes=plt.subplots(1,2,figsize=(13,4));labels=[a['source_id'][:3]+' '+a['level'] for a in eq];axes[0].semilogy(labels,[max(float(a['force_residual_relative']),1e-16) for a in eq],'o-',label='Force/F');axes[0].semilogy(labels,[max(float(a['moment_residual_over_Ft']),1e-16) for a in eq],'s-',label='Moment/Ft');axes[0].axhline(1e-5,c='red',ls=':');axes[0].tick_params(axis='x',rotation=45);axes[0].legend();axes[1].bar(labels,[float(a['Umax_mm']) for a in eq]);axes[1].tick_params(axis='x',rotation=45);axes[1].set_ylabel('Umax(mm)');save(fig,'Native_equilibrium_and_displacement','Signed global reaction audit on actual nativecoordinates; peaknodal stress not used for convergence.')
  fig,axes=plt.subplots(len(qualified),1,figsize=(10,2.6*len(qualified)),squeeze=False)
  for i,s in enumerate(qualified):
   b=read(cases[s]/'02_mesh_import/M2/BVP_ASSEMBLY.json');lo=rows(cases[s]/'02_mesh_import/M2/NODAL_LOAD_ASSEMBLY.csv');ax=axes[i,0]
   for port in b['ports']:
    ax.axhline(port['traction_min_MPa'],ls=':',alpha=.4);ax.axhline(port['traction_max_MPa'],ls=':',alpha=.4)
   ax.bar([p['patch'] for p in b['ports']],[p['area_mm2'] for p in b['ports']]);ax.set(title=s[:3]+' actual quadratic load ports;F=53200N each',ylabel='Port area(mm²)')
  save(fig,'Standardized_load_ports','Actual port areas with integrated affine force/moment coefficients retained inBVPJSON;100MPa is nominal normalization.')
  repairids=[s for s in qualified if (cases[s]/'ACTUAL_MOVED_NODES.csv').exists() and rows(cases[s]/'ACTUAL_MOVED_NODES.csv')]
  if repairids:
   fig,ax=plt.subplots(figsize=(10,4))
   for s in repairids:
    d=rows(cases[s]/'ACTUAL_MOVED_NODES.csv');ax.scatter([s[:3]]*len(d),[float(v['displacement_mm']) for v in d],label=s[:3])
   ax.set(ylabel='Actual interior midside movement(mm)',xlabel='Source');save(fig,'Actual_local_repair_displacements','Only actually changed nodes; corners,connectivity and full external boundary were bitwise preserved.')
 cost=rows(R/'FINAL_STORAGE_ACCOUNTING.csv');fig,axes=plt.subplots(1,2,figsize=(12,4));axes[0].bar([a['source_id'][:3] for a in cost],[float(a['archive_GiB']) for a in cost]);axes[0].set_ylabel('Retained case archive(GiB)');bottom=np.zeros(len(cost))
 for key in ['CAD_s','meshes_and_hierarchy_s','native_imports_audits_s','native_SOLVE_stage_s','recovery_T2_package_s']:
  values=np.array([float(a[key]) for a in cost]);axes[1].bar([a['source_id'][:3] for a in cost],values,bottom=bottom,label=key);bottom+=values
 axes[1].set_ylabel('Controller stage walltime(s)');axes[1].legend(fontsize=6);save(fig,'Observed_storage_and_runtime','All failed candidates retained. Stage wall times include Pythonstartup and I/O; they are not pure solver compute.')
 timeline=rows(R/'04_resource_preflight/CONTROLLER_RESOURCE_SAMPLES.csv');t=np.array([(datetime.datetime.fromisoformat(a['UTC'])-datetime.datetime.fromisoformat(timeline[0]['UTC'])).total_seconds()/60 for a in timeline]);fig,axes=plt.subplots(2,2,figsize=(12,7));axes[0,0].plot(t,[int(a['workspace_bytes'])/GiB for a in timeline]);axes[0,0].axhline(24,c='red',ls=':');axes[0,0].set_ylabel('Workspace(GiB)');axes[0,1].plot(t,[int(a['E_free_bytes'])/GiB for a in timeline]);axes[0,1].axhline(20,c='red',ls=':');axes[0,1].set_ylabel('E: free(GiB)');axes[1,0].plot(t,[int(a['RAM_available_bytes'])/GiB for a in timeline],label='RAM');axes[1,0].plot(t,[int(a['commit_free_bytes'])/GiB for a in timeline],label='Commit');axes[1,0].axhline(3,c='red',ls=':');axes[1,0].set_ylabel('Available(GiB)');axes[1,0].legend();axes[1,1].plot(t,[int(a['observed_worker_RSS_bytes'])/GiB for a in timeline]);axes[1,1].set_ylabel('Observed workerRSS(GiB)')
 for ax in axes.flat:ax.set_xlabel('Campaign minutes')
 save(fig,'Actual_resource_telemetry','Nominal2s sampling plus directory-scan overhead; observed extrema,not guaranteed instantaneous peaks.')
 fig,ax=plt.subplots(figsize=(8,4));ax.bar(['Historical','Newqualified','Cumulative'],[3,len(qualified),3+len(qualified)]);ax.set_ylim(0,8.5);ax.set_ylabel('Qualified source identities');save(fig,'Cumulative_V1_cohort','Two meshes count as one source. Documentary identities do not prove independent physical coupons.')
 table(R/'SCIENTIFIC_FIGURES.csv',ledger);print('FIGURES_COMPLETE',len(ledger))
if __name__=='__main__':main()
