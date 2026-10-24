from common_r3 import *
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import textwrap
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'figure.dpi':110,'savefig.dpi':145})
OUT=GLOBAL/'19_figures';FIG=[];SIDS=['G08-V1-S355-AW','X10-V1-S355-AW']
def root(s):return GLOBAL/'cases'/s
def meshdir(s,l):return Path(read(root(s)/'SELECTED_MESHES.json')[l]['folder'])
def save(fig,n,name,caption):
 fig.suptitle('R8-E10-R3 | '+name,fontsize=13);fig.tight_layout(rect=(0,0,1,.94));stem=f'{n:02d}_'+name.replace(' ','_').replace('/','_');fig.savefig(OUT/(stem+'.png'));fig.savefig(OUT/(stem+'.pdf'));plt.close(fig);FIG.append(dict(number=n,title=name,PNG='19_figures/'+stem+'.png',PDF='19_figures/'+stem+'.pdf',caption=caption));print('FIGURE',n,name,flush=True)
def textfig(title,lines):
 fig,ax=plt.subplots(figsize=(11,5));ax.axis('off');ax.text(.02,.95,title+'\n\n'+'\n'.join(textwrap.fill(z,100) for z in lines),transform=ax.transAxes,va='top',fontsize=11);return fig
def draw(ax,xyz,tri,val,title,label='MPa',cmap='viridis',limits=None):
 t=mtri.Triangulation(xyz[:,0],xyz[:,1],tri);t.set_mask(np.any(~np.isfinite(val[tri]),axis=1));kw={} if limits is None else dict(vmin=limits[0],vmax=limits[1]);im=ax.tripcolor(t,val,shading='gouraud',cmap=cmap,**kw);ax.set(xlabel='Global X [mm]',ylabel='Global Y [mm]',title=title);ax.set_aspect('equal');plt.colorbar(im,ax=ax,label=label,fraction=.04);return im
def main():
 data={s:np.load(root(s)/'13_numerical_qualification/COMPARISON_FIELDS.npz') for s in SIDS};tri={s:np.load(root(s)/'01_frozen_protocol/source/triangles.npy') for s in SIDS};src={s:np.load(root(s)/'01_frozen_protocol/geometry/solid_source.npz') for s in SIDS};datum={s:read(root(s)/'01_frozen_protocol/PARENT_DATUM.json') for s in SIDS};metrics={s:read(root(s)/'13_numerical_qualification/COMPLETE_METRICS.json') for s in SIDS};short=lambda s:s.split('-')[0]
 for n,s in [(1,SIDS[0]),(2,SIDS[1])]:
  f=data[s];fig=plt.figure(figsize=(10,5));ax=fig.add_subplot(projection='3d');x=f['xyz'][::3];cc=ax.scatter(*x.T,c=x[:,2],s=2,cmap='viridis');fig.colorbar(cc,ax=ax,label='Global Z [mm]',shrink=.6);ax.set(xlabel='X [mm]',ylabel='Y [mm]',zlabel='Z [mm]');ax.set_box_aspect([60,28,5]);save(fig,n,short(s)+' measured front','Original measured-front XYZ displayed unchanged; processed-source provenance and raw registration limits remain.')
 fig,axes=plt.subplots(1,2,figsize=(13,5))
 for ax,s in zip(axes,SIDS):
  x=data[s]['xyz'];d=datum[s];plane=d['intercept_Z_mm']+d['slope_X']*(x[:,0]-d['origin_X_mm'])+d['slope_Y']*(x[:,1]-d['origin_Y_mm']);draw(ax,x,tri[s],plane,short(s)+' robust front-parent plane','Datum Z [mm]')
 save(fig,3,'Parent plane fits','Outer10percentX strips, originalT0area weights, frozenHuber fit; no measured rear used.')
 fig,axes=plt.subplots(1,2,figsize=(12,4))
 for ax,s in zip(axes,SIDS):
  a=np.load(root(s)/'03_parent_datum'/(s+'.npz'));ax.hist(a['residual_mm'],bins=60,color='#267da3');ax.set(xlabel='Parent residual [mm]',ylabel='Source points',title=short(s))
 save(fig,4,'Parent fit residuals','Unweighted display histogram only; actual acceptance RMS and quantiles use originalT0weights.')
 fig,axes=plt.subplots(1,2,figsize=(12,4))
 for ax,s in zip(axes,SIDS):
  a=src[s];j=len(a['y'])//2;ax.plot(a['x'],a['front'][:,j],label='Unchanged measured-front CAD');ax.plot(a['x'],a['back'][:,j],label='Assumed planar rear');ax.set(xlabel='Global X [mm]',ylabel='Global Z [mm]',title=short(s)+' at Y mid');ax.legend(fontsize=8)
 save(fig,5,'Front and rear sections','Rear is a true19mm normal offset from the front-derived parent datum, not a measured rear.')
 fig=plt.figure(figsize=(13,5))
 for j,s in enumerate(SIDS,1):
  ax=fig.add_subplot(1,2,j,projection='3d');a=src[s];ii=np.arange(0,len(a['x']),15);jj=np.arange(0,len(a['y']),5);X,Y=np.meshgrid(a['x'][ii],a['y'][jj],indexing='ij');ax.plot_wireframe(X,Y,a['front'][np.ix_(ii,jj)],color='#267da3',lw=.3);ax.plot_wireframe(X,Y,a['back'][np.ix_(ii,jj)],color='#a8a8a8',lw=.3);ax.set(xlabel='X [mm]',ylabel='Y [mm]',zlabel='Z [mm]',title=short(s));ax.set_box_aspect([60,28,20])
 save(fig,6,'Standardized computational solids','Graph-wireframe display; each actual STEP independently exported, reimported and closed-solid qualified.')
 fig=plt.figure(figsize=(13,5))
 for j,s in enumerate(SIDS,1):
  ax=fig.add_subplot(1,2,j,projection='3d');m=np.load(meshdir(s,'M2')/'mesh.npz');lab=np.load(meshdir(s,'M2')/'FULL_SOURCE_FIDELITY.npz')['patch_labels']
  for patch in np.unique(lab):
   p=m['xyz'][m['tri6'][lab==patch,:3]].mean(1)[::12];ax.scatter(*p.T,s=1,label=str(patch))
  ax.set(xlabel='X',ylabel='Y',zlabel='Z',title=short(s));ax.set_box_aspect([60,28,20]);ax.legend(fontsize=6)
 save(fig,7,'Measured and assumed patches','Measured-front lineage, assumed rear, four synthetic closures are kept separate.')
 fig,axes=plt.subplots(1,2,figsize=(13,5))
 for ax,s in zip(axes,SIDS):
  a=np.load(root(s)/'05_CAD_fidelity'/(s+'.npz'));draw(ax,data[s]['xyz'],tri[s],a['source_forward_gap_mm'],short(s),'Forward gap [mm]')
 save(fig,8,'Source to CAD fidelity','All68457sourcepoints retained; reverse940800quadrature samples separately audited against canonicalT0triangles.')
 for n,s in [(9,SIDS[0]),(10,SIDS[1])]:
  fig,axes=plt.subplots(1,2,figsize=(13,5))
  for ax,l in zip(axes,['M1','M2']):
   m=np.load(meshdir(s,l)/'mesh.npz');lab=np.load(meshdir(s,l)/'FULL_SOURCE_FIDELITY.npz')['patch_labels'];co=m['xyz'];ft=m['tri6'][lab=='MEASURED_FRONT',:3];ax.triplot(co[:,0],co[:,1],ft,lw=.12,color='#244c76');ax.set(xlabel='X [mm]',ylabel='Y [mm]',title=l+' boundary corner display');ax.set_aspect('equal')
  save(fig,n,short(s)+' M1 M2 meshes','The native elements and surface mapping are quadratic. Corner wireframes are visualization only.')
 fig,ax=plt.subplots(figsize=(10,4));rows1=rows(GLOBAL/'SOURCE_FE_FIDELITY.csv');labels=[short(z['source_id'])+' '+z['level'] for z in rows1];ax.bar(labels,[float(z['near_weld_edge_median_mm']) for z in rows1],label='Median');ax.plot(labels,[float(z['near_weld_edge_P90_mm']) for z in rows1],'ro',label='P90');ax.set(ylabel='Actual near-weld edge [mm]');ax.legend();save(fig,11,'Achieved near weld refinement','Actual M2/M1median andP90 ratios, and curvedface densities, determine hierarchy rather than requestedsizes.')
 fig,axes=plt.subplots(2,2,figsize=(12,9))
 for row,s in enumerate(SIDS):
  for col,l in enumerate(['M1','M2']):a=np.load(meshdir(s,l)/'FULL_SOURCE_FIDELITY.npz');draw(axes[row,col],data[s]['xyz'],tri[s],a['source_forward_mm'],short(s)+' '+l,'Quadratic FE gap [mm]')
 save(fig,12,'Quadratic source fidelity','All-source inversequadraticprojection; no linearfacet substitution for the frozenfidelitymetric.')
 fig,axes=plt.subplots(1,2,figsize=(12,4))
 for ax,s in zip(axes,SIDS):
  for l in ['M1','M2']:
   z=np.load(meshdir(s,l)/'GLOBAL_QUALITY.npz')['quality'];ax.hist(z,bins=80,density=True,histtype='step',label=l)
  ax.axvline(.02,c='red',ls='--');ax.set(xlabel='minSICN',ylabel='Density',title=short(s));ax.legend()
 save(fig,13,'SICN distributions','Selectedmeshes only; rejectedX10M2_C1lowSICN0.0037136 is preserved separately.')
 fig,ax=plt.subplots(figsize=(10,4));names=[];vals=[]
 for s in SIDS:
  for l in ['M1','M2']:names.append(short(s)+' '+l);vals.append(np.load(meshdir(s,l)/'GLOBAL_QUALITY.npz')['min_Q1_J'].min())
 ax.bar(names,vals);ax.set(ylabel='Minimum sampled det J [mm3]',title='73 whole-mesh samples; expanded local checks separately recorded');save(fig,14,'Jacobian diagnostics','Positive finite sampling is not a global continuous-positivity proof. ExactBernstein certificates apply only to listed elements.')
 audit=read(root(SIDS[1])/'08_quadratic_quality/REPAIR_ROOT_CAUSE_AND_ACTUAL_CHANGE_AUDIT.json');fig=textfig('X10 M2 bounded interior recovery',[f"One element below SICN gate: 0.00371358; sampled Jacobians were positive.","S1 trial1: three eligible internal midsides; exactly ONE node changed.","Gmsh node144307 moved0.0026291034mm; corners, entire boundary and connectivity unchanged.","Selected M2_C2: minSICN0.0350; whole-mesh quality and source fidelity pass.","Expanded Q2:909 points over11potential-support elements;4elements actually affected.","Local counterfactual straightening is diagnostic only; no source/CAD modification."]);save(fig,15,'Local mesh recovery','BaselineM2_C1 and selectedM2_C2 retained, with completeactualnodechangeaudit and exactlocalBernsteincertificates.')
 save(textfig('Actual new native shape checks',["G08 M1/M2 and X10 M1/M2: zero fatal shape errors.","All four native imports: zero shape warning messages.","SHPP ON in PREP7; no warning suppression or threshold changes.","Gmsh parameter-metadata messages are recorded separately.","Historical C02 warning remains a historical result, not a new R3 warning."]),16,'Native shape warning audit','Nativewarningregistry is header-only because no newnativewarning occurred.')
 fig,axes=plt.subplots(1,2,figsize=(12,4))
 for ax,s in zip(axes,SIDS):
  c=root(s);bp=read(c/'02_mesh_import/M2/BVP_ASSEMBLY.json');m=np.load(meshdir(s,'M2')/'mesh.npz');lab=np.load(meshdir(s,'M2')/'FULL_SOURCE_FIDELITY.npz')['patch_labels'];origin=np.array(bp['loadline_origin'])
  for p in bp['ports']:
   ii=np.unique(m['tri6'][lab==p['patch']]);v=m['xyz'][ii];tr=abs(np.c_[np.ones(len(v)),v[:,1]-origin[1],v[:,2]-origin[2]]@p['coefficients']);ax.scatter(v[:,2],tr,s=3,label=p['patch'])
  ax.set(xlabel='Port Z [mm]',ylabel='Traction magnitude [MPa]',title=short(s));ax.legend(fontsize=7)
 save(fig,17,'Standardized applied traction','GlobalXaffine traction integrated onactualTri6ports; prescribedforce53200Nperside,not blanket100MPatraction.')
 save(textfig('Source-specific force lines',[short(s)+': '+str(read(root(s)/'02_mesh_import/M2/BVP_ASSEMBLY.json')['loadline_origin'])+' mm' for s in SIDS]+['Constant global X at both actual ports; same continuum BVP across M1/M2.','Six scalar corner gauges remove rank-six rigid motion; no full-face clamp.']),18,'Load ports and intended line','Force line derived from eachsourcefrontdatum and full computationaldesign, not copiedfromC02.')
 fig,axes=plt.subplots(1,2,figsize=(12,4));balance=rows(GLOBAL/'NATIVE_EQUILIBRIUM.csv');lab=[short(z['source_id'])+' '+z['level'] for z in balance];axes[0].bar(lab,[float(z['force_residual']) for z in balance]);axes[1].bar(lab,[float(z['moment_residual_Ft']) for z in balance]);axes[0].set(ylabel='Force residual / F');axes[1].set(ylabel='Moment residual / (F t)');save(fig,19,'Native force and moment balance','Signedappliedplusreactionvectors; F53200N,Ft1010800Nmm. Allresiduals≤1e-5.')
 for number,key,title,label in [(20,'FE_displacement','Native displacement results','|U| [mm]'),(21,'sigma1_tensile','Native tensile principal stress','Tensile sigma1 [MPa]')]:
  fig,axes=plt.subplots(1,2,figsize=(13,5))
  for ax,s in zip(axes,SIDS):
   a=np.load(root(s)/'10_source_mapping/M2/SOURCE_MAPPING.npz');v=a[key];v=np.linalg.norm(v,axis=1) if key=='FE_displacement' else v;draw(ax,data[s]['xyz'],tri[s],v,short(s)+' M2',label)
  save(fig,number,title,'Actualsolveddisplacementfield evaluated throughquadraticshape functions. Stress is directelementtensorrecovery,not storedANSYSlabelcopy.')
 fig,axes=plt.subplots(1,2,figsize=(13,5))
 for ax,s in zip(axes,SIDS):
  a=np.load(root(s)/'10_source_mapping/M2/SOURCE_MAPPING.npz');v=np.where(a['halo'],a['valid'].astype(float),np.nan);draw(ax,data[s]['xyz'],tri[s],v,short(s)+' mapping halo','Valid mapping fraction',limits=(0,1))
 save(fig,22,'Original source stress mapping','39200queriedpointspermesh; exteriorpointsretainedbutnotstressqueried. FrozenT2supportisaseparatecore.')
 allfine=[data[s]['M2'][data[s]['common']] for s in SIDS];limits=(min(v.min() for v in allfine),max(v.max() for v in allfine))
 for number,s in [(23,SIDS[0]),(24,SIDS[1])]:
  fig,axes=plt.subplots(1,2,figsize=(13,5))
  for ax,l in zip(axes,['M1','M2']):draw(ax,data[s]['xyz'],tri[s],data[s][l],short(s)+' '+l,'T2 [MPa]',limits=limits)
  save(fig,number,short(s)+' M1 M2 T2 maps','UnchangedoriginalT0areaweights,1mm3Dchord radius,principaltensileclippingbeforeaverage; sharedcolor scale.')
 fig,axes=plt.subplots(1,2,figsize=(13,5))
 for ax,s in zip(axes,SIDS):
  dd=data[s]['M2']-data[s]['M1'];lim=float(np.nanmax(abs(dd)));draw(ax,data[s]['xyz'],tri[s],dd,short(s)+' fine minus coarse','Delta T2 [MPa]','coolwarm',(-lim,lim))
 save(fig,25,'M1 M2 T2 difference maps','Difference is an observedtwo-mesh sensitivity contrast, not a rigorous FE error bound.')
 profile=[]
 for num,j,title,width in [(26,1,'Along weld T2 profiles',.5),(27,0,'Transverse T2 profiles',1.)]:
  fig,axes=plt.subplots(1,2,figsize=(12,4))
  for ax,s in zip(axes,SIDS):
   f=data[s];mask=f['common'];x=f['xyz'];lo=np.floor(x[mask,j].min()/width)*width;bb=np.arange(lo,x[mask,j].max()+width,width)
   for l in ['M1','M2']:
    lines=[]
    for a,b in zip(bb[:-1],bb[1:]):
     take=mask&(x[:,j]>=a)&(x[:,j]<b)
     if take.any():v=float(np.average(f[l][take],weights=f['area'][take]));lines.append(((a+b)/2,v));profile.append(dict(source_id=s,level=l,axis='Y' if j==1 else 'X',lo_mm=a,hi_mm=b,areaweighted_T2_MPa=v))
    ax.plot(*np.array(lines).T,label=l)
   ax.set(xlabel=('Y' if j==1 else 'X')+' [mm]',ylabel='Areaweighted bin T2 [MPa]',title=short(s));ax.legend()
  save(fig,num,title,'Binnedcommoncoremeans. No independentlyvalidated physicaltoetracks are inferred fromtheseprofiles.')
 table(GLOBAL/'17_numerical_qualification/SPATIAL_T2_PROFILES.csv',profile)
 fig,ax=plt.subplots(figsize=(11,4));rr=rows(GLOBAL/'T2_WHOLE_AND_REGIONAL_METRICS.csv');rr=[z for z in rr if z.get('region')];ax.bar([short(z['source_id'])+' '+z['region'] for z in rr],[float(z['normalized_L2']) for z in rr]);ax.axhline(.03,c='red',ls='--');ax.set(ylabel='Regional normalized L2');ax.tick_params(axis='x',rotation=20);save(fig,28,'Regional normalized L2','Geometryonly weld/parent/collar proxies fixed beforestresses; gate0.030.')
 fig,axes=plt.subplots(1,2,figsize=(13,5))
 for ax,s in zip(axes,SIDS):
  f=data[s];v=np.where(f['common'],f['high_M1'].astype(int)+2*f['high_M2'].astype(int),np.nan);draw(ax,f['xyz'],tri[s],v,short(s),'0 neither /1 M1 /2 M2 /3 both',limits=(0,3))
 save(fig,29,'High95 spatial agreement','InterpolatedweightedCDFqualificationthreshold; originalsourceareaIoU,not meshnodeintersection.')
 fig,axes=plt.subplots(1,2,figsize=(13,5))
 for ax,s in zip(axes,SIDS):
  g=np.load(root(s)/'01_protocol_freeze/TARGET_GEOMETRY_SUPPORT.npz');draw(ax,g['xyz'],tri[s],g['halo'].astype(int)+g['core'].astype(int),short(s),'0 exterior /1 halo /2 core',limits=(0,2))
 save(fig,30,'Frozen source support','SupportfixedbeforeSOLVEandcheckedafterward; sourcecoverage andT2neighborhoodsupport reportedseparately.')
 cf=np.load(HIST_R2/'13_numerical_qualification/COMPARISON_FIELDS.npz');all3=[('C02 historical',cf,np.load(HIST_R2/'01_protocol_freeze/R1_frozen/source/triangles.npy'))]+[(short(s)+' new',data[s],tri[s]) for s in SIDS];vals=[f['M2'][f['common']] for _,f,_ in all3];lim=(min(v.min() for v in vals),max(v.max() for v in vals));fig,axes=plt.subplots(3,1,figsize=(10,13))
 for ax,(name,f,t) in zip(axes,all3):draw(ax,f['xyz'],t,f['M2'],name,'M2 T2 [MPa]',limits=lim)
 save(fig,31,'Three source M2 T2 comparison','HistoricalC02fromunchangedR2reference. DifferentcanonicalXoriginsandreliefsarepreserved; no C02newsolve.')
 rows2=rows(GLOBAL/'M1_M2_MESH_COUNTS.csv');fig,ax=plt.subplots(figsize=(11,4));ax.bar([short(z['source_id'])+' '+z['level'] for z in rows2],[int(z['nodes']) for z in rows2]);ax.axhline(350000,c='red',ls='--');ax.set(ylabel='Selected native node count');save(fig,32,'Per source mesh counts','Onlyselectedlevelsplotted; one rejectedX10M2candidate is retained andcounted separately.')
 nr=rows(GLOBAL/'NATIVE_SOLVE_REGISTRY.csv');fig,axes=plt.subplots(1,2,figsize=(12,4));lab=[short(z['source_id'])+' '+z['level'] for z in nr];axes[0].bar(lab,[float(z['native_solve_log_elapsed_s']) for z in nr]);axes[0].set(ylabel='MAPDL logged wall time [s]');axes[1].bar(lab,[float(z['observed_RSS_bytes'])/1024**3 for z in nr],label='RSS');axes[1].bar(lab,[float(z['observed_private_bytes'])/1024**3 for z in nr],alpha=.3,label='Private');axes[1].set(ylabel='Observed native memory [GiB]');axes[1].legend();save(fig,33,'Runtime and memory','Two-second solver-process sampling; archive andknowncomponent timings inCSV. Separate CAD/fidelitysubtimes were not measured.')
 mat=rows(GLOBAL/'THREE_SOURCE_PILOT_MATRIX.csv');fig,ax=plt.subplots(figsize=(12,4));ax.axis('off');t=ax.table(cellText=[[short(z['source_id']),z['CAD'],z['meshes'],z['native_solutions'],z['T2']] for z in mat],colLabels=['Source','CAD','Mesh pair','Native','T2'],cellLoc='center',loc='center');t.auto_set_font_size(False);t.set_fontsize(9);t.scale(1,2);save(fig,34,'Final qualification matrix','HistoricalC02two solutionsplusfournewR3solutions;3of3conditionalnumericaltargetsqualified.')
 forecasts=rows(GLOBAL/'FULL42_RESOURCE_FORECAST.csv');fig,ax=plt.subplots(figsize=(11,4));ax.bar([z['scenario'] for z in forecasts],[float(z['required_free_for39_GiB']) for z in forecasts],label='39 additional archives +20GiB reserve');ax.axhline(float(forecasts[0]['current_free_GiB']),c='red',ls='--',label='Measured current free space');ax.set(ylabel='Required free disk [GiB]',title='Forecast scenarios; no full production authorized');ax.legend(fontsize=8);save(fig,35,'Updated production storage budget','Selectedpilotcostsarenot populationyieldestimates. Forty-twoscreenedidentitiesinclude3alreadyqualified;39remain.')
 save(textfig('Research decision',['Three of three V1 references qualified, with four new sequential SOLVEs in R3.','X10 M2 needed one bounded interior midside repair; all source surfaces preserved.','Conditional two-mesh numerical consistency; no asymptotic or physical validation.','Pilot sources are selected documentary groups, not certified independent coupons.','A larger V1 phase requires separate scope and adequate storage. No automatic production.','AI training, AI inference, external predictions and independent-generalization claims remain unauthorized.']),36,'Limitations and next stage','Successful FEpilotdoesnot establishgeneralizableAIorrobustnesstotheexternalAalborggeometry.')
 table(GLOBAL/'SCIENTIFIC_FIGURES.csv',FIG)
if __name__=='__main__':protect();main()
