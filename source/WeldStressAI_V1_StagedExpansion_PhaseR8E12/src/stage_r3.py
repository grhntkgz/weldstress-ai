from common_r3 import *
def main(stage,level=None):
 protect();may_execute_source();path=GLOBAL/'21_reproducibility/STAGE_RUNTIME_LEDGER.json';ledger=read(path) if path.exists() else [];assert not any(a['source_id']==SID and a['stage']==stage and a.get('level')==level and a['status']=='COMPLETED' for a in ledger),'Do not repeat completed production stage';entry=dict(UTC=now(),source_id=SID,stage=stage,level=level,status='STARTED');ledger.append(entry);write(path,ledger);t=time.perf_counter()
 try:
  if stage=='solve':
   from solve_r2 import run
   run(level)
  elif stage=='recover_map_tensor':
   from recover_r2 import run
   run(level)
  elif stage=='t2':
   from t2_r2 import main
   main()
  else:raise ValueError(stage)
  entry.update(status='COMPLETED',elapsed_s=time.perf_counter()-t);write(path,ledger)
 except Exception as exc:
  entry.update(status='FAILED',elapsed_s=time.perf_counter()-t,error=repr(exc));write(path,ledger)
  # Only a genuine scientific gate failure is a final campaign stop. Host exceptions remain auditable.
  if stage=='solve' and (R/('06_native_M1' if level=='M1' else '07_native_M2')/'input.dat').exists():write(GLOBAL/'21_reproducibility/CAMPAIGN_STOP.json',dict(source_id=SID,UTC=now(),stage=stage,level=level,reason=repr(exc),actual_SOLVE_budget_consumed=True))
  raise
if __name__=='__main__':main(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else None)
