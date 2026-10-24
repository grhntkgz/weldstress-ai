"""Attach explicit sidecars without overwriting any original prediction payload."""
from common_e13 import *
import numpy as np
def main():
 verify_seal();registry=rows(R/'PREDICTION_REGISTRY.csv');sources={a['source_id']:a for a in rows(R/'QUALIFIED13_SOURCE_REGISTRY.csv')};support={}
 for sid,rec in sources.items():
  d=dict(np.load(R/'01_dataset/targets'/(sid+'.npz')));p=R/'06_predictions'/('SOURCE_SUPPORT_'+sid+'.npz');np.savez(p,source_ids=d['source_ids'],xyz=d['xyz'],area=d['area'],original_core=d['core'],reference_valid=d['valid'],region=d['region']);support[sid]=p
 output=[]
 for a in registry:
  sid=a['source_id'];p=Path(a['path']);assert sha(p)==a['SHA256'];side=p.with_suffix('.provenance.json');record=dict(UTC=now(),prediction_path=str(p),prediction_SHA256=a['SHA256'],model=a['model'],seed=a['seed'],fold=a['fold'],canonical_source_id=sid,heldout_plate_id='ORIGINAL_S355MLO_PLATE_'+a['plate'],checkpoint_path=a['checkpoint'],checkpoint_SHA256=a['checkpoint_SHA256'],actual_reference_V1_path=sources[sid]['qualified_M2_target_path'],actual_reference_V1_SHA256=sources[sid]['qualified_M2_target_SHA256'],original_support_path=str(support[sid]),original_support_SHA256=sha(support[sid]),original_core_and_area_preserved=True,prediction_units='MPa',stitching='disjoint original source row tiles; count exactly 1',query_tile_size=512 if a['model']=='N1_POINT_TRANSFORMER' else 'pointwise closed-form',context_points=4096 if a['model']=='N1_POINT_TRANSFORMER' else None,metric_version=read(R/'METRIC_SPECIFICATION.json')['version'],recipe_SHA256=sha(R/'MODEL_AND_TRAINING_SEAL.json'),source_split_seal_SHA256=sha(R/'DATASET_AND_SPLIT_SEAL.json'));write(side,record);output.append(dict(**a,reference_SHA256=record['actual_reference_V1_SHA256'],support_path=str(support[sid]),support_SHA256=record['original_support_SHA256'],provenance_path=str(side),provenance_SHA256=sha(side)))
 table(R/'21_reproducibility/PREDICTION_PROVENANCE_REGISTRY.csv',output);print('EXPLICIT_PREDICTION_PROVENANCE_COMPLETE',len(output),flush=True)
if __name__=='__main__':main()
