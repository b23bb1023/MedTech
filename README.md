# MedTech

### Clinical data exploration, feature engineering, and SF 36 regression

MedTech is a notebook-based analysis of a clinical masterchart combining demographic measurements, tumour site and staging, questionnaire responses, and Prakriti-related attributes. The work takes a wide, incomplete spreadsheet through data-quality inspection and feature engineering, explores its structure with PCA and K-means, and compares three regression approaches for the spreadsheet's `SF 36` outcome.

The original saved analysis covered **226 records**, **207 input columns**, and **three regression model families**. This repository presents that work with documented methods, preserved aggregate results, a cleaned notebook, and reusable preprocessing.

**Start here:** [analysis notebook](MedTech.ipynb) · [detailed methods and results](docs/analysis.md) · [data dictionary](docs/data-dictionary.md) · [local data setup](data/README.md)

## What this project demonstrates

| Area | Work completed |
|---|---|
| Data assessment | Inspected dimensions, column types, missingness, and inconsistent category labels in a 207-column export. |
| Cleaning | Removed identity fields and redundant raw questionnaire columns; selected high-missingness fields for removal. |
| Feature engineering | Normalized site labels, grouped rare categories, applied one-hot encoding, parsed TNM labels, mapped overall stage, and encoded V/P/K membership. |
| Numeric preparation | Applied mean imputation and standardization to the feature matrix. |
| Structure exploration | Computed a 100-component PCA representation, inspected K-means inertia for k=1–9, and explored a five-cluster configuration. |
| Regression | Compared linear regression, a 200-tree random forest, and XGBoost using an 80/20 split. |
| Evaluation and interpretation | Reported MAE, MSE, and R², and inspected random forest feature importances. |

The project demonstrates an exploratory machine-learning workflow. It does not establish a clinical prediction tool, validated patient subgroups, or causal effects.

## Data and analysis objective

The source was a locally stored masterchart CSV. Its saved notebook outputs show 226 rows and 207 columns, including:

- Demographic and measurement fields such as age, weight, height, pulse rate, and sex.
- Tumour site, a TNM string, overall stage, and pain.
- The outcome labeled `SF 36`, raw `Q1`–`Q36`, and scored `Value_Q1`–`Value_Q36` fields.
- Prakriti labels, `Vatta`, `Pitta`, and `Kapha` fields, and coded physical, behavioural, and lifestyle attributes.
- Identity fields and many spreadsheet-export columns labeled `Unnamed:`.

The regression objective was to estimate the numeric `SF 36` column. The repository does not include the score-construction formula, questionnaire version, clinical codebook, cohort recruitment details, or data-collection protocol. Consequently, `SF 36` is described here as the **spreadsheet outcome**, without assuming a standard domain scoring scale.

The source dataset is **not included**. Re-running the analysis requires an authorized local copy with the expected schema. The MIT license covers this repository's software and documentation; it does not grant access to the dataset or rights to third-party questionnaire material.

## Workflow

### 1. Inspect and clean the masterchart

The original notebook reviewed dataframe shapes, dtypes, missing-value counts, and categorical frequencies. It removed six identifying fields, dropped the 30 columns with the most missing entries, and removed the raw `Q1`–`Q36` columns while retaining their scored counterparts.

The cleaned notebook removes the known `CR` record identifier as well, avoids row-level dataframe previews, and keeps inputs in an ignored local data directory. Saved notebook outputs and execution counts are cleared before publication.

### 2. Engineer interpretable numeric features

- **Site:** lowercase and trim labels; group categories occurring fewer than five times into `other`; one-hot encode with a reference category. The original workflow did not merge semantic synonyms such as `glottis` and `glottic`.
- **TNM:** extract T, N, and M values, reducing letter substages to their parent numeric categories. The inherited `Tumorsize` name means T category, not a measured tumour dimension.
- **Overall stage:** preserve the original numeric mapping I→6, II→5, III→4, IVA→3, IVB→2, IVC→1. This is an encoding convention with larger numbers for earlier stage.
- **Prakriti:** normalize V/P/K codes and create binary membership indicators. The cleaned version names these `Vata_present`, `Pitta_present`, and `Kapha_present`, preserving the pre-existing numeric scores.
- **Missing values and scale:** filter highly incomplete features, mean-impute remaining missing values, and standardize inputs.

For supervised models, site categories, missingness selection, imputation, and scaling are now learned inside pipelines using **training records only**. Mean imputation and treating coded responses as numeric remain exploratory choices requiring codebook review.

### 3. Explore feature-space structure

The original notebook fitted PCA with 100 components. It also fitted K-means directly on the standardized feature matrix, evaluated inertia for k=1–9, and selected k=5 for exploration. PCA was computed separately; it was **not** used as input to the clustering or regression models.

![Original saved K-means elbow plot for k=1 to 9](docs/assets/original-elbow.png)

*This figure is preserved from the original saved run. It shows the inertia trend, but does not establish that five clusters are optimal or clinically meaningful. The original exploratory matrix included the outcome and `CR`; the cleaned exploratory branch excludes both, so its plot will differ.*

The cleaned notebook adds a cumulative PCA explained-variance plot and aggregate cluster counts. These are generated when local data is supplied; no new cohort findings are asserted here.

### 4. Compare regression approaches

The original regression used 142 predictors, an 80/20 random split with seed 42, and a standardized `SF 36` target. With 226 records, the split yields 180 training and 46 test records.

| Model | Original configuration |
|---|---|
| Linear regression | `LinearRegression()` |
| Random forest | `RandomForestRegressor(n_estimators=200)` |
| XGBoost | `XGBRegressor()` |

The original forest had no explicit random seed, and the exact package versions were not recorded. The cleaned notebook adds explicit seeds, a mean-prediction baseline, and two feature settings using the same hold-out split:

1. **Without scored questionnaire items:** the primary exploratory prediction setting excludes `Value_Q1`–`Value_Q36`.
2. **With scored questionnaire items:** a separate reconstruction comparison retains those fields to examine the original feature design.

The cleaned notebook predicts the outcome in its original spreadsheet units. Its newly generated MAE/MSE values therefore use a different scale from the historical results below.

## Original recorded results

These are transcribed from the original notebook's saved evaluation output at commit `5e85afdf46489024e6df7c699b45e9cd398960b9`. They have **not been recomputed** during the repository cleanup. Full-precision values and provenance are recorded in [original-results.json](docs/original-results.json).

| Model | MAE ↓ | MSE ↓ | R² ↑ |
|---|---:|---:|---:|
| Linear regression | 0.002446 | 0.000236 | 0.999806 |
| Random forest, 200 trees | 0.278531 | 0.156415 | 0.870832 |
| XGBoost | 0.273296 | 0.146704 | 0.878851 |

MAE is in standardized outcome units; MSE is in squared standardized outcome units. R² is dimensionless. Linear regression recorded the strongest fit in this saved run; XGBoost recorded slightly lower errors than the forest.

**Interpretation matters:** the original imputer and scaler were fitted before the train/test split, exposing them to the held-out distribution. Its predictors also included the record identifier and scored questionnaire items. If those items were used to calculate `SF 36`, the near-perfect linear fit may reflect reconstruction of an existing score. That is a hypothesis from the feature design, not a confirmed scoring relationship. The scoring formula is unavailable, so these values should remain historical exploratory results rather than evidence of independent clinical prediction.

## Run the cleaned notebook

Use Python **3.10 or later** and launch Jupyter from the repository root.

```bash
git clone https://github.com/b23bb1023/MedTech.git
cd MedTech
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-xgboost.txt
python -m ipykernel install --user --name medtech --display-name "Python (MedTech)"
jupyter lab MedTech.ipynb
```

On Windows, activate the environment with `.venv\Scripts\Activate.ps1` in PowerShell. Select the **Python (MedTech)** kernel in Jupyter.

Place the CSV at `data/medtech_masterchart.csv`. To use another location, set `MEDTECH_DATA_PATH` before starting Jupyter:

```bash
export MEDTECH_DATA_PATH="/path/to/authorized/masterchart.csv"
jupyter lab MedTech.ipynb
```

PowerShell equivalent: `$env:MEDTECH_DATA_PATH = "C:\path\to\authorized\masterchart.csv"`.

The XGBoost requirements file is optional: without it, the notebook explicitly skips that model and runs the other comparisons. The dependency ranges are a setup specification, not a lockfile for the original environment.

Run cells in order. Only aggregate summaries and charts are displayed. Optional aggregate exports go to ignored `outputs/`; inspect them before sharing.

## Repository guide

| Path | Purpose |
|---|---|
| `MedTech.ipynb` | Documented analysis workflow with cleared outputs and portable local input configuration. |
| `medtech/preprocessing.py` | Reusable training-aware feature transformer. |
| `docs/analysis.md` | Original methods, result provenance, changes, limitations, and future work. |
| `docs/data-dictionary.md` | Field groups, explicit encodings, and original feature inventory. |
| `docs/original-results.json` | Exact saved metrics from the original run. |
| `docs/assets/original-elbow.png` | Original aggregate elbow figure. |
| `data/README.md` | Expected local data format and handling instructions. |
| `requirements*.txt` | Notebook dependencies and optional XGBoost dependency. |
| `scripts/check_notebook.py` | Notebook syntax, output, and personal-path checks; optional output clearing. |
| `tests/` | Synthetic-data checks for preprocessing and pipeline behaviour. |
| `.github/workflows/checks.yml` | Automated checks without accessing the clinical dataset. |
| `CONTRIBUTING.md` | Contribution and safe notebook-sharing workflow. |
| `LICENSE` | MIT license. |

## Validation and remaining work

```bash
python -m unittest discover -s tests -v
python scripts/check_notebook.py
```

Tests use generated data to verify feature handling and pipeline behaviour. They do not reproduce the clinical results. The cleaned notebook has not been executed on the source cohort because the CSV is absent from the repository.

Next steps are to verify the outcome's scoring formula and coded field meanings, review feature availability at prediction time, check repeated-person records, evaluate within cross-validation folds, and assess cluster stability. External validation and appropriate data governance would be required before clinical use. See [the detailed discussion](docs/analysis.md#limitations-and-next-steps).

## License

Software and documentation are available under the [MIT License](LICENSE). Dataset access and third-party material remain subject to their own permissions.
