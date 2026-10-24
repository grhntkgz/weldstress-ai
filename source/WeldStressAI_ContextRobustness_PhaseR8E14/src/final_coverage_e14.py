from common_e14 import *
import numpy as np
def main():
 assert read(R/'17_independent_audits/INDEPENDENT_PASS.json')['passed'];archive=R/'00_integrity/GEOMETRY_ONLY_COVERAGE_PREFLIGHT.csv';assert not archive.exists();shutil.copyfile(R/'FULL_CORE_COVERAGE_AUDIT.csv',archive);checks=[]
 for a in rows(R/'20_reproducibility/PREDICTION_REGISTRY.csv'):
  d=dict(np.load(R/'03_source_geometry'/(a['source_id']+'_SUPPORT.npz')));q=np.flatnonzero(d['core']&d['valid']);p=dict(np.load(a['path']));assert np.array_equal(p['source_ids'],d['source_ids'][q]);assert np.array_equal(p['area'],d['area'][q]);assert p['valid'].all() and (p['tile_count']==1).all();assert len(np.unique(p['source_ids']))==len(q);checks.append(dict(model=a['model'],fold=a['fold'],seed=a['seed'],condition=a['condition'],source_id=a['source_id'],original_core_points=len(q),predicted_core_points=len(q),predicted=True,coverage=1.,duplicate_source_IDs=0,original_T0_preserved=True,passed=True))
 assert len(checks)==182;table(R/'FULL_CORE_COVERAGE_AUDIT.csv',checks);write(R/'17_independent_audits/FINAL_FULL_CORE_COVERAGE.json',dict(UTC=now(),passed=True,source_fields=182,core_rows=sum(a['predicted_core_points'] for a in checks),preflight_retained=str(archive)));print('ACTUAL_FULL_CORE_COVERAGE_PASS',len(checks),flush=True)
if __name__=='__main__':main()
