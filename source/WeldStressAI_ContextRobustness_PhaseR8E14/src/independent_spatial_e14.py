from common_e14 import *
import numpy as np,math
from independent_e14 import q95
def main():
 assert read(R/'17_independent_audits/INDEPENDENT_PASS.json')['passed'];registry=rows(R/'20_reproducibility/PREDICTION_REGISTRY.csv');reported=rows(R/'SOURCE_CONTEXT_METRICS.csv');shifts=rows(R/'CONTEXT_PREDICTION_CHANGES.csv');diagnostics=rows(R/'SPATIAL_ERROR_DIAGNOSTICS.csv');checks=[];regional=[];full={}
 for a in registry:
  if a['condition']=='FULL':full[a['model'],a['seed'],a['source_id']]=dict(np.load(a['path']))['pred_MPa']
 def check(a,name,value,expected):
  error=abs(float(value)-float(expected));assert math.isclose(float(value),float(expected),abs_tol=1e-8,rel_tol=1e-10),(a,name,value,expected);checks.append(dict(model=a['model'],seed=a['seed'],condition=a['condition'],source_id=a['source_id'],check=name,absolute_error=error,passed=True))
 for a in registry:
  sid=a['source_id'];d=dict(np.load(H/'01_dataset/targets'/(sid+'.npz')));q=np.flatnonzero(d['core']&d['valid']);p=dict(np.load(a['path']));v=p['pred_MPa'];y=d['T2_MPa'][q];w=d['area'][q];x=d['xyz'][q];s=math.fsum(map(float,w));hy=y>=q95(y,w);hp=v>=q95(v,w);wy=math.fsum(float(w[i]) for i in range(len(w)) if hy[i]);wp=math.fsum(float(w[i]) for i in range(len(w)) if hp[i]);cy=[math.fsum(float(w[i])*float(x[i,j]) for i in range(len(w)) if hy[i])/wy for j in range(3)];cp=[math.fsum(float(w[i])*float(x[i,j]) for i in range(len(w)) if hp[i])/wp for j in range(3)];centroid=math.sqrt(math.fsum((b-c)**2 for b,c in zip(cy,cp)));row=next(b for b in reported if all(a[k]==b[k] for k in ['model','seed','condition','source_id']));check(a,'high95_centroid_distance_mm',centroid,row['high95_centroid_distance_mm'])
  for values,name in [(v,'pred_std_MPa'),(y,'reference_std_MPa')]:
   mean=math.fsum(float(b)*float(c) for b,c in zip(w,values))/s;std=math.sqrt(math.fsum(float(b)*(float(c)-mean)**2 for b,c in zip(w,values))/s);check(a,name,std,row[name])
  fp=math.fsum(float(w[i]) for i in range(len(w)) if hp[i] and not hy[i]);fn=math.fsum(float(w[i]) for i in range(len(w)) if hy[i] and not hp[i]);check(a,'false_positive_area_mm2',fp,row['false_positive_area_mm2']);check(a,'false_negative_area_mm2',fn,row['false_negative_area_mm2']);f=full[a['model'],a['seed'],sid];delta=v-f;change=next(b for b in shifts if all(a[k]==b[k] for k in ['model','seed','condition','source_id']));sumsquare=math.fsum(float(b)*float(c)**2 for b,c in zip(w,delta));norm=math.fsum(float(b)*float(c)**2 for b,c in zip(w,f));check(a,'mean_signed_prediction_shift_MPa',math.fsum(float(b)*float(c) for b,c in zip(w,delta))/s,change['mean_signed_prediction_shift_MPa']);check(a,'RMS_prediction_shift_MPa',math.sqrt(sumsquare/s),change['RMS_prediction_shift_MPa']);check(a,'prediction_change_L2',math.sqrt(sumsquare/norm),change['prediction_change_L2']);check(a,'maximum_absolute_prediction_change_MPa',max(map(abs,delta)),change['maximum_absolute_prediction_change_MPa']);check(a,'predicted_maximum_amplitude_change_MPa',float(max(v)-max(f)),change['predicted_maximum_amplitude_change_MPa']);diag=next(b for b in diagnostics if all(a[k]==b[k] for k in ['model','seed','condition','source_id']));check(a,'nominal_reference_normalized_MAE',float(row['MAE_MPa'])/100,diag['mean_absolute_relative_error'])
  for region in set(map(int,d['region'][q])):
   z=np.flatnonzero(d['region'][q]==region);ww=w[z];dd=delta[z];ff=f[z];tot=math.fsum(map(float,ww));numer=math.fsum(float(b)*float(c)**2 for b,c in zip(ww,dd));de=math.fsum(float(b)*float(c)**2 for b,c in zip(ww,ff));vector_mean=float(np.average(dd,weights=ww));scalar_mean=math.fsum(float(b)*float(c) for b,c in zip(ww,dd))/tot;vector_rms=float(np.sqrt(np.average(dd*dd,weights=ww)));scalar_rms=math.sqrt(numer/tot);check(a,'region_'+str(region)+'_prediction_shift_mean',scalar_mean,vector_mean);check(a,'region_'+str(region)+'_prediction_shift_RMS',scalar_rms,vector_rms);regional.append(dict(**{k:a[k] for k in ['model','seed','condition','source_id','plate']},region=region,mean_signed_prediction_shift_MPa=scalar_mean,RMS_prediction_shift_MPa=scalar_rms,prediction_change_L2=math.sqrt(numer/de)))
  print('SPATIAL_SHIFT_CHECKED',a['model'],a['seed'],a['condition'],sid,flush=True)
 # Independently check every reported primary plate/study aggregation, including centroid, amplitudes and variance.
 plate=rows(R/'PLATE_CONTEXT_METRICS.csv');study=rows(R/'SEED_CONTEXT_METRICS.csv')
 for a in plate:
  ss=[b for b in reported if all(a[k]==b[k] for k in ['model','seed','condition','plate'])]
  for key in a:
   if key in ['model','seed','condition','plate','sources']:continue
   assert math.isclose(float(a[key]),math.fsum(float(b[key]) for b in ss)/len(ss),abs_tol=1e-9,rel_tol=1e-10),(a,key)
 for a in study:
  pp=[b for b in plate if all(a[k]==b[k] for k in ['model','seed','condition'])]
  for key in a:
   if key.startswith('equal_plate_'):assert math.isclose(float(a[key]),math.fsum(float(b[key[len('equal_plate_'):]]) for b in pp)/5,abs_tol=1e-9,rel_tol=1e-10)
 table(R/'17_independent_audits/INDEPENDENT_SPATIAL_SHIFT_CHECKS.csv',checks);table(R/'09_context_sensitivity/REGIONAL_PREDICTION_CHANGES.csv',regional);write(R/'17_independent_audits/SPATIAL_SHIFT_PASS.json',dict(UTC=now(),passed=True,checks=len(checks),maximum_abs_error=max(a['absolute_error'] for a in checks),fields=182,additional_to_primary_checks=True));print('ALL_SPATIAL_SHIFT_AUDITS_PASS',len(checks),flush=True)
if __name__=='__main__':main()
