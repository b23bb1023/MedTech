# Local input data

The clinical source CSV is not distributed in this repository. Use only a copy you are authorized to analyze. No sample rows have been extracted from the original notebook for redistribution.

## Location

Save the input as `data/medtech_masterchart.csv`, or set `MEDTECH_DATA_PATH` before starting Jupyter. Files in this directory other than this guide are ignored by Git. CSV, spreadsheet, serialized-model, and generated-output files are also ignored elsewhere in the repository.

## Expected schema

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

## Working and sharing

The notebook removes known identity columns before aggregate inspection, but numeric traits and rare combinations can still be sensitive. Keep the source file, row-level predictions, and model artifacts local. A removed name column is not a guarantee of anonymization.

Before committing an executed notebook, clear outputs with `python scripts/check_notebook.py --clear` and inspect the diff. Submit aggregate results only after checking that they are appropriate to publish. Data and third-party questionnaire rights are separate from the repository's software license.
