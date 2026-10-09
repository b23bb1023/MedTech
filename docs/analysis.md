# Analysis notes

## Scope and evidence

This document describes the work present in the original `MedTech.ipynb` and the changes made to present it responsibly. The source repository initially contained that notebook alone. It had 63 code cells, saved dataframe previews, an elbow plot, a crowded feature-importance plot, and model evaluation output. It contained no markdown explanation, dataset, dependency specification, or scoring codebook.

The original notebook was inspected at commit `5e85afdf46489024e6df7c699b45e9cd398960b9`. Its blob SHA was `0760c2f46401a3bf4d1a180e8634c2a695c8c5f8`. Counts, model parameters, and metrics below come from its code and saved outputs. They are observations of that artifact, not a rerun or a new clinical study.

## Original analysis, step by step

### Input assessment

The input shape was 226 × 207. Initial dtypes were 121 integer columns, 79 floating-point columns, and seven object columns. The notebook inspected the dataframe, head, shape, dtypes, and missing-value ranking.

Eighteen columns in the displayed missingness ranking were entirely missing. Other examples included highly incomplete physical-attribute fields and `Unnamed:` export columns. The workflow removed a fixed set of the 30 most incomplete columns, without a documented missingness threshold or sensitivity analysis.

### Column removal

The original six-field removal covered `Sno`, `Name`, `Place of birth`, `date`, `month`, and `year`, leaving 201 columns. Removing 30 highly incomplete columns left 171. Removing raw `Q1`–`Q36` left 135. The scored `Value_Q1`–`Value_Q36` fields remained.

The numeric `CR` record identifier was still present in the modeling matrix. The duplicated text field `Prakriti.1` was removed later, before imputation.

### Site handling

The notebook lowercased and stripped site strings. Categories with fewer than five records in the full cohort were grouped into `other`. One-hot encoding used `drop_first=True`, producing eight dummy columns and a 142-column dataframe at that step.

Case normalization combined differently capitalized sinonasal and nasopharyngeal labels. Semantic aliases were not reconciled: `glottis` was grouped as rare while `glottic` remained a distinct category. Likewise, the rare `oropharynx` label was not merged with `oropharyngeal`. A future mapping needs clinical review, not string similarity alone.

### TNM and overall stage

Regex parsing extracted T, N, and M components from `staging (TNM)`, including strings with a `ry` prefix. T1a/T1b became 1; T4a/T4b became 4. N2a/N2b/N2c became 2, and N3 sublabels became 3. M was converted to a numeric value. The source string was dropped, creating a 144-column intermediate dataframe.

This compression loses substage information and does not implement the clinical rules for deriving overall stage. `Tumorsize` is a legacy column name for T category. `Lymphnodes` is N category, not a measured node count.

Overall stage used the mapping I→6, II→5, III→4, IVA→3, IVB→2, IVC→1. Numeric differences between these codes are an encoding assumption, not a measured biological distance.

### Prakriti

The source normalized Prakriti strings to uppercase, sorted the letters, and encoded presence of V, P, and K. It added `Vata` but assigned into the existing `Pitta` and `Kapha` columns, replacing their original numeric contents. The existing `Vatta` column remained. After dropping Prakriti and its duplicate, the numeric matrix had 143 columns.

The cleaned transformer explicitly separates membership indicators from the original score fields. It does not assign medical meaning to the membership patterns or questionnaire codes.

### Imputation, scaling, and exploration

`SimpleImputer(strategy="mean")` and `StandardScaler()` were fitted on all 226 records and all 143 columns, including `SF 36`. The saved output reported zero missing values after imputation.

PCA requested 100 components and produced a 226 × 100 representation. The notebook did not save explained-variance statistics or a loading analysis. K-means operated on the original standardized matrix rather than on the PCA representation. It assessed inertia at k=1–9 and fitted k=5. No cluster profiles, stability estimates, silhouette scores, or independent clinical interpretation were recorded.

The preserved elbow figure is available in `docs/assets/original-elbow.png`. A decline in inertia is expected as k increases; the curve alone is insufficient to validate a particular number of patient subgroups.

### Regression and feature importance

The source dropped `SF 36` from the standardized matrix to obtain 142 predictors and used the standardized column as y. An 80/20 random split used `random_state=42`. Model fits were ordinary least squares, a random forest with 200 trees, and default XGBoost. Neither tree model had an explicit seed in the original code.

Evaluation printed MAE, MSE, and R² in the order linear regression → random forest → XGBoost. Exact results are preserved in `original-results.json`. The final figure plotted every forest importance in a small chart, making labels hard to inspect; no ranked table or interpretation was recorded.

## Why the historical scores need context

Two separate concerns affect interpretation:

1. **Preprocessing leakage:** full-cohort imputation and standardization used held-out information before the split. This compromises the independence of the evaluation. [Scikit-learn's guidance](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage) recommends learning preprocessing only on training data and composing it with the model in a pipeline.
2. **Possible score reconstruction:** predictors included `Value_Q1`–`Value_Q36`. If `SF 36` was derived from those scored items, the linear model could approximate a scoring rule. The exceptionally high R² is consistent with that possibility, but the available notebook cannot confirm the relationship.

The source also retained a record identifier, used a high-dimensional matrix relative to the sample size, and reported one split without uncertainty estimates. Its scores are recorded faithfully, but are not presented as evidence of generalization to a new population.

## What the cleaned notebook changes

| Element | Original | Cleaned workflow |
|---|---|---|
| Presentation | Code-only exploration with repeated dataframe dumps. | Markdown explanations, focused aggregate summaries, and explicit interpretation. |
| Input | Personal absolute path. | Repository-relative default with `MEDTECH_DATA_PATH` override. |
| Known identity fields | Six dropped after initial previews; `CR` retained. | Seven known fields dropped immediately; transformer also excludes them defensively. |
| Public SF 36 notebook outputs | Identifiable rows, local kernel paths, warnings, and disposed-controller errors. | SF 36 outputs remain cleared. Later notebooks retain separately reviewed aggregate outputs guarded by a content manifest. |
| Missingness selection | Top 30 columns from full cohort, even if a selected count were zero. | All-empty features plus up to 30 features actually containing missing values; learned from training records for supervised fits. |
| Site vocabulary | Learned from full cohort. | Learned from training records; unseen sites map to `other`. |
| Prakriti indicators | Overwrote existing Pitta/Kapha fields. | Separate presence fields preserve numeric scores; absent codes stay missing until imputation. |
| Target | Standardized with full cohort, then extracted. | Raw numeric outcome kept separate; missing/non-finite outcomes excluded. |
| Imputer and scaler | Fitted before splitting. | Fitted inside each supervised pipeline after splitting. |
| Questionnaire predictors | Retained in the only regression setting. | Primary setting excludes them; a separate reconstruction comparison includes them. |
| Baseline | None. | Mean predictor added as a reference. |
| Randomness | Split/K-means seed only; K-means default restarts. | Model seeds explicit; K-means uses 10 restarts. |
| PCA and K-means | Included the outcome and identifier. | Exclude both; retain scored items for descriptive exploration. |
| PCA size | Exactly 100. | At most 100, capped by rows and features; cumulative variance chart added. |
| Feature importance | All labels in a small chart. | Top 20 forest importances for the primary setting. |

These changes intentionally prevent an exact replay of the original numeric outputs. New results belong to the cleaned protocol and must be labeled with that protocol and environment. Even the questionnaire-inclusive comparison is not an exact replication of the legacy run.

The unsupervised branch fits descriptive transforms on the full labeled cohort. It is separate from the supervised pipelines and does not pass learned parameters into them. It remains an exploratory description of this sample.

## Reproducibility status

The notebook is portable once the CSV and dependencies are available. The package ranges do not recreate an undocumented historical environment; the only original version available in notebook metadata was Python 3.10.19.

Automated checks use synthetic fixtures for identifier exclusion, outcome exclusion, Prakriti-score preservation, unseen sites, training-only missingness and scaling, and both feature settings. Notebook checks compile code cells and require cleared outputs and portable paths. These checks do not validate the clinical cohort or reproduce the historical scores. XGBoost is an optional dependency and is skipped explicitly if unavailable.

Local cleanup validation passed 13 tests, with the optional XGBoost test skipped because that dependency was unavailable. All notebook code cells also completed using a generated 226-record fixture, running the baseline, linear model, and random forest in both feature settings and rendering three charts. JSON structure, Python syntax, output clearing, local links, and personal-path checks passed. `nbformat` was unavailable locally, so full notebook schema validation is configured in CI but was not part of that local check. No synthetic metric is presented as a clinical result.

## Limitations and next steps

- **Scoring and codebook:** establish how `SF 36` and each `Value_Q` field were constructed. Review coded responses before treating them as continuous quantities or using mean imputation. Explain every retained `Unnamed:` field or remove it using a justified schema.
- **Cohort provenance:** document recruitment, collection dates, eligibility, authorization, and whether records represent unique people. These details are absent from the original artifact.
- **Feature availability:** define the prediction time and ensure that predictors are available then. Questionnaire-inclusive results need a separate reconstruction interpretation unless the scoring relationship is ruled out.
- **Evaluation:** use training-only pipelines within cross-validation; keep an untouched final evaluation set if selecting models. Use grouped or temporal splits when the sampling structure requires them, and report uncertainty.
- **Missingness and encoding:** compare a justified missingness threshold with the inherited fixed count. Review site aliases, stage encoding, TNM substage loss, and missing Prakriti handling with domain expertise.
- **Clustering:** inspect stability, alternative k values, and cluster summaries after a privacy review. No meaningful clinical subgroups were demonstrated by the original notebook.
- **Interpretability:** consider permutation importance on held-out data. Impurity importance alone is sensitive to correlated predictors and does not establish causation.
- **External validity:** assess performance on an independently collected cohort before any clinical application.

Repository cleanup removes sensitive information from the new file version. Earlier commits still contain the original uploaded notebook; changing current files does not erase Git history. History rewriting is a separate repository operation and was not performed.
