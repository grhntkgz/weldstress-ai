"""Source-backed report assembly after production. Preserves preregistered amendment."""
from setup_e11r1 import *
def mt(z,cols=None):
 if not z:return 'No executed records; unavailable values are null/NOT_EXECUTED.'
 cols=cols or list(z[0]);return '| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'+'\n'.join('| '+' | '.join(str(a.get(k,'')) for k in cols)+' |' for a in z)
def md(n,b):(R/n).write_text('# '+n[:-3].replace('_',' ')+'\n\n'+b+'\n',encoding='utf8')
def finish_links():
 p=R/'R8E11R1_MASTER_REPORT.md';text=p.read_text(encoding='utf8');marker='## Reviewable figures and native files'
 if marker not in text:
  text+='\n\n'+marker+'\n\n[All scientific figures]('+str(R/'SCIENTIFIC_FIGURES.csv').replace('\\','/')+') · [Cumulative V1 registry]('+str(R/'CUMULATIVE_QUALIFIED_V1_TARGET_REGISTRY.csv').replace('\\','/')+')\n\n'
  for name in ['08_Original_source_T2_M1_M2_and_differences.png','12_Numerical_target_qualification.png']:text+='!['+name+']('+str(R/'23_figures'/name).replace('\\','/')+')\n\n'
  for q in rows(R/'FROZEN_SELECTED_FIVE_SOURCES.csv'):
   sid=q['source_id'];text+=sid+': [M2 native database]('+str(R/'cases'/sid/'07_native_M2/MODEL.db').replace('\\','/')+') · [M2 native result]('+str(R/'cases'/sid/'07_native_M2/file.rst').replace('\\','/')+') · [Qualified target package]('+str(R/'cases'/sid/'QUALIFIED_V1_PACKAGE/TARGET_PROVENANCE.json').replace('\\','/')+')\n\n'
  p.write_text(text,encoding='utf8')
def main():
 f=read(R/'R8E11R1_FINAL_COUNTS.json');a=read(R/'RESOURCE_BUDGET_AMENDMENT.json');live=read(R/'LIVE_RESOURCE_MEASUREMENT.json');res=f['resources'];queue=rows(R/'FROZEN_SELECTED_FIVE_SOURCES.csv');st=rows(R/'SOURCE_EXECUTION_LEDGER.csv');mets=rows(R/'T2_NUMERICAL_METRICS.csv');eq=rows(R/'NATIVE_EQUILIBRIUM.csv');nat=rows(R/'NATIVE_SOLVE_REGISTRY.csv');quals=rows(R/'QUADRATIC_JACOBIAN_AUDIT.csv');hier=rows(R/'M1_M2_REFINEMENT.csv');cost=rows(R/'FINAL_STORAGE_ACCOUNTING.csv');regions=rows(R/'T2_REGIONAL_METRICS.csv');registry=rows(R/'CUMULATIVE_QUALIFIED_V1_TARGET_REGISTRY.csv');forecast=rows(R/'REMAINING_COHORT_FORECAST.csv');new=rows(R/'NEW_QUALIFIED_V1_TARGET_REGISTRY.csv');geometry=rows(R/'SOURCE_GEOMETRY_FIDELITY.csv');cad=[r for r in geometry if r['scope']=='CAD'];fe=[r for r in geometry if r['scope']=='QUADRATIC_FE'];warnings=rows(R/'NATIVE_SHAPE_WARNINGS.csv');errors=rows(R/'NATIVE_SHAPE_ERRORS.csv');repairs=rows(R/'LOCAL_MESH_REPAIR_REGISTRY.csv')
 status=f"""Campaign status: **{f['campaign_status']}**.

New qualified targets: **{f['new_qualified_targets']}/5**; cumulative qualified source identities: **{f['cumulative_qualified_targets']}**. Actual native SOLVE invocations: **{f['actual_native_SOLVE_invocations']}/10**, successful solutions: **{f['successful_native_solutions']}**; preprocessing jobs: **{f['native_preprocessing_jobs']}**. No historical target was re-solved, no AI training or inference was run, and no source was replaced.

The sole prospective amendment was workspace16→24GiB. Historical R8-E11 remains correctly resource-blocked under16GiB. The amendment was sealed before production. All material, geometry, mesh, BVP, T2 and campaign-stop criteria remain unchanged.

"""
 resource=f"""Live initial E: free space was **{live['E_free_GiB']:.6f}GiB**, C: **{live['C_free_GiB']:.6f}GiB**. Available RAM **{live['RAM_available_GiB']:.6f}GiB**, commit **{live['commit_available_GiB']:.6f}GiB**. Read-only license query reported available ansys capacity; actual native checkouts are evidenced in completed jobs.

The original forecast is **17.259678117GiB peak new occupation**, comprising17.009678117GiB persistent allowance plus0.25GiB simultaneous temporary allowance. It is neither final archive alone nor a measured instantaneous peak. The persistent term includes five cap-scaled source archives,4GiB additional retained-failure allowance and0.5GiB shared release overhead. No forecast component was reduced after the old block. New24GiB cap gives **6.740321883GiB planning headroom**. Expected remaining physical disk after forecast: **{a['expected_remaining_free_disk_GiB']:.6f}GiB**, above20GiB reserve.

All phase-controlled TEMP/TMP, CAD/mesher temporaries and MAPDL job directories are on E: inside this independent R1 workspace. C: is also monitored with a declared2GiB system/fallback reserve. Unrelated application data were not redirected. No external phase scratch was configured; no exhaustive filesystem-I/O trace was performed to prove absence of all small library/license side effects.

Observed controller sampling: nominal2s plus filesystem-scan overhead. Sampled peak workspace **{res['sampled_peak_workspace_bytes']/GiB:.6f}GiB**; postproduction snapshot **{res['postproduction_workspace_bytes']/GiB:.6f}GiB**; minimum sampled E: free **{res['minimum_sampled_E_free_bytes']/GiB:.6f}GiB**. Observed peak worker RSS **{res['sampled_peak_worker_RSS_bytes']/GiB:.6f}GiB**, private allocation **{res['sampled_peak_worker_private_bytes']/GiB:.6f}GiB**. These are sampled extrema, not guaranteed continuous peaks. Final manifest verification receipt adds the completed release size and current free disk after figures/reports. Operation gates forecast additional allocation before every major stage; no observed24GiBcap or20GiBdiskreserve violation was accepted.

Source-specific observations use CONTROLLER_RESOURCE_SAMPLES.csv and native per-job telemetry. Parent-controller generic pre-stage gate rows in the raw ACTUAL_RESOURCE_TIMELINE.csv retained a defaultX23 source label; their resource measurements are valid. The unchanged raw file is retained, and25_reproducibility/RESOURCE_GATES_ATTRIBUTED.csv adds source/stage attribution by matching the next durable stage timestamp within2s, with original_source_id retained. Worker gates and2scontroller source labels were already correct; no numerical/resource values are altered.

"""
 integrity="""Historical E9, C02R2, G08/X10R3 and blocked E11 releases were independently reverified read-only. The original1432 historical bindings were checked, followed by complete manifest checks including E11. The original46 E9 tests passed unchanged. E11 had0CAD/0mesh/0SOLVE artifacts; its selection, stop and preregistration hashes remain unchanged. The historical C02/G08/X10 target hashes were checked before production and again at release.

The parent preregistration and stop are bound in PARENT_PROTOCOL_HASHES.json. The amendment JSON includes the amendment Markdown hash; AMENDMENT_PREREGISTRATION_SEAL.json binds both and supplies the amendment JSON hash without a self-hash circularity. Production gate timestamps are later than this seal. Final manifest binds new scripts and evidence. Historical input files are protected read-only by the worker audit hook.

Thirteen scientific geometry/quality/BVP/tensor/T2 kernel modules are byte-identical to the qualified R3implementation; see25_reproducibility/SCIENTIFIC_KERNEL_REUSE.json. Independent workspace/queue and durable-budget bookkeeping adaptations are documented separately from numerical changes; there are no scientific parameter changes.
"""
 selection="""The exact parent CSV was copied byte-for-byte as FROZEN_SELECTED_FIVE_SOURCES.csv. Canonical IDs, source hashes and order were read from this sealed registry, never inferred from prefixes. No new feature declaration, ranking artifact or selection decision was created. The parent E11 read-only release verifier replayed its stored-ranking and geometry-descriptor consistency checks during historical integrity verification; this audit did not amend or replace the frozen selection. The previously selected sequence remains:

"""+mt(queue,['order','source_id','dependency_group','original_phase'])
 dependence="""Source-family labels provide documentary grouping, not physical coupon/plate independence. Parent plate and batch relationships remain unknown. No new independent-coupon claim, near-duplicate exclusion proof or independent generalization claim is made. Historical twelve R6test identities remain quarantined; no historical test target or AI error influenced production.
"""
 geometrytext="""The measured front is preserved through unchanged original68457XYZ points, source IDs,134400canonical T0triangles, original weights and topology. Historical authoritative front BRep is retained; only the explicitly assumed rear and four synthetic closures are constructed. The front-only parent fit uses original-area-weighted outer10%X strips, frozen Huber1.345IRLS,20iterations and1e-12coefficient stop. Parent thresholds:RMS<=0.10mm,P95<=0.20mm,abs slopes<=0.02.

Rear equation: zrear=beta0+betaX(X-Xmid)+betaY(Y-Ymid)−19sqrt(1+betaX²+betaY²), a true19mm normal offset; measured rear is not used. Continuous front/rear separation is bounded from the source spline poles and rear extrema; source/STEP topology and export/reimport were checked. Kernel-computed and graph-integral volumes are retained separately; neither defines the nominal force.

Frozen geometry gates use full source forward same-XY P95<=0.010mm,max<=0.040mm and seven-point curved-face reverse comparison against canonical T0triangles with the same limits. Actual closest-T0 diagnostics are reported separately and do not replace a stricter same-XY gate. Original float32-coordinate representation produces micrometre-scale domain endpoint differences; the inherited rounding policy is disclosed in CAD receipts, with no source coordinates changed.

"""
 meshtext="""M1/M2 use unchanged Tet10/SOLID187-compatible quadratic topology, near-weld targets0.40/0.30mm, parent0.60mm,bulk2.5mm and frozen geometry-only sizing. Every complete generated or materialized candidate counts toward3/level/source; CAD budget retains the stricter2/source bound. Nodecap350000,Tet10cap230000,minSICN0.020,zero nonpositive sampled Jacobians and invalid elements.

Independent73-point whole-mesh Jacobian/SICN and scalar checks, shared midsides, all-used nodes, one volume component and boundaryEuler2 are tested. Expanded local samples and Bernstein bounds apply where used; finite whole-mesh samples do not prove continuous global positivity.

M2 must have actual median andP90 near-weld edges<=0.98M1 and greater curved-face density. Common CAD is hash-bound; symmetric quadratic patch-domain differences are retained as diagnostics, not silently redefined source-fidelity gates.

"""
 bvptext="""E=210000MPa,nu0.30 are isotropic linear-elastic modelling assumptions, not measured specimen properties. Units:mm,N,MPa; static,NLGEOMOFF,PCG1e-8,2CPU. Nominal100MPa is a numerical reference load.

Each source's documented nominal19mm thickness and full-design Yspan28mm were checked, giving53200N per end port. The common force line is (Ymid,parent(Xmid,Ymid)−9.5sqrt(1+bx²+by²)), parallel to globalX. Actual quadratic end-port areas determine an affine traction basis[1,Y−Yline,Z−Zline]; resultant right-hand-side[±53200,0,0]. Traction bounds50..150MPa and applied force/couple tolerances1e-8 are checked, including independent36point Duffy versus7point Dunavant integration.

Six scalar gauges suppress six rigid modes: leftrearYmin UX/UY/UZ,leftrearYmax UX/UZ,leftfrontYmin UX. No arbitrary full clamp, lateral restraint, remote eccentricity or bending load was added. Global reaction force/F and moment/(F×19) must each be<=1e-5. Signed applied/reaction quantities and coordinate origins are retained.

"""
 recoverytext="""Actual native nodal displacements are recovered with the unchanged independent quadratic isoparametric pipeline: J→strain→C:strain→full six-component stress tensor. Native tensor permutation is explicit. Independent direct tensor samples and native element-average diagnostics distinguish recovery arithmetic from field interpretation.

Stresses are evaluated by inverse quadratic boundary mapping at original source XY and source identity, not nearest-node replacement. The source geometry audit covers all68457points; stress mapping is deliberately limited to the frozen39200point halo, and the complete T2core is34200points. Mapping coverage1.0 refers to intended support, not the full front. T2common-core evaluated area fractions are explicitly reported by source; unqueried outer points are not zeros.

T2=original T0area-weighted mean of max(lambda_max(C:epsilon),0) within1mm same-face3DEuclidean chord(+1e-7mm query tolerance). Principal stress is computed before averaging. Complete weight coverage>=1−1e-10;halo10/2mm,core11/3mm. No projected2Dneighborhood, field smoothing, high-point deletion or tensor-before-eigenvalue averaging.

Frozen region labels are geometry proxies: height>=0.5mm weld proxy,2mm projected adjacent collar,remaining parent. They are not independently validated physical weld-toe tracks. High95 uses the inherited interpolated weightedCDF, distinct from a machine-learning stepCDF metric.

Whole normalized L2<=0.020,worstregional<=0.030,High95areaIoU>=0.800,mapping/commoncore coverage>=0.990. FineM2norm is the L2denominator; no coarse substitution. Independent scalar neighborhoods,math.fsumstatistics and alternate metric arithmetic must reproduce values before target release.

"""
 limitations="""These are conditional numerical V1 targets under a measured-front/assumed-planar-rear standardized BVP. Numerical verification is not physical experimental stress validation. Two meshes establish bounded numerical consistency, not asymptotic convergence or independently verified local notch radii. Sampling, reconstructed CAD representation, unknown raw registration, boundary truncation and assumed rear remain sources of physical model uncertainty. The numerical metrics do not bound those physical errors.

No residual welding stress,plasticity,thermal effects,contact,crackgrowth,fatigue life or grinding optimization is modelled. No AI training,inference,Aalborg prediction or fresh independent generalization evaluation occurred. Five geometry-diverse selected sources are not a random sample of the42eligible family; their observed yield and cost do not constitute population confidence bounds.
"""
 numeric=mt(mets,['source_id','M1_mean_T2_MPa','M2_mean_T2_MPa','whole_L2','worst_regional_L2','high95_area_IoU','M2_max_T2_MPa','M2_nominal_Kmax','M2_mapping_coverage'])
 stop='No mandatory stop occurred; all five completed.' if not f['campaign_stop'] else 'Actual mandatory stop:\n\n'+json.dumps(f['campaign_stop'],indent=2)
 further="""A separate phase may expand the remaining eligible cohort only with a fresh storage plan, unchanged source/FE/T2gates and durable stop/recovery budgets. Do not infer full-cohort cost/yield from a selected sample. No automatic further production or AI work is authorized by this release. Before grouped model training, establish a sufficiently diverse qualified cohort, physical-dependency lineage, leakage-resistant grouped splits and a prospective independent holdout/validation plan.
"""
 reports={
 'HISTORICAL_R8E11_STOP_VERIFICATION.md':integrity+'Historical forecast17.259678117GiB exceeded16GiB by1.259678117GiB while physical disk reserve passed. That decision remains correct and unchanged.',
 'PARENT_PREREGISTRATION_INTEGRITY.md':integrity,
 'FROZEN_FIVE_SOURCE_SELECTION.md':selection,
 'HISTORICAL_V1_TARGET_INTEGRITY.md':integrity+mt(rows(R/'HISTORICAL_V1_TARGET_HASHES.csv'),['source_id','target_path','target_hash']),
 'LIVE_RESOURCE_ASSESSMENT.md':resource,
 'CONSERVATIVE_STORAGE_REFORECAST.md':resource+mt(rows(R/'STORAGE_FORECAST_COMPONENTS.csv')),
 'RESOURCE_GATE_DECISION.md':resource+'\n\n'+json.dumps(read(R/'RESOURCE_GATE_DECISION.json'),indent=2),
 'R8E9_PROTOCOL_COMPLIANCE.md':integrity+meshtext+bvptext+recoverytext,
 'SOURCE_DEPENDENCY_AUDIT.md':dependence+selection,
 'CAD_PRODUCTION.md':geometrytext+mt(cad,['source_id','passed','CAD_attempt','STEP_export_reimport','source_forward_P95_mm','source_forward_max_mm','CAD_reverse_P95_mm','CAD_reverse_max_mm','continuous_minimum_separation_bound_mm','STEP_SHA256']),
 'SOURCE_GEOMETRY_FIDELITY.md':geometrytext+mt(fe,['source_id','level','forward_P95_mm','forward_max_mm','reverse_P95_mm','reverse_max_mm','passed']),
 'M1_M2_MESH_QUALIFICATION.md':meshtext+mt(quals,['source_id','level','candidate','nodes','Tet10','minSICN','minimum_Q1_J_mm3','negative_J_elements','zero_J_elements','pre_solver_qualified'])+'\n\n'+mt(hier,['source_id','median_edge_ratio','P90_edge_ratio','surface_density_ratio','passed']),
 'LOCAL_TET10_RECOVERY.md':meshtext+'\nAll failed candidates were retained. Actual trials:\n\n'+mt(repairs)+'\n\nActually moved node records:\n\n'+mt(rows(R/'ACTUAL_MOVED_NODES.csv')),
 'NATIVE_IMPORT_AND_SHAPE_CHECKS.md':f'Actual native preprocessing jobs:{f["native_preprocessing_jobs"]}. Exact Tet10 permutation[0,1,2,3,4,5,6,7,9,8],native DB coordinate/connectivity roundtrip and component mapping are verified per case. Fatal shape errors block; warnings retain element locations,independent quality and classification.\n\nWarnings:\n\n'+mt(warnings)+'\n\nErrors:\n\n'+mt(errors),
 'STANDARDIZED_BVP_ASSEMBLY.md':bvptext+mt(rows(R/'STANDARDIZED_BVP_AUDIT.csv'),['source_id','level','force_N','nominal_thickness_mm','loadline_origin','rigid_gauge_rank','all_assembly_gates_passed']),
 'PRE_SOLVE_QUALIFICATION.md':bvptext+'Both mesh/native levels pass before M1SOLVE; source-specific PRE_SOLVE_GATE_SEALED.json binds input hashes. No gate is waived. Schema audits occur before FEproduction and native solving. See PRE_SOLVE_GATES.csv for all source/gate outcomes.',
 'NATIVE_ANSYS_EXECUTION.md':status+'Each job runs isolated and sequentially. SOLVE logs must show actual loadstep/substep completion and RUNCOMPLETED; exitcode/RST alone are insufficient. Native outputs were saved before independent audits. No completed SOLVE was repeated.\n\n'+mt(nat,['source_id','level','completed','native_errors','native_warnings','peak_RSS_bytes','peak_private_bytes','Umax_mm']),
 'FORCE_MOMENT_EQUILIBRIUM.md':bvptext+mt(eq,['source_id','level','force_residual_relative','moment_residual_over_Ft','gauge_motion_max_mm','Umax_mm','equilibrium_passed']),
 'INDEPENDENT_TENSOR_RECOVERY.md':recoverytext+mt(rows(R/'TENSOR_INDEPENDENT_CHECKS.csv')),
 'ORIGINAL_SOURCE_STRESS_MAPPING.md':recoverytext+mt(rows(R/'SOURCE_STRESS_MAPPING.csv')),
 'V1_T2_NUMERICAL_QUALIFICATION.md':recoverytext+numeric+'\n\nRegional results:\n\n'+mt(regions),
 'INDEPENDENT_T2_VERIFICATION.md':recoverytext+'See T2_INDEPENDENT_VERIFICATION.csv and each case T2_COMPLETE_INDEPENDENT_AUDIT.csv,INDEPENDENT_METRIC_AUDIT.csv; final release verifier rechecks scalar neighborhoods and weighted statistics. No source support was reselected after stress inspection.',
 'FIVE_SOURCE_PRODUCTION_SUMMARY.md':status+mt(st)+numeric+'\n\n'+stop,
 'CUMULATIVE_V1_DATASET_REGISTRY.md':status+dependence+mt(registry,['source_id','qualification_status','T2_L2','T2_worst_regional_L2','T2_high95_IoU','qualified_M2_target_SHA256','release_workspace']),
 'ACTUAL_RESOURCE_ACCOUNTING.md':resource+mt(cost),
 'REMAINING_COHORT_RESOURCE_FORECAST.md':mt(forecast)+'\n\n'+further+' These scenarios include selected-source observed persistent archives with explicit recovery multipliers. They are not guaranteed peak-capacity bounds or qualification-yield forecasts. The historical17.19GiB figure belonged to the former39-source mean estimate, not this completed campaign.',
 'SCIENTIFIC_LIMITATIONS.md':limitations+dependence,
 'FINAL_R8E11R1_DECISION.md':status+numeric+'\n\n'+stop+'\n\n'+resource+limitations+further,
 'README_REPRODUCIBILITY.md':'Use the existing Phase5E Python environment. Run src/verify_release_e11r1.py -B via Python for read-only final audit. Do not rerun completed native jobs; campaign_e11r1.py skips completed stages and refuses unreviewed interrupted stages. Frozen parent/amendment hashes and source-specific pre-solve seals bind scientific inputs. All historical workspaces remain read-only. Root tables index actual case artifacts; full decks,DB/RST,source arrays,CSVmaps and packages remain under cases. The immutable amendment is not rewritten by report generation. Receipt/manifest/seal exclusions resolve self-reference. No optional S2/S3 recovery is claimed when unexecuted.'
 }
 for n,b in reports.items():md(n,b)
 questions=re.findall(r'^\d+\. (.+)$',(R/'01_protocol_freeze/USER_SPECIFICATION.txt').read_text(encoding='utf-8-sig').split('# 26. REQUIRED FINAL QUESTIONS')[1].split('# 27.')[0],re.M);assert len(questions)==45
 answers=[
 'Yes. The unchanged historical forecast17.259678117GiB exceeded16GiB; physical disk reserve passed. The old stop remains correct.',
 'Yes. Historical16GiB and prospective24GiB are separate; no historical artifact was changed.',
 'Yes. Amendment and parent hashes were sealed before resource decision and all new production.',
 'Yes,46/46 unchanged E9 tests passed again.',
 'Yes. Original1432 links and complete E9/R2/R3/E11 manifests checked; final preservation checks rehash again.',
 'Yes. Parent selection copied byte-for-byte; no reranking or replacement.',
 ', '.join(a['source_id'] for a in queue)+'.',
 f'{live["E_free_GiB"]:.9f}GiB at the timestamp in LIVE_RESOURCE_MEASUREMENT.json.',
 'Controlled TEMP/TMP,CAD/mesh temporaries and native job directories all E: inside this newworkspace. C: system/fallback reserve monitored separately.',
 '17.259678117GiB peak allowance including0.25GiB temporary storage; retained failure allowance4GiB. No optimistic reduction.',
 'Yes, forecast headroom6.740321883GiB under24GiB.',
 f'Yes. Forecast leaves{a["expected_remaining_free_disk_GiB"]:.6f}GiB>=20GiB.',
 f'Initial RAM{live["RAM_available_GiB"]:.6f}GiB andcommit{live["commit_available_GiB"]:.6f}GiB passed; operation-specific gates repeated.',
 'No. First CAD began only after amendment seal and RESOURCE_PREFLIGHT_PASS.',
 str(f['new_CAD_candidates'])+' actual CAD candidates.',
 str(f['full_M1_candidates'])+' M1 and '+str(f['full_M2_candidates'])+' M2 complete candidates,including materialized repairs.',
 ', '.join(sorted({a['source_id'] for a in repairs})) if repairs else 'None; no local recovery was needed.',
 'Original source arrays are byte-identical by SHA256; repaired mesh coordinates,if any,do not alter measured source geometry.',
 'See actual CAD/FEfidelity tables. Only sources passing all mandatory gates release targets; unexecuted stages are not labelled PASS.',
 'See M1_M2_MESH_QUALIFICATION.md; actualquality/hierarchy receipts are source-specific.',
 'Native imports/shape checks are evidenced per executed level; target release requires all nativegates.',
 str(len(warnings))+' classified warned-element records;'+str(len(errors))+' nativeerrorrecords. See CSVs and per-case logs.',
 'Executed BVPs use verified nominal force53200N/source,common loadline,independent actual-port force/moment quadrature and rank6gauges.',
 str(f['actual_native_SOLVE_invocations'])+' actual new SOLVE invocations.',
 str(f['successful_native_solutions'])+' verified completed solutions.',
 'Every released source requires reaction force/moment<=1e-5. Actual values in NATIVE_EQUILIBRIUM.csv.',
 'Every released source passes independent tensor checks; exact errors in TENSOR_INDEPENDENT_CHECKS.csv.',
 'Every released source passes original-ID inverse quadratic mapping,with intended support and coverage reported separately from full-front geometry.',
 'OriginalT0areas,IDs,XYZ and frozen geometry-only core/halo are preserved; no support reselection after stress.',
 numeric,
 mt(mets,['source_id','high95_area_IoU']),
 ', '.join(a['source_id'] for a in new) if new else 'No new package qualified.',
 str(f['cumulative_qualified_targets'])+' source identities; meshes are not counted as separate specimens.',
 stop,
 'No later source ran after a mandatory stop.' if f['campaign_stop'] else 'No stop occurred; all selected sources proceeded in order.',
 f'Sampled peak{res["sampled_peak_workspace_bytes"]/GiB:.6f}GiB;postproduction{res["postproduction_workspace_bytes"]/GiB:.6f}GiB. Final receipt adds completed release size. No guaranteed continuous-peak claim.',
 f'{res["minimum_sampled_E_free_bytes"]/GiB:.6f}GiB on E: in controller samples.',
 'All observed usage and operation forecasts complied with24GiB. Sampling does not establish an exact continuous maximum.',
 'All observed free space and prospective operation gates complied with20GiB E:reserve; C: monitored with2GiBsystemreserve.',
 mt(cost,['source_id','archive_GiB','wall_components_s','native_SOLVE_stage_s']),
 dependence,
 'Yes. Conditional finite-element-derived targets,not experimentally measured physical stresses.',
 further,
 mt(forecast,['scenario','remaining_eligible','required_free_with20GiBreserve','current_free_GiB','additional_disk_GiB']),
 further
 ];assert len(answers)==45
 body=status+integrity+'\n## Frozen selection\n\n'+selection+'\n\n## Resource amendment and observed cost\n\n'+resource+'\n\n## Actual numerical results\n\n'+numeric+'\n\n## Verification method\n\n'+geometrytext+meshtext+bvptext+recoverytext+'\n\n## Campaign stop\n\n'+stop+'\n\n## Scientific scope\n\n'+limitations+'\n\n## Answers to45required questions\n\n'+'\n\n'.join('### '+str(i)+'. '+q+'\n\n'+ans for i,(q,ans) in enumerate(zip(questions,answers),1));md('R8E11R1_MASTER_REPORT.md',body)
 finish_links();print('REPORTS_READY',len(reports)+2,'includingpreservedamendment')
if __name__=='__main__':main()
