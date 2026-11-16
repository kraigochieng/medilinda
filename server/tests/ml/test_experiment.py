"""A small end-to-end run of the experiment (#145).

It needs MLflow, which is in the `train` group. CI installs the `dev` group only,
so CI skips this file. Run it with `uv run --group train pytest tests/ml/test_experiment.py`.
"""

from pathlib import Path

import pandas as pd
import pytest

mlflow = pytest.importorskip("mlflow")

from medilinda_ml.candidates import candidate_named  # noqa: E402
from medilinda_ml.experiment import run_experiment  # noqa: E402
from medilinda_ml.paths import DATA_DIR  # noqa: E402
from medilinda_ml.selection import check_data_matches, read_selection  # noqa: E402


@pytest.fixture
def small_data(tmp_path: Path) -> Path:
    """A 400-row part of the training data, so the run takes seconds."""
    path = tmp_path / "small.csv"
    pd.read_csv(DATA_DIR / "data.csv").head(400).to_csv(path, index=False)
    return path


@pytest.fixture
def experiment_result(tmp_path: Path, small_data: Path):
    result = run_experiment(
        data_path=small_data,
        selection_path=tmp_path / "selection.json",
        tracking_dir=tmp_path / "runs",
        candidates=[candidate_named(name="decision_tree"), candidate_named(name="naive_bayes")],
        cv_splits=3,
        cv_repeats=1,
    )
    yield result
    mlflow.set_tracking_uri("file:///dev/null")


def test_the_run_writes_a_selection_that_names_one_of_the_candidates(
    tmp_path, small_data, experiment_result
):
    selection = read_selection(path=tmp_path / "selection.json")

    assert selection.estimator in {"decision_tree", "naive_bayes"}
    assert selection == experiment_result.selection
    check_data_matches(selection=selection, data_path=small_data)


def test_the_selection_features_are_a_non_empty_list_of_the_selected_columns(experiment_result):
    assert experiment_result.selection.features == experiment_result.selected_features
    assert len(experiment_result.selected_features) >= 1


def test_the_winner_has_the_highest_cross_validation_score(experiment_result):
    best = max(result.cv_mean_weighted_f1 for result in experiment_result.candidate_results)

    assert experiment_result.winner.cv_mean_weighted_f1 == best


def test_mlflow_holds_one_parent_run_with_one_child_run_for_each_candidate(
    tmp_path, experiment_result
):
    client = mlflow.MlflowClient(tracking_uri=(tmp_path / "runs").as_uri())
    experiment = client.get_experiment_by_name("medilinda-causality")
    runs = client.search_runs([experiment.experiment_id])
    parent = client.get_run(experiment_result.selection.experiment_run_id)

    assert parent.data.tags["stage"] == "experiment"
    assert parent.data.tags["winner"] == experiment_result.winner.name
    children = [run for run in runs if run.data.tags.get("mlflow.parentRunId") == parent.info.run_id]
    named = {run.data.tags.get("candidate") for run in children} - {None}
    assert named == {"decision_tree", "naive_bayes"}


def test_no_run_logs_a_metric_of_the_test_split(tmp_path, experiment_result):
    client = mlflow.MlflowClient(tracking_uri=(tmp_path / "runs").as_uri())
    experiment = client.get_experiment_by_name("medilinda-causality")

    metric_names = {
        name for run in client.search_runs([experiment.experiment_id]) for name in run.data.metrics
    }

    assert metric_names
    assert not any(name.startswith("test_") for name in metric_names)
