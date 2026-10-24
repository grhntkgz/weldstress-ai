from common_e15 import *
import numpy as np

def table(p,data,fields=None):
 # Large sequential buffers avoid thousands of small synchronous external-drive writes.
 p=Path(p);assert p.is_relative_to(R);p.parent.mkdir(parents=True,exist_ok=True);iterator=iter(data);first=next(iterator,None)
 with p.open('w',encoding='utf8',newline='',buffering=8*1024**2) as f:
  writer=csv.DictWriter(f,fieldnames=fields or (list(first) if first else ['status']));writer.writeheader()
  if first is not None:writer.writerow(first);writer.writerows(iterator)

def main():
 assert read(R/'21_reproducibility/EVALUATION_COMPLETE.json')['passed'];gate();registry=rows(R/'21_reproducibility/REPLAY_REGISTRY.csv')+rows(R/'21_reproducibility/INTERVENTION_REGISTRY.csv');counts={}
 def rawrows(overlap=False):
  count=0
  for a in registry:
   if (a['variant']=='OVERLAP')!=overlap:continue
   g=dict(np.load(a['path']));ck=a['model']+'_'+a['fold']+'_s'+a['seed']
   for i in range(len(g['source_ids'])):
    count+=1;yield dict(source_id=a['source_id'],source_point_id=int(g['source_ids'][i]),checkpoint_id=ck,condition=a['condition'],variant=a['variant'],tile_id=int(g['tile_id'][i]),prediction_MPa=float(g['pred_MPa'][i]))
  counts['RAW_OVERLAP_PREDICTIONS.csv' if overlap else 'RAW_CONTEXT_PREDICTIONS.csv']=count
 for overlap in [False,True]:
  filename='RAW_OVERLAP_PREDICTIONS.csv' if overlap else 'RAW_CONTEXT_PREDICTIONS.csv';table(R/filename,rawrows(overlap));print('EXPORTED',filename,counts[filename],flush=True);gate()
 def weightrows():
  count=0
  for a in registry:
   if a['variant']!='OVERLAP':continue
   for policy in ['S1','S2']:
    p=R/'13_stitching_interventions'/(Path(a['path']).stem+'_'+policy+'_WEIGHTS.npz');d=dict(np.load(p));ck=a['model']+'_'+a['fold']+'_s'+a['seed']
    for i in range(len(d['weight'])):count+=1;yield dict(source_id=a['source_id'],source_point_id=int(d['source_ids'][i]),checkpoint_id=ck,condition=a['condition'],policy=policy,tile_id=int(d['tile_id'][i]),weight=float(d['weight'][i]))
  counts['STITCHING_WEIGHTS.csv']=count
 table(R/'STITCHING_WEIGHTS.csv',weightrows());print('EXPORTED_WEIGHTS',counts['STITCHING_WEIGHTS.csv'],flush=True);gate()
 def stitched():
  count=0
  for a in rows(R/'SOURCE_LEVEL_FIELD_METRICS.csv'):
   if a['policy'] not in ['S0','S1','S2']:continue
   p=dict(np.load(a['path']));ck=a['model']+'_'+a['fold']+'_s'+a['seed']
   for i in range(len(p['source_ids'])):count+=1;yield dict(source_id=a['source_id'],source_point_id=int(p['source_ids'][i]),checkpoint_id=ck,condition=a['condition'],policy=a['policy'],prediction_MPa=float(p['pred_MPa'][i]))
  counts['STITCHED_SOURCE_PREDICTIONS.csv']=count
 table(R/'STITCHED_SOURCE_PREDICTIONS.csv',stitched());print('EXPORTED_STITCHED',counts['STITCHED_SOURCE_PREDICTIONS.csv'],flush=True);gate()
 def adjacent(labels=False):
  count=0
  for sr in rows(R/'SOURCE_CORE_REGISTRY.csv'):
   sid=sr['source_id'];d=dict(np.load(R/'02_source_geometry'/sid/'ADJACENCY.npz'));core=dict(np.load(R/'02_source_geometry'/sid/'CORE.npz'));cross=d['tile_id'][d['pairs'][:,0]]!=d['tile_id'][d['pairs'][:,1]]
   for i,pair in enumerate(d['pairs']):
    count+=1
    if labels:yield dict(source_id=sid,source_point_id_i=int(d['source_ids'][i,0]),source_point_id_j=int(d['source_ids'][i,1]),X50_X43_pair_class='CROSS_TILE_BOUNDARY' if cross[i] else 'WITHIN_SAME_TILE',FULL_pair_class='WITHIN_SAME_TILE',primary_horizontal=bool(d['x_axis_edge'][i]))
    else:yield dict(source_id=sid,source_point_id_i=int(d['source_ids'][i,0]),source_point_id_j=int(d['source_ids'][i,1]),physical_distance_mm=float(d['distance_mm'][i]),canonical_T0_triangle_edge=True,primary_horizontal=bool(d['x_axis_edge'][i]))
  counts['TILE_BOUNDARY_PAIR_LABELS.csv' if labels else 'ADJACENT_SOURCE_PAIRS.csv']=count
 table(R/'ADJACENT_SOURCE_PAIRS.csv',adjacent());table(R/'TILE_BOUNDARY_PAIR_LABELS.csv',adjacent(True))
 def matchedrows():
  count=0
  for sr in rows(R/'SOURCE_CORE_REGISTRY.csv'):
   sid=sr['source_id'];d=dict(np.load(R/'02_source_geometry'/sid/'CORE.npz'))
   for condition in ['FULL','X50','X43']:
    for i,ident in enumerate(d['source_ids']):count+=1;yield dict(source_id=sid,source_point_id=int(ident),condition=condition,tile_A=0 if condition=='FULL' else int(d['tile_id'][i]),tile_B=0 if condition=='FULL' else int(d['tile_id'][i]),shift_X_mm=0 if condition=='FULL' else 2.,contrast='FULL_CDF_PHASE_SAMPLING_ONLY' if condition=='FULL' else 'SHIFTED_VISIBLE_WINDOW',same_physical_XYZ=True,valid=True)
  counts['MATCHED_POINT_CONTEXT_PAIRS.csv']=count
 table(R/'MATCHED_POINT_CONTEXT_PAIRS.csv',matchedrows())
 overlaps=[]
 for sr in rows(R/'SOURCE_CORE_REGISTRY.csv'):
  sid=sr['source_id'];full=dict(np.load(H/'02_geometry'/(sid+'.npz')))
  for tile in range(5):
   for condition in ['X50','X43']:
    old=dict(np.load(J/'07_context_geometry'/sid/(condition+'_'+str(tile)+'.npz')));new=dict(np.load(R/'02_source_geometry'/sid/(condition+'_SHIFT_'+str(tile)+'.npz')));ca=set(old['source_ids'][old['context']]);cb=set(new['source_ids'][new['context']]);overlaps.append(dict(source_id=sid,plate=sid[0],tile=tile,condition=condition,context_A_points=len(ca),context_B_points=len(cb),shared_context_IDs=len(ca&cb),context_Jaccard=len(ca&cb)/len(ca|cb),original_visible_points=len(old['xyz']),shifted_visible_points=len(new['xyz']),actual_A_X_min_mm=float(old['xyz'][:,0].min()),actual_A_X_max_mm=float(old['xyz'][:,0].max()),actual_B_X_min_mm=float(new['xyz'][:,0].min()),actual_B_X_max_mm=float(new['xyz'][:,0].max())))
 table(R/'07_same_point_contexts/CONTEXT_POINT_OVERLAP.csv',overlaps);write(R/'21_reproducibility/CSV_EXPORT_COUNTS.json',counts);print('EXPORT_COMPLETE',sum(counts.values()),flush=True)
if __name__=='__main__':main()
