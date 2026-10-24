from common_e13 import *
import numpy as np
def main():
 verify_seal();folds=rows(R/'OUTER_LOPO_FOLDS.csv');receipts=[]
 for fold in ['F1','F2','F3','F4','F5']:
  rr=[a for a in folds if a['fold']==fold];tr=[a['source_id'] for a in rr if a['role']=='train'];te=[a['source_id'] for a in rr if a['role']=='heldout'];X=[];Y=[];W=[]
  for sid in tr:
   g=dict(np.load(R/'02_geometry'/(sid+'.npz')));d=dict(np.load(R/'01_dataset/targets'/(sid+'.npz')));m=d['core']&d['valid'];w=d['area'][m];w=w/w.sum()/(4*sum(s[0]==sid[0] for s in tr));X.append(g['features'][m].astype('f8'));Y.append(d['T2_MPa'][m]/100);W.append(w)
  x=np.concatenate(X);y=np.concatenate(Y);w=np.concatenate(W);assert abs(w.sum()-1)<1e-12;mean=np.sum(w[:,None]*x,axis=0);std=np.sqrt(np.sum(w[:,None]*(x-mean)**2,axis=0));std[std<1e-12]=1.;z=(x-mean)/std;ym=float(w@y);beta=np.linalg.solve(z.T@(w[:,None]*z)+np.eye(19),z.T@(w*(y-ym)))
  p=R/'04_baselines'/(fold+'.npz');np.savez(p,mean=mean,std=std,beta=beta,intercept=ym,alpha=1.)
  for sid in te:
   g=dict(np.load(R/'02_geometry'/(sid+'.npz')));n=len(g['features'])
   for model,pred in [('B0_CONSTANT',np.full(n,ym*100)),('B1_GEOMETRY_RIDGE',100*(ym+((g['features']-mean)/std)@beta))]:
    out=R/'06_predictions'/(model+'_'+fold+'_'+sid+'.npz');np.savez(out,source_ids=g['source_ids'],xyz=g['xyz'],area=g['area'],pred_MPa=pred,valid=np.ones(n,dtype=bool),tile_count=np.ones(n,dtype='i4'))
    receipts.append(dict(model=model,fold=fold,seed='NA',source_id=sid,plate=sid[0],path=str(out),SHA256=sha(out),checkpoint=str(p),checkpoint_SHA256=sha(p)))
  write(R/'04_baselines'/(fold+'_FIT.json'),dict(UTC=now(),train_sources=tr,heldout_sources=te,training_point_count=len(y),train_plates=sorted({s[0] for s in tr}),constant_K=ym,alpha=1,scaler_SHA256=sha(p),weighted_training_mean_only=True,heldout_target_access=False))
  print('BASELINES_COMPLETE',fold,flush=True)
 table(R/'04_baselines/PREDICTION_REGISTRY.csv',receipts)
if __name__=='__main__':main()
