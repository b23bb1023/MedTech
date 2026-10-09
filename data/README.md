# Local input data

The clinical source CSV is not distributed in this repository. Use only a copy you are authorized to analyze. No sample rows have been extracted from the original notebook for redistribution.

## Location

For SF 36, use `data/medtech_masterchart.csv` or `MEDTECH_DATA_PATH`. For notebooks 01–04, use `data/medtech_final.csv` or `MEDTECH_FINAL_DATA_PATH`. Launch Jupyter from the repository root. The exports have different schemas; do not assume one replaces the other.

Private inputs, serialized models and generated outputs are ignored. The reviewed aggregate workbook at `results/medtech-results.xlsx` is an explicit exception.

## SF 36 schema

Use a UTF-8 CSV with a header row. The original export had 226 records and 207 columns; these dimensions are historical observations, not requirements for a new input.

| Fields | Expected representation |
|---|---|
| `SF 36` | Numeric outcome. Missing/non-finite outcomes are excluded, not imputed. |
| `Site` | Text tumour-site label. Missing/rare/unseen values map to `other`. |
| `staging (TNM)` | TNM label containing supported T0–T4, N0–N3, M0–M1 categories, with optional letter substages. |
| `Staging` | One of I, II, III, IVA, IVB, IVC; missing is allowed. |
| `Prakriti` | V/P/K combination, case-insensitive; missing is allowed. |
| Other retained measurements and coded attributes | Numeric columns. Unexplained text columns raise an actionable error rather than being silently discarded. |
| `Value_Q1`–`Value_Q36` | Numeric scored items, if available; used only by the reconstruction and descriptive branches. |
| `Q1`–`Q36`, `Prakriti.1` | Optional original fields, automatically excluded. |
| `Sno`, `Name`, `Place of birth`, `date`, `month`, `year`, `CR` | Optional known identity fields, automatically excluded. |

`Site`, `staging (TNM)`, `Staging`, `Prakriti`, and the outcome are required columns. Review [the data dictionary](../docs/data-dictionary.md) for inherited encodings and unresolved meanings. Do not rename or infer the clinical meaning of coded fields without the source codebook.

## Final-masterchart schema for notebooks 01–04

| Fields | Expected representation |
|---|---|
| `staging (TNM)` | Text with supported T/N labels; notebooks 01–02 also require M for a joint label. |
| `Pain`, `weight`, `height`, `Pulse rate` | Numeric; records missing these are filtered before historical scaling. |
| `Site` | Tumour-site category included in every feature setting. |
| `Value_Q*` | Numeric scored questionnaire fields; `_final` versions take preference. |
| `V_Q*`, `P_Q*`, `K_Q*` | Numeric V/P/K-coded question fields; meanings require the codebook. |

Names are normalized and duplicate column labels removed after final-column selection. Saved shapes were 226×54, 226×220 and 226×256; these are observations, not requirements. Inspect the schema without displaying patient rows.

Full-cohort min-max scaling and zero-filling selected features are historical choices retained to explain saved results. Review them before confirmatory evaluation.

## Working and sharing

The notebook removes known identity columns before aggregate inspection, but numeric traits and rare combinations can still be sensitive. Keep the source file, row-level predictions, and model artifacts local. A removed name column is not a guarantee of anonymization.

Notebooks 01–04 retain reviewed historical aggregate outputs. The manifest rejects new/changed outputs until reviewed. Clear one locally executed notebook with `python scripts/check_notebook.py path/to/notebook.ipynb --clear` when its outputs should not be shared. Inspect the diff. Data and questionnaire rights remain separate from software licensing.
