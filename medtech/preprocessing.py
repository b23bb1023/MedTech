"""Deterministic feature engineering with training-only selection and encoding."""

import re

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted


class MedTechFeatures(TransformerMixin, BaseEstimator):
    """Prepare the masterchart without learning from held-out records.

    Known identifiers and the outcome are always excluded. Questionnaire values
    are excluded by default; enable them only for the reconstruction comparison.
    This transformer does not certify that a dataset has been anonymized.
    """

    IDENTIFIERS = {"sno", "name", "place of birth", "date", "month", "year", "cr"}
    REQUIRED = {"Site", "staging (TNM)", "Staging", "Prakriti"}
    STAGE_MAP = {"I": 6, "II": 5, "III": 4, "IVA": 3, "IVB": 2, "IVC": 1}

    def __init__(self, include_questionnaire_values=False, missing_columns_to_drop=30,
                 min_site_count=5):
        self.include_questionnaire_values = include_questionnaire_values
        self.missing_columns_to_drop = missing_columns_to_drop
        self.min_site_count = min_site_count

    @staticmethod
    def _sites(series):
        return series.astype("string").str.lower().str.strip().fillna("other").replace("", "other")

    def _validate(self, X):
        if not isinstance(X, pd.DataFrame):
            raise TypeError("MedTechFeatures expects a pandas DataFrame.")
        if X.columns.duplicated().any():
            raise ValueError("Input column names must be unique.")
        missing = self.REQUIRED - set(X.columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

    def _engineer(self, X):
        self._validate(X)
        frame = X.copy()
        excluded = [c for c in frame if
                    c.strip().lower() in self.IDENTIFIERS or
                    c in {"SF 36", "Prakriti.1"} or
                    re.fullmatch(r"Q(?:[1-9]|[12][0-9]|3[0-6])", c) or
                    (not self.include_questionnaire_values and
                     re.fullmatch(r"Value_Q(?:[1-9]|[12][0-9]|3[0-6])", c))]
        frame = frame.drop(columns=excluded)

        sites = self._sites(frame.pop("Site"))
        sites = sites.where(sites.isin(self.common_sites_), "other")
        encoded = pd.get_dummies(pd.Categorical(sites, categories=self.site_levels_),
                                 prefix="Site", drop_first=True, dtype=float)
        encoded.index = frame.index
        frame = pd.concat([frame, encoded], axis=1)

        tnm = frame.pop("staging (TNM)").astype("string").str.upper().str.strip()
        parts = tnm.str.extract(r"T([0-4])[AB]?N([0-3])[ABC]?M([01])")
        invalid = tnm.notna() & tnm.ne("") & parts.isna().any(axis=1)
        if invalid.any():
            raise ValueError("Some TNM labels cannot be parsed; review them privately.")
        parts.columns = ["Tumorsize", "Lymphnodes", "Metastasis"]
        for column in parts:
            frame[column] = pd.to_numeric(parts[column], errors="coerce").astype(float)

        stage = frame["Staging"].astype("string").str.upper().str.strip()
        unknown = stage.notna() & stage.ne("") & ~stage.isin(self.STAGE_MAP)
        if unknown.any():
            raise ValueError("Unrecognized Staging labels; update the documented mapping.")
        frame["Staging"] = stage.map(self.STAGE_MAP).astype(float)

        prakriti = frame.pop("Prakriti").astype("string").str.upper().str.strip()
        invalid = prakriti.notna() & prakriti.ne("") & ~prakriti.str.fullmatch(r"[VPK]+", na=False)
        if invalid.any():
            raise ValueError("Unrecognized Prakriti codes; review the source codebook.")
        for letter, column in [("V", "Vata_present"), ("P", "Pitta_present"),
                               ("K", "Kapha_present")]:
            present = prakriti.str.contains(letter, regex=False, na=False).astype(float)
            frame[column] = present.where(prakriti.notna() & prakriti.ne(""), np.nan)
        # Preserve existing Vatta, Pitta and Kapha scores; do not overwrite them.
        non_numeric = [c for c in frame if not pd.api.types.is_numeric_dtype(frame[c])]
        if non_numeric:
            raise ValueError(f"Unexpected non-numeric features: {non_numeric}")
        return frame.astype(float)

    def fit(self, X, y=None):
        self._validate(X)
        if self.missing_columns_to_drop < 0 or self.min_site_count < 1:
            raise ValueError("Use a non-negative drop count and a positive site threshold.")
        counts = self._sites(X["Site"]).value_counts()
        self.common_sites_ = sorted(counts[counts >= self.min_site_count].index.tolist())
        self.site_levels_ = sorted(set(self.common_sites_) | {"other"})
        engineered = self._engineer(X)
        missing = engineered.isna().sum().sort_values(ascending=False, kind="stable")
        ranked = missing[missing > 0].index.tolist()
        # Always remove fully empty columns, then up to 30 with missing values.
        self.dropped_columns_ = list(dict.fromkeys(
            engineered.columns[engineered.isna().all()].tolist() +
            ranked[:self.missing_columns_to_drop]))
        self.feature_names_out_ = np.asarray(
            [c for c in engineered if c not in self.dropped_columns_], dtype=object)
        self.n_features_in_ = X.shape[1]
        self.feature_names_in_ = np.asarray(X.columns, dtype=object)
        if not len(self.feature_names_out_):
            raise ValueError("No features remain after missingness filtering.")
        return self

    def transform(self, X):
        check_is_fitted(self, "feature_names_out_")
        engineered = self._engineer(X)
        missing = set(self.feature_names_out_) - set(engineered.columns)
        if missing:
            raise ValueError(f"Input is missing trained features: {sorted(missing)}")
        return engineered.loc[:, self.feature_names_out_]

    def get_feature_names_out(self, input_features=None):
        check_is_fitted(self, "feature_names_out_")
        return self.feature_names_out_.copy()
