"""Tests of the PPB report totals: the sums, and the percents that the report prints."""

import pytest
from medilinda_ml.marginals import (
    ALL_DISTRIBUTIONS,
    CRITERIA_FOR_SERIOUSNESS,
    AGE_GROUP,
    ACTION_TAKEN,
    GENDER,
    IS_SERIOUS,
    OUTCOME,
    PREGNANCY_STATUS_OF_FEMALES,
    SEVERITY,
    TB_COMBINATION_MENTIONS,
    CountedDistribution,
    proportions,
)
from pydantic import ValidationError


@pytest.mark.parametrize("distribution", ALL_DISTRIBUTIONS, ids=lambda item: item.name)
def test_every_distribution_has_a_source_and_sums_to_its_total(distribution: CountedDistribution) -> None:
    assert sum(distribution.counts.values()) == distribution.total
    assert distribution.source


@pytest.mark.parametrize("distribution", ALL_DISTRIBUTIONS, ids=lambda item: item.name)
def test_the_proportions_sum_to_one(distribution: CountedDistribution) -> None:
    assert sum(proportions(distribution=distribution).values()) == pytest.approx(1.0)


def test_a_distribution_whose_counts_do_not_add_up_is_refused() -> None:
    with pytest.raises(ValidationError):
        CountedDistribution(name="broken", counts={"a": 1, "b": 2}, total=4, source="test")


@pytest.mark.parametrize(
    ("distribution", "category", "printed_percent"),
    [
        (AGE_GROUP, "adult", 77.38),
        (AGE_GROUP, "elderly", 14.29),
        (GENDER, "female", 61.90),
        (SEVERITY, "mild", 42.86),
        (SEVERITY, "severe", 14.58),
        (IS_SERIOUS, "yes", 19.64),
        (CRITERIA_FOR_SERIOUSNESS, "hospitalization", 51.52),
        (ACTION_TAKEN, "drug_withdrawn", 61.31),
        (OUTCOME, "recovering", 37.80),
        (PREGNANCY_STATUS_OF_FEMALES, "not_pregnant", 60.10),
    ],
)
def test_the_percent_matches_the_percent_that_the_report_prints(
    distribution: CountedDistribution, category: str, printed_percent: float
) -> None:
    assert proportions(distribution=distribution)[category] * 100 == pytest.approx(printed_percent, abs=0.01)


def test_the_combination_medicines_are_mostly_rhze() -> None:
    shares = proportions(distribution=TB_COMBINATION_MENTIONS)

    assert shares["rhze"] > 0.9
    assert set(shares) == {"rhze", "rhz", "rh"}
