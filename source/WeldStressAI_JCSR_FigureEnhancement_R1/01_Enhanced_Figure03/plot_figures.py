from common import *
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,FancyArrowPatch
from matplotlib.colors import Normalize,TwoSlopeNorm
from matplotlib.lines import Line2D
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.titlesize':8.5,'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,'axes.linewidth':.55,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','savefig.facecolor':'white'})
WIDTH=190/25.4
def save(fig,folder,stem):
 for ext in ['png','pdf','svg']:fig.savefig(D/folder/(stem+'.'+ext),dpi=600,facecolor='white')
 # Print-width verification previews, not additional scientific results.
 fig.savefig(D/'06_Scientific_QA'/(stem+'_190mm_preview.png'),dpi=180,facecolor='white')
 fig.savefig(D/'06_Scientific_QA'/(stem+'_140mm_preview.png'),dpi=180*140/190,facecolor='white')
 plt.close(fig)
sel=json.loads((D/'01_Enhanced_Figure03/ILLUSTRATIVE_QUERY_SELECTION.json').read_text());windows=json.loads((D/'01_Enhanced_Figure03/EXACT_WINDOW_AND_NEIGHBOR_EVIDENCE.json').read_text());sid=sel['source_id'];sr=next(r for r in rows(P/'R2_1_SOURCE_REGISTRY.csv') if r['source_id']==sid);g=dict(np.load(sr['geometry_path']));x=g['xyz'];q=sel['original_row'];p=x[q];fc=rows(D/'01_Enhanced_Figure03/QUERY_FEATURE_VALUES.csv')
fig=plt.figure(figsize=(WIDTH,8.25));fig.text(.055,.976,'(a) Processed measured G07 surface and exact observation support',weight='bold',fontsize=9,va='top')
ax=fig.add_axes([.035,.748,.45,.205],projection='3d');surface=ax.plot_trisurf(x[:,0],x[:,1],x[:,2],triangles=g['triangles'],color='#a8bac8',linewidth=0,antialiased=False,rasterized=True,shade=True);ax.scatter(*p,c='black',marker='D',s=16,depthshade=False);ax.set_box_aspect(np.ptp(x,axis=0));ax.view_init(elev=27,azim=-65);ax.set(xlabel='X (mm)',ylabel='Y (mm)',zlabel='',xticks=[130,150,170],yticks=[20,40],zticks=[]);ax.tick_params(pad=0,labelsize=7);ax.xaxis.labelpad=3;ax.yaxis.labelpad=3;ax.zaxis.labelpad=2;ax.text2D(.02,.82,'Canonical Z normal to XY (mm)',transform=ax.transAxes,fontsize=7);fig.text(.045,.747,'True 3D aspect; measured Z span %.2f mm'%np.ptp(x[:,2]),fontsize=7.5)
ax2=fig.add_axes([.56,.766,.395,.18]);ax2.scatter(x[:,0],x[:,1],c='#d7dde1',s=.10,rasterized=True)
colors=['#222222','#a65f13','#793e8e'];styles=['-','--',':']
for w,c,ls in zip(windows,colors,styles):
 ax2.add_patch(Rectangle((w['actual_X_min'],w['actual_Y_min']),w['actual_X_max']-w['actual_X_min'],w['actual_Y_max']-w['actual_Y_min'],fill=False,edgecolor=c,ls=ls,lw=1.1))
nb=g['neighbors'][q];ax2.scatter(x[nb,0],x[nb,1],facecolors='none',edgecolors='#2676a8',s=10,lw=.5);ax2.scatter(*p[:2],c='black',marker='D',s=18,zorder=5);ax2.annotate('fixed q',p[:2],xytext=(p[0]-9,p[1]+8),arrowprops={'arrowstyle':'->','lw':.6},fontsize=7.5);ax2.annotate('tension +X',xy=(181,18),xytext=(155,18),arrowprops={'arrowstyle':'->','lw':.8},fontsize=7.5);ax2.set(xlabel='Canonical X (mm)',ylabel='Y (mm)',aspect='equal',xlim=(124,186),ylim=(15,45),xticks=[130,150,170,185],yticks=[20,30,40]);ax2.legend([Line2D([0],[0],color=c,ls=ls,lw=1.1) for c,ls in zip(colors,styles)],['FULL','X50','X43'],loc='upper left',ncol=3,fontsize=7,frameon=False,handlelength=1.7,columnspacing=.7)
ni=fig.add_axes([.405,.868,.10,.066]);ni.scatter(x[nb,0],x[nb,1],s=5,c='#2676a8');ni.scatter(p[0],p[1],c='black',marker='D',s=10);ni.set_title('16 neighbors',fontsize=6.5,pad=2);ni.set_aspect('auto');ni.set_ylim(p[1]-.05,p[1]+.05);ni.set_xticks([]);ni.set_yticks([]);ni.set_axis_off()
fig.text(.055,.708,f"Illustrative original ID {sel['source_point_id']}; q = ({p[0]:.3f}, {p[1]:.3f}, {p[2]:.3f}) mm; tile {sel['tile']}",fontsize=8)
fig.text(.055,.683,'(b) Same measured point, different numerical representations',weight='bold',fontsize=9)
ta=fig.add_axes([.05,.439,.90,.226]);ta.set_axis_off()
formulas=[['Channels','Historical N1 / N2','Visible-local N3'],['0–2  position','(x − visible centroid) / 60','(x − registered tile anchor) / 60'],['3–5  normal','visible normal','visible normal, oriented +Z'],['6–8  spans','visible-domain XYZ spans / 60','visible 16-neighbor XYZ spans / 60'],['9–12  load / tag','[1, 0, 0]; front tag 0','[1, 0, 0]; front tag 0'],['13–15  local','relief; normal variation; log(1 + area)','visible relief; normal variation; log(1 + area)'],['16–17  normal spread','visible-global normal X/Y std','visible 16-neighbor normal X/Y std'],['18  Z descriptor','visible-global Z span / 60','visible 16-neighbor Z std / 60']]
tt=ta.table(cellText=formulas,cellLoc='left',colWidths=[.20,.37,.43],bbox=[0,0,1,1]);tt.auto_set_font_size(False);tt.set_fontsize(7.2)
for (i,j),cell in tt.get_celld().items():cell.set_edgecolor('#d8dde1');cell.set_linewidth(.4);cell.set_facecolor('#eaf0f3' if i==0 else 'white');cell.PAD=.08;cell.set_text_props(weight='bold' if i==0 else 'normal')
ma=fig.add_axes([.235,.332,.705,.086]);ma.set(xlim=(-.5,18.5),ylim=(3.5,-.5));labels=['N1/N2 X50','N1/N2 X43','N3 X50','N3 X43'];matrix=[]
for model,cond in [('historical','X50'),('historical','X43'),('N3','X50'),('N3','X43')]:
 rr=sorted([r for r in fc if r['condition']==cond],key=lambda r:int(r['channel']));vv=[r[model+'_changed_vs_FULL']=='True' for r in rr];matrix.append(vv)
for i,row in enumerate(matrix):
 for j,diff in enumerate(row):ma.text(j,i,'×' if diff else '·',ha='center',va='center',color='#a65f13' if diff else '#5d6770',fontsize=10 if diff else 9)
ma.set(xticks=range(19),xticklabels=list(range(19)),yticks=range(4),yticklabels=labels);ma.tick_params(length=0,labelsize=7);ma.xaxis.tick_top();ma.set_xlabel('')
for spine in ma.spines.values():spine.set_visible(False)
fig.text(.055,.315,'× differs from FULL; · identical at this point (exact stored-feature comparison).',fontsize=7.5)
fig.text(.055,.297,'All 19 N3 channels are identical here; the visible contextual support still changes.',fontsize=7.5)
fig.text(.055,.270,'(c) Executed compact SurfacePT: local and contextual branches',weight='bold',fontsize=9)
ca=fig.add_axes([.045,.074,.91,.18]);ca.set_axis_off()
def box(x0,y0,w,h,label):ca.add_patch(Rectangle((x0,y0),w,h,facecolor='#f5f7f8',edgecolor='#536878',lw=.65));ca.text(x0+w/2,y0+h/2,label,ha='center',va='center',fontsize=7.4)
def arrow(a,b):ca.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','lw':.7,'color':'#333333'})
box(.0,.37,.15,.32,'19 input\nchannels');box(.19,.37,.15,.32,'Shared\nencoder\nwidth 24');box(.39,.60,.27,.36,'Local attention\n3 × 16 neighbors\nLearned scale weights');box(.39,.04,.27,.34,'4096 visible points\nMean encoded context');box(.72,.34,.16,.39,'Fusion\nPer-query\nLayerNorm');box(.92,.34,.08,.39,'Scalar\nT2')
arrow((.15,.53),(.19,.53));arrow((.34,.57),(.39,.77));arrow((.34,.48),(.39,.20));arrow((.66,.77),(.72,.59));arrow((.66,.20),(.72,.46));arrow((.88,.53),(.92,.53));ca.text(.0,-.10,'7228 parameters; one multiscale block; no query-to-query attention or pooling.',fontsize=7.5)
fig.text(.055,.035,'(d) Unchanged measured q + changed support / encoding → prediction can change',fontsize=8,weight='bold');fig.text(.055,.015,'This is a computational representation effect, not a change in physical stress.',fontsize=7.5)
save(fig,'01_Enhanced_Figure03','Fig03_Geometry_Representation_Observation_Context')

# Rendering uses unchanged original triangle connectivity and vertex values.
# Gouraud display interpolation within those triangles is not field resampling.
fig=plt.figure(figsize=(WIDTH,7.6));plotdata=[];scales=[];panel=0;connectivity=[]
for row,sid in enumerate(['G07','X23']):
 a=dict(np.load(D/'02_New_Figure07'/(sid+'_EXACT_PLOT_ARRAYS.npz')));xyz=a['xyz'];vals=[a['T2_MPa'],a['N2'],a['N3']];lo=float(min(v.min() for v in vals));hi=float(max(v.max() for v in vals));err=float(max(abs(a['N2_error']).max(),abs(a['N3_error']).max()));norm=Normalize(lo,hi);enorm=TwoSlopeNorm(vmin=-err,vcenter=0,vmax=err)
 sr=next(r for r in rows(P/'R2_1_SOURCE_REGISTRY.csv') if r['source_id'].startswith(sid));geom=dict(np.load(sr['geometry_path']));lookup={int(k):i for i,k in enumerate(a['source_ids'])};mapping=np.array([lookup.get(int(k),-1) for k in geom['source_ids']]);tri=mapping[geom['triangles']];tri=tri[(tri>=0).all(axis=1)]
 assert np.array_equal(geom['xyz'][mapping>=0],xyz[mapping[mapping>=0]])
 np.save(D/'02_New_Figure07'/(sid+'_ORIGINAL_CORE_TRIANGLES.npy'),tri)
 connectivity.append({'source_id':sid,'original_geometry_SHA256':sha(sr['geometry_path']),'triangles':len(tri),'triangle_SHA256':arrsha(tri),'rule':'Unchanged original triangle connectivity restricted to three original core IDs; Gouraud vertex rendering only; no different mesh or field resampling.'})
 scales.append({'source_id':sid,'stress_min_MPa':lo,'stress_max_MPa':hi,'error_min_MPa':-err,'error_center_MPa':0,'error_max_MPa':err,'limits_rule':'Exact joint finite extrema of all three source stress fields, and joint maximum absolute signed error; no clipping','equal_XY_aspect':True})
 top=.963-row*.48;fig.text(.065,top,f'{sid}-V1-S355-AW  |  FULL  |  seed 20261021',fontsize=9,weight='bold')
 bottom1=top-.185;bottom2=top-.425
 def draw(ax,v,cmap,norm):
  artist=ax.tripcolor(xyz[:,0],xyz[:,1],tri,v,shading='gouraud',cmap=cmap,norm=norm,rasterized=True)
  ax.set(aspect='equal',xlim=(xyz[:,0].min(),xyz[:,0].max()),ylim=(xyz[:,1].min(),xyz[:,1].max()),xticks=np.linspace(xyz[:,0].min()+3,xyz[:,0].max()-3,3).round(),yticks=[20,30,40]);ax.tick_params(length=2,pad=2)
  return artist
 for j,(v,title) in enumerate(zip(vals,['Frozen FE T2','Saved N2','Saved N3'])):
  ax=fig.add_axes([.065+j*.275,bottom1,.235,.145]);sc=draw(ax,v,'viridis',norm);ax.set_title('('+chr(97+panel)+') '+title,loc='left',pad=5);panel+=1
  if j==0:ax.set_ylabel('Y (mm)')
  else:ax.set_yticklabels([])
  plotdata.append({'source_id':sid,'panel':title,'values_array':v,'IDs_SHA256':arrsha(a['source_ids']),'values_SHA256':arrsha(v)})
 cb=fig.colorbar(sc,cax=fig.add_axes([.89,bottom1+.005,.012,.135]));cb.set_label('T2 (MPa)',fontsize=8,labelpad=4);cb.ax.tick_params(labelsize=7,length=2)
 for j,model in enumerate(['N2','N3']):
  v=a[model+'_error'];ax=fig.add_axes([.065+j*.415,bottom2,.37,.19]);sc=draw(ax,v,'coolwarm',enorm);ax.set_title('('+chr(97+panel)+') '+model+' − FE',loc='left',pad=5);panel+=1;ax.set_xlabel('Canonical X (mm)' if row==1 else '')
  if j==0:ax.set_ylabel('Y (mm)')
  else:ax.set_yticklabels([])
  plotdata.append({'source_id':sid,'panel':model+' signed error','values_array':v,'IDs_SHA256':arrsha(a['source_ids']),'values_SHA256':arrsha(v)})
 cb=fig.colorbar(sc,cax=fig.add_axes([.89,bottom2+.005,.012,.18]));cb.set_label('Error (MPa)',fontsize=8,labelpad=4);cb.ax.tick_params(labelsize=7,length=2)
save(fig,'02_New_Figure07','Fig07_FE_vs_N2_N3_Stress_Fields')
table('02_New_Figure07/ORIGINAL_CONNECTIVITY_RENDERING.csv',connectivity)

table('02_New_Figure07/EXACT_COLOR_SCALES.csv',scales)
table('02_New_Figure07/PLOTTED_ARRAY_HASHES.csv',[{k:v for k,v in r.items() if k!='values_array'} for r in plotdata])
js('06_Scientific_QA/PLOT_EXECUTION.json',{'script_SHA256':sha(__file__),'figure03_source_point_ID':sel['source_point_id'],'selected_point_changed_channels_N1_N2_X50':[j for j,v in enumerate(matrix[0]) if v],'selected_point_changed_channels_N1_N2_X43':[j for j,v in enumerate(matrix[1]) if v],'selected_point_changed_channels_N3_X50':[j for j,v in enumerate(matrix[2]) if v],'selected_point_changed_channels_N3_X43':[j for j,v in enumerate(matrix[3]) if v],'Figure07_panels':len(plotdata),'field_resampling_to_different_mesh':False,'render_interpolation':'Gouraud on unchanged original canonical triangles; exact original vertex fields retained','field_clipping':False,'new_thresholds':False,'High95_in_main':'Not overlaid to avoid obscuring stress; unchanged historical High95 maps retained in SI.','PNG_export_DPI':600,'figure_width_mm':190,'SVG':'Vector labels and geometry overlays with rasterized scientific scatter/surface; original XYZ and values unchanged.','new_FE_training_inference_experiments':0})
print('PLOTS COMPLETE',flush=True)
