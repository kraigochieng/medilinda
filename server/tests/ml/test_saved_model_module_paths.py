"""A saved model is a pickle. It stores the module path of each class it uses.

If a module moves or is renamed, the saved model no longer loads (issue #116).
These tests fix the module paths and the output of the classes that the saved
pipeline and the SHAP explainer use.
"""

import pickle

import pandas as pd
import pytest
from medilinda_ml.data.set_datatypes import DatatypeSetter
from medilinda_ml.features.build_features import (
    MinMaxScalingTransformer,
    NumericalImputer,
)
from medilinda_ml.utils import ShapModelWrapper
from sklearn.pipeline import Pipeline

SAVED_MODULE_PATHS: list[bytes] = [
    b"medilinda_ml.data.set_datatypes",
    b"medilinda_ml.features.build_features",
]


@pytest.fixture
def fitted_pipeline() -> Pipeline:
    training_rows = pd.DataFrame(
        {
            "patient_gender": ["female", "male", "female"],
            "date_of_onset_of_reaction": ["2025-10-15", "2025-10-16", None],
            "patient_weight_kg": [50.0, 100.0, None],
        }
    )
    pipeline = Pipeline(
        steps=[
            (
                "datatypes",
                DatatypeSetter(
                    categorical_columns=["patient_gender"],
                    date_columns=["date_of_onset_of_reaction"],
                    verbose=False,
                ),
            ),
            (
                "imputer",
                NumericalImputer(numerical_columns=["patient_weight_kg"], verbose=False),
            ),
            (
                "scaler",
                MinMaxScalingTransformer(
                    numerical_columns=["patient_weight_kg"], verbose=False
                ),
            ),
        ]
    )
    return pipeline.fit(training_rows)


def test_the_pickle_stores_the_module_paths_that_a_saved_model_needs(
    fitted_pipeline: Pipeline,
) -> None:
    pickled_pipeline: bytes = pickle.dumps(fitted_pipeline)

    for module_path in SAVED_MODULE_PATHS:
        assert module_path in pickled_pipeline


def test_the_unpickled_pipeline_gives_the_stored_output(
    fitted_pipeline: Pipeline,
) -> None:
    unpickled_pipeline: Pipeline = pickle.loads(pickle.dumps(fitted_pipeline))
    new_rows = pd.DataFrame(
        {
            "patient_gender": ["female", "male"],
            "date_of_onset_of_reaction": ["2025-10-20", "not a date"],
            "patient_weight_kg": [50.0, None],
        }
    )

    output = unpickled_pipeline.transform(new_rows)

    # The imputer fills a missing weight with -1. The scaler then maps -1..100 to 0..1.
    assert output["patient_weight_kg"].tolist() == pytest.approx([51 / 101, 0.0])
    assert output["date_of_onset_of_reaction"].iloc[0] == pd.Timestamp("2025-10-20")
    assert pd.isna(output["date_of_onset_of_reaction"].iloc[1])
    assert str(output["patient_gender"].dtype) == "category"


def test_the_shap_wrapper_unpickles_and_calls_the_model() -> None:
    class FakeModel:
        def predict_proba(self, frame: pd.DataFrame) -> list[list[float]]:
            return [[float(frame["a"].iloc[0]), 1.0]]

    wrapper = ShapModelWrapper(model=None, column_names=["a"])
    unpickled_wrapper: ShapModelWrapper = pickle.loads(pickle.dumps(wrapper))
    unpickled_wrapper.model = FakeModel()

    assert unpickled_wrapper([[3.0]]) == [[3.0, 1.0]]
    assert b"medilinda_ml.utils" in pickle.dumps(wrapper)
