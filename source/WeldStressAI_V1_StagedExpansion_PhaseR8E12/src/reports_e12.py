"""Evidence-linked engineering reports; decisions track actual execution, not planned yield."""
from setup_e11r1 import *
import re,math
def mt(z,keys=None):
 if not z:return 'No executed records; see the corresponding CSV header.\n'
 keys=keys or list(z[0]);out=['| '+' | '.join(keys)+' |','|'+'|'.join(['---']*len(keys))+'|']
 for a in z:
  vals=[]
  for k in keys:
   v=a.get(k,'NOT_EXECUTED')
   if isinstance(v,float):v=f'{v:.9g}'
   elif isinstance(v,str) and re.fullmatch(r'[-+]?(?:\d+\.\d*|\d*\.\d+)(?:[eE][-+]?\d+)?',v):v=f'{float(v):.9g}'
   vals.append(str(v).replace('|','/').replace('\n',' ')[:220])
  out.append('| '+' | '.join(vals)+' |')
 return '\n'.join(out)+'\n'
def readable(s):
 # Format prose units/counts without changing technical identifiers, filenames or numerical values.
 s=re.sub(r'(?<=\d)(GiB|MPa|Nmm|mm|iterations|points|sources|development|historical|independent|documentary|original|new|eligible|qualified|physical|candidate|sample|native|scalar|test|plate|parent|full|fixed|geometry|additional|local|different|canonical|possible|pairs|coupons|source|dimensional|point)',r' \1',s)
 return s.replace('outer10%X','outer 10% X').replace('per-source19mm','per-source 19 mm')
def main():
 f=read(R/'R8E12_FINAL_COUNTS.json');live=read(R/'LIVE_RESOURCE_MEASUREMENT.json');gate=read(R/'RESOURCE_GATE_DECISION.json');p=read(R/'01_provenance/AUDIT_RECEIPT.json');q=rows(R/'FROZEN_SELECTED_FIVE_SOURCES.csv');met=rows(R/'T2_NUMERICAL_METRICS.csv');eq=rows(R/'NATIVE_EQUILIBRIUM.csv');quality=rows(R/'QUADRATIC_JACOBIAN_AUDIT.csv');warnings=rows(R/'NATIVE_SHAPE_WARNINGS.csv');errors=rows(R/'NATIVE_SHAPE_ERRORS.csv');registry=rows(R/'CUMULATIVE_QUALIFIED_V1_TARGET_REGISTRY.csv');new=rows(R/'NEW_QUALIFIED_V1_TARGET_REGISTRY.csv');cost=rows(R/'FINAL_STORAGE_ACCOUNTING.csv');resources=read(R/'04_resource_preflight/ACTUAL_RESOURCE_ACCOUNTING.json');features=read(R/'03_geometry_only_selection/FEATURE_DECLARATION.json');sel=' → '.join(a['source_id'] for a in q)
 method='''The V1 target is a conditional numerical reference, not an experimental stress label. The publisher-processed measured front is retained at its original source IDs, coordinates, canonical triangles and T0 areas. Published processing includes aligned coordinates and a p=0.995 spline filter; no new smoothing is applied. Raw-scan registration and physical notch-radius accuracy remain unresolved.

The fixed area-weighted outer10%X Huber1.345 parent fit uses at most20iterations and coefficient stop1e-12. Parent acceptance is RMS≤0.10mm, P95≤0.20mm and |slope|≤0.02. The assumed rear is the parent plane offset19mm in its normal direction; four closures are synthetic. Full source→CAD and quadraticFE fidelity require P95≤0.010mm and maximum≤0.040mm, with forward/reverse definitions recorded separately.

Material E=210000MPa and ν=0.30 are modelling assumptions. Native ANSYS231/SOLID187 uses static linear elasticity, NLGEOM OFF, PCG1e-8, two threads. Nominal100MPa times documented19mm thickness and full28mm Yspan gives53200N at each port. Integrated affine Xtraction uses the common prescribed load line; six scalar gauges remove exactly six rigid modes. Applied force/couple tolerances are1e-8 and reaction tolerances1e-5 with frozen F and Ft normalization. No arbitrary loaded-face clamp is introduced.

M1/M2 nominal near-weld sizes0.40/0.30mm, parent0.60mm, bulk2.50mm and seed20261017 are unchanged. Tet10 quality requires SICN≥0.020 and positive Jacobians at73fixed points, one conforming solid, ≤350000nodes and ≤230000tetrahedra. Finite sampling is not a continuous whole-element positivity proof. M2/M1 median/P90 edge ratios≤0.98 and density>1 verify actual refinement.

Stress tensors come from the actual solved Tet10 displacement gradients and isotropic elasticity. Tensile maximum principal stress is clipped at zero before averaging. T2 uses original T0vertexareas in a same-face1mm three-dimensional Euclidean chord neighborhood, radius tolerance1e-7mm and complete-weight coverage≥1−1e-10. Full measured geometry, queried mapping halo and T2core are distinct. The source arrays have68457full-front points. Halo and core counts are read from each frozen source mask rather than assumed from the prior39200halo/34200core examples; seeSOURCE_SUPPORT_COUNTS.csv. C16 has39151queried halo points under the unchanged coordinate-distance rule. No source coordinates or masks are adjusted to force matching counts. No target is assigned outside valid support. The mapping/core masks are geometry-frozen before stress recovery.

Two-mesh qualification uses identical IDs/areas: whole normalizedL2≤0.020, worst regionalL2≤0.030, interpolated weighted-CDF high95areaIoU≥0.800 and coverage≥0.990; the fine M2 field is the denominator. Geometry-only weld/collar/parent proxy regions are not physically validated weld-toe tracks. Independent scalar tensor, brute-force T2, metric and CSV-roundtrip checks accompany release. Two-level agreement is numerical consistency, not demonstrated asymptotic convergence or physical local-notch validation.

There is no residual stress, plasticity, contact, crack growth, thermal simulation or fatigue-life prediction. No AI training, AI inference, external solver run, hyperparameter search or full-cohort production occurs in this phase.'''
 lineage='''Original metadata.csv, scan_files.csv, archive member contents/hashes/headers, package geometry_provenance.json, repository metadata, original readme and dissertation were inspected for all47development identities and12historical exposedtest identities. Test access was limited to provenance; no test target or AI-performance files were used for prospective selection.

A new documentary finding supersedes, without modifying, earlier UNKNOWN plate fields: dissertation §3.2.6/Figure3.9, PDFpage56, explicitly defines the initial letter as the steel plate code assigned during welding and the number as the specimen location within that plate. The S355MLO material scope is retained because letters also occur for other materials. Thus C/E/G/H/X are five documented parent-plate code groups, and59canonical coupon identifiers are traceable (47development,12historicaltest). This is documentary identity evidence, not independently authenticated physical serial-number certification. No47independent-plate claim is made.

Metadata absent for an AW state is linked only to an unambiguous treatment sibling with the same documented coupon stem, material/geometry and nominal thickness; the original metadata SpecimenName and condition are retained as evidence. It is not relabelled as direct AW metadata. Identical repeated X04 scan-table rows were collapsed for joins; originals remain unchanged and do not count as repeated acquisitions.

The thesis §4.3/PDFpage87 documents the Keyence LJ-V7080 method,0.05mm transverse spacing,0.5mm line spacing and separate surface scans. It does not provide per-source scan-session IDs, acquisition dates, instrument serials, precise cut coordinates, weld-bead IDs or manufacturing-batch identifiers. ZIP dates are packaging timestamps. Shared instrument family, grid or publication does not establish a shared acquisition session or production batch.

Confirmed same-plate and same-coupon relations imply mandatory grouping. Batch-level relations remain UNKNOWN; distinct plate codes do not establish cross-batch independence. All five plate groups occur in both development and historical exposedtest provenance, so source-identity separation alone is insufficient for a plate-independent historical test claim. The12historical tests remain quarantined.

The forensic screen was declared before computation: exact hashes; triangle/grid identity; translation-normalized rounded fingerprints; fixed-grid plane-detrended relief RMS/P95/correlation under four discrete mirror states and five prescribed offsets; a rigid-invariant fixed-point distance signature. Thresholds RMS≤0.005mm, P95≤0.010mm and correlation≥0.999 are screening choices, not measurement accuracy claims. No fitted rigid/nonrigid registration or stress-informed threshold tuning occurred.1081development pairs yielded0possible-duplicate flags. Common triangle connectivity reflects the standard grid, not shared physical identity. Low similarity never proves independence. Repeated/overlapping acquisitions outside this bounded screen remain possible.

Existing Aalborg provenance describes one conservative documented plate group with uncertain section/coupon independence; it is already exposed. No new external analysis was run and no untouched physically independent external validation cohort is established.'''
 lineage+='\n\nSource credit: Christian Dänekas, Research Data on Fatigue Tests of As-Welded, Deep-Rolled, and HFMI-Treated Joints, [DOI10.25835/0dojws6u](https://doi.org/10.25835/0dojws6u), [CCBY4.0](https://creativecommons.org/licenses/by/4.0/). E12 standardized rear/CAD, meshes, native solutions and T2 targets are derived numerical work, not original publisher experimental stress labels.\n\nPrimary local evidence: [dissertation nomenclature, extracted lines2162onward](E:/welding/WeldScan-FEA/data/metadata/dissertation_extracted.txt:2162), [original dissertation PDF, page56](E:/welding/WeldScan-FEA/data/metadata/dissertation.pdf), [original scan-file mapping](E:/welding/WeldScan-FEA/data/metadata/scan_files.csv), [original nominal metadata](E:/welding/WeldScan-FEA/data/metadata/metadata.csv), [publisher readme](E:/welding/WeldScan-FEA/data/raw/readme.md). Actual SHA256bindings are in01_provenance/PROVENANCE_INPUT_HASHES.csv.'
 selection='The exact prospective execution order is **'+sel+'**. The sealed E11 eight-feature geometry matrix and median/IQR scaling over the unchanged42eligible geometries were reused. References start with the eight qualified sources. Before ranking, a lexicographic objective was declared: prefer a documented parent plate absent from current references, then maximize the minimum standardized Euclidean geometry distance; absolute distance ties≤1e-12 use canonical ID lexicographic order. H12 adds missing H plate coverage; later rounds use geometric diversity. Unknown batch/session lineage does not exclude a candidate. Stress, K, solver outcomes and AI performance are absent from features. All160candidate-round rows, queue order and source hashes were sealed before CAD. Failed sources are not substituted. Selection is independently replayed by src/selection_audit_e12.py.'
 numerical=mt(met,['source_id','M1_mean_T2_MPa','M2_mean_T2_MPa','M2_max_T2_MPa','M2_nominal_Kmax','whole_L2','worst_regional_L2','high95_area_IoU','qualified'])
 decision=mt([dict(dimension=k,status=f[k]) for k in ['historical_inputs','physical_lineage','physical_independence','selection','resource_status','numerical_resource_gate','campaign_status','dataset_status','AI_readiness','independent_external_validation','overall_status']],['dimension','status'])
 resource='The current preflight measured Efree='+f"{live['E_free_GiB']:.6f}"+'GiB, Cfree='+f"{live['C_free_GiB']:.6f}"+'GiB, RAMavailable='+f"{live['RAM_available_GiB']:.6f}"+'GiB and commitavailable='+f"{live['commit_available_GiB']:.6f}"+'GiB. Conservative five-source peak='+f"{gate['forecast_peak_GiB']:.6f}"+'GiB, against24GiB cap. Remaining Espace after forecast='+f"{gate['expected_remaining_free_GiB']:.6f}"+'GiB, above20GiB reserve. Forecast uses all eight historical archives, largest1.430329GiB scaled350000/193962, four retained0.20GiB failed candidates per source (4GiB total),0.25GiB sequential transient headroom and0.5GiB phase overhead. Historical native-directory and retained scratch sizes are separately recorded. A continuous transient scratch peak cannot be reconstructed and is not invented. All controlled TEMP/TMP/MPLCONFIGDIR and CAD/mesh/native outputs are under the new E12root. Csystem reserve2GiB and available RAM/commit reserves3GiB are checked. Licensed feature availability is a snapshot; native checkout and completion are separately verified.\n\nActual resources:\n\n'+mt([{k:v for k,v in resources.items() if k!='source_archives'}],['sampled_peak_workspace_bytes','postproduction_workspace_bytes','minimum_sampled_E_free_bytes','sampled_peak_worker_RSS_bytes','sampled_peak_worker_private_bytes','C_minimum_sampled_free_bytes'])+'\nTelemetry is nominal2s plus filesystem-scan overhead. These are observed extrema, not continuous peaks. Later report/manifest bytes appear in the final release snapshot; no historical artifact was deleted.'
 resource+='\n\nAdministrative closeout correction: the first common-support CSV exporter repeatedly decompressed NPZ arrays per row. Only the two verified phase-owned exporter processes were terminated. The incomplete CSV and failed-stage ledger were preserved, arrays were cached once, and the export was rerun. No CAD, mesh, native solution, tensor recovery or T2 target was rerun or modified. See26_closeout/EXPORT_IMPLEMENTATION_CORRECTION.json and POSTPROCESSING_LEDGER.json. Their retained bytes and monitored resource samples remain in the new workspace.'
 grouped='''A future from-scratch model experiment can use the five documentary parent-plate groups as mandatory partition units: all coupons from one plate, all repeated scans, all crops and both mesh levels of a source remain together. FUTURE_GROUPED_SPLIT_FEASIBILITY.csv enumerates leave-one-documented-plate-out candidate designs and actual source counts; it contains no trained fold results. This is stronger than provisional source-family grouping. A batch-independent physical validation split is NOT verifiable because batch/session genealogy is absent. PHYSICAL_GROUPED_AI_EVALUATION_READY means the documented plate grouping design is available, not that physical independence or fresh independent generalization is established. Historical exposedtest identities and previously exposed Aalborg data cannot become a fresh external cohort through regrouping. Obtain author-confirmed plate/batch/acquisition ledgers and a separately held-out new cohort before independent physical generalization claims.'''
 parts={
 'HISTORICAL_V1_INTEGRITY.md':'Four historical read-only release verifiers passed; all8fine target hashes were independently checked, and2918manifest bindings were rehashed during initial verification.3768unique file contents were freshly hashed across the historical read-only verifier pass; cache entries are scoped to unchanged path/size/mtime within that pass, never stored expected hashes.47/42/5/8/34counts and12test quarantine were reconciled. The original46tests passed. See00_integrity logs and HISTORICAL_RELEASE_HASHES.json.',
 'FROZEN_PROTOCOL_VERIFICATION.md':method+'\n13pure scientific modules are byte-identical to qualifiedR3; administrative root/queue/resource/provenance adapters are listed in src/adapt_e12.py and00_integrity/SCIENTIFIC_KERNEL_REUSE.json. The independent24GiB authorization does not amend historical E11policies.',
 'REMAINING34_SOURCE_REGISTRY.md':mt(rows(R/'REMAINING34_ELIGIBILITY.csv')),
 'PHYSICAL_PROVENANCE_AUDIT.md':lineage,
 'PHYSICAL_DEPENDENCY_GRAPH.md':lineage+'\nGraph: PHYSICAL_DEPENDENCY_GRAPH.json and PHYSICAL_DEPENDENCY_EDGES.csv bind entity pairs to documentary fields, confidence, verification, grouping and UTC.',
 'GEOMETRY_DUPLICATE_SCREENING.md':lineage+'\nSee01_provenance/FORENSIC_SCREEN_PREREGISTRATION.json, GEOMETRY_DUPLICATE_SCREEN.csv, all1081pair rows in GEOMETRY_PAIRWISE_SCREEN.csv and the header-only POTENTIAL_SHARED_SPECIMEN_PAIRS.csv because no threshold flag occurred.',
 'SOURCE_LINEAGE_UNCERTAINTIES.md':lineage,
 'SOURCE_SELECTION_PROTOCOL.md':selection,
 'FIVE_SOURCE_PREREGISTRATION.md':selection+'\n\n'+mt(q,['order','source_id','dependency_group','nominal_thickness_mm','eligible']),
 'LIVE_RESOURCE_PREFLIGHT.md':resource,
 'CONSERVATIVE_RESOURCE_FORECAST.md':resource+'\n\n'+mt(rows(R/'FIVE_SOURCE_STORAGE_FORECAST.csv'),['scenario','batch_peak_GiB','retained_failed_attempt_allowance_GiB','temporary_solver_headroom_GiB','historical_archives']),
 'STANDARDIZED_PARENT_DATUM.md':method+'\n\n'+mt(rows(R/'PARENT_DATUM_FITS.csv'),['source_id','parent_RMS_mm','parent_P95_abs_mm','slope_X','slope_Y','screen_pass']),
 'STANDARDIZED_CAD_GEOMETRY.md':method+'\nNewCADcandidates='+str(f['new_CAD_candidates'])+'. All candidates/failures are retained; no historicalfrontSTEP was overwritten.',
 'SOURCE_CAD_FIDELITY.md':method+'\n\n'+mt(rows(R/'SOURCE_CAD_FIDELITY.csv'),['source_id','level','scope','passed','source_forward_P95_mm','source_forward_max_mm','CAD_reverse_P95_mm','CAD_reverse_max_mm']),
 'M1_M2_MESH_QUALITY.md':method+'\n\n'+mt(quality,['source_id','level','candidate','nodes','Tet10','minSICN','minimum_Q1_J_mm3','pre_solver_qualified']),
 'TET10_REPAIR_AND_RECOVERY.md':f"Actual local trials={f['local_repair_trials']};actual moved nodes={f['actual_moved_nodes']};M1/M2fullcandidatecounts={f['full_M1_candidates']}/{f['full_M2_candidates']}. S1 interior midside optimization may preserve all corners/connectivity/external boundaries; eligible support is not counted as moved. All73point/globalquality and full-source fidelity checks are repeated for a retained repair candidate. No optional S2orS3 execution is claimed when absent. Candidate limits2CAD,3M1,3M2and stricter inherited3S1trials/source remain durable. SeeLOCAL_MESH_REPAIR_ATTEMPTS.csv, LOCAL_NODE_DISPLACEMENTS.csv and per-case ACTUAL_REPAIR_AUDIT.json.",
 'NATIVE_SOLID187_IMPORT.md':method+'\n\n'+mt(rows(R/'NATIVE_IMPORT_COUNTS.csv'))+'\nGmsh permutation[0,1,2,3,4,5,6,7,9,8] and coordinate/connectivity roundtrip are independently checked using native DB/CDB evidence.',
 'STANDARDIZED_BVP_ASSEMBLY.md':method+'\nSigned integration and independent36pointDuffy versus7pointDunavant audits are retained in02_mesh_import per mesh. Material association, ports and rank-six gauges are checked before native SOLVE.',
 'NATIVE_SHAPE_CHECKS.md':'SHPP ON is applied inPREP7. Native warnings are retained and classified with actual element identity/location and independent quality; fatal errors block. No warning suppression.\n\nWarnings:\n\n'+mt(warnings)+'\nErrors:\n\n'+mt(errors),
 'PRE_SOLVE_GATES.md':method+'\nSource-specific PRE_SOLVE_GATE_SEALED.json binds actual source,CAD,mesh,BVP,native imports and schemas before SOLVE.\n\n'+mt(rows(R/'PRE_SOLVE_GATES.csv')),
 'NATIVE_ANSYS_EXECUTION.md':f"Nativepreprocessingjobs={f['native_preprocessing_jobs']};SOLVEinvocations={f['actual_native_SOLVE_invocations']}/10;successfulsolutions={f['successful_native_solutions']}. Jobs are sequential,2SOLVEs/source maximum; interrupted stages require evidence reconciliation rather than automatic retry. Exit0or anRST alone is insufficient: actual LOADSTEP1SUBSTEP1COMPLETED/RUNCOMPLETED markers, finite displacement/stress output and equilibrium must pass.\n\n"+mt(rows(R/'SOURCE_EXECUTION_LEDGER.csv')),
 'FORCE_MOMENT_EQUILIBRIUM.md':method+'\n\n'+mt(eq,['source_id','level','force_residual_relative','moment_residual_over_Ft','Umax_mm','equilibrium_passed']),
 'INDEPENDENT_TENSOR_RECOVERY.md':method+'\n\n'+mt(rows(R/'INDEPENDENT_TENSOR_CHECKS.csv')),
 'ORIGINAL_SOURCE_MAPPING.md':method+'\nFull pointwise SOURCE_T2_M1.csv/SOURCE_T2_M2.csv retain specimenIDand original pointID; blank outside-support targets are not zero. Full sourcegeometrycoverage and queriedhalocoverage are separate quantities.\n\n'+mt(rows(R/'SOURCE_MAPPING_COVERAGE.csv')),
 'V1_T2_QUALIFICATION.md':method+'\n\n'+numerical,
 'INDEPENDENT_T2_VERIFICATION.md':method+'\nScalar T2 checks reconstruct neighbors by direct distance against all original points rather than reuse cached sparse neighborhoods. Final release audit additionally checks full CSVroundtrip and scalar constitutive tensors from actual displacements.\n\n'+mt(rows(R/'INDEPENDENT_T2_VERIFICATION.csv')),
 'CUMULATIVE_QUALIFIED_V1_DATASET.md':mt(registry,['source_id','qualification_status','T2_L2','T2_worst_regional_L2','T2_high95_IoU','confirmed_parent_plate','physical_independence'])+'\nCumulativequalified='+str(len(registry))+';remainingeligible='+str(42-len(registry))+'. M1/M2are one computational source. Historical target bytes are reused unchanged.',
 'PHYSICAL_DEPENDENCY_GROUPS.md':lineage+'\n\n'+mt([a for a in rows(R/'CONFIRMED_PHYSICAL_GROUPS.csv') if a['evidence_level']=='CONFIRMED_PARENT_PLATE_GROUPS']),
 'FUTURE_GROUPED_SPLIT_FEASIBILITY.md':grouped+'\n\n'+mt(rows(R/'FUTURE_GROUPED_SPLIT_FEASIBILITY.csv'),['proposed_holdout_parent_plate','heldout_source_count','training_source_count','evidence_level','cross_plate_batch_relationship','actual_training']),
 'DATA_LEAKAGE_READINESS_AUDIT.md':grouped+'\nAll5platecodes occur in both development and exposedtest provenance. A source-random future split would mix same-plate coupons. Unknown relationships are disclosed rather than declared independent. LEAKAGE_RISK_REGISTRY.csv retains all59identities and quarantine status.',
 'RESOURCE_ACCOUNTING.md':resource+'\n\n'+mt(cost,['source_id','archive_GiB','CAD_s','meshes_and_hierarchy_s','native_imports_audits_s','native_SOLVE_stage_s','recovery_T2_package_s']),
 'REMAINING_COHORT_FORECAST.md':resource+'\n\n'+mt(rows(R/'REMAINING_COHORT_RESOURCE_FORECAST.csv'))+'\nNo further batch is authorized or launched.',
 'SCIENTIFIC_LIMITATIONS.md':method+'\n\n'+lineage+'\n\n'+grouped,
 'FINAL_R8E12_DECISION.md':decision+'\n\n'+numerical+'\nPhysical-lineage investigation and numerical qualification are independent outcomes. OverallPARTIAL explicitly preserves unresolved batch/acquisition/physical-independence limitations even if5/5numericallyqualify.\n\n'+grouped,
 'README_REPRODUCIBILITY.md':'Use E:/welding/outputs/WeldScan_MechanicalBenchmark_Phase5E/.venv/Scripts/python.exe -B with src/verify_release_e12.py for read-only release verification. Do not restart training or native solved jobs. Native input.dat,MODEL.db,file.rst,MODEL.cdb,logs and resource samples remain under cases/<source>. Qualified fine targets and sourceprovenance are under QUALIFIED_V1_PACKAGE; cumulative registry binds their hashes. Manifest excludes only its own self-reference/seal/verification receipt and temporary cache. Scripts copied from prior phases are reference code; obsolete setup_e11r1.main and old release/selection mains must not be executed in this phase. Scientific kernels remain byte-identical; E12 administrative entrypoints are initialize_e12.py,campaign_e11r1.py,aggregate_e12.py,deliverables_e12.py,figures_e12.py,reports_e12.py and verify_release_e12.py.'}
 # All56questions explicitly answered from actual records.
 metric=lambda k:'; '.join(a['source_id'][:3]+': '+format(float(a[k]),'.10g') for a in met) or 'NOT_EXECUTED'
 answers=[
 'Yes. All8historicalfine target packages and the fourhistoricalread-onlyrelease verifiers passed SHA256/scalar checks.',
 'Yes;46/46originaltests passed, log00_integrity/E9_46_TESTS.log.',
 'Yes;42of47developmentidentities pass the unchanged geometric/BVP eligibility screen.',
 'Yes;42−8=34remainingidentities were confirmed before selection.',
 'Originalmetadata/scanmaps/memberhashes/ZIPheaders,geometryprovenance,readme,repositorymetadata and dissertation3.2.6/4.3; no source-specific batch/session ledger.',
 '47documentarydevelopmentcouponidentifiers plus12historicaltestcouponidentifiers;0independentlyauthenticatedphysicalcouponcertifications. Shared-plate dependence prevents treating them as59independentunits.',
 'Five documentaryS355MLOplatecodegroups C/E/G/H/X from explicit nomenclature. No independentlyauditeduniqueplateserialledger or cross-batch independence certificate.',
 'Zero identified manufacturingbatchIDs; commonmanufacturer/method is not proof of samebatch.',
 'Within-source front/back/raw/processedmapping and samecouponstem; sameletter+S355MLO identifies the same documented parentplate under thesis3.2.6. See graph/evidence rows.',
 'Manufacturingbatches,per-sourcesessions/acquisitiontimes,instrumentserials,beadIDs,exactadjacentcutcoordinates and cross-plate independence remain unresolved.',
 'No exact/thresholdpossibleduplicate flags among1081developmentpairs. Sharedgrid/connectivity and repeatedidenticalX04metadata rows are not repeatedscan proof. Bounded screen cannot exclude other overlapping acquisitions.',
 'No. Geometric flags are explicitly onlyPOSSIBLE_DEPENDENCY_FLAG; plate relationships rely on documentary naming definitions.',
 sel,
 'Yes; only frozengeometrydescriptors and documentedplatecoverage were used. No stress,AIerror,Kor solveroutcome feature.',
 'Yes; SOURCE_SELECTION_SEAL.json and PREREGISTRATION_SEAL.json precede CAD and all nativejobs.',
 'Yes; prospectively prefer an unrepresented documentedparentplate, then max-min distance. H12addsHcoverage. Unknownbatch/session status did not exclude sources.',
 f"{live['E_free_GiB']:.9f}GiB at the current preflight timestamp{live['UTC']}.",
 f"{gate['forecast_peak_GiB']:.9f}GiB conservativeworkspacepeak including4GiBfailedcandidateallowance and0.25GiBtransientheadroom.",
 'Yes; '+str(gate['checks']['workspace'])+';24GiBcap unchanged throughout this newphase.',
 f"Yes; projectedfreeEafterforecast{gate['expected_remaining_free_GiB']:.6f}GiB≥20GiB; observedminima separately recorded.",
 resource.split('\n\n')[0],
 'Sourcearrays/IDs/T0/triangles and historicalfrontBRep were reused unchanged; inputhashes and final independentaudit establish preservation for executedsources.',
 '19mm nominal: directmetadata or explicitly linked unambiguoustreatment-siblingmetadata plus thesisS355MLOspecification. Not independently measured specimen thickness.',
 'For executedCAD, parent-derived normaloffset rule and STEPexport/reimport gates apply; see REAR_PLANE_DEFINITIONS.csv. Unexecuted cases remainNOT_EXECUTED.',
 'ExecutedqualifiedCAD/FE must pass bothdirectionsP95≤.010mm/max≤.040mm; actualpassed/status values are inSOURCE_CAD_FIDELITY.csv.',
 str(f['new_CAD_candidates']),
 f"M1={f['full_M1_candidates']};M2={f['full_M2_candidates']};all fullcandidates including failed/repairmaterializations counted.",
 f"Localtrials={f['local_repair_trials']};actualmovednodes={f['actual_moved_nodes']};see retainedcandidateproof,not eligible-nodecounts.",
 'Qualifiedselectedmesh checks: '+mt(quality,['source_id','level','minSICN','minimum_Q1_J_mm3','pre_solver_qualified']),
 'Nativeimport/shapeacceptance is mandatory beforeSOLVE; actual receipts and warning/error tables retained.',
 f"Classifiedwarnedelementrecords={len(warnings)};nativeerrorrecords={len(errors)}. NativeSOLVE warningmessagecounts are also preserved in T2metric/solve receipts.",
 'Yes for executedqualifiedcases:100MPa×19mm×full28mm=53200N/port,globalX,commonparentmid-minus9.5normalfactor loadline; no crop-basedforce.',
 'Independentloadintegration,forces/couples,gaugerank and tractionbounds are pre-solvegates; seeSIGNED_FORCE_MOMENT_AUDIT.csv andsourcepresolveseals.',
 str(f['native_preprocessing_jobs']),str(f['actual_native_SOLVE_invocations']),str(f['successful_native_solutions']),
 mt(eq,['source_id','level','force_residual_relative','moment_residual_over_Ft','equilibrium_passed']),
 'Independentconstitutive scalarchecks use actualTet10U/J/strain; receipts and releaseverification report numericalerrors. No nearestnodal-stresscopy.',
 'See actual SOURCE_MAPPING_COVERAGE.csv: originalpointIDs/XYZ/T0 unchanged; queriedhalo and completecore distinct from fullgeometry.',
 'Yes; originalT0area,1mm3Dsamefacechord,+1e-7tolerance,tensileprincipalbeforeaverage and completeweight1−1e-10 are unchanged.',
 metric('whole_L2'),metric('worst_regional_L2'),metric('high95_area_IoU'),
 '; '.join(a['source_id'] for a in new) or 'None.',str(len(registry)),str(42-len(registry)),
 json.dumps(f['campaign_stop']) if f['campaign_stop'] else 'No mandatorycampaignstop occurred.',
 resource,
 str(f['documented_cumulative_parent_plate_groups'])+'documentaryparentplategroups represented in cumulativequalifiedregistry;0independentlycertifiedcross-batchindependencegroups.',
 'A documentaryparentplate-heldout design is defensible at the naming-evidence level; a batch-independent physicallycertifiedsplit is NOTverifiable.',
 'Missingbatch/session/acquisition/cutpositionrecords and lackofuntouchedexternalcohort; all historicaltestplates overlap developmentplatecodes.',
 'Yes; all12historicalexposedtestIDs remain quarantined; provenanceonly was opened in E12.',
 grouped,
 'No. Aalborg is alreadyexposed and oneconservativeplategroup; no freshphysicallyindependentexternaltestcohort established.',
 method,
 'Separatelyauthorize author-backedplate/batch/acquisitiongenealogy, an untouchedindependentcohort and a preregisteredfrom-scratchplate-heldout learningstudy. FurtherFEproduction requires a newboundedresourcegate/authorization; no automaticcohortlaunch.'
 ]
 assert len(answers)==56
 spec=(R/'R8E12_USER_SPECIFICATION.txt').read_text(encoding='utf-8-sig');block=spec.split('# 29. REQUIRED FINAL SCIENTIFIC QUESTIONS')[1].split('# 30.')[0];questions=re.findall(r'^\d+\. (.+)$',block,re.M);assert len(questions)==56
 master='# R8-E12 — Staged standardized V1 expansion and physical dependency audit\n\n'+decision+'\nNumerical results:\n\n'+numerical+'\nFrozen selection: '+sel+'\n\n'+lineage+'\n\n'+resource+'\n\n'+grouped+'\n\n'
 for i,(question,answer) in enumerate(zip(questions,answers),1):master+=f'### {i}. {question}\n\n{answer}\n\n'
 master+='## Inspectable outputs\n\n[Fine target qualification](V1_T2_QUALIFICATION.md), [physical evidence](PHYSICAL_PROVENANCE_AUDIT.md), [grouped design](FUTURE_GROUPED_SPLIT_FEASIBILITY.md), [independent release receipt](25_reproducibility/INDEPENDENT_RELEASE_VERIFICATION.json).\n\n![M2 T2](23_figures/23_Original_source_M2_T2.png)\n\n![Physical graph](23_figures/07_Physical_dependency_graph.png)\n'
 (R/'R8E12_MASTER_REPORT.md').write_text(readable(master),encoding='utf8')
 parts['README_REPRODUCIBILITY.md']+='\n\nTargeted visual QA uses visual_qa_e12.py for legends and stress_visual_scale_e12.py for common M1/M2 scales and zero-centered differences; no stress values change. Final sealing uses seal_release_e12.py, which hashes all durable new artifacts and rereads historical bindings before independent tensor/T2/CSV verification. Read-only repeat audit is verify_release_e12.py without --write-receipt. Native completed jobs must never be rerun to reproduce a report.'
 for name,body in parts.items():(R/name).write_text(readable('# '+name.removesuffix('.md').replace('_',' ')+'\n\n'+body+'\n'),encoding='utf8')
 shutil.copy2(R/'HISTORICAL_V1_INTEGRITY.md',R/'R8E12_HISTORICAL_INTEGRITY.md');shutil.copy2(R/'SOURCE_LINEAGE_UNCERTAINTIES.md',R/'DEPENDENCY_AUDIT_LIMITATIONS.md')
 print('REPORTS_READY',len(parts)+1,'56explicitquestions',flush=True)
if __name__=='__main__':main()
