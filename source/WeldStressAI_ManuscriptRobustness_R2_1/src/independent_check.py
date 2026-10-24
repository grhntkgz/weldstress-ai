"""Independent checker: Python sorting/bisect, dot/weighted moments, separate contour construction.
Does not import primary metric or geometry modules.
"""
from pathlib import Path
import json,math,bisect,itertools,hashlib,datetime
import numpy as np,pandas as pd
D=Path(__file__).resolve().parents[1];reg=pd.read_csv(D/'R2_1_SOURCE_REGISTRY.csv');fr=pd.read_csv(D/'FROZEN_FIELD_ANALYSIS_REGISTRY.csv',keep_default_na=False)
rank=pd.read_csv(D/'THRESHOLD_ROBUSTNESS_SOURCE.csv');common=pd.read_csv(D/'REFERENCE_THRESHOLD_DIAGNOSTICS.csv');region=pd.read_csv(D/'REGIONAL_ERROR_SOURCE.csv');g0=pd.read_csv(D/'G0_COLLAR_BASELINE_RESULTS.csv');g1=pd.read_csv(D/'G1_GEOMETRY_RANKING_RESULTS.csv');checks=[];geometry_checks=[];aggregate_checks=[]
def close(a,b,kind,key):
 if np.isnan(a) and np.isnan(b):return
 error=abs(a-b);assert error<=1e-8+1e-10*abs(b),(kind,key,a,b,error);checks.append(dict(kind=kind,key=key,absolute_error=error,status='PASS'))
def ordered(v,ids):return sorted(range(len(v)),key=lambda i:(-float(v[i]),int(ids[i])))
def prefix_masks(v,w,ids):
 ix=ordered(v,ids);acc=list(itertools.accumulate(float(w[i]) for i in ix));total=math.fsum(map(float,w));out={}
 for frac in [.01,.05,.10]:
  target=frac*total;k=bisect.bisect_left(acc,target);hi=min(k+1,len(ix));lo=max(hi-1,0);al=acc[lo-1] if lo else 0;ah=acc[hi-1];n=hi if abs(ah-target)<=abs(al-target) else lo;mask=np.zeros(len(v),bool);mask[ix[:n]]=True;out[frac]=mask
 return out
def pct(v,w,q):
 ix=sorted(range(len(v)),key=lambda i:float(v[i]));total=math.fsum(map(float,w));cdf=[a/total for a in itertools.accumulate(float(w[i]) for i in ix)];j=bisect.bisect_left(cdf,q)
 if j<=0:return float(v[ix[0]])
 if j>=len(v):return float(v[ix[-1]])
 a,b=cdf[j-1],cdf[j];return float(v[ix[j-1]])+(q-a)/(b-a)*(float(v[ix[j]])-float(v[ix[j-1]]))
def metrics(a,b,w,x):
 ar=float(np.dot(w,a.astype(float)));ap=float(np.dot(w,b.astype(float)));inter=float(np.dot(w,(a.astype(int)*b).astype(float)));union=ar+ap-inter;fn=ar-inter;fp=ap-inter
 cr=np.array([np.dot(w*a,x[:,k])/ar for k in range(3)]) if ar else np.full(3,np.nan);cp=np.array([np.dot(w*b,x[:,k])/ap for k in range(3)]) if ap else np.full(3,np.nan)
 return dict(IoU=inter/union if union else np.nan,precision=inter/ap if ap else np.nan,recall=inter/ar if ar else np.nan,FN_mm2=fn,FP_mm2=fp,reference_area_mm2=ar,predicted_area_mm2=ap,reference_fraction=ar/math.fsum(w),predicted_fraction=ap/math.fsum(w),centroid_separation_mm=float(math.sqrt(math.fsum((cr-cp)**2))),intersection_mm2=inter,union_mm2=union)
for _,sr in reg.iterrows():
 sid=sr.source_id;full=dict(np.load(sr.geometry_path));t=dict(np.load(sr.target_path));m=t['core']&t['valid'];x=t['xyz'][m];ids=t['source_ids'][m];w=t['area'][m];y=t['T2_MPa'][m];labels=t['region'][m];refs=prefix_masks(y,w,ids);rth={f:pct(y,w,1-f) for f in [.01,.05,.10]};geo=dict(np.load(D/'geometry_only'/(sid+'.npz')));score=geo['score'][m];gmasks=prefix_masks(score,w,ids)
 # Independent contour reconstruction: cross each unique mesh edge once, then connect per triangle.
 d=json.loads(sr.datum_json);xyz=full['xyz'];h=(xyz[:,2]-d['intercept_Z_mm']-d['slope_X']*(xyz[:,0]-d['origin_X_mm'])-d['slope_Y']*(xyz[:,1]-d['origin_Y_mm']))/math.sqrt(1+d['slope_X']**2+d['slope_Y']**2)-.5
 assert np.all(h!=0),'Exact level-vertex case requires explicit independent verification, not substitution'
 intersections={};segments=[]
 for tri in full['triangles']:
  if h[tri].min()>0 or h[tri].max()<0:continue
  points=[]
  for u,v in [(int(tri[0]),int(tri[1])),(int(tri[1]),int(tri[2])),(int(tri[2]),int(tri[0]))]:
   if (h[u]<0)!=(h[v]<0):
    key=(min(u,v),max(u,v))
    if key not in intersections:
     a,b=key;intersections[key]=(h[b]*xyz[a,:2]-h[a]*xyz[b,:2])/(h[b]-h[a])
    points.append(intersections[key])
  assert len(points)==2;segments.append(points)
 seg=np.array(segments);assert len(seg)==len(geo['segments_XY'])
 # Reconstruct nearest distance using endpoint/interior alternatives in independent arithmetic.
 a=seg[:,0];v=seg[:,1]-a;den=np.einsum('ij,ij->i',v,v);dist=np.empty(len(x))
 for begin in range(0,len(x),256):
  da=x[begin:begin+256,None,:2]-a;dot=np.einsum('ijk,jk->ij',da,v);length2=np.einsum('ijk,ijk->ij',da,da);db=x[begin:begin+256,None,:2]-seg[:,1];end2=np.einsum('ijk,ijk->ij',db,db);d2=np.where(dot<=0,length2,np.where(dot>=den,end2,length2-dot**2/den));dist[begin:begin+256]=np.sqrt(np.maximum(0,d2.min(axis=1)))
 err=float(abs(dist+score).max());assert err<1e-7,(sid,err);geometry_checks.append(dict(source_id=sid,independent_segments=len(seg),distance_max_error_mm=err,geometry_score_target_free=True,rank_membership_independently_checked=True,status='PASS'))
 for frac in [.01,.05,.10]:
  for table,predmask in [(g0,labels==2),(g1,gmasks[frac])]:
   row=table[(table.source_id==sid)&(table.budget==frac)].iloc[0]
   for c,val in metrics(refs[frac],predmask,w,x).items():close(val,float(row[c]),'GEOMETRY_METRIC',sid+':'+str(frac)+':'+c)
 for _,f in fr[fr.source_id==sid].iterrows():
  fieldid=f.field_id;data=dict(np.load(f.path));take=np.flatnonzero(m) if len(data['pred_MPa'])==len(m) else np.arange(m.sum());p=data['pred_MPa'][take];predmasks=prefix_masks(p,w,ids);stored=dict(np.load(D/'qa'/'masks'/(fieldid+'.npz')))
  for frac in [.01,.05,.10]:
   code=f'{int(frac*100):02d}';assert np.array_equal(refs[frac],stored['ref_rank_'+code]);assert np.array_equal(predmasks[frac],stored['pred_rank_'+code]);row=rank[(rank.field_id==fieldid)&(rank.scheme=='RANK_BUDGET')&(rank.budget==frac)].iloc[0]
   for c,val in metrics(refs[frac],predmasks[frac],w,x).items():close(val,float(row[c]),'RANK_MASK_METRIC',fieldid+':'+str(frac)+':'+c)
   a=y>=rth[frac];b=p>=rth[frac];assert np.array_equal(a,stored['ref_common_'+code]);assert np.array_equal(b,stored['pred_common_'+code]);row=common[(common.field_id==fieldid)&(common.budget==frac)].iloc[0];close(rth[frac],row.FE_threshold_MPa,'FE_PERCENTILE',fieldid+':'+str(frac))
   for c,val in metrics(a,b,w,x).items():close(val,float(row[c]),'COMMON_THRESHOLD_METRIC',fieldid+':'+str(frac)+':'+c)
  a=y>=pct(y,w,.95);b=p>=pct(p,w,.95);assert np.array_equal(a,stored['ref_historical']);assert np.array_equal(b,stored['pred_historical']);row=rank[(rank.field_id==fieldid)&(rank.scheme=='HISTORICAL_HIGH95')].iloc[0]
  for c,val in metrics(a,b,w,x).items():close(val,float(row[c]),'HISTORICAL_METRIC',fieldid+':'+c)
  e=p-y;ss=math.fsum(float(wi)*float(ei)**2 for wi,ei in zip(w,e));sa=math.fsum(float(wi)*abs(float(ei)) for wi,ei in zip(w,e));gn=math.fsum(float(wi)*float(yi)**2 for wi,yi in zip(w,y));whole=math.fsum(w)
  for code,name in [(0,'PARENT'),(1,'HEIGHT_REGION'),(2,'COLLAR')]:
   mask=labels==code;ww=w[mask];ee=e[mask];yy=y[mask];area=math.fsum(ww);sse=math.fsum(float(a)*float(b)**2 for a,b in zip(ww,ee));sae=math.fsum(float(a)*abs(float(b)) for a,b in zip(ww,ee));norm=math.fsum(float(a)*float(b)**2 for a,b in zip(ww,yy));rr=region[(region.field_id==fieldid)&(region.region==name)].iloc[0]
   met=dict(area_mm2=area,area_fraction=area/whole,MAE_MPa=sae/area,RMSE_MPa=math.sqrt(sse/area),bias_MPa=math.fsum(float(a)*float(b) for a,b in zip(ww,ee))/area,absolute_error_Q95_MPa=pct(abs(ee),ww,.95),reference_mean_MPa=math.fsum(float(a)*float(b) for a,b in zip(ww,yy))/area,reference_Q95_MPa=pct(yy,ww,.95),L2=math.sqrt(sse/norm),SSE_share=sse/ss,SAE_share=sae/sa,globally_normalized_SSE_contribution=sse/gn)
   for c,val in met.items():close(val,float(rr[c]),'REGIONAL_METRIC',fieldid+':'+name+':'+c)
 print('INDEPENDENT_SOURCE_VERIFIED',sid,flush=True)
# Independently aggregate with explicit Python groups, not the primary groupby helper.
for source_name,plate_name,macro_name,dims in [('THRESHOLD_ROBUSTNESS_SOURCE.csv','THRESHOLD_ROBUSTNESS_PLATE.csv','THRESHOLD_ROBUSTNESS_MACRO.csv',['scheme','budget']),('REFERENCE_THRESHOLD_DIAGNOSTICS.csv','REFERENCE_THRESHOLD_PLATE.csv','REFERENCE_THRESHOLD_MACRO.csv',['scheme','budget']),('REGIONAL_ERROR_SOURCE.csv','REGIONAL_ERROR_PLATE.csv','REGIONAL_ERROR_MACRO.csv',['region'])]:
 rows=pd.read_csv(D/source_name).to_dict('records');pt=pd.read_csv(D/plate_name).to_dict('records');mt=pd.read_csv(D/macro_name).to_dict('records');skip={'field_id','source_id','plate','model','seed','condition','retrospective','region_code',*dims};numeric=[c for c in rows[0] if c not in skip and isinstance(rows[0][c],(float,int))]
 def matches(a,b,keys):return all(a[k]==b[k] for k in keys)
 def average(seq):
  seq=[float(v) for v in seq if pd.notna(v)];return math.fsum(seq)/len(seq) if seq else float('nan')
 for row in pt:
  selected=[a for a in rows if matches(a,row,['model','condition','plate']+dims)];seeds=set(str(a['seed']) for a in selected)
  for c in numeric:
   value=average(average(a[c] for a in selected if str(a['seed'])==s) for s in seeds);close(value,float(row[c]),'PLATE_AGGREGATION',source_name+':'+str([row[k] for k in ['model','condition','plate']+dims])+':'+c);aggregate_checks.append(1)
 for row in mt:
  selected=[a for a in rows if matches(a,row,['model','condition']+dims)];seeds=set(str(a['seed']) for a in selected)
  for c in numeric:
   per_seed=[]
   for s in seeds:
    per_plate=[average(a[c] for a in selected if str(a['seed'])==s and a['plate']==p) for p in 'CEGHX'];per_seed.append(average(per_plate))
   close(average(per_seed),float(row[c]),'SEED_EQUAL_PLATE_AGGREGATION',source_name+':'+str([row[k] for k in ['model','condition']+dims])+':'+c);aggregate_checks.append(1)
pd.DataFrame(checks).to_csv(D/'qa'/'INDEPENDENT_NUMERIC_CELL_CHECKS.csv',index=False);pd.DataFrame(geometry_checks).to_csv(D/'qa'/'INDEPENDENT_GEOMETRY_SCORE_CHECKS.csv',index=False)
report=dict(status='PASS',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),fields=299,numeric_cells=len(checks),aggregate_cells=len(aggregate_checks),max_absolute_cell_error=max(r['absolute_error'] for r in checks),geometry_sources=13,independent_geometry_max_distance_error_mm=max(r['distance_max_error_mm'] for r in geometry_checks),rank_common_historical_masks='ALL EXACT',independent_methods='Python sorted and itertools.accumulate/bisect; independent percentile interpolation; dot-product set arithmetic; math.fsum weighted errors; explicit Python plate/seed grouping; independently constructed contour edge intersections and distance algebra',new_prediction_execution=False)
(D/'qa'/'INDEPENDENT_AUDIT_PASS.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
