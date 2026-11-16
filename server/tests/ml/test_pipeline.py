"""The shared pipeline builder gives the same pipeline as the committed model (#141).

These tests load the committed model and build a pipeline with the same estimator
class and the same columns. They compare the two step by step. The estimator and
the columns change with each new model, so the test reads them from the model.
"""

import pytest
from imblearn.pipeline import Pipeline
from medilinda_ml.columns import FINAL_COLUMNS
from medilinda_ml.model_store import read_version
from medilinda_ml.pipeline import build_pipeline, preprocessing_steps
from server.config import MODELS_DIR
from sklearn.base import BaseEstimator
from sklearn.tree import DecisionTreeClassifier


@pytest.fixture(scope="module")
def committed_pipeline() -> Pipeline:
    return read_version(root=MODELS_DIR, version="latest").pipeline


@pytest.fixture
def built_pipeline(committed_pipeline: Pipeline) -> Pipeline:
    committed_classifier: BaseEstimator = committed_pipeline.steps[-1][1]
    return build_pipeline(
        estimator=type(committed_classifier)(),
        final_columns=committed_pipeline.named_steps["final_column"].columns,
    )


def test_the_steps_have_the_same_names_in_the_same_order(
    committed_pipeline, built_pipeline
):
    assert [name for name, _ in built_pipeline.steps] == [
        name for name, _ in committed_pipeline.steps
    ]


def parameters_without_verbose(step) -> dict[str, object]:
    """The constructor parameters of a step, except `verbose`.

    The training turns every `verbose` flag off before it saves the model, so
    the saved model and a new pipeline differ in this one parameter on purpose.
    """
    return {
        name: value
        for name, value in step.get_params(deep=False).items()
        if name != "verbose"
    }


def test_each_step_before_the_classifier_has_the_same_class_and_parameters(
    committed_pipeline, built_pipeline
):
    committed_steps = committed_pipeline.steps[:-1]
    built_steps = built_pipeline.steps[:-1]

    for (name, committed_step), (_, built_step) in zip(committed_steps, built_steps):
        assert type(built_step) is type(committed_step), name
        assert parameters_without_verbose(built_step) == parameters_without_verbose(
            committed_step
        ), name


def test_the_classifier_has_the_same_class(committed_pipeline, built_pipeline):
    assert type(built_pipeline.steps[-1][1]) is type(committed_pipeline.steps[-1][1])


def test_smote_comes_after_the_column_selection_and_before_the_classifier(
    built_pipeline,
):
    names = [name for name, _ in built_pipeline.steps]

    assert names[-3:] == ["final_column", "smote", "classifier"]


def test_the_final_columns_reach_the_column_selection_step():
    pipeline = build_pipeline(
        estimator=DecisionTreeClassifier(), final_columns=FINAL_COLUMNS
    )

    assert pipeline.named_steps["final_column"].columns == FINAL_COLUMNS


def test_each_call_gives_new_step_objects():
    first = preprocessing_steps()
    second = preprocessing_steps()

    for (_, first_step), (_, second_step) in zip(first, second):
        assert first_step is not second_step
