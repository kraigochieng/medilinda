"""The features of the new report fields (decision DR-8): other causes, labs, and the eye exam.

A flag becomes 1 for yes, 0 for no, and -1 for "not recorded". A lab value that was not measured becomes -1.
The text columns become 0 or 1 columns. The original columns are dropped.
"""

import pandas as pd
from medilinda_ml.columns import HISTORY_FLAG_COLUMNS, LAB_COLUMNS
from sklearn.base import BaseEstimator, TransformerMixin

NOT_RECORDED = -1.0


def _flag_value(value: object) -> float:
    """Return 1 for a true flag, 0 for a false flag, and -1 when the flag is missing."""
    if value is None or (isinstance(value, float) and value != value):
        return NOT_RECORDED
    return 1.0 if str(value).lower() == "true" else 0.0


class HistoryFeaturesTransformer(BaseEstimator, TransformerMixin):
    """Turn the history, antiretroviral, lab and eye columns into numbers. Pure: it returns a new frame."""

    def fit(self, X: pd.DataFrame, y: object = None) -> "HistoryFeaturesTransformer":
        """Learn nothing: the encoding is fixed."""
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Return the frame with the new columns as numbers."""
        frame = X.copy()
        for column in HISTORY_FLAG_COLUMNS:
            frame[column] = frame[column].map(_flag_value).astype(float)
        for column in LAB_COLUMNS:
            frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(NOT_RECORDED)
        for value in ("nnrti_based", "dolutegravir_based", "unknown"):
            frame[f"antiretroviral_{value}"] = (frame["antiretroviral"] == value).astype(float)
        for value in ("abnormal", "normal"):
            frame[f"visual_exam_{value}"] = (frame["visual_exam"] == value).astype(float)
        return frame.drop(columns=["antiretroviral", "visual_exam"])
