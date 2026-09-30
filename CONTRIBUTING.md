# Contributing

Open a focused pull request with the problem, the resulting behaviour, and validation. Changes to feature definitions should explain their effect on the analysis and distinguish new results from the archived original run.

## Local checks

From the repository root, install `requirements.txt`; install `requirements-xgboost.txt` if changing the XGBoost comparison.

```bash
python -m unittest discover -s tests -v
python scripts/check_notebook.py
```

Tests use generated fixtures and need no source clinical data. To check a notebook after local execution:

```bash
python scripts/check_notebook.py --clear
python scripts/check_notebook.py
```

Inspect the final diff. Do not commit private data, record previews, row-level predictions, credentials, personal file paths, or serialized clinical models. Avoid attaching source records to public issues. The checker catches cleared-output and path issues; it is not a complete detector for sensitive information.

## Analysis changes

Keep learned preprocessing inside training folds. Document new category mappings, questionnaire inclusion, target scale, seeds, package versions, and evaluation protocol. Do not overwrite `docs/original-results.json` with a new run; it is a historical record. Keep raw cohort results separate from synthetic test results.
