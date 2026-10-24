"""Sequential checkpointed controller. Every completed stage is skipped on restart; no SOLVE repeats."""
from setup_e11r1 import R,read,rows,write,table,now,sha,GiB
import sys,os,subprocess,time,psutil,shutil
PY=R.parent/'WeldScan_MechanicalBenchmark_Phase5E/.venv/Scripts/python.exe'
STAGES=[
 ('CAD',['geometry_r3.py']),('SCHEMA',['schema_check_r3.py']),
 ('M1_MESH',['mesh_r3.py','M1']),('M2_MESH',['mesh_r3.py','M2']),
 ('MESH_PAIR',['pair_native_r3.py','pair']),('NATIVE_PREPARE',['pair_native_r3.py','prepare']),
 ('NATIVE_M1',['pair_native_r3.py','native','M1']),('NATIVE_M2',['pair_native_r3.py','native','M2']),
 ('NATIVE_ROUNDTRIP',['pair_native_r3.py','audit']),('PRESOLVE_SEAL',['pair_native_r3.py','seal']),
 ('SOLVE_M1',['stage_r3.py','solve','M1']),('SOLVE_M2',['stage_r3.py','solve','M2']),
 ('RECOVERY_M1',['stage_r3.py','recover_map_tensor','M1']),('RECOVERY_M2',['stage_r3.py','recover_map_tensor','M2']),
 ('T2',['stage_r3.py','t2']),('QUALIFIED_PACKAGE',['complete_metrics_r3.py'])]
def refresh():
 records=[]
 for z in rows(R/'FROZEN_SELECTED_FIVE_SOURCES.csv'):
  sid=z['source_id'];c=R/'cases'/sid;rp=c/'CONTROL_STAGE_LEDGER.json';ls=read(rp) if rp.exists() else [];cad=read(c/'17_reproducibility/CAD_ATTEMPTS.json') if (c/'17_reproducibility/CAD_ATTEMPTS.json').exists() else [];meshes=read(c/'14_reproducibility/FULL_CANDIDATE_LEDGER.json') if (c/'14_reproducibility/FULL_CANDIDATE_LEDGER.json').exists() else [];rep=read(c/'14_reproducibility/LOCAL_TRIAL_LEDGER.json') if (c/'14_reproducibility/LOCAL_TRIAL_LEDGER.json').exists() else [];nat=read(c/'17_reproducibility/NATIVE_INVOCATION_LEDGER.json') if (c/'17_reproducibility/NATIVE_INVOCATION_LEDGER.json').exists() else [];qual=read(c/'13_numerical_qualification/QUALIFICATION_DECISION.json') if (c/'13_numerical_qualification/QUALIFICATION_DECISION.json').exists() else None;status='QUALIFIED' if (c/'QUALIFIED_V1_PACKAGE/REPRODUCIBILITY_MANIFEST.json').exists() else ls[-1]['status'] if ls else 'QUEUED'
  records.append(dict(source_id=sid,order=z['order'],status=status,last_checkpoint=ls[-1]['stage'] if ls else 'AMENDMENT_SEALED',CAD_attempts=len(cad),M1_candidates=sum(a['mesh_level']=='M1' for a in meshes),M2_candidates=sum(a['mesh_level']=='M2' for a in meshes),repair_trials=len(rep),native_preprocessing=sum(a['kind'].startswith('PREPROCESS') for a in nat),SOLVEs=sum(a['kind']=='SOLVE' for a in nat),successful_SOLVEs=sum(a['kind']=='SOLVE' and a['status']=='NATIVE_COMPLETED_AND_VERIFIED' for a in nat),qualified=bool(qual and qual['qualified'])))
 table(R/'SOURCE_EXECUTION_LEDGER.csv',records)
def sample(sid,stage,pid):
 # Monitor only; never kills an active scientific worker. Resource gates precede stages and native jobs.
 from common_r3 import memory
 m=memory();rss=private=0
 try:
  proc=psutil.Process(pid)
  for p in [proc]+proc.children(recursive=True):
   mi=p.memory_info();rss+=mi.rss;private+=getattr(mi,'private',0)
 except psutil.Error:pass
 z=dict(UTC=m['UTC'],source_id=sid,stage=stage,workspace_bytes=m['workspace_bytes'],E_free_bytes=m['free_disk_bytes'],C_free_bytes=shutil.disk_usage('C:/').free,RAM_available_bytes=m['RAM_available_bytes'],commit_free_bytes=m['commit_free_bytes'],observed_worker_RSS_bytes=rss,observed_worker_private_bytes=private)
 path=R/'04_resource_preflight/CONTROLLER_RESOURCE_SAMPLES.csv'
 import csv
 h=not path.exists()
 with path.open('a',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(z))
  if h:w.writeheader()
  w.writerow(z)
def main():
 assert read(R/'RESOURCE_GATE_DECISION.json')['decision']=='RESOURCE_PREFLIGHT_PASS';stop=R/'21_reproducibility/CAMPAIGN_STOP.json';assert not stop.exists()
 for z in rows(R/'FROZEN_SELECTED_FIVE_SOURCES.csv'):
  sid=z['source_id'];c=R/'cases'/sid;ledgerpath=c/'CONTROL_STAGE_LEDGER.json';ledger=read(ledgerpath) if ledgerpath.exists() else [];env=dict(os.environ,R3_SOURCE=sid,TEMP=str(R/'tmp'),TMP=str(R/'tmp'),PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2')
  for stage,args in STAGES:
   prior=[a for a in ledger if a['stage']==stage]
   if prior:
    if prior[-1]['status']=='COMPLETED':continue
    raise RuntimeError('Interrupted stage requires explicit evidence reconciliation; no automatic retry:'+sid+':'+stage)
   # Modest postprocess estimate; native/meshing modules enforce their own stricter operation forecasts.
   import common_r3
   common_r3.SID=sid
   from common_r3 import resource_gate
   try:resource_gate(ram=int(.3*GiB),commit=int(.4*GiB),disk=int(.1*GiB))
   except AssertionError as e:
    write(stop,dict(UTC=now(),source_id=sid,stage=stage,kind='RESOURCE_SAFE_BOUNDARY_STOP',reason=str(e),active_job_terminated=False));refresh();return
   entry=dict(UTC=now(),source_id=sid,stage=stage,status='STARTED',script_sha256=sha(R/'src'/args[0]));ledger.append(entry);write(ledgerpath,ledger);refresh();log=c/(stage+'.log');t=time.perf_counter();print('START',sid,stage,flush=True)
   with log.open('wb') as f:
    p=subprocess.Popen([str(PY),'-B','-u',str(R/'src'/args[0])]+args[1:],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
    while p.poll() is None:sample(sid,stage,p.pid);time.sleep(2)
   entry.update(status='COMPLETED' if p.returncode==0 else 'INTERRUPTED_REQUIRES_RECONCILIATION',exit_code=p.returncode,elapsed_s=time.perf_counter()-t,log_SHA256=sha(log));write(ledgerpath,ledger);refresh();print(entry['status'],sid,stage,round(entry['elapsed_s'],2),flush=True)
   if p.returncode!=0:
    if 'RESOURCE_PREFLIGHT_BLOCKED' in log.read_text(errors='replace') and not stop.exists():write(stop,dict(UTC=now(),source_id=sid,stage=stage,kind='RESOURCE_SAFE_BOUNDARY_STOP',reason=log.read_text(errors='replace')[-2000:],actual_SOLVE_invocations=sum(a['kind']=='SOLVE' for a in read(c/'17_reproducibility/NATIVE_INVOCATION_LEDGER.json')) if (c/'17_reproducibility/NATIVE_INVOCATION_LEDGER.json').exists() else 0))
    raise RuntimeError('Stage stopped; inspect actual log; no repeated native jobs:'+str(log))
   if stop.exists():print('MANDATORY_CAMPAIGN_STOP',read(stop),flush=True);return
  assert read(c/'13_numerical_qualification/QUALIFICATION_DECISION.json')['qualified'];assert (c/'QUALIFIED_V1_PACKAGE/REPRODUCIBILITY_MANIFEST.json').exists();refresh();print('SOURCE_QUALIFIED',sid,flush=True)
 write(R/'21_reproducibility/PRODUCTION_COMPLETED.json',dict(UTC=now(),five_sources_qualified=True,source_order=[a['source_id'] for a in rows(R/'FROZEN_SELECTED_FIVE_SOURCES.csv')]))
if __name__=='__main__':main()
