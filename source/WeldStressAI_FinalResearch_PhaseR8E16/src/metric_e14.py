import numpy as np,math
def quantile(v,w,q=.95):
 i=np.argsort(v,kind='stable');return float(np.interp(q,np.cumsum(w[i])/w.sum(),v[i]))

def metric(y,p,w,xyz):
 e=p-y;s=w.sum();sse=float(w@(e*e));den=float(w@(y*y));ym=float(w@y/s);sst=float(w@((y-ym)**2));qy=quantile(y,w);qp=quantile(p,w);hy=y>=qy;hp=p>=qp;inter=float(w[hy&hp].sum());union=float(w[hy|hp].sum());cy=np.sum(xyz[hy]*w[hy,None],0)/w[hy].sum();cp=np.sum(xyz[hp]*w[hp,None],0)/w[hp].sum()
 return dict(MAE_MPa=float(w@abs(e)/s),RMSE_MPa=math.sqrt(sse/s),bias_MPa=float(w@e/s),L2=math.sqrt(sse/den),R2=1-sse/sst if sst>1e-12*s else None,pred_mean_MPa=float(w@p/s),ref_mean_MPa=ym,pred_max_MPa=float(p.max()),ref_max_MPa=float(y.max()),max_ratio_error=float(p.max()/y.max()-1),Q95_error_MPa=qp-qy,ref_Q95_MPa=qy,pred_Q95_MPa=qp,high95_IoU=inter/union,high95_precision=inter/float(w[hp].sum()),high95_recall=inter/float(w[hy].sum()),high95_centroid_distance_mm=float(np.linalg.norm(cy-cp)),area_mm2=float(s),SSE=sse,ref_square_sum=den)
