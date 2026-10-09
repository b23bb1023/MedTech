# Contributing

Open a focused pull request with the problem, the resulting behaviour, and validation. Changes to feature definitions should explain their effect on the analysis and distinguish new results from the archived original run.

## Local checks

From the repository root, install `requirements.txt`; install `requirements-xgboost.txt` if changing the XGBoost comparison.

```bash
python -m unittest discover -s tests -v
python scripts/check_notebook.py
```

Tests use generated fixtures and no clinical data. The checker inspects all five notebooks by default. Historical outputs are allowed only when matching `results/notebook-output-manifest.json`. New or changed outputs require privacy review. To clear one notebook after local execution:

```bash
python scripts/check_notebook.py notebooks/01_joint_tnm_pain.ipynb --clear
python scripts/check_notebook.py
```

Inspect the final diff. Do not commit private data, record previews, row-level predictions, credentials, personal paths or serialized clinical models. The checker catches output changes, selected credential patterns and local paths; it is not a complete sensitive-information detector. To retain new outputs, review every output, confirm appropriate aggregate content, and update digests using the checker's `output_digest` helper. A new digest alone is not a privacy review.

## Analysis changes

Keep learned preprocessing inside training folds. Document new category mappings, questionnaire inclusion, target scale, seeds, package versions, and evaluation protocol. Do not overwrite `docs/original-results.json` with a new run; it is a historical record. Keep raw cohort results separate from synthetic test results.

Assign distinct run IDs to different experiments. Retain real workbook-only results with missing sources and update `docs/phase-2.md` when found. Missing metrics remain blank, not zero. Distinguish final-fold matrices from pooled matrices, and fold dispersion from variability between model settings.
