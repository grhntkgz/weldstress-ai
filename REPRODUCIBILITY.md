# Reproducibility and restoration

The expanded public release supplies the retained bulk data and model binaries missing from the original two small archives. The file/asset manifests describe exactly what can be downloaded. `source/` exposes archived Python files unchanged for review; runnable sibling-workspace paths are restored from the release assets, not inferred from this code-only view.

## Safe artifact-only commands

```console
python tools/download_artifacts.py --destination downloads
python tools/verify_and_restore.py --downloads downloads
python tools/verify_and_restore.py --downloads downloads --restore restored
```

Python 3.10+ standard library is required. The repository and release assets are public; the archived downloader still uses GitHub credentials, while assets can also be downloaded directly from the public release page. They never import research code or start ANSYS, training, inference or optimization. They verify each archive SHA-256, exact membership, each member SHA-256 and byte size. The restorer resolves paths inside the selected destination, rejects path traversal/symlinks and refuses to replace differing files. Downloading and checking the data does not rerun scientific validation.

For the old small preparation snapshot only, `python verify_release.py` still verifies its refreshed root manifest and archived provenance. That is not a check of the large release assets.

## Historical environments and path dependencies

The recorded neural environment uses CPU PyTorch 2.6.0. The separate B2 environment records XGBoost 3.0.2, scikit-learn 1.6.1 and NumPy 2.2.6. Source also uses NumPy, SciPy, pandas, matplotlib and psutil; CAD/meshing/native extraction stages additionally require their historical CAD/Gmsh/ANSYS environments and licenses. Retained configuration, source and environment reports are supplied. These records are not a tested portable lockfile.

Archive members preserve `outputs/<original-stage>/...` sibling layout. Registries and guards retain historical `E:/welding/outputs` paths and stage-specific expectations; restoration elsewhere alone does not port these entry points. Do not run archived campaign/solver entry points as a smoke test. A future separately authorized portability effort should use a new workspace, map paths explicitly, validate dependency imports, and preserve held-out splits and closed outcomes.

## Verified level by stage

| Stage | Retained material / verified limit |
|---|---|
| Geometry preparation | Processed XYZ/IDs/triangles/T0 and context arrays supplied; original raw archive external, independent raw registration unresolved |
| FE construction | M1/M2 native inputs/databases, meshes, processed solids, BVP and quality/qualification records supplied; fresh native build/solve not executed |
| Native stress extraction | Native results and processing/mapping source supplied; clean-environment extraction not executed |
| T2 construction | Frozen references, source weights/IDs and operator/qualification records supplied; no new reference field produced |
| Features | Feature arrays, context geometry, original query/core and source definitions supplied; no fresh full regeneration |
| Neural training | 30 final N1/N2/N3 checkpoints, seed/fold/config/training records supplied; no retraining or bitwise-training certification |
| Neural inference | Source, retained checkpoints and canonical predictions supplied; no fresh model execution during release |
| XGBoost | Five models, source/config/sample/prediction records supplied; no new inference |
| Controlled substitutions | All 832 fields and source/contracts supplied; no new interventions |
| Spatial evaluation | Source/area/mask contracts and comparison/robustness tables supplied; retained published-cell arithmetic was checked in the final manuscript audit |
| Tables/figures/manuscript | Retained outputs, source and final verified author package supplied; final audit reports state performed checks and author/journal limitations |

Current conclusion: retained-artifact availability and byte integrity can be verified independently by repository users. A clean end-to-end computational reproduction and independent physical stress/fatigue validation remain NOT TESTED/NOT CLAIMED. The repository and its release assets are publicly accessible as of 24 October 2026.


## Original C02 mesh-pair dependency

The initial native C02 solver stage references the preceding R8E10R1 mesh-pair source. An additional **60 files (56,803,727 original bytes)** are preserved in the small Git-tracked `auxiliary/c02-original-mesh-source.zip` (33,103,122 compressed bytes), with per-member/ZIP hashes in `release/REPOSITORY_AUXILIARY_FILES.csv`. Both original C02 meshes, labelled MSH files, the frozen STEP and measured-source arrays match their original mesh-pair release hashes. These add to the 7,716 files in the large release assets and bring the original selected mesh-pair coverage to all 26 M1/M2 meshes. Default `tools/verify_and_restore.py` includes this repository-local auxiliary archive when verifying/restoring all assets. The original sources and results were not changed.
