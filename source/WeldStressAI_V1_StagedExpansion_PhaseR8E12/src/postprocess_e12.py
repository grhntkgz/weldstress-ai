"""Sequential administrative closeout; never invokes CAD, meshing, native ANSYS or AI."""
from setup_e11r1 import *
import subprocess,os,time,psutil
PY=B/'WeldScan_MechanicalBenchmark_Phase5E/.venv/Scripts/python.exe'
def main():
 assert (R/'21_reproducibility/PRODUCTION_COMPLETED.json').exists() or (R/'21_reproducibility/CAMPAIGN_STOP.json').exists()
 assert not any((p.info['name'] or '').lower()=='ansys231.exe' for p in psutil.process_iter(['name']))
 ledgerpath=R/'26_closeout/POSTPROCESSING_LEDGER.json';ledger=read(ledgerpath) if ledgerpath.exists() else [];stages=[]
 for a in rows(R/'FROZEN_SELECTED_FIVE_SOURCES.csv'):
  if (R/'cases'/a['source_id']/'14_reproducibility/FULL_CANDIDATE_LEDGER.json').exists():stages.append(('REPAIR_AUDIT_'+a['source_id'],'repair_audit_e12.py',a['source_id']))
 stages += [(s,p,'PHASE_POSTPROCESS') for s,p in [('AGGREGATE','aggregate_e12.py'),('TABLES','deliverables_e12.py'),('FIGURES','figures_e12.py'),('REPORTS','reports_e12.py')]]
 for stage,script,sid in stages:
  prior=[a for a in ledger if a['stage']==stage]
  if prior and prior[-1]['status']=='COMPLETED':continue
  import common_r3
  common_r3.SID=sid;common_r3.resource_gate(ram=int(1.3*GiB),commit=int(1.8*GiB),disk=int(.15*GiB));env=dict(os.environ,R3_SOURCE=sid,TEMP=str(R/'tmp'),TMP=str(R/'tmp'),MPLCONFIGDIR=str(R/'tmp'),PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2');entry=dict(UTC=now(),stage=stage,script=script,script_SHA256=sha(R/'src'/script),status='STARTED');ledger.append(entry);write(ledgerpath,ledger);path=R/'26_closeout'/(stage+'.log');print('POST_START',stage,flush=True);t=time.perf_counter()
  with path.open('wb') as log:
   p=subprocess.Popen([str(PY),'-B','-u',str(R/'src'/script)],cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT)
   from campaign_e11r1 import sample
   while p.poll() is None:sample(sid,stage,p.pid);time.sleep(2)
  entry.update(status='COMPLETED' if p.returncode==0 else 'FAILED_ADMINISTRATIVE_STAGE',exit_code=p.returncode,elapsed_s=time.perf_counter()-t,log_SHA256=sha(path));write(ledgerpath,ledger);print('POST_END',stage,entry['status'],flush=True)
  if p.returncode:raise RuntimeError('Postprocess stopped; no FE rerun is permitted:'+str(path))
  if stage=='FIGURES':
   ts=rows(R/'04_resource_preflight/CONTROLLER_RESOURCE_SAMPLES.csv');res=read(R/'04_resource_preflight/ACTUAL_RESOURCE_ACCOUNTING.json');res.update(sampled_peak_workspace_bytes=max(int(a['workspace_bytes']) for a in ts),minimum_sampled_E_free_bytes=min(int(a['E_free_bytes']) for a in ts),sampled_peak_worker_RSS_bytes=max(int(a['observed_worker_RSS_bytes']) for a in ts),sampled_peak_worker_private_bytes=max(int(a['observed_worker_private_bytes']) for a in ts),minimum_sampled_available_RAM_bytes=min(int(a['RAM_available_bytes']) for a in ts),minimum_sampled_available_commit_bytes=min(int(a['commit_free_bytes']) for a in ts),C_minimum_sampled_free_bytes=min(int(a['C_free_bytes']) for a in ts),postprocess_monitor_scope='Includesrepairaudits,aggregation,exportsandfigures at2s sampling;reportsfinishafterthissnapshot;finalreleasereceiptusesalltelemetry');write(R/'04_resource_preflight/ACTUAL_RESOURCE_ACCOUNTING.json',res);f=read(R/'R8E12_FINAL_COUNTS.json');f['resources']=res;write(R/'R8E12_FINAL_COUNTS.json',f)
 print('POSTPROCESSING_READY_FOR_VISUAL_QA_AND_SEAL',flush=True)
if __name__=='__main__':main()
