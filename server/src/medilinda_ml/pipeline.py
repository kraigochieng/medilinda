"""The pipeline that the experiment and the training share.

The notebook and `train_model.py` build the model with these functions, so the
model of the experiment is the model of the production training.
"""

from typing import Final

from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from medilinda_ml.columns import (
    COLUMNS_FOR_ONE_HOT,
    COLUMNS_TO_DROP,
    DATE_COLUMNS,
    DRUG_NAMES,
    INITIAL_CATEGORICAL_COLUMNS,
    NUMERICAL_COLUMNS,
)
from medilinda_ml.data.set_datatypes import DatatypeSetter
from medilinda_ml.features.history_features import HistoryFeaturesTransformer
from medilinda_ml.features.build_features import (
    DropColumnsTransformer,
    DrugDateDifferenceTransformer,
    FinalColumnSelectorTransformer,
    MinMaxScalingTransformer,
    NumberOfSuspectedDrugsTransformer,
    NumericalImputer,
    OneHotEncodingTransformer,
    PatientAgeImputer,
    PatientBMITransformer,
)
from sklearn.base import BaseEstimator

RESAMPLING_SEED: Final[int] = 42


def preprocessing_steps(*, include_history: bool = False) -> list[tuple[str, BaseEstimator]]:
    """Return the steps that turn a raw report into the columns before the selection.

    Each call returns new step objects, so two pipelines never share a fitted step.
    With include_history, a step first turns the new report fields (decision DR-8) into numbers.
    """
    history_steps: list[tuple[str, BaseEstimator]] = (
        [("history_features", HistoryFeaturesTransformer())] if include_history else []
    )
    return [
        *history_steps,
        (
            "set_datatypes",
            DatatypeSetter(
                categorical_columns=INITIAL_CATEGORICAL_COLUMNS,
                date_columns=DATE_COLUMNS,
            ),
        ),
        ("patient_age_imputer", PatientAgeImputer()),
        ("patient_bmi", PatientBMITransformer()),
        (
            "drug_date_difference",
            DrugDateDifferenceTransformer(drug_names=DRUG_NAMES, date_columns=DATE_COLUMNS),
        ),
        (
            "num_of_suspected_drugs",
            NumberOfSuspectedDrugsTransformer(drug_names=DRUG_NAMES),
        ),
        ("drop_irrelevant_columns", DropColumnsTransformer(columns=COLUMNS_TO_DROP)),
        ("numerical_imputer", NumericalImputer(numerical_columns=NUMERICAL_COLUMNS)),
        (
            "one_hot_encoding",
            OneHotEncodingTransformer(categorical_columns=COLUMNS_FOR_ONE_HOT),
        ),
        (
            "numerical_scaling",
            MinMaxScalingTransformer(numerical_columns=["patient_bmi"]),
        ),
    ]


def build_pipeline(
    *, estimator: BaseEstimator, final_columns: list[str], include_history: bool = False
) -> Pipeline:
    """Return the full pipeline: preprocessing, column selection, SMOTE, then the estimator.

    SMOTE is a step of the pipeline, so cross-validation resamples inside each fold.
    """
    return Pipeline(
        [
            *preprocessing_steps(include_history=include_history),
            ("final_column", FinalColumnSelectorTransformer(columns=final_columns)),
            ("smote", SMOTE(random_state=RESAMPLING_SEED)),
            ("classifier", estimator),
        ]
    )
