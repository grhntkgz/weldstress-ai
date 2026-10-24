from common_r2 import *
from scipy.sparse import csr_matrix
from scipy.spatial import cKDTree
import math

def quantile(v,w,q):
 order=np.argsort(v);return float(np.interp(q,np.cumsum(w[order])/w.sum(),v[order]))
def compare(a,b,w,mask,region='whole'):
 aa=a[mask];bb=b[mask];ww=w[mask];dd=aa-bb
 return dict(region=region,points=int(mask.sum()),area_mm2=float(ww.sum()),M1_mean_T2_MPa=float(np.average(aa,weights=ww)),M2_mean_T2_MPa=float(np.average(bb,weights=ww)),MAE_MPa=float(np.average(abs(dd),weights=ww)),RMSE_MPa=float(np.sqrt(np.average(dd*dd,weights=ww))),normalized_L2=float(np.sqrt(np.sum(ww*dd*dd)/np.sum(ww*bb*bb))),normalization='Fine M2 areaweighted field L2, inherited E8B compare_r1 convention',M1_max_T2_MPa=float(aa.max()),M2_max_T2_MPa=float(bb.max()),M1_max_K=float(aa.max()/100),M2_max_K=float(bb.max()/100))
def main():
 g=np.load(R/'01_protocol_freeze/TARGET_GEOMETRY_SUPPORT.npz');x=g['xyz'];ids=g['source_ids'];area=g['area'];core=g['core'];ii=g['core_indices'];cols=g['neighbor_indices'];ptr=g['neighbor_indptr'];region=g['region'];mat=csr_matrix((area[cols],cols,ptr),shape=(len(ii),len(x)));den=np.array(mat.sum(1)).ravel();fields={};valids={};audits=[];tree=cKDTree(x)
 for level in ['M1','M2']:
  a=np.load(R/'10_source_mapping'/level/'SOURCE_MAPPING.npz');assert np.array_equal(a['xyz'],x) and np.array_equal(a['area'],area) and np.array_equal(a['source_ids'],ids);cov=(mat@a['valid'].astype(float))/den;ok=(cov>=1-1e-10)&a['valid'][ii];t2=np.full(len(x),np.nan);t2[ii]=np.where(ok,(mat@np.nan_to_num(a['sigma1_tensile']))/den,np.nan);valid=np.zeros(len(x),bool);valid[ii]=ok;fields[level]=t2;valids[level]=valid
  # Independent neighborhoods and scalar math.fsum for deterministic 256points.
  checks=[]
  for i in ii[np.linspace(0,len(ii)-1,256,dtype=int)]:
   nb=np.array(tree.query_ball_point(x[i],1+1e-7));assert a['valid'][nb].all();value=math.fsum(float(area[j])*float(a['sigma1_tensile'][j]) for j in nb)/math.fsum(float(area[j]) for j in nb);checks.append(abs(value-t2[i]))
  err=max(checks);assert err<=1e-8;audits.append(dict(level=level,independent_scalar_T2_points=256,max_error_MPa=err,inherited_tolerance_MPa=1e-8,passed=True))
  folder=R/('11_T2_M1' if level=='M1' else '12_T2_M2');np.savez_compressed(folder/'SOURCE_T2.npz',source_ids=ids,xyz=x,area=area,T2_MPa=t2,K_T2=t2/100,valid=valid,core=core,region=region)
  write(folder/'T2_RECEIPT.json',dict(level=level,UTC=now(),core_points=int(core.sum()),valid_T2_points=int(valid.sum()),valid_T2_area_mm2=float(area[valid].sum()),core_coverage=float(area[valid].sum()/area[core].sum()),mean_T2_MPa=float(np.average(t2[valid],weights=area[valid])),max_T2_MPa=float(t2[valid].max()),max_K_T2=float(t2[valid].max()/100),definition='Areaweighted originalT0,1mm3DEuclideanCHORDsameface+1e-7,principal tensile clipping BEFORE averaging',independent_scalar_max_error_MPa=err))
  table(R/f'SOURCE_T2_{level}.csv',[dict(source_id=int(ids[i]),X=x[i,0],Y=x[i,1],Z=x[i,2],T0_area_mm2=area[i],region=int(region[i]),frozen_core=bool(core[i]),valid_T2=bool(valid[i]),T2_MPa=float(t2[i]) if valid[i] else '',K_T2=float(t2[i]/100) if valid[i] else '') for i in range(len(x))])
 common=core&valids['M1']&valids['M2'];coverage=float(area[common].sum()/area[core].sum());a=fields['M1'];b=fields['M2'];whole=compare(a,b,area,common);regional=[compare(a,b,area,common&(region==k),name) for k,name in [(0,'parent_proxy'),(1,'weld_proxy'),(2,'adjacent_collar')]];q1=quantile(a[common],area[common],.95);q2=quantile(b[common],area[common],.95);h1=common&(a>=q1);h2=common&(b>=q2);iou=float(area[h1&h2].sum()/area[h1|h2].sum());high=dict(M1_threshold_MPa=q1,M2_threshold_MPa=q2,high95_area_IoU=iou,M1_high_area_mm2=float(area[h1].sum()),M2_high_area_mm2=float(area[h2].sum()),threshold_rule='Interpolated weighted CDF, inherited FE qualification; not MLstableStepCDF')
 table(R/'T2_NUMERICAL_METRICS.csv',[whole]);table(R/'T2_REGIONAL_METRICS.csv',regional);table(R/'T2_HIGH95_METRICS.csv',[high]);table(R/'T2_INDEPENDENT_AUDIT.csv',audits);table(R/'T2_COMMON_SUPPORT.csv',[dict(source_id=int(ids[i]),core=bool(core[i]),M1_valid=bool(valids['M1'][i]),M2_valid=bool(valids['M2'][i]),common=bool(common[i]),T0_area_mm2=area[i]) for i in range(len(x))]);np.savez_compressed(R/'13_numerical_qualification/COMPARISON_FIELDS.npz',xyz=x,area=area,source_ids=ids,core=core,common=common,region=region,M1=a,M2=b,high_M1=h1,high_M2=h2)
 # Full metrics independent scalar audit; separate arithmetic paths and manual interpolatedCDF.
 def independent_quant(v,w):
  pairs=sorted(zip(v,w),key=lambda p:p[0]);tot=math.fsum(float(p[1]) for p in pairs);cum=0.;previous_cdf=0.;previous_val=float(pairs[0][0])
  for value,weight in pairs:
   cum+=float(weight);cdf=cum/tot
   if cdf>=.95:
    return previous_val+(float(value)-previous_val)*(.95-previous_cdf)/(cdf-previous_cdf)
   previous_cdf=cdf;previous_val=float(value)
  return float(pairs[-1][0])
 independent_metrics=[]
 for key,mask in [('whole',common)]+[(z['region'],common&(region==k)) for k,z in enumerate(regional)]:
  jj=np.flatnonzero(mask);num=math.fsum(float(area[i])*float(a[i]-b[i])**2 for i in jj);denom=math.fsum(float(area[i])*float(b[i])**2 for i in jj);value=math.sqrt(num/denom);reported=whole if key=='whole' else next(z for z in regional if z['region']==key);assert abs(value-reported['normalized_L2'])<1e-12;independent_metrics.append(dict(metric=key+'_L2',independent=value,reported=reported['normalized_L2'],absolute_difference=abs(value-reported['normalized_L2']),passed=True))
 iq1=independent_quant(a[common],area[common]);iq2=independent_quant(b[common],area[common]);assert abs(iq1-q1)<1e-9 and abs(iq2-q2)<1e-9
 ih1=common&(a>=iq1);ih2=common&(b>=iq2);iiou=math.fsum(float(v) for v in area[ih1&ih2])/math.fsum(float(v) for v in area[ih1|ih2]);assert abs(iiou-iou)<1e-12;independent_metrics.append(dict(metric='high95_area_IoU',independent=iiou,reported=iou,absolute_difference=abs(iiou-iou),passed=True));table(R/'13_numerical_qualification/INDEPENDENT_METRIC_AUDIT.csv',independent_metrics)
 tensors=[read(R/'09_tensor_recovery'/f'{l}_INDEPENDENT_TENSOR_RECEIPT.json') for l in ['M1','M2']];mapping=[read(R/'10_source_mapping'/l/'MAPPING_AUDIT.json') for l in ['M1','M2']];checks=dict(whole_L2=whole['normalized_L2']<=.02,worst_regional_L2=max(z['normalized_L2'] for z in regional)<=.03,high95_IoU=iou>=.8,common_core_coverage=coverage>=.99,mapping_coverage=all(z['passed'] for z in mapping),independent_tensor=all(z['independent_qualified'] for z in tensors),independent_T2=all(z['passed'] for z in audits),independent_metrics=all(z['passed'] for z in independent_metrics));qualified=all(checks.values());decision=dict(UTC=now(),qualified=qualified,checks=checks,whole=whole,regional=regional,high95=high,common_points=int(common.sum()),common_area_mm2=float(area[common].sum()),core_coverage=coverage,target_version=VERSION,target_semantics_SHA256=read(R/'01_protocol_freeze/R1_frozen/TARGET_STANDARD_PLANAR_V1.json')['semantics_SHA256'],designated_release_mesh='M2',physical_validation=False,asymptotic_convergence=False);write(R/'13_numerical_qualification/QUALIFICATION_DECISION.json',decision)
 registry=[]
 if qualified:
  dest=R/'13_numerical_qualification/QUALIFIED_C02_V1_M2_TARGET.npz';shutil.copy2(R/'12_T2_M2/SOURCE_T2.npz',dest);registry=[dict(source_id=SID,target_version=VERSION,target_semantics_hash=decision['target_semantics_SHA256'],status='QUALIFIED',qualification_scope='Conditional two-mesh numerical consistency only',mesh='M2',target_path=str(dest),target_hash=sha(dest),M1_mesh_hash=sha(LEVELS['M1']/'mesh.npz'),M2_mesh_hash=sha(LEVELS['M2']/'mesh.npz'),core_points=int(common.sum()))]
 table(R/'QUALIFIED_V1_TARGET_REGISTRY.csv',registry,['source_id','target_version','target_semantics_hash','status','qualification_scope','mesh','target_path','target_hash','M1_mesh_hash','M2_mesh_hash','core_points'])
 print('T2_QUALIFICATION',decision,flush=True)

if __name__=='__main__':protect();main()
