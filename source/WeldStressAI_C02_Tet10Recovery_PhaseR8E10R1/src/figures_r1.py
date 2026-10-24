from common_r1 import *
from quality_r1 import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.interpolate import RectBivariateSpline
from PIL import Image,ImageDraw

def main():
 protect();plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'savefig.dpi':145,'axes.spines.top':False,'axes.spines.right':False});old=np.load(R/'00_integrity/baseline/mesh.npz');m1=np.load(R/'06_recovered_M1/M1_C1/mesh.npz');m2=np.load(R/'07_refined_M2/M2_C1/mesh.npz');q0=np.load(R/'08_quadratic_quality/ORIGINAL_GLOBAL_QUALITY.npz');q1=np.load(R/'06_recovered_M1/M1_C1/GLOBAL_QUALITY.npz');q2=np.load(R/'07_refined_M2/M2_C1/GLOBAL_QUALITY.npz');loc=np.load(R/'03_local_mesh_topology/LOCAL_SUPPORT.npz');a1=np.load(R/'06_recovered_M1/M1_C1/FULL_SOURCE_FIDELITY.npz');a2=np.load(R/'07_refined_M2/M2_C1/FULL_SOURCE_FIDELITY.npz');src=np.load(R/'01_frozen_protocol/geometry/solid_source.npz');patch=old['xyz'][old['tet10'][loc['bad_element_indices']]];ledger=[]
 titles=['Frozen standardized C02 solid','Original invalid M1 mesh','Two invalid Tet10 elements','Corners and midside positions','Quadratic Jacobian signs','Local original SICN','One ring topology','Two ring topology','Curved front edge geometry','Patch and interface proximity','Independent kinematic checks','Root cause evidence','Interior repair displacements','Original and repaired elements','Local SICN before and after','Local Jacobian before and after','Global SICN distributions','Full source fidelity','Recovered M1 mesh','Qualified M2 mesh','Achieved mesh refinement','Quadratic boundary comparison','Frozen source feature conformity','Mechanical port geometry','Final pre solver decision']
 def save(n,fig,source,description):
  fig.suptitle(f'{n:02d}. {titles[n-1]}',fontsize=15,fontweight='bold');fig.text(.02,.015,'C02 R8-E10-R1 | '+description+' | No native solve or AI run',fontsize=8,color='#48586d');fig.tight_layout(rect=[0,.06,1,.93]);stem=f'{n:02d}_'+titles[n-1].lower().replace(' ','_')
  for ext in ['png','pdf']:fig.savefig(R/'12_figures'/(stem+'.'+ext))
  ledger.append(dict(candidate_id='VISUAL_'+str(n),figure=n,title=titles[n-1],source=source,evidence=description,png='12_figures/'+stem+'.png',pdf='12_figures/'+stem+'.pdf'));plt.close(fig)
 def axes3d(title=None,fig=None,pos=111):
  if fig is None:fig=plt.figure(figsize=(10,6))
  ax=fig.add_subplot(pos,projection='3d');ax.set(xlabel='X (mm)',ylabel='Y (mm)',zlabel='Z (mm)');ax.view_init(26,-67)
  if title:ax.set_title(title,fontsize=10)
  return fig,ax
 def tetedges(ax,co,color='#6589a5',label=None,lw=1.):
  t=np.linspace(0,1,31)
  for k,(i,j) in enumerate(GM_EDGES):
   p=((1-t)*(1-2*t))[:,None]*co[i]+(t*(2*t-1))[:,None]*co[j]+(4*t*(1-t))[:,None]*co[4+k];ax.plot(p[:,0],p[:,1],p[:,2],c=color,lw=lw,label=label if k==0 else None)
 def fullmesh(n,m,a,label):
  fig,ax=axes3d(label);faces=m['xyz'][a['front_tri6'][:,:3]][::4];coll=Poly3DCollection(faces,facecolors='#cfdeea',edgecolors='#7d98ac',linewidths=.25);ax.add_collection3d(coll);p=m['xyz'][a['front_tri6'][:,:3]].reshape(-1,3);ax.set(xlim=(p[:,0].min(),p[:,0].max()),ylim=(p[:,1].min(),p[:,1].max()),zlim=(-.5,3));ax.set_box_aspect([60,28,8]);ax.view_init(60,-78);save(n,fig,'Actual mesh.npz / FULL_SOURCE_FIDELITY.npz','Corner facets for mesh display only; geometry checks use curved faces')
 #1 frozen solid, no CAD or mesh generation.
 fig,ax=axes3d();x=src['x'][::25];y=src['y'][::4];X,Y=np.meshgrid(x,y,indexing='ij');ax.plot_wireframe(X,Y,src['front'][::25,::4],lw=.4,color='#5286ab',label='Measured-derived front');ax.plot_wireframe(X,Y,src['back'][::25,::4],lw=.4,color='#ce994a',label='Assumed rear')
 for i,j in [(0,0),(0,-1),(-1,0),(-1,-1)]:ax.plot([X[i,j]]*2,[Y[i,j]]*2,[src['front'][::25,::4][i,j],src['back'][::25,::4][i,j]],c='#9b7185')
 ax.set_box_aspect([60,28,20]);ax.legend(fontsize=8);save(1,fig,'Frozen STEP and solid_source.npz','Authoritative STEP unchanged')
 oldaudit=np.load(R/'00_integrity/baseline/QUADRATIC_GEOMETRY_AUDIT.npz');fullmesh(2,old,oldaudit,'Original M1; two invalid volume elements; not solved')
 fig,ax=axes3d()
 for k,co in enumerate(patch):tetedges(ax,co,['#b65e4c','#b68c43'][k],f'Gmsh element {38861 if k==0 else 45699}',1.7)
 ax.legend(fontsize=8);save(3,fig,'Original Tet10 coordinates','Actual quadratic edges of both invalid elements')
 fig,ax=axes3d();co=patch[0];tetedges(ax,co,lw=1.1);ax.scatter(co[:4,0],co[:4,1],co[:4,2],c='#445e77',s=40,label='Corners');ax.scatter(co[4:,0],co[4:,1],co[4:,2],c='#bc684c',s=30,label='Midsides')
 for j,p in enumerate(co):ax.text(*p,str(j+1),fontsize=8)
 ax.legend(fontsize=8);save(4,fig,'INVALID_ELEMENT_NODE_COORDINATES.csv','Gmsh positions1-10; native permutation audited separately')
 fig=plt.figure(figsize=(12,5));L=samples_Q2();N=np.concatenate([L*(2*L-1),4*L[:,NATIVE_EDGES[:,0]]*L[:,NATIVE_EDGES[:,1]]],axis=1)
 for k,co in enumerate(patch):
  _,ax=axes3d('Original tag '+str([38861,45699][k]),fig,121+k);p=N@co[NATIVE_PERM];det=custom_quality(co[None],L)[0][0];sign=det<0;ax.scatter(p[~sign,0],p[~sign,1],p[~sign,2],s=2,alpha=.25,c='#7497b2',label='Positive sampled J');ax.scatter(p[sign,0],p[sign,1],p[sign,2],s=8,c='#bf5548',label='Negative sampled J');ax.legend(fontsize=7)
 save(5,fig,'Original element coordinates;909 Q2 samples','Finite-sample signs; not stress')
 rings=np.array(loc['ring2']);center=old['xyz'][old['tet10'][rings,:4]].mean(1);fig,ax=axes3d();p=ax.scatter(center[:,0],center[:,1],center[:,2],c=q0['quality'][rings],cmap='coolwarm_r',s=70,vmin=-.15,vmax=1);fig.colorbar(p,ax=ax,shrink=.65,label='Original minSICN');save(6,fig,'Original global quality; two-ring indices','Actual element-center quality')
 for n,key in [(7,'ring1'),(8,'ring2')]:
  fig,ax=axes3d()
  for e in loc[key]:
   co=old['xyz'][old['tet10'][e]];bad=e in loc['bad_element_indices'];tetedges(ax,co,'#b65645' if bad else '#a8b8c5',None,.9 if bad else .45)
  save(n,fig,'LOCAL_SUPPORT.npz',f'{len(loc[key])} face-ring elements; full moved-node support also checked')
 # Actual shared edge curve, linear chord and frozen CAD section.
 co=patch[0];k=1;i,j=GM_EDGES[k];t=np.linspace(0,1,101);linear=co[i]*(1-t[:,None])+co[j]*t[:,None];quad=((1-t)*(1-2*t))[:,None]*co[i]+(t*(2*t-1))[:,None]*co[j]+(4*t*(1-t))[:,None]*co[4+k];sp=RectBivariateSpline(src['x'][::2],src['y'],src['front'][::2],s=0);cad=sp.ev(linear[:,0],linear[:,1]);fig,ax=plt.subplots(figsize=(10,5));ax.plot(t,linear[:,2],label='Straight edge chord');ax.plot(t,quad[:,2],label='Actual quadratic boundary edge');ax.plot(t,cad,ls='--',label='Unchanged CAD at same XY');ax.scatter([.5],[co[4+k,2]],c='#bb5d49',label='Shared on-CAD midside');ax.set(xlabel='Edge parameter',ylabel='Z (mm)');ax.legend();save(9,fig,'Original shared edge15562; frozen front spline','No boundary node moved by S1')
 fig,ax=plt.subplots(figsize=(10,5));points=src['source_xyz'];ax.scatter(points[::25,0],points[::25,1],s=1,c='#ccd7e0');fc=patch[:,:4].mean(1);ax.scatter(fc[:,0],fc[:,1],s=50,c='#b95a49',label='Invalid element centers');ax.plot([119.975,119.975,179.975,179.975,119.975],[16,44,44,16,16],c='#6c8da6',label='Synthetic cap interfaces');ax.set(xlabel='X (mm)',ylabel='Y (mm)',aspect='equal');ax.legend(fontsize=8);save(10,fig,'Frozen design bounds and original failure coordinates','Failure is on front; rear and cap junctions distant')
 fig,ax=plt.subplots(figsize=(10,5));x=np.arange(2);p0=[-.01392271759721177,-.011836143654685802];p1=[.11120308802092843,.10501555767811889];ax.bar(x-.18,p0,width=.36,label='Actual quadratic minimum J');ax.bar(x+.18,p1,width=.36,label='Straight corner determinant');ax.set_xticks(x,['38861','45699']);ax.set(xlabel='Original Gmsh element tag',ylabel='Determinant (mm³)');ax.axhline(0,c='k',lw=.8);ax.legend();save(11,fig,'Independent scalar / vectorized derivatives','Corner validity does not imply quadratic validity')
 fig,ax=plt.subplots(figsize=(11,6));ax.axis('off');items=[('Ordering / shared nodes','Correct API edge map; zero shared-node conflicts'),('Corner inversion','Rejected: both positive; face angles about31.6 degrees'),('Boundary curvature','Shared on-CAD midside depressed0.078675 mm'),('Volume layout','Straight interior midsides did not accommodate curvature'),('Causal diagnostic','Only shared boundary midside straightened: both local maps positive'),('Admissible repair','Keep boundary fixed; optimize four shared interior midsides')]
 for j,(h,b) in enumerate(items):ax.text(.02,.94-j*.15,h+' — '+b,transform=ax.transAxes,fontsize=10,bbox=dict(boxstyle='round,pad=.45',fc='#edf3f9',ec='#7792aa'))
 save(12,fig,'Hypothesis matrix and single-midside diagnostics','Supported numerical mechanism; no measured-defect claim')
 changed=np.flatnonzero(np.any(old['xyz']!=m1['xyz'],axis=1));p=old['xyz'][changed];delta=m1['xyz'][changed]-p;fig=plt.figure(figsize=(12,5));ax=fig.add_subplot(121);ax.bar(['dX','dY','dZ'],delta[0],color=['#6587a2','#a88f4e','#b7634d']);ax.axhline(0,c='k',lw=.7);ax.set_ylabel('Coordinate change (mm)');ax.set_title('Only Gmsh node86669 moved;4 eligible variables',fontsize=10);ax=fig.add_subplot(122,projection='3d');ax.quiver(0,0,0,*delta[0],color='#447f9e',arrow_length_ratio=.15);ax.scatter(0,0,0,c='#b5654c',s=35,label='Original');ax.scatter(*delta[0],c='#447f9e',s=35,label='Repaired');ax.set(xlabel='dX (mm)',ylabel='dY (mm)',zlabel='dZ (mm)',xlim=(-.006,.001),ylim=(-.001,.002),zlim=(-.022,.002));ax.view_init(25,-68);ax.legend(fontsize=8);save(13,fig,'ACTUAL_COORDINATE_CHANGE_AUDIT.json','One actual interior-node displacement; actual mm scale')
 fig=plt.figure(figsize=(12,5))
 for j,(m,title) in enumerate([(old,'Original'),(m1,'Repaired M1')]):
  _,ax=axes3d(title,fig,121+j)
  for e in loc['bad_element_indices']:tetedges(ax,m['xyz'][m['tet10'][e]],'#b55c49' if j==0 else '#50829f',lw=1.6)
 save(14,fig,'Original and M1_C1 exact Tet10 coordinates','Same corners, shared connectivity and external boundary')
 affected=loc['affected_support_elements'];x=np.arange(len(affected))
 for n,key,ylabel in [(15,'quality','minSICN'),(16,'min_Q1_J','Minimum Q1 determinant (mm³)')]:
  fig,ax=plt.subplots(figsize=(11,5));ax.bar(x-.2,q0[key][affected],width=.4,label='Original');ax.bar(x+.2,q1[key][affected],width=.4,label='M1_C1');ax.axhline(.02 if n==15 else 0,c='#b15c4e',ls='--',label='Frozen acceptance lower limit');ax.set_xticks(x,affected,rotation=60,fontsize=8);ax.set(xlabel='Original mesh array element index',ylabel=ylabel);ax.legend(fontsize=8);save(n,fig,'All14 complete moved-node support elements','Neighbors included; no new invalidity elsewhere')
 fig,ax=plt.subplots(figsize=(10,5));bins=np.linspace(-.15,1,100)
 for z,name,col in [(q0,'Original invalid M1','#bb6751'),(q1,'Recovered M1','#527d9e'),(q2,'M2','#b49748')]:ax.hist(z['quality'],bins=bins,histtype='step',density=True,label=name,color=col,lw=1.4)
 ax.axvline(.02,c='#ae5143',ls='--');ax.set(xlabel='minSICN',ylabel='Element-fraction density',yscale='log');ax.legend();save(17,fig,'Whole-domain quality arrays','Independent formula agrees with Gmsh for all elements')
 fig,axs=plt.subplots(1,2,figsize=(12,5))
 for ax,key,title in [(axs[0],'source_forward_mm','Full-source forward gap'),(axs[1],'reverse_sameXY_mm','Curved-face reverse gap')]:
  for a,name,col in [(a1,'M1_C1','#547f9f'),(a2,'M2_C1','#c09448')]:
   v=np.sort(a[key]);ax.plot(v,np.arange(1,len(v)+1)/len(v),label=name,c=col)
  ax.axvline(.04,c='#bc5a4a',ls='--',label='Frozen max0.040 mm');ax.set(xlabel=title+' (mm)',ylabel='Empirical fraction');ax.legend(fontsize=8)
 save(18,fig,'Fresh complete source/curved-face fidelity arrays','Geometry only; no stress field')
 fullmesh(19,m1,a1,'Recovered M1; all pre-solver gates pass');fullmesh(20,m2,a2,'M2; one independently generated candidate')
 f1=read(R/'06_recovered_M1/M1_C1/SOURCE_FIDELITY.json');f2=read(R/'07_refined_M2/M2_C1/SOURCE_FIDELITY.json');fig,axs=plt.subplots(1,2,figsize=(11,5));x=np.arange(2);axs[0].bar(x-.17,[f1['near_weld_edge_median_mm'],f1['near_weld_edge_P90_mm']],width=.34,label='M1');axs[0].bar(x+.17,[f2['near_weld_edge_median_mm'],f2['near_weld_edge_P90_mm']],width=.34,label='M2');axs[0].set_xticks(x,['Median','P90']);axs[0].set_ylabel('Near-weld corner edge (mm)');axs[0].legend();axs[1].bar(['M1','M2'],[f1['front_face_density_per_mm2'],f2['front_face_density_per_mm2']],color=['#587e9c','#cb994e']);axs[1].set_ylabel('Curved front faces / mm²');save(21,fig,'M1_M2_REFINEMENT.csv','Achieved size ratios0.7505/0.7418; density ratio1.7649')
 data=rows(R/'10_mesh_hierarchy/QUADRATIC_BOUNDARY_COMPARISON.csv');fig,ax=plt.subplots(figsize=(11,5));labels=[v['patch'].replace('MEASURED_','').replace('ASSUMED_','') for v in data[:6]];x=np.arange(6);ax.bar(x-.17,[float(v['bounded_actual_quad_patch_distance_max_mm']) for v in data[:6]],width=.34,label='M2 -> M1');ax.bar(x+.17,[float(v['bounded_actual_quad_patch_distance_max_mm']) for v in data[6:]],width=.34,label='M1 -> M2');ax.set_xticks(x,labels,rotation=15);ax.set_ylabel('Actual bounded quadratic patch gap (mm)');ax.legend();save(22,fig,'Both directions; all six actual quadratic boundary patches','Local closest diagnostic; global chart max0.011574564 mm')
 feature=np.load(R/'03_local_mesh_topology/FROZEN_SOURCE_FEATURE_PROXY.npz')['feature_XYZ'];fig,ax=plt.subplots(figsize=(10,5));ax.scatter(points[::25,0],points[::25,1],s=1,c='#d5dfe7');ax.scatter(feature[::8,0],feature[::8,1],s=3,c='#6c9562',label='Frozen normal-height0.5 mm contour proxy');ax.scatter(fc[:,0],fc[:,1],s=35,c='#b65c4b',label='Original failure centers');ax.set(xlabel='Source X (mm)',ylabel='Source Y (mm)',aspect='equal');ax.legend(fontsize=8);save(23,fig,'Original T0 edges and source heights','Geometry-only feature proxy; not validated physical toe locations')
 pref=read(R/'11_mechanical_mesh_preflight/M1_C1.json');fig,ax=axes3d('Defined BVP only; no forces or constraints applied');x=src['x'][[0,-1]]
 for patchname in ['XMIN_CAP','XMAX_CAP']:
  faces=m1['xyz'][m1['tri6'][a1['patch_labels']==patchname]][:,:3];ax.add_collection3d(Poly3DCollection(faces,facecolors='#b9cedd',edgecolors='#8ba5ba',linewidths=.25,alpha=.5))
 ax.plot(x,[30,30],[-9.37643484024406]*2,c='#bd8d41',label='Intended common X loadline')
 for p in pref['pins']:co=p['xyz'];ax.scatter(*co,c='#b95b4c',s=25)
 ax.set(xlim=(119,181),ylim=(15,45),zlim=(-20,3));ax.set_box_aspect([60,28,20]);ax.legend(fontsize=8);save(24,fig,'Actual gauge coordinates / port corner-facet display; quadratic integration audited','19mm nominal /28mm full width; defined53200 N only')
 fig,ax=plt.subplots(figsize=(11,6));ax.axis('off');items=[('ROOT_CAUSE_VERIFIED','Correct corners/order; curvature-placement incompatibility'),('C02_M1_QUALIFIED','One S1 trial;1of4eligible nodes moved;boundary unchanged'),('C02_M2_QUALIFIED','One M2 candidate; meaningful refinement achieved'),('PAIR PRE-SOLVER QUALIFIED','Same CAD/source; geometry, topology and BVP mesh checks pass'),('NATIVE / T2 NOT EXECUTED','Native import, warnings, equilibrium and stress checks still required')]
 for j,(h,b) in enumerate(items):ax.text(.03,.93-j*.18,h+'\n'+b,transform=ax.transAxes,va='top',fontsize=10,bbox=dict(boxstyle='round,pad=.6',fc='#ecf3f9',ec='#6d91ac'))
 save(25,fig,'Final qualification receipts','Mesh qualification is not stress-target validation')
 assert len(ledger)==25;table(R/'SCIENTIFIC_FIGURES.csv',ledger);contact=Image.new('RGB',(1800,7*280),'#d9e0e6')
 for i,z in enumerate(ledger):
  im=Image.open(R/z['png']).convert('RGB');assert im.width>=1000 and im.height>=500;im.thumbnail((440,245));tile=Image.new('RGB',(450,280),'white');tile.paste(im,((450-im.width)//2,0));ImageDraw.Draw(tile).text((8,251),f"{z['figure']:02d} {z['title']}",fill='black');contact.paste(tile,((i%4)*450,(i//4)*280))
 contact.save(R/'12_figures/CONTACT_SHEET.png');write(R/'14_reproducibility/FIGURE_RECEIPT.json',dict(UTC=now(),source_id=SID,candidate_id='M1_C1__M2_C1',protocol_version=VERSION,PNG=25,PDF=25,native_figures=0,AI_figures=0,source='SCIENTIFIC_FIGURES.csv',actual_data_only=True));print('25_SCIENTIFIC_FIGURE_PAIRS_COMPLETE',flush=True)
if __name__=='__main__':main()
