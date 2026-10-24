from common_r1 import *
def main():
 protect();assert read(R/'14_reproducibility/RELEASE_PREFLIGHT.json')['passed'];exclude=['REPRODUCIBILITY_MANIFEST.json','REPRODUCIBILITY_MANIFEST.csv','14_reproducibility/RELEASE_SEAL.json','14_reproducibility/INDEPENDENT_RELEASE_VERIFICATION.json'];items=[]
 for f in sorted(R.rglob('*')):
  if not f.is_file():continue
  rel=f.relative_to(R).as_posix()
  if rel in exclude or rel.startswith('tmp/'):continue
  items.append(dict(path=rel,bytes=f.stat().st_size,sha256=sha(f)))
 write(R/'REPRODUCIBILITY_MANIFEST.json',dict(UTC=now(),source_id=SID,protocol_version=VERSION,status='R8E10R1_MESH_RECOVERY_COMPLETE',scope='All durable R1files except explicit self/seal/verifier exclusions and temp cache',excluded=exclude+['tmp/**'],files=items,source_code_hashes=[z for z in items if z['path'].startswith('src/')],mesh_pair_release_SHA256=sha(R/'MESH_PAIR_RELEASE.json'),original_failed_mesh_SHA256=sha(R/'00_integrity/baseline/mesh.npz'),native_SOLVEs=0,AI_runs=0,V1_stress_targets=0))
 # Plain manifest CSV is intentionally not a scientific specimen record.
 with (R/'REPRODUCIBILITY_MANIFEST.csv').open('w',encoding='utf8',newline='') as f:w=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);w.writeheader();w.writerows(items)
 write(R/'14_reproducibility/RELEASE_SEAL.json',dict(UTC=now(),manifest_SHA256=sha(R/'REPRODUCIBILITY_MANIFEST.json'),CSV_SHA256=sha(R/'REPRODUCIBILITY_MANIFEST.csv'),durable_artifacts=len(items),status='MESH_PAIR_PRE_SOLVER_QUALIFIED;NO_NATIVE_EXECUTION'))
 print('R1_SEALED_ARTIFACTS',len(items),flush=True)
if __name__=='__main__':main()
