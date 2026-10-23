# Reproducibility scope

## Available now

The archives provide original research Python source, released tables and explicit definitions of model architecture, original vertex areas, area-weighted errors, High95 thresholds, grouped evaluation and the retained robustness contracts. `verify_release.py` checks repository bytes, source/export provenance and ZIP integrity without importing or executing the archived code.

R8E16 `model_e3.py` contains the executed SurfacePT forward override; `base_arch.py` supplies its parent layers. Other model classes in that parent module are historical definitions, not additional experiments in this article. Read `N3_ARCHITECTURE_AND_TRAINING.json` for the actual 19-input, width-24, one-block, 7,228-parameter model, two fixed seeds and final-epoch checkpoint policy.

The recorded neural environment uses CPU PyTorch 2.6.0. The separate B2 environment uses XGBoost 3.0.2, scikit-learn 1.6.1 and NumPy 2.2.6. This is descriptive environment information, not a tested portable dependency lock. Python packages used by historical modules also include NumPy, pandas, SciPy, matplotlib and psutil; document-generation modules may require python-docx. Do not install or run those modules to perform the standard-library integrity check.

## Not yet a standalone end-to-end package

Archived code assumes the original sibling-workspace layout (R8E12, R8E13, R8E14, R8E15, R8E16 and manuscript-assessment workspaces), frozen protocol seals and geometry/target/prediction arrays. Source files are retained byte-for-byte so those historical dependencies remain visible. Local-drive guards and resource thresholds are not portable configuration. The research-source archive is an audit/code archive, not a one-command reproduction claim.

Complete retraining, field-level metric recomputation, native FE reproduction and checkpoint inference cannot be reproduced solely from this first repository snapshot. They need separately curated and licensed original artifacts, a dependency map, download locations and environment validation. No trained checkpoint is being advertised as included merely because its registry is included.

Before a public version, the author must decide the distribution scope, rights/license and access mechanism for required bulk artifacts; test the intended entry points in a separate directory; and record a fixed version tag and full commit SHA. Do not overwrite frozen research outputs, tune on historical tests or launch a new scientific campaign as part of publication preparation.
