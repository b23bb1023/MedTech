# Phase 2: recover sources and extend the analysis

This is the durable handoff for the next research phase. Workbook-only metrics are **real recorded research results supplied by the project author**. Missing source files are a provenance gap, not a reason to discard results or treat them as synthetic.

## Source files not yet located

| Backlog | Evidence retained | Source status | Next action |
|---|---|---|---|
| P2-01: RF/SVM Stage and Pain classifiers | Workbook rows 241–273; 12 target/configuration rows with all seven metrics in the Phase 2 worksheet and JSON. | No matching experiment in the four supplied notebooks or existing SF 36 notebook. | Recover notebook(s), target encodings, splits, class mappings and outputs. |
| P2-02: alternate T/N/Pain MLP run | Table 6 rows 33–41; nine configurations with all T/N and pain metrics. | Notebook 03 implements this family, but its saved numbers differ. | Locate the exact run or earlier version; keep both runs separate until matched. |
| P2-03: earlier joint-TNM function version | Notebook 01 original cells 27–28 and workbook follow-on VPK/ALL runs use 226 input rows. | Outputs exist; the executed definition differs from the current augmented runner. | Recover that version and confirm reported pain RMSE. |
| P2-04: top-ten outlier analysis | No ranks, per-record errors or predictions saved in any of the five reviewed notebooks or workbook. | Source not found; aggregate errors cannot recover rankings. | Recover predictions or missing notebook, then add an anonymized ranked error summary. |

P2-01 repeats `VALUE` for 54-, 220- and 256-feature configurations. The latter widths resemble VPK and ALL, but this is only a **candidate mapping**. Original and candidate labels are kept in separate columns.

Its recorded descriptions indicate a 10-class Stage task and a 21-class Pain task, unlike available notebooks' 21-class **joint TNM** task and continuous pain regression. Recover definitions before comparing scores. Some Pain accuracy and weighted-recall values differ; retain both and confirm whether they came from different evaluations, subsets or reporting conventions.

## Follow-up research

1. Recover feature codebook and questionnaire score-construction rules. Audit question content overlapping the target.
2. Move all preprocessing, including missing-value handling and site encoding, into training folds. Keep final evaluation records unaltered and augment only training data.
3. Add site-only, VALUE-only and VPK-only ablations. Use identical splits and repeated seeds across comparisons.
4. Store per-fold scores, successful/failed fold counts, class labels and out-of-fold predictions privately. Publish reviewed aggregate uncertainty, pooled confusion counts and distinct round/threshold PCA results.
5. Recover top-ten outliers and publish error rank, magnitude and setting without record identifiers, demographics, clinical row contents or links to patient rows. Examine minority labels and feature-quality conditions with aggregate counts.
6. Revisit PCA with nested comparisons and check whether small CV gains survive repeated evaluation. Historical pooled-decoding SD is not a confidence interval.

This phase does not alter historical Git history or replace missing analyses with invented results. Reconcile newly recovered outputs against source coordinates and assign distinct run IDs when experiments differ.
