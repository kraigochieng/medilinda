"""Tests of the case sampler: the causal order, the invariants, and the PPB totals."""

import ast
import random
from datetime import date
from pathlib import Path

import medilinda_ml.case_sampler as case_sampler_module
import pytest
from medilinda_ml.case_sampler import (
    SampledCase,
    sample_case,
    sample_event,
    sample_exposures,
    sample_grading,
    sample_regimen,
)
from medilinda_ml.reaction_knowledge import KNOWN_CATEGORIES_BY_DRUG, ReactionCategory
from medilinda_ml.report_fields import DrugName
from medilinda_ml.sampler_assumptions import SamplerAssumptions

REFERENCE_DATE = date(2026, 11, 1)
SAMPLE_SIZE = 4000


def many_cases(*, seed: int = 7, count: int = SAMPLE_SIZE, assumptions: SamplerAssumptions | None = None) -> list[SampledCase]:
    """Sample many cases from one seed."""
    random_source = random.Random(seed)
    if assumptions is None:
        return [sample_case(random_source=random_source, reference_date=REFERENCE_DATE) for _ in range(count)]
    return [
        sample_case(random_source=random_source, reference_date=REFERENCE_DATE, assumptions=assumptions)
        for _ in range(count)
    ]


@pytest.fixture(scope="module")
def cases() -> list[SampledCase]:
    """A large sample that the tests of the totals and the invariants share."""
    return many_cases()


def test_the_same_seed_gives_the_same_case() -> None:
    first = sample_case(random_source=random.Random(3), reference_date=REFERENCE_DATE)
    second = sample_case(random_source=random.Random(3), reference_date=REFERENCE_DATE)

    assert first == second


def test_different_seeds_give_different_cases() -> None:
    first = sample_case(random_source=random.Random(3), reference_date=REFERENCE_DATE)
    second = sample_case(random_source=random.Random(4), reference_date=REFERENCE_DATE)

    assert first != second


def test_the_sampler_never_reads_the_who_umc_level() -> None:
    tree = ast.parse(Path(case_sampler_module.__file__).read_text())
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    } | {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}

    assert not any("who_umc" in name or "case_facts" in name for name in imported)
    assert "CausalityLevel" not in imported


def test_the_dates_are_in_causal_order(cases: list[SampledCase]) -> None:
    for case in cases:
        report = case.report
        starts = [exposure.start_date for exposure in report.exposures if exposure.start_date is not None]
        stops = [exposure.stop_date for exposure in report.exposures if exposure.stop_date is not None]
        assert all(stop >= start for start in starts for stop in stops)
        if report.onset_date is not None:
            assert all(report.onset_date >= start for start in starts)
            assert all(stop >= report.onset_date for stop in stops)
            assert case.report_date >= report.onset_date
        assert all(case.report_date >= stop for stop in stops)


def test_a_combination_medicine_is_one_exposure_to_all_its_drugs() -> None:
    random_source = random.Random(11)
    regimens = [sample_regimen(random_source=random_source) for _ in range(500)]
    combinations = [regimen for regimen in regimens if regimen.name != "separate"]

    assert combinations
    assert all(regimen.suspected == regimen.taken for regimen in combinations)
    exposures = sample_exposures(regimen=combinations[0], start_date=date(2026, 1, 1), stop_date=date(2026, 2, 1))
    taken = [exposure for exposure in exposures if exposure.start_date is not None]
    assert {exposure.start_date for exposure in taken} == {date(2026, 1, 1)}
    assert {exposure.stop_date for exposure in taken} == {date(2026, 2, 1)}


def test_a_drug_is_never_the_true_cause_of_a_reaction_it_does_not_cause() -> None:
    random_source = random.Random(5)
    assumptions = SamplerAssumptions()
    for _ in range(1500):
        regimen = sample_regimen(random_source=random_source)
        event = sample_event(random_source=random_source, assumptions=assumptions, suspected=regimen.suspected)
        known = {ReactionCategory.NONSPECIFIC}.union(*(KNOWN_CATEGORIES_BY_DRUG[drug] for drug in regimen.suspected))
        assert not event.is_drug_related or event.category in known


def test_death_is_consistent_in_the_grading() -> None:
    random_source = random.Random(9)
    gradings = [sample_grading(random_source=random_source, action_taken="drug_withdrawn") for _ in range(3000)]

    assert any(grading.severity == "fatal" for grading in gradings)
    for grading in gradings:
        assert (grading.severity == "fatal") == (grading.outcome == "death")
        assert (grading.criteria_for_seriousness == "death") == (grading.severity == "fatal")
        assert grading.is_serious == (grading.criteria_for_seriousness is not None)


def test_only_a_female_adult_or_adolescent_can_be_pregnant(cases: list[SampledCase]) -> None:
    pregnant = {"first_trimester", "second_trimester", "third_trimester"}
    for case in cases:
        if case.patient.pregnancy_status in pregnant:
            assert case.patient.gender == "female"
            assert case.patient.age_years >= 12


def test_the_body_size_is_plausible(cases: list[SampledCase]) -> None:
    for case in cases:
        patient = case.patient
        body_mass_index = patient.weight_kg / (patient.height_cm / 100) ** 2
        assert 11.0 <= body_mass_index <= 36.0
        assert 40.0 <= patient.height_cm <= 220.0


def test_the_drug_details_cover_only_the_drugs_that_were_taken(cases: list[SampledCase]) -> None:
    for case in cases[:500]:
        taken = {exposure.drug for exposure in case.report.exposures if exposure.start_date is not None or exposure.stop_date is not None}
        detailed = {details.drug for details in case.drug_details}
        assert taken <= detailed
        assert all(details.route == "oral" for details in case.drug_details)


@pytest.mark.parametrize(
    ("measure", "expected", "tolerance"),
    [
        (lambda case: case.patient.gender == "female", 0.619, 0.03),
        (lambda case: case.grading.severity == "mild", 0.4286, 0.03),
        (lambda case: case.grading.is_serious, 0.1964, 0.03),
        (lambda case: case.grading.action_taken == "drug_withdrawn", 0.6131, 0.03),
    ],
    ids=["female", "mild", "serious", "withdrawn"],
)
def test_the_totals_match_the_ppb_report(cases: list[SampledCase], measure: object, expected: float, tolerance: float) -> None:
    share = sum(1 for case in cases if measure(case)) / len(cases)  # type: ignore[operator]  # the measure is a one-argument function

    assert share == pytest.approx(expected, abs=tolerance)


def test_a_missing_onset_can_be_forced() -> None:
    cases_without_onset = many_cases(count=50, assumptions=SamplerAssumptions(onset_missing=1.0))

    assert all(case.report.onset_date is None for case in cases_without_onset)


def test_no_ticked_suspected_drug_can_be_forced() -> None:
    cases_without_tick = many_cases(count=50, assumptions=SamplerAssumptions(no_suspected_drug_ticked=1.0))

    assert all(not any(exposure.suspected for exposure in case.report.exposures) for case in cases_without_tick)


def test_the_four_drug_names_are_the_only_exposures(cases: list[SampledCase]) -> None:
    for case in cases[:200]:
        assert [exposure.drug for exposure in case.report.exposures] == list(DrugName)
