"""Load the training frame: the rows with a level that the model predicts, and the columns of one feature set.

The generated dataset has two feature sets:

- "app": the columns that the app collects today. The production model uses this set.
- "full": the app columns and the new report fields of decision DR-8 (issue #174).

The diagnostics of the generator (the clean label, the latent cause) are in another file. This loader
refuses a frame that has one of those columns, so training cannot read the answer.
"""

from pathlib import Path
from typing import Final, Literal

import pandas as pd
from medilinda_ml.columns import REPORT_EXTRA_COLUMNS, TARGET_COLUMN, TARGET_LEVELS
from medilinda_ml.errors import TrainingDataLeakError

FeatureSet = Literal["app", "full"]

FORBIDDEN_COLUMNS: Final[list[str]] = ["causality_by_rule", "is_drug_related", "regimen"]


def prepare_training_frame(*, frame: pd.DataFrame, feature_set: FeatureSet) -> pd.DataFrame:
    """Return the rows of the four levels, with the columns of the feature set. Pure.

    Raises TrainingDataLeakError if the frame has a diagnostic column.
    """
    leaked = [column for column in FORBIDDEN_COLUMNS if column in frame.columns]
    if leaked:
        raise TrainingDataLeakError(columns=leaked)
    rows = frame[frame[TARGET_COLUMN].isin(TARGET_LEVELS)].reset_index(drop=True)
    if feature_set == "app":
        return rows.drop(columns=REPORT_EXTRA_COLUMNS, errors="ignore")
    return rows


def load_training_frame(*, path: Path, feature_set: FeatureSet) -> pd.DataFrame:
    """Side effect (disk): read the dataset file (CSV, or CSV compressed with gzip) and prepare it."""
    return prepare_training_frame(frame=pd.read_csv(path), feature_set=feature_set)
