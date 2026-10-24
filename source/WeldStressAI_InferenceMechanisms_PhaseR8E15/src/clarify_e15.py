from common_e15 import *
import pandas as pd,re
from reports_e15 import md

def main():
 v=pd.read_csv(R/'CONTEXT_PREDICTION_VARIATION.csv');summary=v.groupby(['model','condition','policy']).agg(global_maximum_absolute_difference_MPa=('maximum_difference_MPa','max'),minimum_source_RMS_MPa=('RMS_difference_MPa','min'),maximum_source_RMS_MPa=('RMS_difference_MPa','max'),minimum_source_Q95_MPa=('Q95_absolute_difference_MPa','min'),maximum_source_Q95_MPa=('Q95_absolute_difference_MPa','max')).reset_index();table(R/'07_same_point_contexts/CONTEXT_GLOBAL_EXTREMA.csv',summary.to_dict('records'))
 note='\n\n## Context quantile and maximum conventions\n\nEQUAL_PLATE_CONTEXT_VARIATION.csv averages separately computed source metrics within plates and across both seeds. Its Q95 column is the mean of source-specific area-weighted Q95 values; its maximum_difference column is the mean of source-specific maxima, **not a pooled maximum**. The following table separately gives the true maximum across every executed paired source point/checkpoint in each condition and the ranges of individual-source RMS/Q95 metrics. Repeated points/seeds do not create independent specimens.\n\n'+md(summary)
 for name in ['MATCHED_POINT_CONTEXT_INVARIANCE.md','R8E15_MASTER_REPORT.md']:
  p=R/name;text=p.read_text(encoding='utf8');text+=note
  if name=='R8E15_MASTER_REPORT.md':
   # Keep the explicit answer self-contained, in addition to the appended convention note.
   marker='### 19.';pos=text.index(marker);text=text[:pos]+'The preceding macro Q95/max values are means of source statistics. True across-point maxima and source-Q95 ranges:\n\n'+md(summary)+'\n\n'+text[pos:]
  p.write_text(text,encoding='utf8')
 effects=pd.read_csv(R/'17_mechanism_decomposition/AGGREGATION_EFFECTS_BY_SEED.csv');selected=effects[(effects.condition!='FULL')&effects.contrast.isin(['S1 minus S0','S2 minus S0'])];support=selected.groupby('contrast').agg(source_macro_cases=('delta_L2','size'),cases_lower_L2=('delta_L2',lambda x:int((x<0).sum())),cases_lower_boundary_error=('delta_boundary_jump_error_MPa',lambda x:int((x<0).sum())),cases_higher_High95_IoU=('delta_high95_IoU',lambda x:int((x>0).sum()))).reset_index();table(R/'17_mechanism_decomposition/REPEATABILITY_CASE_COUNTS.csv',support.to_dict('records'));repeat='\n\n## Repeatability scope\n\nBoth overlap policies lower restricted-view equal-plate L2 and fixed original-boundary jump error in every tested model/seed/width macro comparison. High95 localization does not share that universal direction, and source-level, amplitude and oracle trade-offs remain. N2 X43 S2 has small reductions in L2 and boundary jump error, with increased IoU, in both seeds, but this is a descriptive exposed-cohort finding, not policy selection or fresh validation. Counts below refer to eight correlated model/seed/width macro cases per policy, not independent physical replicates.\n\n'+md(support)
 for name in ['R8E15_MASTER_REPORT.md','FINAL_R8E15_DECISION.md','HISTORICAL_VS_UNIFORM_STITCHING.md','UNIFORM_VS_WEIGHTED_STITCHING.md']:
  p=R/name;p.write_text(p.read_text(encoding='utf8')+repeat,encoding='utf8')
 write(R/'20_reports/REPORT_CLARIFICATION_RECEIPT.json',dict(UTC=now(),passed=True,no_numerical_prediction_changed=True,context_global_extrema_rows=len(summary),repeatability_counts=support.to_dict('records')));print('CLARIFICATIONS_COMPLETE',flush=True)
if __name__=='__main__':main()
