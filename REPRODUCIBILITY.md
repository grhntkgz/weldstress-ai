# Reproducibility and restoration

The expanded private release supplies the retained bulk data and model binaries missing from the original two small archives. The file/asset manifests describe exactly what can be downloaded. `source/` exposes archived Python files unchanged for review; runnable sibling-workspace paths are restored from the release assets, not inferred from this code-only view.

## Safe artifact-only commands

```console
python tools/download_artifacts.py --destination downloads
python tools/verify_and_restore.py --downloads downloads
python tools/verify_and_restore.py --downloads downloads --restore restored
```

Python 3.10+ standard library and authorized GitHub access suffice for these tools. They never import research code or start ANSYS, training, inference or optimization. They verify each archive SHA-256, exact membership, each member SHA-256 and byte size. The restorer resolves paths inside the selected destination, rejects path traversal/symlinks and refuses to replace differing files. Downloading and checking the data does not rerun scientific validation.

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

Current conclusion: retained-artifact availability and byte integrity can be verified independently by authorized repository users. A clean end-to-end computational reproduction and independent physical stress/fatigue validation remain NOT TESTED/NOT CLAIMED. The repository remains private.
