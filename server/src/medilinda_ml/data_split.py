"""The split of the data into training, validation and test rows.

The experiment and the training both split with this function and these seeds,
so they see the same rows. The test rows are for the final run only.
"""

from typing import Final

import pandas as pd
from medilinda_ml.columns import TARGET_COLUMN
from pydantic import BaseModel, ConfigDict
from sklearn.model_selection import train_test_split

SPLIT_SEED: Final[int] = 42
TEST_FRACTION: Final[float] = 0.25
VALIDATION_FRACTION: Final[float] = 0.2


class DataSplit(BaseModel):
    """The six parts of a split: features and target for each of the three sets."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    X_train: pd.DataFrame
    X_val: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_val: pd.Series
    y_test: pd.Series


def split_dataset(*, df: pd.DataFrame) -> DataSplit:
    """Split the rows into training, validation and test sets, stratified by the target.

    Pure: the same data frame always gives the same split.
    """
    features = df.drop(columns=[TARGET_COLUMN], axis=1)
    target = df[TARGET_COLUMN]

    X_train_and_val, X_test, y_train_and_val, y_test = train_test_split(
        features, target, stratify=target, test_size=TEST_FRACTION, random_state=SPLIT_SEED
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_and_val,
        y_train_and_val,
        stratify=y_train_and_val,
        test_size=VALIDATION_FRACTION,
        random_state=SPLIT_SEED,
    )
    return DataSplit(
        X_train=X_train,
        X_val=X_val,
        X_test=X_test,
        y_train=y_train,
        y_val=y_val,
        y_test=y_test,
    )
