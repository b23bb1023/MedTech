"""Behavioural checks with generated data; no clinical records are used."""

import unittest

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from medtech import MedTechFeatures


def synthetic_data(n=80):
    rng = np.random.default_rng(42)
    frame = pd.DataFrame({
        "Sno": np.arange(n), "Name": ["Synthetic record"] * n,
        "CR": np.arange(n) + 1000, "date": 1, "month": 1, "year": 2000,
        "Place of birth": "Synthetic location",
        "Age": rng.integers(30, 80, n), "weight": rng.integers(45, 90, n),
        "height": rng.integers(150, 190, n), "Pulse rate": rng.integers(60, 100, n),
        "Sex": rng.integers(1, 3, n), "Pain": rng.integers(1, 10, n),
        "Site": np.resize(["Oral cavity", "Glottic", "Supraglottic"], n),
        "staging (TNM)": np.resize(["T1bN0M0", "T4aN2cM0", "ryT2N1M0"], n),
        "Staging": np.resize(["I", "IVA", "III"], n),
        "Prakriti": np.resize(["kv", "P", "VPK"], n), "Prakriti.1": "unused",
        "Vatta": rng.integers(1, 20, n), "Pitta": rng.integers(1, 20, n),
        "Kapha": rng.integers(1, 20, n),
    })
    for i in range(1, 37):
        frame[f"Q{i}"] = rng.integers(1, 5, n)
        frame[f"Value_Q{i}"] = rng.integers(0, 101, n)
    frame["SF 36"] = frame["Age"] * 3 + frame["weight"] * 2 + rng.normal(0, 10, n)
    return frame


class FeatureTests(unittest.TestCase):
    def test_identifiers_outcome_and_raw_items_never_become_features(self):
        prepared = MedTechFeatures(missing_columns_to_drop=0).fit_transform(synthetic_data())
        self.assertFalse(set(MedTechFeatures.IDENTIFIERS) & {c.lower() for c in prepared})
        self.assertNotIn("SF 36", prepared)
        self.assertNotIn("Prakriti.1", prepared)
        self.assertFalse(any(c.startswith("Q") or c.startswith("Value_Q") for c in prepared))

    def test_questionnaire_comparison_is_explicit(self):
        frame = synthetic_data()
        default = MedTechFeatures().fit_transform(frame)
        comparison = MedTechFeatures(include_questionnaire_values=True).fit_transform(frame)
        self.assertEqual(comparison.shape[1] - default.shape[1], 36)
        self.assertIn("Value_Q36", comparison)

    def test_tnm_stage_and_prakriti_scores_are_preserved(self):
        frame = synthetic_data()
        result = MedTechFeatures().fit_transform(frame)
        self.assertEqual(result["Tumorsize"].iloc[:3].tolist(), [1, 4, 2])
        self.assertEqual(result["Lymphnodes"].iloc[:3].tolist(), [0, 2, 1])
        self.assertEqual(result["Staging"].iloc[:3].tolist(), [6, 3, 4])
        for column in ["Vatta", "Pitta", "Kapha"]:
            np.testing.assert_array_equal(result[column], frame[column])
        self.assertEqual(result["Vata_present"].iloc[:3].tolist(), [1, 0, 1])
        self.assertEqual(result["Pitta_present"].iloc[:3].tolist(), [0, 1, 1])
        self.assertEqual(result["Kapha_present"].iloc[:3].tolist(), [1, 0, 1])

    def test_missing_prakriti_does_not_become_confirmed_absence(self):
        frame = synthetic_data()
        frame.loc[0, "Prakriti"] = np.nan
        result = MedTechFeatures(missing_columns_to_drop=0).fit_transform(frame)
        self.assertTrue(result.loc[0, ["Vata_present", "Pitta_present", "Kapha_present"]].isna().all())

    def test_unseen_sites_share_the_other_bucket_and_keep_feature_order(self):
        train = synthetic_data()
        train["Site"] = "oral cavity"
        encoder = MedTechFeatures().fit(train)
        held_out = train.iloc[:2].copy()
        held_out["Site"] = "unseen site"
        result = encoder.transform(held_out)
        self.assertEqual(result.columns.tolist(), encoder.get_feature_names_out().tolist())
        # Here 'oral cavity' is the dropped reference category.
        self.assertEqual(result["Site_other"].tolist(), [1, 1])
        self.assertEqual(encoder.common_sites_, ["oral cavity"])

    def test_missingness_decisions_are_learned_from_training_only(self):
        train = synthetic_data()
        train["Empty"] = np.nan
        train["Incomplete"] = 1.0
        train.loc[:39, "Incomplete"] = np.nan
        train.loc[0, "Age"] = np.nan
        encoder = MedTechFeatures(missing_columns_to_drop=1).fit(train)
        self.assertEqual(encoder.dropped_columns_, ["Empty"])
        # All-empty features are removed plus the ranked budget, with overlap counted once.
        held_out = synthetic_data(10)
        held_out["Empty"] = 2.0
        held_out["Incomplete"] = np.nan
        result = encoder.transform(held_out)
        self.assertNotIn("Empty", result)
        self.assertIn("Incomplete", result)
        self.assertIn("Age", result)

    def test_imputation_and_scaling_do_not_change_after_test_transform(self):
        train = synthetic_data()
        train.loc[0, "Age"] = np.nan
        pipeline = Pipeline([
            ("features", MedTechFeatures(missing_columns_to_drop=0)),
            ("imputer", SimpleImputer(strategy="mean")),
            ("scaler", StandardScaler()),
        ]).fit(train)
        means = pipeline.named_steps["scaler"].mean_.copy()
        age_index = list(pipeline.named_steps["features"].get_feature_names_out()).index("Age")
        self.assertAlmostEqual(pipeline.named_steps["imputer"].statistics_[age_index], train["Age"].mean())
        self.assertAlmostEqual(means[age_index], train["Age"].mean())
        held_out = synthetic_data(10)
        held_out["Age"] = 10000
        pipeline.transform(held_out)
        np.testing.assert_array_equal(means, pipeline.named_steps["scaler"].mean_)

    def test_schema_errors_are_actionable(self):
        with self.assertRaisesRegex(ValueError, "Missing required columns"):
            MedTechFeatures().fit(synthetic_data().drop(columns="Site"))
        frame = synthetic_data()
        frame.loc[0, "staging (TNM)"] = "unparseable"
        with self.assertRaisesRegex(ValueError, "cannot be parsed"):
            MedTechFeatures().fit(frame)
        frame = synthetic_data()
        frame["Unexpected text"] = "coded text"
        with self.assertRaisesRegex(ValueError, "Unexpected non-numeric"):
            MedTechFeatures().fit(frame)

    def test_regression_pipelines_fit_in_both_settings(self):
        frame = synthetic_data()
        models = [LinearRegression(), RandomForestRegressor(n_estimators=5, random_state=42)]
        for include_values in [False, True]:
            for model in models:
                pipeline = Pipeline([
                    ("features", MedTechFeatures(include_questionnaire_values=include_values)),
                    ("imputer", SimpleImputer(strategy="mean")),
                    ("scaler", StandardScaler()), ("model", clone(model)),
                ])
                pipeline.fit(frame.iloc[:60], frame["SF 36"].iloc[:60])
                prediction = pipeline.predict(frame.iloc[60:])
                self.assertEqual(prediction.shape, (20,))
                self.assertTrue(np.isfinite(prediction).all())

    def test_xgboost_when_installed(self):
        try:
            from xgboost import XGBRegressor
        except ImportError:
            self.skipTest("Optional xgboost dependency is not installed.")
        frame = synthetic_data()
        pipeline = Pipeline([
            ("features", MedTechFeatures()), ("imputer", SimpleImputer()),
            ("scaler", StandardScaler()),
            ("model", XGBRegressor(n_estimators=5, random_state=42, n_jobs=1)),
        ]).fit(frame.iloc[:60], frame["SF 36"].iloc[:60])
        self.assertTrue(np.isfinite(pipeline.predict(frame.iloc[60:])).all())


if __name__ == "__main__":
    unittest.main()
