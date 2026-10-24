# WeldStress AI

Research companion to **Geometry representation and observation context in learning stress fields from scanned welded joints**.

**Private retained-artifact release.** The repository remains private; this does not establish public data/code availability. [Versioned release assets](https://github.com/grhntkgz/weldstress-ai/releases/tag/reproducibility-2026-10-24) now supply the curated bulk artifacts omitted from the original preparation snapshot. No new DOI, code/data license or scientific result is created by this delivery.

## What is supplied

- 7,716 retained files, 17.669 GB before ZIP compression, in 31 independently verifiable data archives.
- Original processed front geometries, original point IDs/areas/triangles, FULL/X50/X43 context geometry, query/core arrays and N3 features for the thirteen-specimen article cohort.
- 30 frozen N1/N2/N3 neural checkpoints, five XGBoost models, configurations, splits, seeds, training records and source.
- All 299 canonical article comparison prediction fields and 832 factorial prediction fields; numerical FE/T2 references, metric and robustness tables.
- All thirteen specimens' retained M1/M2 ANSYS databases, result files and input decks, supporting processed solids/mesh/mapping/BVP/qualification records.
- Final revised manuscript DOCX/PDF, actual G07 point-cloud and executed-M2 figures, final source/reference/document audits and SHA-256 evidence (inside `manuscript-01.zip`).
- Readable retained Python source under `source/`, in addition to the unchanged original two small snapshot ZIPs.

See [COMPLETE_RELEASE.md](COMPLETE_RELEASE.md) for scope and exclusions, [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for restoration/dependencies, and `release/ARTIFACT_MANIFEST.csv` for every file and SHA-256. Large binaries live in the repository's GitHub Release assets, not regular Git history, following [GitHub's large-binary guidance](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases).

- Additional original C02-mesh-source dependency: 60 files in the small Git-tracked `auxiliary/c02-original-mesh-source.zip`, included automatically by the full verification/restoration command. Total retained artifact coverage: **7,776 files**; see `release/REPOSITORY_AUXILIARY_FILES.csv`.

## Download and verify — no simulation or model execution

```console
python tools/download_artifacts.py --destination downloads
python tools/verify_and_restore.py --downloads downloads
python tools/verify_and_restore.py --downloads downloads --restore restored
```

Authorized access to the private repository is required. The downloader uses `GH_TOKEN`/`GITHUB_TOKEN` or the existing Git credential helper; do not put a token in a script or commit. Restoration creates `restored/outputs/<historical-stage>/...` and refuses to overwrite different existing files. It does not run archived research scripts. Historical absolute-path guards and licensed/software dependencies remain: see the reproducibility limits before invoking any archived computational entry point.

## Scientific scope and source attribution

The article uses thirteen processed measured weld fronts from five documentary groups, two fixed seeds, an assumed planar rear, isotropic linear elasticity E=210 GPa and ν=0.30, and standardized nominal tension 100 MPa. T2 is a declared numerical area-weighted tensile-principal-stress reference, not an experimentally measured stress or physically validated weld-toe stress. The conclusion remains **METHOD_IMPROVEMENT_MIXED**: relative localization improves in aggregate while whole-field and peak-amplitude errors worsen; group-X and extreme-threshold failures remain included. Previously examined groups do not establish fresh independent generalization or fatigue-life validation.

Original source scans/experimental metadata are linked via [Dänekas, version 1.0, DOI 10.25835/0dojws6u](https://doi.org/10.25835/0dojws6u), CC BY 4.0. The original third-party raw archive is not mirrored. No new FE solve, meshing, training, inference or optimization was executed while preparing this release. See [DATA_SOURCES.md](DATA_SOURCES.md), [RIGHTS_AND_RELEASE_STATUS.md](RIGHTS_AND_RELEASE_STATUS.md) and [AVAILABILITY_DRAFT.md](AVAILABILITY_DRAFT.md).
