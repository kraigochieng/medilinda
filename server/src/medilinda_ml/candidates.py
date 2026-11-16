"""The estimators that the experiment compares, with the grid of each one."""

from pydantic import BaseModel, ConfigDict
from sklearn.base import BaseEstimator
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from medilinda_ml.errors import UnknownCandidateError

ESTIMATOR_SEED = 42


class Candidate(BaseModel):
    """One estimator and the values that the search tries for each of its parameters."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    estimator: BaseEstimator
    param_grid: dict[str, list[object]]


def all_candidates() -> list[Candidate]:
    """Return a new Candidate for each estimator, so no search shares an estimator object."""
    return [
        Candidate(
            name="decision_tree",
            estimator=DecisionTreeClassifier(random_state=ESTIMATOR_SEED),
            param_grid={"max_depth": [25, 50, 100]},
        ),
        Candidate(
            name="ada_boost",
            estimator=AdaBoostClassifier(random_state=ESTIMATOR_SEED),
            param_grid={"n_estimators": [10, 50], "learning_rate": [0.1, 1.0]},
        ),
        Candidate(
            name="logistic_regression",
            estimator=LogisticRegression(
                random_state=ESTIMATOR_SEED, max_iter=1000, solver="saga"
            ),
            param_grid={"C": [0.01, 0.1, 1, 10], "penalty": ["l2"]},
        ),
        Candidate(
            name="random_forest",
            estimator=RandomForestClassifier(random_state=ESTIMATOR_SEED),
            param_grid={
                "n_estimators": [50, 100, 200],
                "max_depth": [None, 10, 30, 50],
                "max_features": ["sqrt", "log2"],
            },
        ),
        Candidate(
            name="gradient_boosting",
            estimator=GradientBoostingClassifier(random_state=ESTIMATOR_SEED),
            param_grid={
                "n_estimators": [50, 100],
                "learning_rate": [0.01, 0.1],
                "max_depth": [3, 5],
                "subsample": [0.8, 1.0],
            },
        ),
        Candidate(
            name="svm",
            estimator=SVC(probability=True, random_state=ESTIMATOR_SEED),
            param_grid={"kernel": ["rbf"], "C": [0.1, 1, 3], "gamma": ["scale", "auto"]},
        ),
        Candidate(
            name="knn",
            estimator=KNeighborsClassifier(),
            param_grid={
                "n_neighbors": [3, 5, 7],
                "weights": ["uniform", "distance"],
                "p": [1, 2],
            },
        ),
        Candidate(name="naive_bayes", estimator=GaussianNB(), param_grid={}),
    ]


def candidate_named(*, name: str) -> Candidate:
    """Return the candidate with this name. Raise UnknownCandidateError if none has it."""
    candidates_by_name = {candidate.name: candidate for candidate in all_candidates()}
    if name not in candidates_by_name:
        raise UnknownCandidateError(name=name, known=sorted(candidates_by_name))
    return candidates_by_name[name]
