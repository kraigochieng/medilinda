"""The shared pipeline builder gives the same pipeline as the committed model (#141).

The committed model was trained with the code that was inline in train_model.py.
These tests load that model and the new builder, and compare them step by step.
"""

import pytest
from imblearn.pipeline import Pipeline
from medilinda_ml.columns import FINAL_COLUMNS
from medilinda_ml.model_store import read_version
from medilinda_ml.pipeline import build_pipeline, preprocessing_steps
from server.config import MODELS_DIR
from sklearn.tree import DecisionTreeClassifier


@pytest.fixture(scope="module")
def committed_pipeline() -> Pipeline:
    return read_version(root=MODELS_DIR, version="latest").pipeline


@pytest.fixture
def built_pipeline() -> Pipeline:
    return build_pipeline(
        estimator=DecisionTreeClassifier(random_state=42), final_columns=FINAL_COLUMNS
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


def test_the_final_columns_reach_the_column_selection_step(built_pipeline):
    selector = built_pipeline.named_steps["final_column"]

    assert selector.columns == FINAL_COLUMNS


def test_each_call_gives_new_step_objects():
    first = preprocessing_steps()
    second = preprocessing_steps()

    for (_, first_step), (_, second_step) in zip(first, second):
        assert first_step is not second_step
