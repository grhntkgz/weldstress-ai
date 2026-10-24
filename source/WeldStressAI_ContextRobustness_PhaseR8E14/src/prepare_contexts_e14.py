from common_e14 import *
import numpy as np
from scipy.spatial import cKDTree
from geometry_e13 import single_geometry
def cdf_unique(x,area,indices,count):
 order=indices[np.lexsort((x[indices,2],x[indices,1],x[indices,0]))];cdf=np.cumsum(area[order])/area[order].sum();ids=order[np.minimum(np.searchsorted(cdf,(np.arange(count)+.5)/count),len(order)-1)];chosen=list(dict.fromkeys(map(int,ids)))
 if len(chosen)<count:
  used=set(chosen)
  for i in order:
   if int(i) not in used:chosen.append(int(i));used.add(int(i))
   if len(chosen)==count:break
 assert len(chosen)==count and len(set(chosen))==count;return np.array(chosen,dtype='i8')
def main():
 verify_protocol();windows=[];audits=[];overlap=[];tiles=[];registry=[]
 for sid in [a['source_id'] for a in rows(R/'QUALIFIED13_SOURCE_REGISTRY.csv')]:
  gate();full=dict(np.load(H/'02_geometry'/(sid+'.npz')));support=dict(np.load(R/'03_source_geometry'/(sid+'_SUPPORT.npz')));x=full['xyz'];tri=full['triangles'];area=full['area'];core=support['core'];tileids=support['tile_id'];out=R/'07_context_geometry'/sid;out.mkdir(exist_ok=True);dout=R/'15_context_density_controls'/sid;dout.mkdir(exist_ok=True)
  # Exact full-view feature reconstruction gates the intervention implementation.
  recomputed=single_geometry(x,tri,full['source_ids'])
  for name in ['features','area','normal','context','neighbors','neighbors_1mm','neighbors_3mm']:assert np.array_equal(recomputed[name],full[name]),(sid,name)
  registry.append(dict(source_id=sid,condition='FULL',feasible=True,core_points=int(core.sum()),visible_original_points=len(x),hidden_features=False))
  for tile in np.unique(tileids[core]):
   q=np.flatnonzero(core&(tileids==tile));center=(x[q,0].min()+x[q,0].max())/2
   tiles.append(dict(source_id=sid,tile=int(tile),query_points=len(q),X_center_mm=float(center),query_X_min=float(x[q,0].min()),query_X_max=float(x[q,0].max()),query_ID_SHA256=hashlib.sha256(full['source_ids'][q].tobytes()).hexdigest()))
   for condition,width in [('X50',50.),('X43',43.)]:
    lower=max(x[:,0].min(),center-width/2);upper=min(x[:,0].max(),center+width/2);visible=(x[:,0]>=lower-1e-8)&(x[:,0]<=upper+1e-8);ids=np.flatnonzero(visible);assert visible[q].all();inv=np.full(len(x),-1,dtype='i8');inv[ids]=np.arange(len(ids));localtri=inv[tri[np.all(visible[tri],axis=1)]];g=single_geometry(x[ids],localtri,full['source_ids'][ids]);assert len(np.unique(g['source_ids'][g['context']]))==4096
    path=out/(condition+'_'+str(int(tile))+'.npz');np.savez(path,**g);np.save(out/(condition+'_'+str(int(tile))+'_IDS.npy'),g['source_ids']);np.save(out/(condition+'_'+str(int(tile))+'_CONTEXT_IDS.npy'),g['source_ids'][g['context']]);localq=np.searchsorted(g['source_ids'],full['source_ids'][q]);assert np.array_equal(g['source_ids'][localq],full['source_ids'][q]);assert np.max(abs(g['xyz'][localq]-x[q]))==0
    # No cropped boundary can cut the required query neighborhood: record exact observed query-to-edge margin.
    margin=np.minimum(x[q,0]-g['xyz'][:,0].min(),g['xyz'][:,0].max()-x[q,0]);assert margin.min()>3
    ctx=g['xyz'][g['context']];nn=cKDTree(ctx).query(ctx,k=2)[0][:,1];qx=cKDTree(ctx).query(x[q])[0];actual=float(np.ptp(g['xyz'][:,0]));yspan=float(np.ptp(g['xyz'][:,1]));warea=float(g['area'].sum());featdelta=g['features'][localq].astype('f8')-full['features'][q];a=dict(source_id=sid,condition=condition,tile=int(tile),nominal_X_mm=width,declared_X_min=float(lower),declared_X_max=float(upper),actual_X_min=float(g['xyz'][:,0].min()),actual_X_max=float(g['xyz'][:,0].max()),actual_X_mm=actual,actual_Y_mm=yspan,visible_points=len(ids),context_points=4096,context_unique=4096,observed_area_mm2=warea,context_density_per_mm2=4096/warea,source_density_per_mm2=len(ids)/warea,context_NN_Q05_mm=float(np.quantile(nn,.05)),context_NN_median_mm=float(np.median(nn)),context_NN_Q95_mm=float(np.quantile(nn,.95)),query_context_NN_P95_mm=float(np.quantile(qx,.95)),query_X_boundary_min_mm=float(margin.min()),truncation_ratio=1-actual/width,full_context_overlap=int(len(set(g['source_ids'][g['context']])&set(full['source_ids'][full['context']]))),feature_query_RMS_change=float(np.sqrt(np.mean(featdelta**2))),coverage=1.,geometry_path=str(path),geometry_SHA256=sha(path),original_T0_unchanged=True,hidden_features=False)
    windows.append(a);audits.append(a);overlap.append(dict(source_id=sid,condition=condition,tile=int(tile),shared_with_FULL=a['full_context_overlap'],fraction_of_4096=a['full_context_overlap']/4096))
    if condition=='X43':
     ctxinside=cdf_unique(x,area,ids,4080);ctxoutside=cdf_unique(x,area,np.flatnonzero(~visible),16);density=np.r_[ctxinside,ctxoutside];assert len(set(density))==4096;np.save(dout/(str(int(tile))+'.npy'),density)
     for cname,cids in [('D0',density),('FULL',full['context'])]:
      dnn=cKDTree(x[cids]).query(x[cids],k=2)[0][:,1];da=dict(a);da.update(condition=cname,visible_points=len(x),nominal_X_mm=float(np.ptp(x[:,0])),declared_X_min=float(x[:,0].min()),declared_X_max=float(x[:,0].max()),actual_X_min=float(x[:,0].min()),actual_X_max=float(x[:,0].max()),actual_X_mm=float(np.ptp(x[:,0])),observed_area_mm2=float(area.sum()),context_density_per_mm2=4096/float(area.sum()),source_density_per_mm2=len(x)/float(area.sum()),context_NN_Q05_mm=float(np.quantile(dnn,.05)),context_NN_median_mm=float(np.median(dnn)),context_NN_Q95_mm=float(np.quantile(dnn,.95)),query_context_NN_P95_mm=float(np.quantile(cKDTree(x[cids]).query(x[q])[0],.95)),query_X_boundary_min_mm=float(np.minimum(x[q,0]-x[:,0].min(),x[:,0].max()-x[q,0]).min()),truncation_ratio=0.,feature_query_RMS_change=0.,full_context_overlap=len(set(cids)&set(full['context'])),geometry_path=str(H/'02_geometry'/(sid+'.npz')),geometry_SHA256=sha(H/'02_geometry'/(sid+'.npz')));audits.append(da)
   print('VISIBLE_CONTEXTS_PREPARED',sid,int(tile),flush=True)
  for condition in ['X50','X43','D0']:registry.append(dict(source_id=sid,condition=condition,feasible=True,core_points=int(core.sum()),visible_original_points='window-specific' if condition!='D0' else len(x),hidden_features=False))
 table(R/'OBSERVATION_WINDOW_COORDINATES.csv',windows);table(R/'OBSERVATION_CONTEXT_DENSITY.csv',audits);table(R/'CONTEXT_POINT_OVERLAP.csv',overlap);table(R/'INFERENCE_TILE_REGISTRY.csv',tiles);table(R/'OBSERVATION_CONDITION_REGISTRY.csv',registry)
 def idrows(context_only=False):
  for a in windows:
   sid=a['source_id'];p=R/'07_context_geometry'/sid/(a['condition']+'_'+str(a['tile'])+('_CONTEXT_IDS.npy' if context_only else '_IDS.npy'))
   for ident in np.load(p):yield dict(source_id=sid,condition=a['condition'],tile=a['tile'],source_point_id=int(ident),role='selected_context' if context_only else 'visible_candidate')
 table(R/'OBSERVATION_SOURCE_POINT_IDS.csv',idrows());table(R/'06_observation_protocol/SELECTED_CONTEXT_POINT_IDS.csv',idrows(True));table(R/'CONTEXT_DENSITY_CONTROL.csv',[a for a in audits if a['condition']=='D0']);table(R/'FULL_CORE_COVERAGE_AUDIT.csv',[dict(source_id=a['source_id'],condition=a['condition'],core_points=a['core_points'],predicted=False,geometry_coverage=1.,feasible=True) for a in registry])
 write(R/'00_integrity/G2_G3_G4_CONTEXT_PASS.json',dict(UTC=now(),passed=True,sources=13,conditions=4,cropped_windows=len(windows),full_core_retained=True,feature_reconstruction_full_exact=True,density_control='FEASIBLE_NONUNIFORM_PARTIAL_MATCH',N2_recipe_sealed_before_context_generation=True))
if __name__=='__main__':main()
