from setup_e11r1 import *
import itertools,math
def audit_lineage():
 q=read(B/'WeldStressAI_SingleSurface_Transfer_PhaseR8E3/00_protocol/QUARANTINE.json');prov=rows(R/'SOURCE_PROVENANCE_REGISTRY.csv');lookup={a['source_id']:a for a in prov};assert len(prov)==59 and set(lookup)==set(q['development_IDs']+q['historical_test_IDs'])
 assert len({a['confirmed_parent_plate'] for a in prov})==5
 for a in prov:
  assert a['confirmed_parent_plate']=='ORIGINAL_S355MLO_PLATE_'+a['source_id'][0];assert a['physical_status']=='PHYSICAL_DEPENDENCE_CONFIRMED' and a['between_plate_independence']=='PHYSICAL_INDEPENDENCE_UNRESOLVED';assert a['manufacturing_batch']==a['scan_session']=='UNKNOWN';assert a['target_values_opened']==a['AI_performance_opened']=='False'
 graph=read(R/'PHYSICAL_DEPENDENCY_GRAPH.json');ids={a['id'] for a in graph['nodes']};assert all(a['source_entity'] in ids and a['target_entity'] in ids for a in graph['edges'])
 for a in graph['edges']:
  assert a['evidence_file'] and a['evidence_field'] and a['audit_timestamp']
  if a['relationship_type']=='CONFIRMED_SAME_PARENT_PLATE':assert a['verified'] and a['mandatory_grouping'] and a['classification']=='CONFIRMED_SAME_PARENT_PLATE'
 pairs=rows(R/'GEOMETRY_PAIRWISE_SCREEN.csv');assert len(pairs)==1081;expected={tuple(v) for v in itertools.combinations(sorted(q['development_IDs']),2)};assert {(a['source_a'],a['source_b']) for a in pairs}==expected
 for a in pairs:
  flag=float(a['RMS_mm'])<=.005 and float(a['P95_mm'])<=.01 and float(a['correlation'])>=.999
  assert (a['screen_flag']=='POSSIBLE_DEPENDENCY_FLAG')==flag and a['confirmed_common_origin_from_geometry']=='False'
 if (R/'FUTURE_GROUPED_SPLIT_FEASIBILITY.csv').exists():
  for a in rows(R/'FUTURE_GROUPED_SPLIT_FEASIBILITY.csv'):
   train=set(a['training_sources'].split(';'));held=set(a['heldout_sources'].split(';'));assert not train&held;assert not {lookup[s]['confirmed_parent_plate'] for s in train}&{lookup[s]['confirmed_parent_plate'] for s in held};assert not (train|held)&set(q['historical_test_IDs']);assert a['actual_training']==a['actual_validation']=='False'
 return dict(status='PASS',sources=59,development47=47,historical_test_provenance12=12,documentary_parent_plate_groups=5,cross_batch_independence=False,geometry_pairs=1081,actual_AI_training=0)
if __name__=='__main__':print(audit_lineage())
