"""Administrative status completion from actual native receipts, without touching scientific outputs."""
from setup_e11r1 import *
def main():
 for name in ['NEW_QUALIFIED_V1_TARGET_REGISTRY.csv','CUMULATIVE_QUALIFIED_V1_TARGET_REGISTRY.csv']:
  data=rows(R/name)
  for a in data:
   if a['qualification_status']=='QUALIFIED_NEW_E11R1':
    for l,folder in [('M1','06_native_M1'),('M2','07_native_M2')]:
     receipt=read(R/'cases'/a['source_id']/folder/'SOLVE_COMPLETE.json');assert receipt['completed'] and receipt['equilibrium_passed'];a[l+'_native_status']='NATIVE_COMPLETED_AND_VERIFIED'
  fields=list(dict.fromkeys(k for a in data for k in a));table(R/name,data,fields)
 f=read(R/'R8E11R1_FINAL_COUNTS.json');assert f['new_qualified_targets']==5 and f['successful_native_solutions']==10
 f.update(overall_status='R8E11R1_COMPLETE',production_status='5_OF_5_NEW_V1_TARGETS_QUALIFIED',dataset_status='8_TOTAL_V1_TARGETS_QUALIFIED',AI_status='AI_TRAINING_NOT_EXECUTED',external_validation_status='EXTERNAL_VALIDATION_NOT_ESTABLISHED',uncompleted_mandatory_numerical_checks=[])
 write(R/'R8E11R1_FINAL_COUNTS.json',f)
 write(R/'25_reproducibility/ADMINISTRATIVE_POSTPROCESSING_AUDIT.json',dict(UTC=now(),postprocessing_correction='CSVaggregationhadaninitialduplicatelevelkeyword;correctedbeforetables/reportsrelease',scientific_results_modified=False,additional_SOLVE_invocations=0,new_experimental_configurations=0,native_completion_statuses='DerivedfromactualSOLVE_COMPLETEreceipts',source_selection='Parentreadonlyverifierreplayedconsistencychecks;no newselectionartifactordecisionwascreated',resource_source_attribution='Rawdefaultcontrollerlabelpreserved;UTC-basedattributedsupplementaddedatfinalseal'))
 print('ADMINISTRATIVE_METADATA_COMPLETE;10nativeSOLVEsunchanged')
if __name__=='__main__':main()
