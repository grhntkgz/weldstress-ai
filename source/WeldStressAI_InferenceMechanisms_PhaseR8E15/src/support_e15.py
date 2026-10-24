from common_e15 import *
import numpy as np,pandas as pd

def main():
 # Read-only historical density evidence; no additional inference/configuration.
 old=pd.read_csv(J/'SEED_CONTEXT_METRICS.csv');ss=old[(old.model=='N1')&old.condition.isin(['FULL','D0'])].copy();table(R/'10_density_controls/HISTORICAL_D0_SCORE_EVIDENCE.csv',ss.to_dict('records'));out=[]
 for seed in sorted(ss.seed.unique()):
  full=ss[(ss.seed==seed)&(ss.condition=='FULL')].iloc[0];density=ss[(ss.seed==seed)&(ss.condition=='D0')].iloc[0]
  for metric in ['equal_plate_L2','equal_plate_MAE_MPa','equal_plate_high95_IoU']:
   out.append(dict(seed=int(seed),metric=metric,FULL=float(full[metric]),D0=float(density[metric]),D0_minus_FULL=float(density[metric]-full[metric]),source='immutable E14 SEED_CONTEXT_METRICS.csv',classification='partial nonuniform density control; full features retained'))
 table(R/'10_density_controls/D0_MINUS_FULL_METRICS.csv',out)
 # Original released implementation provenance, explicitly including the FULL single-view branch.
 paths=[H/'src/model_e3.py',H/'src/base_arch.py',J/'src/context_e14.py',J/'src/infer_e14.py',J/'src/prepare_contexts_e14.py',J/'src/geometry_e13.py',J/'src/spatial_profiles_e14.py'];table(R/'00_historical_integrity/ORIGINAL_IMPLEMENTATION_HASHES.csv',[dict(path=str(p),SHA256=sha(p),purpose='authoritative released inference/representation/diagnostic code') for p in paths]);print('SUPPORT_COMPLETE',flush=True)
if __name__=='__main__':main()
