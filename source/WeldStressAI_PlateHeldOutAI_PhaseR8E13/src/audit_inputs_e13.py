from common_e13 import *
import numpy as np
def main():
 reg=rows(R/'QUALIFIED13_SOURCE_REGISTRY.csv');groups=rows(E12/'CONFIRMED_PARENT_PLATE_GROUPS.csv');bound=[]
 for a in reg:
  sid=a['source_id'];matches=[g for g in groups if sid in g['members'].split(';')];assert len(matches)==1 and matches[0]['group_id']==a['confirmed_parent_plate'];assert a['target_version']=='T2_STANDARD_PLANAR_REAR_V1__LE210000_NU030__NOM100_TW_XMID__FRONT_HUBER_NORMALOFFSET__CORE11_3__V231_QT10_2M__PBA_CHORD1_T0';assert float(a['mapping_coverage'])>=.99 and float(a['T2_L2'])<=.02 and float(a['T2_worst_regional_L2'])<=.03 and float(a['T2_high95_IoU'])>=.8
  case=Path(a['qualified_M2_target_path']).parent
  # Discover only within the registered release/case; no target replacement or regeneration.
  release=Path(a['release_workspace']);c=release/'cases'/sid
  if not c.exists():c=release
  expected=json.loads(a['native_solution_hashes'])
  for level,folder in [('M1','06_native_M1'),('M2','07_native_M2')]:
   for name,key in [('MODEL.db','DB_SHA256'),('file.rst','RST_SHA256')]:
    p=c/folder/name;assert p.exists(),str(p);h=sha(p);assert h==expected[level][key],str(p);bound.append(dict(source_id=sid,kind=level+'_'+key,path=str(p),sha256=h,passed=True))
  d=dict(np.load(R/'01_dataset/targets'/(sid+'.npz')));assert np.all(d['valid'][d['core']]);assert np.array_equal(d['source_ids'],np.arange(len(d['xyz'])))
 for a in rows(E12/'01_provenance/PROVENANCE_INPUT_HASHES.csv'):assert sha(a['path'])==a['sha256']
 table(R/'00_integrity/NATIVE_PROVENANCE_HASHES.csv',bound);write(R/'00_integrity/INPUT_AUDIT_COMPLETE.json',dict(UTC=now(),passed=True,documentary_groups_verified=5,qualified_targets=13,native_hashes=len(bound),reference_units='MPa',all_original_core_valid=True))
 print('INPUT_AUDIT_COMPLETE',len(bound),flush=True)
if __name__=='__main__':main()
