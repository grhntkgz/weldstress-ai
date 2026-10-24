from common_e14 import *
def main():
 assert read(R/'17_independent_audits/INDEPENDENT_PASS.json')['passed'];bound=rows(R/'00_integrity/HISTORICAL_RELEASE_HASHES.csv');checks=[];start=time.monotonic()
 for i,a in enumerate(bound):
  p=Path(a['path']);actual=sha(p);assert actual==a['SHA256'];s=p.stat();checks.append(dict(path=str(p),expected_SHA256=a['SHA256'],actual_SHA256=actual,bytes=s.st_size,mtime_ns=s.st_mtime_ns,passed=True))
  if i%200==0:gate();print('POST_EXECUTION_HISTORY_HASH',i,len(bound),flush=True)
 table(R/'20_reproducibility/FINAL_HISTORICAL_HASHES.csv',checks);write(R/'20_reproducibility/FINAL_HISTORICAL_AUDIT.json',dict(UTC=now(),passed=True,artifacts=len(checks),elapsed_s=time.monotonic()-start,after_all_training_and_independent_metric_checks=True,ledger_SHA256=sha(R/'20_reproducibility/FINAL_HISTORICAL_HASHES.csv')));print('FINAL_HISTORICAL_AUDIT_PASS',len(checks),flush=True)
if __name__=='__main__':main()
