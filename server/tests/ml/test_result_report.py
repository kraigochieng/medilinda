"""Tests of the result report (issue #164): the baseline, one scenario, and the Markdown."""

import pytest
from medilinda_ml.data_generation import generate_tables
from medilinda_ml.result_report import constant_baseline_weighted_f1, evaluate_scenario, render_markdown
from medilinda_ml.selection import ModelSelection


@pytest.fixture(scope="module")
def tables():  # type: ignore[no-untyped-def]  # a pair of data frames
    """A generated dataset that is large enough for a stratified split."""
    return generate_tables(rows=3000, seed=21, label_noise=0.05)


def small_selection() -> ModelSelection:
    """Return a selection of a small decision tree on two columns of the app."""
    return ModelSelection(
        estimator="decision_tree",
        params={"max_depth": 5},
        features=["dechallenge_yes", "patient_bmi"],
        data_sha256="a" * 64,
        split_seed=42,
        experiment_run_id="abc",
        cv_weighted_f1=0.5,
    )


def test_the_constant_model_scores_below_a_good_model() -> None:
    labels = ["possible"] * 60 + ["likely"] * 30 + ["unlikely"] * 10

    baseline = constant_baseline_weighted_f1(labels=labels)

    assert 0.4 < baseline < 0.6


def test_a_scenario_measures_the_test_rows_against_both_labels(tables) -> None:  # type: ignore[no-untyped-def]
    dataset, diagnostics = tables

    result = evaluate_scenario(name="small", selection=small_selection(), dataset=dataset, diagnostics=diagnostics)

    assert result.feature_count == 2
    assert result.against_noisy_label.rows == result.test_rows
    assert result.against_clean_label.rows == result.test_rows
    assert sum(sum(row) for row in result.against_clean_label.confusion_matrix) == result.test_rows


def test_the_markdown_has_the_tables_and_the_limit(tables) -> None:  # type: ignore[no-untyped-def]
    dataset, diagnostics = tables
    result = evaluate_scenario(name="small", selection=small_selection(), dataset=dataset, diagnostics=diagnostics)

    text = render_markdown(scenarios=[result], noise_scenarios=[result], baseline=0.46, rows=3000)

    assert "# Results of the models on the synthetic data" in text
    assert "do not show clinical accuracy" in text
    assert "| small |" in text
    assert "## Confusion matrices" in text
