"""The pure rules of the experiment: how it picks the winner, and how it cleans parameters."""

from typing import Final

from medilinda_ml.errors import NoCandidateResultsError
from pydantic import BaseModel, JsonValue

CLASSIFIER_PREFIX: Final[str] = "classifier__"


class CandidateResult(BaseModel):
    """What the search found for one candidate, measured on the training rows only."""

    name: str
    best_params: dict[str, JsonValue]
    cv_mean_weighted_f1: float
    cv_std_weighted_f1: float
    validation_weighted_f1: float


def choose_winner(*, results: list[CandidateResult]) -> CandidateResult:
    """Return the result with the highest mean cross-validation weighted F1.

    A tie goes to the earlier result in the list, which is the simpler candidate.
    Raises NoCandidateResultsError if the list is empty.
    """
    if not results:
        raise NoCandidateResultsError()
    winner = results[0]
    for result in results[1:]:
        if result.cv_mean_weighted_f1 > winner.cv_mean_weighted_f1:
            winner = result
    return winner


def to_json_params(*, search_params: dict[str, object]) -> dict[str, JsonValue]:
    """Return the parameters of the classifier as plain JSON values.

    The search names a parameter `classifier__max_depth`. The result names it `max_depth`.
    NumPy numbers become Python numbers.
    """
    cleaned: dict[str, JsonValue] = {}
    for name, value in search_params.items():
        plain_name = name.removeprefix(CLASSIFIER_PREFIX)
        cleaned[plain_name] = value.item() if hasattr(value, "item") else value
    return cleaned
