from common_e10 import *
from protocol_core import front_parent_datum,plane_z,port_feasibility
from scipy.interpolate import RectBivariateSpline
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
sys.path.insert(0,str(R/'src/vendor'))
from shape5e import Q

def original_height(ref,points):
 x=ref['x'];y=ref['y'];z=ref['front'];i=np.clip(np.searchsorted(x,points[:,0],side='right')-1,0,len(x)-2);j=np.clip(np.searchsorted(y,points[:,1],side='right')-1,0,len(y)-2);u=(points[:,0]-x[i])/(x[i+1]-x[i]);v=(points[:,1]-y[j])/(y[j+1]-y[j]);A=z[i,j];B=z[i+1,j];C=z[i,j+1];D=z[i+1,j+1];return np.where(v<=u,A*(1-u)+B*(u-v)+D*v,A*(1-v)+C*(v-u)+D*u)

def closest_T0(ref,points):
 # All possible nearer original graph triangles lie within this stencil when distance<.04mm.
 # Omitted cells are >=2*dx or >=dy away in XY; recorded and checked below.
 x=ref['x'];y=ref['y'];z=ref['front'];answer=[]
 for st in range(0,len(points),2000):
  p=points[st:st+2000];ii=np.clip(np.searchsorted(x,p[:,0])-1,0,len(x)-2);jj=np.clip(np.searchsorted(y,p[:,1])-1,0,len(y)-2);cand=[]
  for di in [-2,-1,0,1,2]:
   for dj in [-1,0,1]:
    i=np.clip(ii+di,0,len(x)-2);j=np.clip(jj+dj,0,len(y)-2);a=np.c_[x[i],y[j],z[i,j]];b=np.c_[x[i+1],y[j],z[i+1,j]];c=np.c_[x[i],y[j+1],z[i,j+1]];d=np.c_[x[i+1],y[j+1],z[i+1,j+1]];cand.extend([np.stack([a,b,d],axis=1),np.stack([a,d,c],axis=1)])
  t=np.stack(cand,axis=1);a=t[:,:,0];ab=t[:,:,1]-a;ac=t[:,:,2]-a;ap=p[:,None]-a;nn=np.cross(ab,ac);n2=(nn*nn).sum(-1);distplane=(ap*nn).sum(-1);proj=ap-distplane[...,None]/n2[...,None]*nn;aa=(ab*ab).sum(-1);bb=(ab*ac).sum(-1);cc=(ac*ac).sum(-1);u=((proj*ab).sum(-1)*cc-(proj*ac).sum(-1)*bb)/(aa*cc-bb*bb);v=((proj*ac).sum(-1)*aa-(proj*ab).sum(-1)*bb)/(aa*cc-bb*bb);dd=np.where((u>=0)&(v>=0)&(u+v<=1),distplane**2/n2,np.inf)
  for k,l in [(0,1),(1,2),(2,0)]:
   a=t[:,:,k];edge=t[:,:,l]-a;ap=p[:,None]-a;s=np.clip((ap*edge).sum(-1)/(edge*edge).sum(-1),0,1);dd=np.minimum(dd,((ap-s[...,None]*edge)**2).sum(-1))
  answer.extend(np.sqrt(dd.min(1)))
 out=np.array(answer);assert out.max()<min(2*np.diff(x).min(),np.diff(y).min()),'Closest T0 search stencil cannot certify global closest triangle';return out

def run(sid):
 protect();resource_gate(1200*1024**2,1600*1024**2,600*1024**2);assert read(R/'00_integrity/INITIALIZATION_COMPLETE.json')['passed'];queue=rows(R/'R8E10_PILOT_QUEUE.csv');row=next(z for z in queue if z['source_id']==sid);phase=Path(row['original_phase']);g=E3/'02_geometry/single'/sid;out=R/'04_standardized_solids'/sid;out.mkdir(parents=True,exist_ok=True)
 assert not (R/'17_reproducibility/CAMPAIGN_STOP.json').exists();assert not (out/'CAD_QUALIFICATION.json').exists();started=time.perf_counter();xyz=np.load(g/'xyz.npy');tri=np.load(g/'triangles.npy');ids=np.load(g/'source_ids.npy');area=np.load(g/'area.npy');x=np.unique(xyz[:,0]);y=np.unique(xyz[:,1]);nx,ny=len(x),len(y);assert len(xyz)==nx*ny and np.array_equal(xyz.reshape(nx,ny,3)[:,0,0],x);bounds=[float(x[0]),float(x[-1]),float(y[0]),float(y[-1])]
 edge=np.sort(np.vstack([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1);edges,n=np.unique(edge,axis=0,return_counts=True);assert n.max()==2;assert len(xyz)-len(edges)+len(tri)==1;graph=coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(len(xyz),len(xyz)));assert connected_components(graph,directed=False,return_labels=False)==1
 # Explicitly verify the canonical cell diagonal and original winding; no bilinear reference.
 lower=[];upper=[]
 for i in range(nx-1):
  for j in range(ny-1):a=i*ny+j;b=(i+1)*ny+j;c=i*ny+j+1;d=(i+1)*ny+j+1;lower.append([a,b,d]);upper.append([a,d,c])
 assert np.array_equal(tri,np.array(lower+upper));cross=np.cross(xyz[tri[:,1]]-xyz[tri[:,0]],xyz[tri[:,2]]-xyz[tri[:,0]]);assert (cross[:,2]>0).all();assert len(np.unique(ids))==len(ids)
 for name in ['xyz.npy','triangles.npy','source_ids.npy','area.npy','normal.npy']:
  dest=R/'02_source_geometry'/sid/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(g/name,dest);assert sha(dest)==sha(g/name)
 source=np.load(phase/'05_closed_solids'/sid/'solid_source.npz');source_x32=x.copy();source_y32=y.copy();reference_front=xyz[:,2].reshape(nx,ny).copy();x=source['x'];y=source['y'];front=source['front'];assert np.array_equal(front.astype('f4'),reference_front.astype('f4'));bounds=[float(x[0]),float(x[-1]),float(y[0]),float(y[-1])]
 datum,parent=front_parent_datum(xyz,area,bounds);assert datum['screen_pass'],'PARENT_DATUM_FAIL';old=read(E9/'02_inventory/FRONT_DATUM_AND_BVP_DRYRUN.json')[sid]
 for key in ['intercept_Z_mm','slope_X','slope_Y','parent_RMS_mm','parent_P95_abs_mm']:assert abs(datum[key]-old[key])<1e-12
 assert float(row['nominal_thickness_mm'])==19;X,Y=np.meshgrid(x,y,indexing='ij');back=plane_z(np.c_[X.ravel(),Y.ravel(),np.zeros(X.size)],datum,19).reshape(nx,ny);norm=np.sqrt(1+datum['slope_X']**2+datum['slope_Y']**2);minimum=float(((front-back)/norm).min());assert minimum>0
 res=xyz[parent,2]-(datum['intercept_Z_mm']+datum['slope_X']*(xyz[parent,0]-datum['origin_X_mm'])+datum['slope_Y']*(xyz[parent,1]-datum['origin_Y_mm']));np.savez_compressed(R/'03_parent_datum'/(sid+'.npz'),source_ids=ids[parent],source_XYZ=xyz[parent],residual_mm=res,parent_mask=parent)
 datum.update(source_id=sid,nominal_thickness_mm=19,plane_normal=[-datum['slope_X']/norm,-datum['slope_Y']/norm,1/norm],rear_point=[datum['origin_X_mm'],datum['origin_Y_mm'],datum['intercept_Z_mm']-19*norm],signed_normal_plane_offset_mm=-19.,minimum_front_separation_mm=minimum,maximum_front_separation_mm=float(((front-back)/norm).max()),domain_bounds=bounds,physical_dependency_group=row['dependency_group'],physical_independence='UNCERTIFIED',fit_stability_weighted_design_condition=float(np.linalg.cond(np.c_[np.ones(parent.sum()),xyz[parent,0]-datum['origin_X_mm'],xyz[parent,1]-datum['origin_Y_mm']]*np.sqrt(area[parent,None]))))
 write(R/'03_parent_datum'/(sid+'.json'),datum);np.savez_compressed(out/'solid_source.npz',x=x,y=y,front=front,back=back,source_xyz=xyz,source_triangles=tri,source_ids=ids,T0_area=area)
 ledger=read(R/'17_reproducibility/CAD_ATTEMPTS.json') if (R/'17_reproducibility/CAD_ATTEMPTS.json').exists() else [];step=out/'standardized_planar_rear.step';resume=step.exists();entry=next((z for z in ledger if z['source_id']==sid and z['status']=='STARTED'),None)
 if resume:assert entry is not None,'Existing CAD has no recoverable attempt record'
 else:
  assert sum(z['source_id']==sid for z in ledger)<2;entry=dict(UTC=now(),source_id=sid,attempt=1,status='STARTED');ledger.append(entry);write(R/'17_reproducibility/CAD_ATTEMPTS.json',ledger)
 import cadquery as cq
 from OCP.BRep import BRep_Tool
 from surface import cad_surface
 from solid import solid
 oldbody=cq.importers.importStep(str(phase/'05_closed_solids'/sid/'measured_solid.step')).val();ff=[f for f in oldbody.Faces() if f.BoundingBox().xlen>.99*(x[-1]-x[0]) and f.BoundingBox().ylen>.99*(y[-1]-y[0])];assert len(ff)==2;f=max(ff,key=lambda v:v.Center().z);surf=BRep_Tool.Surface_s(f.wrapped);sp=RectBivariateSpline(x[::2],y,front[::2],s=0)
 polemin=min(surf.Pole(i,j).Z() for i in range(1,surf.NbUPoles()+1) for j in range(1,surf.NbVPoles()+1));assert polemin>back.max(),'Continuous front-rear separation bound failed'
 if not resume:
  rr=RectBivariateSpline(x[[0,-1]],y[[0,-1]],back[np.ix_([0,nx-1],[0,ny-1])],kx=1,ky=1,s=0);_,rear=cad_surface(rr);body=solid(f,rear);cq.exporters.export(body,str(step))
 body2=cq.importers.importStep(str(step)).val();assert body2.isValid() and len(body2.Solids())==len(body2.Shells())==1 and BRep_Tool.IsClosed_s(body2.Shells()[0].wrapped)
 ff=[f for f in body2.Faces() if f.BoundingBox().xlen>.99*(x[-1]-x[0]) and f.BoundingBox().ylen>.99*(y[-1]-y[0])];s2=BRep_Tool.Surface_s(max(ff,key=lambda v:v.Center().z).wrapped);z=np.array([s2.Value(float(p[0]),float(p[1])).Z() for p in xyz]);oldz=np.array([surf.Value(float(p[0]),float(p[1])).Z() for p in xyz]);assert abs(z-oldz).max()<1e-9
 inside=(xyz[:,0]>=x[0])&(xyz[:,0]<=x[-1])&(xyz[:,1]>=y[0])&(xyz[:,1]<=y[-1]);assert abs(z[inside]-sp.ev(xyz[inside,0],xyz[inside,1])).max()<1e-8
 err=abs(z-xyz[:,2]);reverse=[];closest=[];ref=dict(x=source_x32,y=source_y32,front=reference_front)
 for r,s,w in Q:
  p=xyz[tri[:,0]]*(1-r-s)+xyz[tri[:,1]]*r+xyz[tri[:,2]]*s;p[:,2]=sp.ev(p[:,0],p[:,1]);reverse.extend(abs(p[:,2]-original_height(ref,p)));closest.extend(closest_T0(ref,p))
 reverse=np.array(reverse);closest=np.array(closest);volume=float(sp.integral(x[0],x[-1],y[0],y[-1])-(back[0,0]+back[-1,-1])/2*(x[-1]-x[0])*(y[-1]-y[0]));ports,line=port_feasibility(dict(x=x,y=y,front=front),datum,19,100*19*(y[-1]-y[0]));assert all(v['screen_pass'] for v in ports)
 checks=dict(one_valid_closed_solid=True,positive_thickness=True,no_voids=len(body2.Shells())==1,front_BRep_unchanged=bool(abs(z-oldz).max()<1e-9),source_forward_P95=bool(np.percentile(err,95)<=.01),source_forward_max=bool(err.max()<=.04),CAD_reverse_P95=bool(np.percentile(reverse,95)<=.01),CAD_reverse_max=bool(reverse.max()<=.04),source_topology=True)
 q=dict(UTC=now(),source_id=sid,passed=all(checks.values()),checks=checks,source_points=len(xyz),source_triangles=len(tri),boundary_edges=int((n==1).sum()),source_graph_Euler=1,source_forward_P95_mm=float(np.percentile(err,95)),source_forward_max_mm=float(err.max()),reverse_samples=len(reverse),CAD_reverse_P95_mm=float(np.percentile(reverse,95)),CAD_reverse_max_mm=float(reverse.max()),CAD_reverse_actual_closest_T0_P95_mm=float(np.percentile(closest,95)),CAD_reverse_actual_closest_T0_max_mm=float(closest.max()),front_BRep_identity_max_mm=float(abs(z-oldz).max()),continuous_minimum_separation_bound_mm=float((polemin-back.max())/norm),volume_span_integral_mm3=volume,default_kernel_volume_mm3=float(body2.Volume()),volume_not_used_for_load=True,STEP_export_reimport=True,STEP_SHA256=sha(step),front='UNCHANGED_HISTORICAL_BREP;SOURCE_T0_FIDELITY_AUDITED',rear='ASSUMED_FRONT_DERIVED_PLANE',caps='FOUR_SYNTHETIC_RULED_CLOSURES',CAD_attempt=1,elapsed_s=time.perf_counter()-started,new_FE_solves=0)
 np.savez_compressed(R/'05_CAD_fidelity'/(sid+'.npz'),source_forward_gap_mm=err,CAD_reverse_gap_mm=reverse,CAD_reverse_actual_closest_T0_mm=closest);write(out/'CAD_QUALIFICATION.json',q);write(R/'09_mechanical_BVP'/(sid+'_ANALYTIC.json'),dict(ports=ports,line=line,force_N=float(100*19*(y[-1]-y[0])),gauge='sixscalarleftcorners',passed=True))
 q['audit_resumed_without_new_CAD_generation']=resume;q['CAD_spline_interior_identity_max_mm']=float(abs(z[inside]-sp.ev(xyz[inside,0],xyz[inside,1])).max());q['source_float32_XY_extrapolation_max_mm']=float(max(np.maximum(x[0]-xyz[:,0],xyz[:,0]-x[-1]).max(),np.maximum(y[0]-xyz[:,1],xyz[:,1]-y[-1]).max(),0));q['source_rounding_policy']='Same inherited analytic graph evaluation on original unchanged source XYZ; spline identity checked inside its finite domain. Full-boundary quadratic inverse tolerance remains historical1e-4; stress mapping1e-5. No source coordinate changed.';write(out/'CAD_QUALIFICATION.json',q)
 entry.update(status='COMPLETE',passed=q['passed'],STEP_SHA256=sha(step));write(R/'17_reproducibility/CAD_ATTEMPTS.json',ledger)
 if not q['passed']:write(R/'17_reproducibility/CAMPAIGN_STOP.json',dict(UTC=now(),stage='CAD_FIDELITY',source_id=sid,evidence=str(out/'CAD_QUALIFICATION.json')))
 print('CAD_QUALIFICATION',q,flush=True);return q
if __name__=='__main__':run(sys.argv[1])
