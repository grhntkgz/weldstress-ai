from common_e16 import *
import numpy as np
from features_e16 import view,core

def main():
 verify_protocol();checks=[];gchecks=[];hashes={};top=rows(R/'01_frozen_dataset/ORIGINAL_TILE_TOPOLOGY.csv')
 for rr in rows(R/'01_frozen_dataset/GEOMETRY_REGISTRY.csv'):
  sid=rr['source_id'];full=dict(np.load(rr['geometry_path']));q=core(sid)
  for c in ['X50','X43']:
   for tile in range(5):
    path=J/'07_context_geometry'/sid/(c+'_'+str(tile)+'.npz');g=dict(np.load(path));tri=g['triangles'];x=g['xyz'];cr=np.cross(x[tri[:,1]]-x[tri[:,0]],x[tri[:,2]]-x[tri[:,0]]);area=np.zeros(len(x));normal=np.zeros_like(x)
    for j in range(3):np.add.at(area,tri[:,j],np.linalg.norm(cr,axis=1)/6);np.add.at(normal,tri[:,j],cr/2)
    normal/=np.linalg.norm(normal,axis=1)[:,None];assert np.allclose(area,g['area'],rtol=1e-12,atol=1e-12);assert np.allclose(normal,g['normal'],rtol=1e-12,atol=1e-12);idx=np.searchsorted(full['source_ids'],g['source_ids']);assert np.array_equal(full['xyz'][idx],g['xyz']);gchecks.append(dict(source_id=sid,condition=c,tile=tile,visible_triangle_area_reconstructed=True,visible_triangle_normal_reconstructed=True,maximum_area_error=float(abs(area-g['area']).max()),maximum_normal_error=float(abs(normal-g['normal']).max()),passed=True))
    for cell in ['F000','F100','F010','F001','F110','F101','F011','F111']:
     f=g['features'].copy();cols=[k for bit,block in zip(cell[1:],[[0,1,2],[6,7,8,18],[16,17]]) if bit=='1' for k in block];f[:,cols]=full['features'][idx][:,cols];hashes[sid,c,tile,cell]=hashlib.sha256(f.tobytes()).hexdigest()
 for path in sorted((R/'05_blockwise_interventions').glob('*_RUNTIME.csv')):
  sourcecache={};seen={};ends={};ckhashes={(a['model'],a['fold'],a['seed']):a['actual_SHA256'] for a in rows(R/'HISTORICAL_MODEL_HASHES.csv')}
  for a in rows(path):
   sid=a['source_id'];c=a['condition'];tile=int(a['tile']);key=(sid,c,tile);assert a['checkpoint_SHA256']==ckhashes[a['model'],a['fold'],a['seed']]
   if key not in sourcecache:
    g=dict(np.load(a['visible_geometry_path']));sourcecache[key]=(g['source_ids'][g['context']],g['source_ids']);
   ctx,visible=sourcecache[key];assert a['feature_SHA256']==hashes[sid,c,tile,a['cell']];assert a['context_ID_SHA256']==hashlib.sha256(ctx.tobytes()).hexdigest();s=core(sid);ii=np.flatnonzero(s['tile_id']==tile);i=int(a['query_start']);n=int(a['query_count']);coveragekey=(a['field'],tile);assert i==ends.get(coveragekey,0);ends[coveragekey]=i+n;ids=s['source_ids'][ii[i:i+n]];assert len(ids)==n;assert a['query_ID_SHA256']==hashlib.sha256(ids.tobytes()).hexdigest();assert np.isin(ids,visible).all();assert a['grad_enabled']=='False';seen[a['field']]=seen.get(a['field'],0)+n
  assert all(v==34200 for v in seen.values());checks.append(dict(scope='factorial',run=path.stem,fields=len(seen),query_rows=sum(seen.values()),all_batch_query_context_feature_hashes=True,coverage=1.,passed=True));print('FACTORIAL_RUNTIME_AUDIT',path.stem,flush=True)
 for path in sorted((R/'13_full_core_predictions').glob('*_RUNTIME.csv')):
  fh={};seen={};ends={};checkpoint_hash=read(R/'11_N3_training'/path.stem.removesuffix('_RUNTIME')/'COMPLETED.json')['checkpoint_SHA256']
  for a in rows(path):
   sid=a['source_id'];c=a['condition'];tile=int(a['tile']);key=(sid,c,tile);g=view(sid,c,tile);assert a['checkpoint_SHA256']==checkpoint_hash
   if key not in fh:fh[key]=hashlib.sha256(g['features'].tobytes()).hexdigest()
   assert a['feature_SHA256']==fh[key];assert a['context_ID_SHA256']==hashlib.sha256(g['source_ids'][g['context']].tobytes()).hexdigest();s=core(sid);ii=np.flatnonzero(s['tile_id']==tile);i=int(a['query_start']);n=int(a['query_count']);coveragekey=(sid,c,tile);assert i==ends.get(coveragekey,0);ends[coveragekey]=i+n;ids=s['source_ids'][ii[i:i+n]];assert len(ids)==n;assert a['query_ID_SHA256']==hashlib.sha256(ids.tobytes()).hexdigest();assert a['grad_enabled']=='False';key=(sid,c);seen[key]=seen.get(key,0)+n
  assert all(v==34200 for v in seen.values());checks.append(dict(scope='N3 inference',run=path.stem,fields=len(seen),query_rows=sum(seen.values()),all_batch_query_context_feature_hashes=True,coverage=1.,passed=True));print('N3_RUNTIME_AUDIT',path.stem,flush=True)
 table(R/'18_independent_verification/VISIBLE_TRIANGLE_RECONSTRUCTION.csv',gchecks);table(R/'18_independent_verification/INFERENCE_RUNTIME_AUDIT.csv',checks);assert len(checks)==30;write(R/'18_independent_verification/RUNTIME_PASS.json',dict(UTC=now(),passed=True,workers=len(checks),visible_geometry_reconstructions=len(gchecks),query_rows=sum(a['query_rows'] for a in checks),feature_interventions_correct=True))
if __name__=='__main__':main()
