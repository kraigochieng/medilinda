"""The estimator candidates (#141)."""

import pytest
from medilinda_ml.candidates import all_candidates, candidate_named
from medilinda_ml.errors import MedilindaMlError, ModelStoreError, UnknownCandidateError
from sklearn.base import clone
from sklearn.datasets import make_classification

EXPECTED_NAMES = [
    "decision_tree",
    "ada_boost",
    "logistic_regression",
    "random_forest",
    "gradient_boosting",
    "svm",
    "knn",
    "naive_bayes",
]


def test_the_candidates_have_the_expected_names_in_order():
    assert [candidate.name for candidate in all_candidates()] == EXPECTED_NAMES


def test_the_decision_tree_grid_is_the_one_of_the_production_training():
    assert candidate_named(name="decision_tree").param_grid == {"max_depth": [25, 50, 100]}


def test_each_call_gives_new_estimator_objects():
    first = {candidate.name: candidate.estimator for candidate in all_candidates()}
    second = {candidate.name: candidate.estimator for candidate in all_candidates()}

    assert all(first[name] is not second[name] for name in first)


def test_an_unknown_name_raises_with_the_known_names():
    with pytest.raises(UnknownCandidateError) as error:
        candidate_named(name="xgboost")

    assert error.value.name == "xgboost"
    assert error.value.known == sorted(EXPECTED_NAMES)


def test_the_candidate_error_and_the_store_error_share_one_base():
    assert issubclass(UnknownCandidateError, MedilindaMlError)
    assert issubclass(ModelStoreError, MedilindaMlError)


@pytest.mark.parametrize(
    "candidate", all_candidates(), ids=[candidate.name for candidate in all_candidates()]
)
def test_each_grid_value_is_valid_for_the_installed_scikit_learn(candidate):
    """Fit on a tiny data set once for each value, so a removed option fails here."""
    features, labels = make_classification(
        n_samples=80, n_features=6, n_informative=4, n_classes=4, random_state=0
    )

    for parameter, values in candidate.param_grid.items():
        for value in values:
            clone(candidate.estimator).set_params(**{parameter: value}).fit(features, labels)
