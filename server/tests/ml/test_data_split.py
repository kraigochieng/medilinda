"""The data split (#145): the experiment and the training must see the same rows."""

import pandas as pd
import pytest
from medilinda_ml.columns import TARGET_COLUMN
from medilinda_ml.data_split import split_dataset
from sklearn.model_selection import train_test_split

LEVELS = ["certain", "likely", "possible", "unlikely"]


@pytest.fixture
def frame() -> pd.DataFrame:
    rows = 1000
    return pd.DataFrame(
        {
            "feature": range(rows),
            TARGET_COLUMN: [LEVELS[index % 4] if index % 10 else "likely" for index in range(rows)],
        }
    )


def test_a_thousand_rows_split_into_600_150_and_250(frame):
    split = split_dataset(df=frame)

    assert (len(split.X_train), len(split.X_val), len(split.X_test)) == (600, 150, 250)


def test_features_and_target_have_the_same_rows_in_each_set(frame):
    split = split_dataset(df=frame)

    assert split.X_train.index.equals(split.y_train.index)
    assert split.X_val.index.equals(split.y_val.index)
    assert split.X_test.index.equals(split.y_test.index)


def test_the_three_sets_share_no_row(frame):
    split = split_dataset(df=frame)

    train, val, test = (set(part.index) for part in (split.X_train, split.X_val, split.X_test))
    assert not (train & val) and not (train & test) and not (val & test)
    assert len(train | val | test) == len(frame)


def test_the_features_do_not_hold_the_target(frame):
    split = split_dataset(df=frame)

    assert TARGET_COLUMN not in split.X_train.columns


def test_each_set_keeps_the_class_shares_of_the_data(frame):
    split = split_dataset(df=frame)
    data_shares = frame[TARGET_COLUMN].value_counts(normalize=True)

    for target in (split.y_train, split.y_val, split.y_test):
        shares = target.value_counts(normalize=True)
        assert (shares - data_shares).abs().max() < 0.02


def test_the_same_data_gives_the_same_split(frame):
    first = split_dataset(df=frame)
    second = split_dataset(df=frame)

    assert first.X_test.index.equals(second.X_test.index)
    assert first.X_train.index.equals(second.X_train.index)


def test_the_split_equals_the_inline_split_that_the_training_used_before(frame):
    """The same two calls, with the same seed, as the code that was inline in train_model.py."""
    features = frame.drop(columns=[TARGET_COLUMN])
    target = frame[TARGET_COLUMN]
    X_train_and_val, X_test, y_train_and_val, _ = train_test_split(
        features, target, stratify=target, test_size=0.25, random_state=42
    )
    X_train, X_val, _, _ = train_test_split(
        X_train_and_val, y_train_and_val, stratify=y_train_and_val, test_size=0.2, random_state=42
    )

    split = split_dataset(df=frame)

    assert split.X_test.index.equals(X_test.index)
    assert split.X_val.index.equals(X_val.index)
    assert split.X_train.index.equals(X_train.index)
