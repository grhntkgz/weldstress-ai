import numpy as np

def quantile(v,w,q):
    k=np.argsort(v,kind='stable');return float(np.interp(q,np.cumsum(w[k])/w.sum(),v[k]))

def budget(v,w,ids,fraction):
    order=np.lexsort((ids,-np.asarray(v,dtype=float)));cum=np.cumsum(w[order]);target=fraction*w.sum();j=int(np.searchsorted(cum,target,side='left'));high=min(j+1,len(order));low=max(high-1,0);alow=cum[low-1] if low else 0;ahigh=cum[high-1] if high else 0
    count=high if abs(ahigh-target)<=abs(alow-target) else low
    mask=np.zeros(len(v),dtype=bool);mask[order[:count]]=True
    cut=float(v[order[count-1]]) if count else np.nan;ties=(v==cut) if count else np.zeros(len(v),bool)
    return mask,dict(requested_fraction=fraction,achieved_fraction=float(w[mask].sum()/w.sum()),quota_error_mm2=float(w[mask].sum()-target),selected_points=int(mask.sum()),cut_score=cut,tie_points=int(ties.sum()),tie_selected_points=int((ties&mask).sum()),tie_split=bool(np.any(ties&mask) and np.any(ties&~mask)),constant_score=bool(np.ptp(v)==0))

def localization(ref,pred,w,xyz):
    area=float(w.sum());inter=float(w[ref&pred].sum());union=float(w[ref|pred].sum());ar=float(w[ref].sum());ap=float(w[pred].sum())
    cent=float(np.linalg.norm(np.average(xyz[ref],axis=0,weights=w[ref])-np.average(xyz[pred],axis=0,weights=w[pred]))) if ar>0 and ap>0 else np.nan
    return dict(IoU=inter/union if union else np.nan,precision=inter/ap if ap else np.nan,recall=inter/ar if ar else np.nan,FN_mm2=float(w[ref&~pred].sum()),FP_mm2=float(w[pred&~ref].sum()),reference_area_mm2=ar,predicted_area_mm2=ap,reference_fraction=ar/area,predicted_fraction=ap/area,centroid_separation_mm=cent,intersection_mm2=inter,union_mm2=union,core_area_mm2=area)

def regional(y,p,w,mask):
    e=p-y;total_sse=float(w@(e*e));total_sae=float(w@abs(e));global_norm=float(w@(y*y));ww=w[mask];a=float(ww.sum())
    if not a:return dict(status='EMPTY_REGION',area_mm2=0.,area_fraction=0.,SSE_share=0.,SAE_share=0.)
    yy=y[mask];ee=e[mask];sse=float(ww@(ee*ee));sae=float(ww@abs(ee));norm=float(ww@(yy*yy));rms=float(np.sqrt(norm/a))
    return dict(status='VALID' if rms>1e-6 else 'UNSTABLE_REFERENCE_NORM',area_mm2=a,area_fraction=a/w.sum(),MAE_MPa=sae/a,RMSE_MPa=float(np.sqrt(sse/a)),bias_MPa=float(ww@ee/a),absolute_error_Q95_MPa=quantile(abs(ee),ww,.95),reference_mean_MPa=float(ww@yy/a),reference_Q95_MPa=quantile(yy,ww,.95),reference_RMS_MPa=rms,L2=float(np.sqrt(sse/norm)) if rms>1e-6 else np.nan,SSE_share=sse/total_sse if total_sse else np.nan,SAE_share=sae/total_sae if total_sae else np.nan,globally_normalized_SSE_contribution=sse/global_norm if global_norm else np.nan,SSE_MPa2_mm2=sse,SAE_MPa_mm2=sae)
