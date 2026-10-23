# WeldStress AI

Research companion to **Geometry representation and observation context in learning stress fields from scanned welded joints**.

**Status: private preparation snapshot.** This repository is not yet a public, versioned scientific release. No repository DOI has been requested. No new FE calculation, training, inference or scientific metric computation was performed while preparing it.

The study concerns thirteen processed measured weld fronts from five documentary parent-plate groups. The numerical FE solid assumes a planar rear, isotropic linear elasticity (E = 210 GPa, Poisson ratio 0.30), and standardized nominal tension of 100 MPa. T2 is a declared original-area-weighted numerical tensile maximum-principal-stress reference; it is not an experimental stress measurement or a validated physical weld-toe stress.

## Contents

| File | Scope |
|---|---|
| `research-source.zip` | Original archived Python source for R8E16 and the R2.1 robustness assessment, with source hashes |
| `derived-tables-and-contracts.zip` | 42 existing supplementary CSV tables, method contracts, and selected checkpoint/training/prediction registries |
| `SOURCE_PROVENANCE.csv` | Original source hashes, exported hashes and disclosed path-only transformations |
| `MANIFEST_SHA256.csv` | SHA-256 checksums for this repository snapshot |
| `verify_release.py` | Standard-library integrity and archive-member verification; does not execute research code |
| `REPRODUCIBILITY.md` | What is and is not reproducible from this first snapshot |
| `DATA_SOURCES.md` | Experimental source attribution and distinction from derived FE/model data |
| `AVAILABILITY_DRAFT.md` | Current honest availability wording and a conditional public-release template |
| `CITATION.md` | Citation guidance without a new DOI |

## Verify and unpack

Use Python 3.10 or newer. No scientific packages are needed for the integrity check:

```console
python verify_release.py
python -m zipfile -e research-source.zip research-source
python -m zipfile -e derived-tables-and-contracts.zip derived-data
```

Do not run archived campaign/training/solver entry points as a repository smoke test. They retain the original multi-workspace dependencies and output-writing behavior. Read `REPRODUCIBILITY.md` first.

## Scientific scope

The retained conclusion is **METHOD_IMPROVEMENT_MIXED**: N3 improves aggregate relative High95 localization compared with N2 while increasing whole-field L2 and worsening absolute peak-amplitude error. Adverse X-group, seed, threshold and regional comparisons remain included. These reused documentary groups do not provide fresh independent generalization validation. No physical stress or fatigue-life validation is claimed. Research remains closed.

The original experimental repository retains its existing DOI; our code/data snapshot has no DOI. Once a public reviewed version exists, cite its repository URL, version tag and full commit identifier. A private link alone does not establish public availability.

## Rights and preparation status

Original scans are linked rather than redistributed here. Code and derived-data licensing has not yet been selected by the rights holders. No new open-source reuse permission is asserted for this preparation snapshot. See `RIGHTS_AND_RELEASE_STATUS.md`. The unpublished article, title page, private author documents, native ANSYS databases/results, complete geometry caches and model binaries are not included.
