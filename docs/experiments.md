# Experiment series and methods

The research explored whether the available coded features contain useful structure or predictive associations. There was no formal paper, preregistered hypothesis or external validation cohort. The notebooks are successive method-development iterations, with distinct targets and evaluation protocols.

## Notebook map

| Notebook | Research question | Implementation | Saved evidence |
|---|---|---|---|
| [SF 36 exploration](../MedTech.ipynb) | What structure exists in the masterchart, and how closely can its spreadsheet outcome be reconstructed? | Feature engineering, PCA, K-means, linear regression, random forest and optional XGBoost. | Historical regression scores and elbow figure are preserved separately; the current notebook has cleared outputs. |
| [01: joint TNM and pain](../notebooks/01_joint_tnm_pain.ipynb) | Can a shared representation predict a joint TNM label and pain? | Shared 64/32/16 MLP, two heads, dropout, AdamW, early stopping and validation subset; an unexecuted alternative is retained separately. | Six recorded feature-set runs and an explicitly labeled in-sample forest diagnostic. |
| [02: joint-TNM architectures](../notebooks/02_joint_tnm_architectures.ipynb) | How does a smaller shared network change the classification/regression trade-off? | Big 64/32/16 and small 32/16/8 MLPs, OneCycleLR, two heads and 120 epochs. | Six runs with confusion matrices, confidence summaries and pain error/variance diagnostics. |
| [03: T/N multitask](../notebooks/03_tn_multitask.ipynb) | Is decomposing TNM into separate T and N targets more informative? | Three heads; small 32/16/8, big 64/32/16 and ultra 128/64/32 architectures. | Nine runs, 18 confusion matrices, confidence and pain diagnostics. |
| [04: classical, ordinal and PCA](../notebooks/04_classical_ordinal_pca.ipynb) | Do simpler models, ordered-label formulations or compressed features reveal more useful signal? | Standard/ordinal classifiers; pain regression; repeated stratified CV with dummy baselines; round/threshold latent decoding; fold-local PCA. | 48 held-out classification summaries, 15 pain regressions, 40 CV summaries, 150 historical PCA summaries and their recorded comparisons. |

Original upload names and zero-based source-cell references are retained in [recorded-results.json](../results/recorded-results.json).

## Feature representations

The final-masterchart notebooks select the preferred `_final` column when available, normalize column names, drop duplicate column labels and coerce selected features to numeric values. Non-finite or missing feature values are filled with zero. Without the clinical codebook, zero must not automatically be interpreted as an observed absence.

| Setting | Columns selected | Saved feature count | Interpretation |
|---|---|---:|---|
| VALUE | `Value_Q*` plus `Site_*` | 54 | Scored questionnaire representation with site context. |
| VPK | `V_Q*`, `P_Q*`, `K_Q*` plus `Site_*` | 220 | V/P/K-coded representation with site context. |
| ALL | Both families plus `Site_*` | 256 | Combined representation. |

These counts describe the saved cohort, not a fixed schema. **Site is included in every setting.** This comparison therefore does not isolate questionnaire scores from site effects. A site-only baseline and feature-family ablations would make useful follow-up experiments.

The representation comparison motivates the semantic question; it does not establish that V/P/K encodings are clinically meaningful constructs. That requires original question definitions, coding rules and independent evidence. Questionnaire content overlapping pain or staging also needs review before interpreting associations as independent prediction.

## Targets and filtering

The joint-TNM notebooks normalize supported T, N and M strings, discard letter suffix distinctions and encode their combined labels. The saved cohort has 21 joint labels. These are **TNM combinations**, not 21 overall cancer-stage categories.

The separate-target notebooks use `keep_suffixes=False` and preserve these saved encoder mappings: `0→T1, 1→T2, 2→T3, 3→T4` and `0→N0, 1→N1, 2→N2, 3→N3`. M is not an output. T is a categorical stage component, not a measured tumour dimension.

All four notebooks require non-missing numeric Pain, weight, height and pulse-rate fields. The saved filtered cohort remains 226 rows. These fields, including Pain, were min-max scaled on the complete filtered dataframe. Pain MAE/RMSE use that normalized scale; MSE uses its square. They cannot be compared directly with standardized SF 36 errors from the older notebook.

## Evaluation protocols

| Protocol | Split and training design | Interpretation |
|---|---|---|
| Early joint-TNM MLP | Rare labels replicated to at least three records before seed-42 stratified splits; early-stopping validation subset. | Copies can overlap training and evaluation. Two later outputs use 226 rows and an unavailable earlier kernel function version. |
| Joint-TNM architecture sweep | Rare-class replication before an 80/20 stratified split; 242 augmented rows and 49 test rows. | Same overlap concern. Torch initialization and replication seeds were not fully recorded. |
| Separate T/N multitask | 80/20 split stratified on T; replication only after splitting training data. | 46 original test rows. Single-split fitting and full-cohort preprocessing still limit performance claims. |
| Classical held-out models | Independent seed-42 80/20 splits for T, N and pain. | 180 training / 46 test rows. Inherited numeric scaling/site encoding use the full cohort; estimator-specific StandardScaler pipelines fit within training. |
| Repeated classification CV | Five folds × three repeats, seed 42; VPK→T and ALL→N. Rare-T oversampling stays in training folds. | Baselines use the same protocol. Saved means exist; per-fold score records and genuine fold SDs do not. |
| PCA CV | StandardScaler/PCA fitted inside training folds; 10, 15, 20, 30 components and 95% variance. | PCA cannot undo earlier full-cohort preprocessing. Historical latent rows combine round and threshold decoding means. |

The ordinal wrapper trains K−1 binary decisions of the form `y > threshold`, converts cumulative probabilities to class probabilities and predicts the largest probability. Latent regression predicts numeric encoded labels, then decodes them by rounding or thresholds estimated from training scores. These encode order differently; neither proves semantic validity of a feature.

## Metric selection

Classification summaries emphasize **balanced accuracy and macro F1** together with dummy baselines. Accuracy and weighted F1 remain available, but large T3/N1 classes can dominate them. Matrix counts show minority-class coverage. Average softmax confidence and entropy are descriptive, not evidence of calibrated certainty.

Pain summaries emphasize **MAE, RMSE and R²**, with outcome units stated. MSE, explained variance and neural prediction/residual variance remain available. Negative R² results are retained because they identify settings that did not improve on a constant predictor in the recorded split.

The historical latent-PCA SD columns describe variation between **two decoding means**, not variability across 15 folds. Standard/ordinal SDs are unavailable because their source summaries contain one already-averaged row. No confidence intervals or significance claims can be recovered from these columns. Historical PCA deltas use a broad-family join that pairs a pooled latent mean with both baseline decoding methods; they are retained as recorded diagnostics rather than treated as clean method-matched improvements.

## Presentation and code corrections

- Added descriptive titles, section headings, method notes and portable final-masterchart inputs.
- Removed row previews, exposed target/feature arrays, raw CSV exports, local warning paths, embedded dataframe HTML and repetitive epoch logs. Useful aggregate metrics and matrices remain embedded.
- Rebuilt the workbook with consistent headers, numeric metrics, separate protocols and a source-coordinate ledger retaining all 1,323 original numeric entries.
- Corrected the first four early pain-error labels to MSE. The two outputs from an unavailable kernel version retain reported RMSE labels.
- Corrected the regression target `N/T` to Pain using the actual `run_regression_suite(..., target_name="pain")` call.
- Restored the ALL follow-on accuracy distinction: original E12 duplicates balanced accuracy 0.1299; the notebook and Table 5 record accuracy 0.087. Both original numbers remain in the ledger.
- Aligned site encoding rows with the filtered dataframe index, corrected classifier-mixin inheritance order and replaced obsolete `squared=False` with an explicit square root.
- Kept future PCA round/threshold runs distinct and matched them to corresponding non-PCA decoding methods. Historical outputs were not silently recomputed.
- Isolated the unexecuted alternative so it does not replace principal models during a normal run.

These changes improve portability, interpretation and privacy. They do not reconstruct the original package environment or produce new cohort measurements. Recovery and confirmatory analysis are tracked in [Phase 2](phase-2.md).
