"""Tests of the training frame, the history features, and the feature sets (issue #172)."""

import pandas as pd
import pytest
from imblearn.pipeline import Pipeline
from medilinda_ml.columns import HISTORY_FLAG_COLUMNS, LAB_COLUMNS, REPORT_EXTRA_COLUMNS, TARGET_COLUMN
from medilinda_ml.data_generation import generate_tables
from medilinda_ml.data_split import split_dataset
from medilinda_ml.dataset_rows import DATASET_COLUMNS, NEW_COLUMNS
from medilinda_ml.errors import TrainingDataLeakError
from medilinda_ml.evaluation import classify, headline_metrics
from medilinda_ml.features.history_features import HistoryFeaturesTransformer
from medilinda_ml.pipeline import build_pipeline, preprocessing_steps
from medilinda_ml.selection import ModelSelection
from medilinda_ml.training_data import prepare_training_frame
from sklearn.preprocessing import OrdinalEncoder
from sklearn.tree import DecisionTreeClassifier


@pytest.fixture(scope="module")
def dataset() -> pd.DataFrame:
    """A generated dataset that is large enough for SMOTE to find neighbours in every class."""
    return generate_tables(rows=3000, seed=11, label_noise=0.05)[0]


def test_the_extra_columns_of_the_columns_module_match_the_dataset_columns() -> None:
    assert set(REPORT_EXTRA_COLUMNS) == set(NEW_COLUMNS)


def test_the_app_feature_set_keeps_only_the_four_levels_and_the_old_columns(dataset: pd.DataFrame) -> None:
    frame = prepare_training_frame(frame=dataset, feature_set="app")

    assert set(frame[TARGET_COLUMN]) == {"certain", "likely", "possible", "unlikely"}
    assert not set(REPORT_EXTRA_COLUMNS) & set(frame.columns)
    assert len(frame) == dataset[TARGET_COLUMN].isin(["certain", "likely", "possible", "unlikely"]).sum()


def test_the_full_feature_set_keeps_the_new_columns(dataset: pd.DataFrame) -> None:
    frame = prepare_training_frame(frame=dataset, feature_set="full")

    assert set(REPORT_EXTRA_COLUMNS) <= set(frame.columns)


def test_a_diagnostic_column_is_refused(dataset: pd.DataFrame) -> None:
    leaking = dataset.assign(causality_by_rule="certain")

    with pytest.raises(TrainingDataLeakError) as error:
        prepare_training_frame(frame=leaking, feature_set="app")

    assert error.value.columns == ["causality_by_rule"]


def test_the_history_features_encode_flags_labs_and_text_columns() -> None:
    frame = pd.DataFrame(
        {
            **{column: [True, False, None] for column in HISTORY_FLAG_COLUMNS},
            "alt_multiple_of_upper_limit": [6.5, None, 1.0],
            "bilirubin_umol_per_l": [None, 51.0, 12.0],
            "antiretroviral": ["nnrti_based", "none", "unknown"],
            "visual_exam": ["abnormal", "not_done", "normal"],
        }
    )

    result = HistoryFeaturesTransformer().fit(frame).transform(frame)

    assert result["alcohol_use"].tolist() == [1.0, 0.0, -1.0]
    assert result["alt_multiple_of_upper_limit"].tolist() == [6.5, -1.0, 1.0]
    assert result["bilirubin_umol_per_l"].tolist() == [-1.0, 51.0, 12.0]
    assert result["antiretroviral_nnrti_based"].tolist() == [1.0, 0.0, 0.0]
    assert result["antiretroviral_unknown"].tolist() == [0.0, 0.0, 1.0]
    assert result["visual_exam_abnormal"].tolist() == [1.0, 0.0, 0.0]
    assert "antiretroviral" not in result.columns
    assert "visual_exam" not in result.columns
    assert set(LAB_COLUMNS) <= set(result.columns)


def test_the_history_features_do_not_change_their_input() -> None:
    frame = pd.DataFrame(
        {
            **{column: [True] for column in HISTORY_FLAG_COLUMNS},
            "alt_multiple_of_upper_limit": [None],
            "bilirubin_umol_per_l": [None],
            "antiretroviral": ["none"],
            "visual_exam": ["normal"],
        }
    )
    before = frame.copy()

    HistoryFeaturesTransformer().transform(frame)

    pd.testing.assert_frame_equal(frame, before)


@pytest.mark.parametrize("feature_set", ["app", "full"])
def test_a_pipeline_fits_and_predicts_on_each_feature_set(dataset: pd.DataFrame, feature_set: str) -> None:
    frame = prepare_training_frame(frame=dataset, feature_set=feature_set)  # type: ignore[arg-type]  # the parameter is a literal
    split = split_dataset(df=frame)
    include_history = feature_set == "full"
    prepared = Pipeline(preprocessing_steps(include_history=include_history)).fit_transform(split.X_train)
    columns = [str(name) for name in prepared.select_dtypes(include=["number", "bool"]).columns][:12]
    encoder = OrdinalEncoder(categories=[["certain", "likely", "possible", "unlikely"]])
    labels = encoder.fit_transform(split.y_train.to_frame()).ravel()
    pipeline = build_pipeline(estimator=DecisionTreeClassifier(random_state=0), final_columns=columns, include_history=include_history)

    pipeline.fit(split.X_train, labels)

    assert len(pipeline.predict(split.X_val)) == len(split.X_val)


def test_a_selection_without_a_feature_set_means_the_app_columns() -> None:
    selection = ModelSelection(
        estimator="decision_tree",
        params={},
        features=["patient_bmi"],
        data_sha256="a" * 64,
        split_seed=42,
        experiment_run_id="abc",
        cv_weighted_f1=0.5,
    )

    assert selection.feature_set == "app"


def test_the_recall_of_certain_is_a_headline_metric_when_the_label_exists() -> None:
    result = classify(
        true_labels=["certain", "certain", "likely", "likely"],
        predicted_labels=["certain", "likely", "likely", "likely"],
        labels=["certain", "likely"],
    )

    assert headline_metrics(split="test", result=result)["test_recall_certain"] == pytest.approx(0.5)


def test_the_dataset_columns_have_the_target_last() -> None:
    assert DATASET_COLUMNS[-1] == TARGET_COLUMN
