"""Tests of the WHO-UMC rules: one test for each row of the example table in issue #164."""

import pytest
from medilinda_ml.case_facts import (
    CaseFacts,
    CausalityLevel,
    Dechallenge,
    Information,
    OtherExplanation,
    Rechallenge,
    TimeRelationship,
)
from medilinda_ml.who_umc import assess
from pydantic import ValidationError


def facts_with(**changes: object) -> CaseFacts:
    """Return facts of a clean, certain case, with the given fields changed."""
    base: dict[str, object] = {
        "time_relationship": TimeRelationship.PLAUSIBLE,
        "other_explanation": OtherExplanation.NONE,
        "dechallenge": Dechallenge.IMPROVED,
        "rechallenge": Rechallenge.POSITIVE,
        "event_definitive": True,
        "information": Information.SUFFICIENT,
    }
    return CaseFacts.model_validate({**base, **changes})


def test_row_1_a_clean_case_with_a_positive_rechallenge_is_certain() -> None:
    assert assess(facts=facts_with()) is CausalityLevel.CERTAIN


def test_row_2_no_rechallenge_and_no_definitive_event_is_likely() -> None:
    facts = facts_with(rechallenge=Rechallenge.NOT_DONE, event_definitive=False)

    assert assess(facts=facts) is CausalityLevel.LIKELY


def test_row_3_another_possible_explanation_is_possible() -> None:
    facts = facts_with(
        other_explanation=OtherExplanation.POSSIBLE,
        dechallenge=Dechallenge.UNKNOWN,
        rechallenge=Rechallenge.UNKNOWN,
    )

    assert assess(facts=facts) is CausalityLevel.POSSIBLE


def test_row_4_an_improbable_time_with_a_plausible_other_cause_is_unlikely() -> None:
    facts = facts_with(
        time_relationship=TimeRelationship.IMPROBABLE,
        other_explanation=OtherExplanation.PLAUSIBLE,
    )

    assert assess(facts=facts) is CausalityLevel.UNLIKELY


def test_row_5_more_data_needed_is_unclassified() -> None:
    assert assess(facts=facts_with(information=Information.MORE_DATA_NEEDED)) is CausalityLevel.UNCLASSIFIED


def test_row_6_a_report_that_cannot_be_judged_is_unclassifiable() -> None:
    assert assess(facts=facts_with(information=Information.CANNOT_BE_JUDGED)) is CausalityLevel.UNCLASSIFIABLE


def test_row_7_a_negative_rechallenge_caps_the_level_at_possible() -> None:
    assert assess(facts=facts_with(rechallenge=Rechallenge.NEGATIVE)) is CausalityLevel.POSSIBLE


def test_row_8_a_value_outside_the_enums_is_refused() -> None:
    with pytest.raises(ValidationError):
        facts_with(time_relationship="very_plausible")


def test_row_9_the_same_facts_give_the_same_level() -> None:
    facts = facts_with()

    assert assess(facts=facts) is assess(facts=facts)


def test_a_positive_rechallenge_does_not_replace_a_definitive_event() -> None:
    assert assess(facts=facts_with(event_definitive=False)) is CausalityLevel.LIKELY


def test_a_reasonable_but_not_plausible_time_cannot_be_certain() -> None:
    assert assess(facts=facts_with(time_relationship=TimeRelationship.REASONABLE)) is CausalityLevel.LIKELY


def test_a_time_that_is_improbable_is_unlikely_even_with_no_other_cause() -> None:
    assert assess(facts=facts_with(time_relationship=TimeRelationship.IMPROBABLE)) is CausalityLevel.UNLIKELY


def test_an_unknown_time_cannot_be_judged_yet() -> None:
    assert assess(facts=facts_with(time_relationship=TimeRelationship.UNKNOWN)) is CausalityLevel.UNCLASSIFIED


def test_no_information_on_withdrawal_gives_possible() -> None:
    assert assess(facts=facts_with(dechallenge=Dechallenge.NOT_DONE)) is CausalityLevel.POSSIBLE


def test_no_improvement_after_withdrawal_gives_possible() -> None:
    assert assess(facts=facts_with(dechallenge=Dechallenge.NOT_IMPROVED)) is CausalityLevel.POSSIBLE


def test_an_unknown_other_explanation_gives_possible() -> None:
    assert assess(facts=facts_with(other_explanation=OtherExplanation.UNKNOWN)) is CausalityLevel.POSSIBLE


def test_information_checks_come_before_the_other_rules() -> None:
    facts = facts_with(
        information=Information.CANNOT_BE_JUDGED,
        time_relationship=TimeRelationship.IMPROBABLE,
    )

    assert assess(facts=facts) is CausalityLevel.UNCLASSIFIABLE


def test_the_facts_are_frozen_so_a_caller_cannot_change_them() -> None:
    facts = facts_with()

    with pytest.raises(ValidationError):
        facts.event_definitive = False  # type: ignore[misc]  # the test proves that the model is frozen
