"""The pure rules of the experiment (#145)."""

import numpy as np
import pytest
from medilinda_ml.errors import NoCandidateResultsError
from medilinda_ml.experiment_rules import CandidateResult, choose_winner, to_json_params


def result(name: str, cv_mean: float) -> CandidateResult:
    return CandidateResult(
        name=name,
        best_params={},
        cv_mean_weighted_f1=cv_mean,
        cv_std_weighted_f1=0.01,
        validation_weighted_f1=0.5,
    )


def test_the_highest_cross_validation_score_wins():
    results = [result("decision_tree", 0.80), result("random_forest", 0.88), result("knn", 0.83)]

    assert choose_winner(results=results).name == "random_forest"


def test_a_tie_goes_to_the_earlier_candidate():
    results = [result("decision_tree", 0.85), result("random_forest", 0.85)]

    assert choose_winner(results=results).name == "decision_tree"


def test_a_single_result_wins():
    assert choose_winner(results=[result("knn", 0.1)]).name == "knn"


def test_the_validation_score_does_not_change_the_winner():
    low_cv_high_validation = result("a", 0.70).model_copy(update={"validation_weighted_f1": 0.99})
    high_cv_low_validation = result("b", 0.80).model_copy(update={"validation_weighted_f1": 0.10})

    assert choose_winner(results=[low_cv_high_validation, high_cv_low_validation]).name == "b"


def test_no_results_raises():
    with pytest.raises(NoCandidateResultsError):
        choose_winner(results=[])


def test_the_classifier_prefix_is_removed():
    assert to_json_params(search_params={"classifier__max_depth": 25}) == {"max_depth": 25}


def test_numpy_numbers_become_python_numbers():
    cleaned = to_json_params(
        search_params={"classifier__max_depth": np.int64(25), "classifier__learning_rate": np.float64(0.1)}
    )

    assert cleaned == {"max_depth": 25, "learning_rate": 0.1}
    assert type(cleaned["max_depth"]) is int
    assert type(cleaned["learning_rate"]) is float


def test_none_and_text_stay_as_they_are():
    cleaned = to_json_params(search_params={"classifier__max_depth": None, "classifier__max_features": "sqrt"})

    assert cleaned == {"max_depth": None, "max_features": "sqrt"}
