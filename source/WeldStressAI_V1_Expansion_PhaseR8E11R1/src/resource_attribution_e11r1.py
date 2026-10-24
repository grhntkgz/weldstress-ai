"""Preserve raw resource gates and add UTC-based controller-stage attribution."""
from setup_e11r1 import *
def main():
 raw=R/'ACTUAL_RESOURCE_TIMELINE.csv';data=rows(raw);events=[]
 for q in rows(R/'FROZEN_SELECTED_FIVE_SOURCES.csv'):
  p=R/'cases'/q['source_id']/'CONTROL_STAGE_LEDGER.json'
  if p.exists():
   for a in read(p):events.append((datetime.datetime.fromisoformat(a['UTC']).timestamp(),q['source_id'],a['stage']))
 result=[];corrected=0;last_stage_end=max(datetime.datetime.fromisoformat(a['UTC']).timestamp()+a.get('elapsed_s',0) for q in rows(R/'FROZEN_SELECTED_FIVE_SOURCES.csv') for a in (read(R/'cases'/q['source_id']/'CONTROL_STAGE_LEDGER.json') if (R/'cases'/q['source_id']/'CONTROL_STAGE_LEDGER.json').exists() else []))
 for a in data:
  t=datetime.datetime.fromisoformat(a['UTC']).timestamp();parent=int(a['predicted_operation_RAM_bytes'])==int(.3*GiB) and int(a['predicted_operation_commit_bytes'])==int(.4*GiB) and int(a['predicted_additional_disk_bytes'])==int(.1*GiB);new=dict(a,original_source_id=a['source_id'],attributed_stage='',attribution='WORKER_GATE_RECORDED_SOURCE')
  if parent:
   future=[e for e in events if 0<=e[0]-t<=2];assert future,'Unmatchedcontrollergate';event=min(future);new.update(source_id=event[1],attributed_stage=event[2],attribution='CONTROLLER_PRE_STAGE_UTC_MATCH');corrected+=a['source_id']!=event[1]
  elif t>last_stage_end:new.update(source_id='PHASE_RELEASE',attributed_stage='POST_PRODUCTION',attribution='RELEASE_OPERATION_AFTER_LAST_STAGE')
  result.append(new)
 table(R/'25_reproducibility/RESOURCE_GATES_ATTRIBUTED.csv',result)
 write(R/'25_reproducibility/RESOURCE_ATTRIBUTION_AUDIT.json',dict(UTC=now(),raw_gate_file=str(raw),raw_gate_SHA256=sha(raw),raw_preserved=True,records=len(data),controller_source_labels_corrected=corrected,reason='ParentcontrollerimportscommonmoduleoncewithdefaultX23;itsgenericprestagegatevaluesarecorrectbutrawsourcefielddefaultedtoX23.2scontrollertelemetryandallworker/nativegatesalreadyrecordactualsource.UTCmatchingaddsaccuratesourcestageattributionwithoutchangingresourcevalues.',attribution_tolerance_s=2,scientific_values_changed=False))
if __name__=='__main__':main()
