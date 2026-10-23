# Data sources and derived data

The original experimental scans and metadata are from Christian Dän­ekas, *Research Data on Fatigue Tests of As-Welded, Deep-Rolled, and HFMI-Treated Joints*, version 1.0, DOI [10.25835/0dojws6u](https://doi.org/10.25835/0dojws6u), under the source release's CC BY 4.0 terms. Cite that source and inspect its metadata and license before reuse. The original scans are not republished by this repository snapshot.

The accepted cohort comprises C02, C05, C16, E21, G04, G07, G08, G16, G25, H12, H19, X10 and X23, all with suffix V1-S355-AW. Five documentary groups C/E/G/H/X determine the held-out splits; production-batch and scan-session independence remain uncertified. Processed scans are already aligned and smoothed; independent raw registration is unresolved.

The included tables are derived computational research artifacts. They describe reconstructed FE models, numerical T2 references, saved model predictions and retrospective assessment; they must not be presented as measured experimental stresses. The rear surface and material/loading constants are modelling assumptions.

Table exports preserve all data rows and scientific values. Machine-specific `E:\welding\outputs` paths become `ARTIFACT_ROOT`, and any user-home prefix becomes `USER_HOME`. Those are unresolved provenance locators, not download links. Original and exported hashes appear separately in `SOURCE_PROVENANCE.csv`.

The complete point arrays, target arrays, native FE databases, geometry caches, prediction fields and binary checkpoints are outside this initial snapshot. Included registries identify historical hashes; those registries do not imply the corresponding files can be downloaded from this repository.
