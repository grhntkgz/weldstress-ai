"""Pure validation/geometry functions. No native solver, mesh or model API."""
import math,hashlib,json
from pathlib import Path
import numpy as np
from scipy.interpolate import RectBivariateSpline
from scipy.spatial import cKDTree

class ProtocolError(ValueError):pass
def require(ok,message):
 if not ok:raise ProtocolError(message)
def number(x,name):require(type(x) in [int,float] and math.isfinite(x),name+' must be a finite real number, not bool/string/null');return float(x)
def target_compatible(records,version,semantics_hash=None):
 require(bool(records),'empty target collection')
 seen=set()
 for r in records:
  require(r.get('target_version')==version,'mixed/legacy target versions')
  require(r.get('status')=='QUALIFIED','planned/unqualified target cannot enter learning')
  require(isinstance(r.get('target_hash'),str) and len(r['target_hash'])==64 and all(c in '0123456789abcdef' for c in r['target_hash']),'missing qualified target hash')
  require(isinstance(r.get('target_semantics_hash'),str) and len(r['target_semantics_hash'])==64 and all(c in '0123456789abcdef' for c in r['target_semantics_hash']),'missing target semantics hash');seen.add(r['target_semantics_hash'])
  if semantics_hash is not None:require(r['target_semantics_hash']==semantics_hash,'target ID reused with changed semantics')
 require(len(seen)==1,'mixed target semantics under one target ID')
 return True
def validate_bvp(c):
 require(c['load_protocol_id']=='BVP_NOMINAL100_TNOM_WFULL_X_COMMONMID_V1','wrong load convention')
 E=number(c['E_MPa'],'E');nu=number(c['nu'],'nu');require(E==210000 and nu==.30,'material contract mismatch')
 t=number(c['nominal_thickness_mm'],'nominal thickness');W=number(c['reference_width_mm'],'reference width');sigma=number(c['reference_stress_MPa'],'sigma');F=number(c['force_per_port_N'],'force');require(t>0 and W>0 and sigma==100,'invalid reference quantities')
 require(abs(F-sigma*t*W)<=1e-10*F,'force is not sigma*t_nom*full_design_width')
 require(c['reference_width_basis']=='FULL_COMPUTATIONAL_DOMAIN_NOT_OBSERVATION_CROP','crop width is not load width')
 require(c['load_direction']==[1,0,0] and c['normalization_MPa']==100,'load/normalization mismatch')
 require(c['thickness_basis'] in ['DOCUMENTED_NOMINAL','INDEPENDENTLY_MEASURED_NOMINAL_PARAMETER'],'unverified thickness cannot silently default')
 require(c['physical_axis_status'] in ['DOCUMENTED_NUMERICAL_FRAME','INFERRED_NOT_PHYSICALLY_CALIBRATED'],'axis status must be explicit')
 require(c['domain_complete_graph'] is True,'hole-bearing domains require another target stratum')
 return True
def acceptance(e):
 required=['CAD_valid','front_IDs_preserved','native_success','native_errors','nodes','elements','minSICN','negative_J','zero_J','invalid_elements','forward_P95_mm','forward_max_mm','reverse_P95_mm','reverse_max_mm','coverage','whole_L2','worst_regional_L2','high95_IoU','force_residual','moment_residual','hierarchy_pass']
 require(all(k in e for k in required),'missing qualification evidence')
 for k in ['CAD_valid','front_IDs_preserved','native_success','hierarchy_pass']:require(type(e[k]) is bool,'qualification booleans must be bool')
 for k in required:
  if k not in ['CAD_valid','front_IDs_preserved','native_success','hierarchy_pass']:number(e[k],k)
 for k in ['nodes','elements']:require(e[k]>0 and type(e[k]) is int,k+' must be a positive integer')
 for k in ['native_errors','negative_J','zero_J','invalid_elements']:require(e[k]>=0 and type(e[k]) is int,k+' must be a nonnegative integer')
 for k in ['forward_P95_mm','forward_max_mm','reverse_P95_mm','reverse_max_mm','whole_L2','worst_regional_L2','force_residual','moment_residual']:require(e[k]>=0,k+' cannot be negative')
 for k in ['coverage','high95_IoU','minSICN']:require(0<=e[k]<=1,k+' must be in[0,1]')
 checks=dict(CAD=e['CAD_valid'],identity=e['front_IDs_preserved'],native=e['native_success'] and e['native_errors']==0,mesh=e['nodes']<=350000 and e['elements']<=230000 and e['minSICN']>=.02 and e['negative_J']==e['zero_J']==e['invalid_elements']==0,geometry=e['forward_P95_mm']<=.01 and e['forward_max_mm']<=.04 and e['reverse_P95_mm']<=.01 and e['reverse_max_mm']<=.04,T2=e['whole_L2']<=.02 and e['worst_regional_L2']<=.03 and e['high95_IoU']>=.8 and e['coverage']>=.99,equilibrium=e['force_residual']<=1e-5 and e['moment_residual']<=1e-5,hierarchy=e['hierarchy_pass'])
 return dict(passed=all(checks.values()),checks=checks)
def validate_splits(records,forbidden=()):
 role_by_group={};source_groups={}
 for r in records:
  require(r['source_id'] not in forbidden,'historical exposed identity in prospective split')
  require(r['role'] in ['train','inner_validation','outer'],'unsupported split role')
  key=(r['fold'],r['dependency_group']);role_by_group.setdefault(key,set()).add(r['role']);source_groups.setdefault(r['source_id'],set()).add(r['dependency_group'])
 require(all(len(v)==1 for v in role_by_group.values()),'dependency leakage across fold roles')
 require(all(len(v)==1 for v in source_groups.values()),'crop/counterfactual changed source dependency')
 return True
def source_correspondence(original_xyz,original_ids,view_xyz,view_ids):
 require(len(np.unique(original_ids))==len(original_ids) and len(np.unique(view_ids))==len(view_ids),'duplicate source IDs')
 order=np.argsort(original_ids);pos=np.searchsorted(original_ids[order],view_ids);require((pos<len(order)).all(),'unrecognized source ID');ix=order[pos];require(np.array_equal(original_ids[ix],view_ids),'unrecognized source ID');require(original_xyz[ix].dtype==view_xyz.dtype and original_xyz[ix].tobytes()==view_xyz.tobytes(),'source coordinates altered');return ix
def crop_source(xyz,triangles,ids,lo,hi):
 require(lo<hi,'invalid crop');keep=(xyz[:,0]>=lo)&(xyz[:,0]<=hi);triangle_ids=np.flatnonzero(np.all(keep[triangles],axis=1));retained=np.unique(triangles[triangle_ids]);require(len(retained)>100,'insufficient crop geometry');inv=np.full(len(xyz),-1);inv[retained]=np.arange(len(retained));view=dict(xyz=xyz[retained],triangles=inv[triangles[triangle_ids]],source_ids=ids[retained],full_indices=retained,original_triangle_ids=triangle_ids);source_correspondence(xyz,ids,view['xyz'],view['source_ids']);require(np.array_equal(retained[view['triangles']],triangles[triangle_ids]),'original triangle identity lost');return view
def front_parent_datum(xyz,area,bounds):
 xmin,xmax,ymin,ymax=bounds;cx=(xmin+xmax)/2;cy=(ymin+ymax)/2;left=xyz[:,0]<=xmin+.1*(xmax-xmin);right=xyz[:,0]>=xmax-.1*(xmax-xmin);keep=left|right;require(left.sum()>=100 and right.sum()>=100,'both parent strips require100points');X=np.c_[np.ones(keep.sum()),xyz[keep,0]-cx,xyz[keep,1]-cy];z=xyz[keep,2];w=area[keep];coef=np.linalg.lstsq(X*np.sqrt(w)[:,None],z*np.sqrt(w),rcond=None)[0]
 for _ in range(20):
  residual=z-X@coef;scale=max(1e-6,1.4826*np.median(abs(residual-np.median(residual))));huber=np.minimum(1,1.345*scale/np.maximum(abs(residual),1e-30));ww=w*huber;new=np.linalg.lstsq(X*np.sqrt(ww)[:,None],z*np.sqrt(ww),rcond=None)[0]
  if np.max(abs(new-coef))<1e-12:coef=new;break
  coef=new
 residual=z-X@coef;order=np.argsort(abs(residual),kind='stable');p95=float(abs(residual)[order[np.searchsorted(np.cumsum(w[order])/sum(w),.95)]])
 summary=dict(rule='FRONT_PARENT_HUBER_OUTER10_NORMAL_OFFSET_V1',origin_X_mm=cx,origin_Y_mm=cy,intercept_Z_mm=float(coef[0]),slope_X=float(coef[1]),slope_Y=float(coef[2]),parent_points=int(keep.sum()),parent_RMS_mm=float(np.sqrt(np.average(residual**2,weights=w))),parent_P95_abs_mm=p95,fit_iterations_limit=20,Huber_c=1.345,physical_datum_calibrated=False)
 summary['screen_pass']=summary['parent_RMS_mm']<=.10 and p95<=.20 and abs(coef[1])<=.02 and abs(coef[2])<=.02
 return summary,keep
def plane_z(xyz,datum,t):return datum['intercept_Z_mm']+datum['slope_X']*(xyz[:,0]-datum['origin_X_mm'])+datum['slope_Y']*(xyz[:,1]-datum['origin_Y_mm'])-t*math.sqrt(1+datum['slope_X']**2+datum['slope_Y']**2)
def port_feasibility(source,datum,t,F):
 x=source['x'];y=source['y'];sp=RectBivariateSpline(x[::2],y,source['front'][::2],s=0);yc=(y[0]+y[-1])/2;zc=datum['intercept_Z_mm']-.5*t*math.sqrt(1+datum['slope_X']**2+datum['slope_Y']**2);knots=np.unique(sp.get_knots()[1]);roots,weights=np.polynomial.legendre.leggauss(5);out=[]
 for X in x[[0,-1]]:
  yy=np.concatenate([(b+a)/2+(b-a)/2*roots for a,b in zip(knots[:-1],knots[1:])]);ww=np.concatenate([(b-a)/2*weights for a,b in zip(knots[:-1],knots[1:])]);zf=sp.ev(np.full(len(yy),X),yy);zb=plane_z(np.c_[np.full(len(yy),X),yy,np.zeros(len(yy))],datum,t);h=zf-zb;require((h>0).all(),'nonpositive section separation');Y=yy-yc;Z1=((zf-zc)**2-(zb-zc)**2)/2;Z2=((zf-zc)**3-(zb-zc)**3)/3
  M=np.array([[sum(ww*h),sum(ww*Y*h),sum(ww*Z1)],[sum(ww*Y*h),sum(ww*Y*Y*h),sum(ww*Y*Z1)],[sum(ww*Z1),sum(ww*Y*Z1),sum(ww*Z2)]],float);coef=np.linalg.solve(M,[F,0,0]);Ybound=max(abs(y-yc));rear_extrema=plane_z(np.c_[[X,X],y[[0,-1]],np.zeros(2)],datum,t);Zbound=max(abs(sp.get_coeffs().min()-zc),abs(sp.get_coeffs().max()-zc),abs(rear_extrema-zc).max());bound=abs(coef[1])*Ybound+abs(coef[2])*Zbound;lo=float(coef[0]-bound);hi=float(coef[0]+bound)
  out.append(dict(X_mm=float(X),area_mm2=float(M[0,0]),mean_traction_MPa=float(F/M[0,0]),affine_coefficients=coef.tolist(),traction_lower_conservative_bound_MPa=lo,traction_upper_conservative_bound_MPa=hi,moment_system_condition=float(np.linalg.cond(M)),screen_pass=lo>=50 and hi<=150))
 return out,dict(Y_mm=float(yc),Z_mm=float(zc))
def local_F1(xyz,normal,area,queries,datum,bounds,has_internal_holes=False):
 require(has_internal_holes is False,'F1 prototype is limited to complete rectangular graphs; hole-aware boundary support is not implemented')
 tree=cKDTree(xyz);features=[];anchor=np.array([datum['origin_X_mm'],datum['origin_Y_mm'],datum['intercept_Z_mm']]);norm=math.sqrt(1+datum['slope_X']**2+datum['slope_Y']**2)
 for i in queries:
  p=xyz[i];nb=np.array(tree.query_ball_point(p,1+1e-7));n3=np.array(tree.query_ball_point(p,3+1e-7));ww=area[nb];meanZ=np.average(xyz[nb,2],weights=ww);meanN=np.average(normal[nb],axis=0,weights=ww);delta=xyz[nb,:2]-p[:2];angle=np.arctan2(delta[:,1],delta[:,0]);sectors=len(np.unique(np.floor((angle+np.pi)/(2*np.pi)*8).clip(0,7)));D=np.c_[np.ones(len(nb)),delta,delta[:,0]**2,delta[:,0]*delta[:,1],delta[:,1]**2];fitgood=len(nb)>=12 and sectors>=6 and np.linalg.matrix_rank(D)==6 and np.linalg.cond(D)<1e6;curv=0.
  if fitgood:coef=np.linalg.lstsq(D*np.sqrt(ww)[:,None],(xyz[nb,2]-p[2])*np.sqrt(ww),rcond=None)[0];curv=2*(coef[3]+coef[5])
  d3=xyz[n3,:2]-p[:2];sectors3=len(np.unique(np.floor((np.arctan2(d3[:,1],d3[:,0])+np.pi)/(2*np.pi)*8).clip(0,7)));edge=min(p[0]-bounds[0],bounds[1]-p[0],p[1]-bounds[2],bounds[3]-p[1]);complete3=edge>=3 and sectors3>=6
  h=(p[2]-(datum['intercept_Z_mm']+datum['slope_X']*(p[0]-datum['origin_X_mm'])+datum['slope_Y']*(p[1]-datum['origin_Y_mm'])))/norm;n=normal[i];features.append(np.r_[(p-anchor)/60,n,h,-n[0]/max(n[2],1e-12),-n[1]/max(n[2],1e-12),[1,0,0],0,p[2]-meanZ,np.linalg.norm(n-meanN),sectors3/8,curv,float(fitgood),float(complete3)])
 out=np.asarray(features,dtype='f4');require(out.shape==(len(queries),19) and np.isfinite(out).all(),'invalid F1 contract');return out
def validate_model_config(c):
 require(c['status']=='PROPOSED_NOT_EXECUTED' and c['execution_authorized'] is False,'training is not authorized')
 require(c['seeds']==[20261019,20261020] and c['folds']==['CV0','CV1','CV2','CV3','CV4'],'unfrozen seeds/folds')
 require(c['epochs']==100 and c['query_points']==512 and c['loss']=='L0_MEAN_SQUARED_K','uncontrolled primary budget/loss')
 require(c['target_version'].startswith('T2_STANDARD_PLANAR_REAR_V1__'),'incompatible primary target')
 require(c['feature_contract'] in ['F0_S1_LEGACY19','F1_FIXED_FRAME_LOCAL19','F2_F1_PLUS_MECHANICS14'],'unknown input')
 require(c['AI_runs_in_E9']==0,'E9 inference/training prohibited');return True
def dryrun_only(argv):require(argv==['--dry-run'],'execution unavailable; only --dry-run is implemented')
