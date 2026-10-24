from common_r3 import *
def main():
 protect();may_execute_source();sealed=read(GLOBAL/'PREREGISTRATION_SEAL.json')
 for a in sealed['files']:assert sha(GLOBAL/a['path'])==a['sha256']
 for path,digest in read(GLOBAL/'SOURCE_HASHES.json')[SID].items():assert sha(path)==digest
 import geometry_e10
 start=time.perf_counter();q=geometry_e10.run(SID)
 if not q['passed']:
  write(GLOBAL/'21_reproducibility/CAMPAIGN_STOP.json',dict(UTC=now(),source_id=SID,stage='CAD_FIDELITY',reason='Source-preserving unchanged historical front BRep failed frozenCADgates; no stressresults or sourcechanges authorized as rescue',evidence=str(R/'04_standardized_solids'/SID/'CAD_QUALIFICATION.json')));return
 for name in ['standardized_planar_rear.step','solid_source.npz']:shutil.copy2(R/'04_standardized_solids'/SID/name,R/'01_frozen_protocol/geometry'/name)
 d=R/'03_parent_datum'/(SID+'.json');shutil.copy2(d,R/'01_frozen_protocol/PARENT_DATUM.json');shutil.copy2(d,R/'01_protocol_freeze/R1_frozen/PARENT_DATUM.json')
 for name in ['xyz.npy','area.npy','triangles.npy','normal.npy','source_ids.npy']:
  for sub in ['01_frozen_protocol/source','01_protocol_freeze/R1_frozen/source']:shutil.copy2(R/'02_source_geometry'/SID/name,R/sub/name)
 write(R/'00_integrity/INITIALIZATION.json',dict(UTC=now(),STEP_SHA256=sha(R/'01_frozen_protocol/geometry/standardized_planar_rear.step')))
 GP=np.full((4,4),(5-np.sqrt(5))/20);np.fill_diagonal(GP,(5+3*np.sqrt(5))/20);samples=np.vstack([np.eye(4),GP,np.full((1,4),.25),np.random.default_rng(20261020).dirichlet(np.ones(4),64)]);(R/'00_integrity/baseline').mkdir(exist_ok=True);np.savez_compressed(R/'00_integrity/baseline/QUADRATIC_GEOMETRY_AUDIT.npz',Jacobian_samples=samples)
 write(R/'04_standardized_solids'/SID/'R3_GEOMETRY_RUNTIME.json',dict(UTC=now(),source_id=SID,elapsed_including_fidelity_s=time.perf_counter()-start,source_arrays_unchanged=True,new_CAD_candidates=1))
 print('SOURCE_STANDARDIZED_GEOMETRY_QUALIFIED',SID,flush=True)
if __name__=='__main__':main()
