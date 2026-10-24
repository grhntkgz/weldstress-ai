# Curated artifact release reproducibility-2026-10-24

Scope: complete retained inputs/outputs curated for the completed thirteen-specimen manuscript comparison, not a mirror of every historical WeldScan/WeldStress project or a newly verified clean-room workflow.

Release: https://github.com/grhntkgz/weldstress-ai/releases/tag/reproducibility-2026-10-24. File manifest: `release/ARTIFACT_MANIFEST.csv`; archive manifest: `release/ASSET_MANIFEST.json`; curation map: `release/CURATION_PLAN.json`.

| Category | Files | Original bytes |
|---|---:|---:|
| geometry-targets | 520 | 2696501150 |
| models | 35 | 14602063 |
| predictions | 299 | 267525854 |
| methods-results | 3339 | 686889553 |
| factorial | 832 | 608206073 |
| features | 156 | 545024156 |
| native-C02-V1-S355-AW | 6 | 655166799 |
| native-G08-V1-S355-AW | 6 | 619389757 |
| native-X10-V1-S355-AW | 6 | 622142318 |
| native-X23-V1-S355-AW | 6 | 626402130 |
| native-G25-V1-S355-AW | 6 | 644555616 |
| native-C05-V1-S355-AW | 6 | 652157939 |
| native-G04-V1-S355-AW | 6 | 634725230 |
| native-E21-V1-S355-AW | 6 | 641672081 |
| native-H12-V1-S355-AW | 6 | 645211060 |
| native-C16-V1-S355-AW | 6 | 643703697 |
| native-H19-V1-S355-AW | 6 | 641540988 |
| native-G16-V1-S355-AW | 6 | 632300419 |
| native-G07-V1-S355-AW | 6 | 622470019 |
| figures | 501 | 361514122 |
| fe-support | 1890 | 3952793013 |
| manuscript | 1 | 54204931 |
| fe-recovery-arrays | 65 | 200131017 |

All 13 registered native M1/M2 cases are included using their actual E10/E11/E12 case roots. The source manifest retains exact bytes, original paths, expected historical hashes where available, and new SHA-256 hashes for all included files. Every ZIP member was hashed and compared locally; remote release-asset SHA-256 and size checks are recorded in `release/GITHUB_COMPLETE_DELIVERY_RECEIPT.json` once upload verification completes. The old small snapshot archives remain as historical artifacts, not the complete release.

## Intentional exclusions

1. Original third-party raw scan archive: use DOI 10.25835/0dojws6u with CC BY 4.0 attribution. Processed article geometry and original identifiers are included.
2. Unrelated earlier specimens/experiments, transient solver scratch/lock files, virtual environments, duplicate qualified-package copies and obsolete page-render caches.
3. Legacy shifted-context/stitching study arrays and very large long-form CSV duplicates outside the final fixed-S0 article comparison. The 299 canonical comparison fields and 832 factorial fields are supplied. Historical reports/manifests can reference excluded old-stage artifacts; their existence as provenance is not a claim that every historical campaign was mirrored.

## Scientific and implementation qualifications

The original reports, receipts and manuscript availability audit describe the situation when each was issued. Their bytes are preserved rather than silently rewritten. This release subsequently adds locally retained artifacts to the same repository. The owner separately authorized public visibility on 24 October 2026. The article's numerical outcomes remain unchanged. In controlled descriptor substitutions context-point identities are fixed, but encoded context values can change. N3 Z anchoring follows the registered tile XY center; the rear datum uses the outer 10% X span on each side. The final manuscript audit documents these corrections.

No clean-environment retraining, native solve, model inference or field-level reanalysis was performed. Artifact completeness, local archive integrity and remote byte delivery are separate from computational reproduction or physical validation. Public access was explicitly authorized separately from the original upload. No new open-source license, article approval or DOI is inferred from this visibility change.


## Original C02 mesh-pair dependency

The initial native C02 solver stage references the preceding R8E10R1 mesh-pair source. An additional **60 files (56,803,727 original bytes)** are preserved in the small Git-tracked `auxiliary/c02-original-mesh-source.zip` (33,103,122 compressed bytes), with per-member/ZIP hashes in `release/REPOSITORY_AUXILIARY_FILES.csv`. Both original C02 meshes, labelled MSH files, the frozen STEP and measured-source arrays match their original mesh-pair release hashes. These add to the 7,716 files in the large release assets and bring the original selected mesh-pair coverage to all 26 M1/M2 meshes. Default `tools/verify_and_restore.py` includes this repository-local auxiliary archive when verifying/restoring all assets. The original sources and results were not changed.
