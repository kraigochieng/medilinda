"""Tests of the mapping from the fields of a report to the WHO-UMC facts."""

from datetime import date, timedelta

import pytest
from medilinda_ml.case_facts import (
    CausalityLevel,
    Dechallenge,
    Information,
    OtherExplanation,
    Rechallenge,
    TimeRelationship,
)
from medilinda_ml.report_fields import (
    Antiretroviral,
    DrugName,
    FormAnswer,
    LabResults,
    MedicalHistory,
    MedicineExposure,
    OtherMedicines,
    ReportFields,
    VisualExam,
)
from medilinda_ml.who_umc import assess
from medilinda_ml.yellow_form_mapping import (
    facts_from_report,
    information_of,
    is_event_definitive,
    other_explanation_of,
    time_relationship_of,
)

START = date(2025, 1, 1)


def clean_history() -> MedicalHistory:
    """Return a history with no other cause, all recorded."""
    return MedicalHistory(
        alcohol_use=False, hepatic_dysfunction=False, renal_dysfunction=False,
        hiv_positive=False, hepatitis_b_or_c=False,
    )


def clean_medicines() -> OtherMedicines:
    """Return other medicines with no other cause, all recorded."""
    return OtherMedicines(antiretroviral=Antiretroviral.NONE, on_cotrimoxazole=False, other_hepatotoxic_medicine=False)


def no_labs() -> LabResults:
    """Return lab results with no test done."""
    return LabResults(alt_multiple_of_upper_limit=None, bilirubin_umol_per_l=None, visual_exam=VisualExam.NOT_DONE)


def report_with(**changes: object) -> ReportFields:
    """Return a clean liver report: pyrazinamide from START, onset 30 days later, stopped after onset."""
    base: dict[str, object] = {
        "onset_date": START + timedelta(days=30),
        "reaction_terms": ["jaundice"],
        "exposures": [
            MedicineExposure(drug=DrugName.PYRAZINAMIDE, suspected=True, start_date=START, stop_date=START + timedelta(days=32)),
            MedicineExposure(drug=DrugName.ETHAMBUTOL, suspected=False, start_date=START, stop_date=None),
        ],
        "history": clean_history(),
        "other_medicines": clean_medicines(),
        "labs": LabResults(alt_multiple_of_upper_limit=6.0, bilirubin_umol_per_l=None, visual_exam=VisualExam.NOT_DONE),
        "dechallenge": FormAnswer.YES,
        "rechallenge": FormAnswer.YES,
    }
    return ReportFields.model_validate({**base, **changes})


def exposure(*, drug: DrugName, start: date | None, stop: date | None = None) -> MedicineExposure:
    """Return a suspected exposure."""
    return MedicineExposure(drug=drug, suspected=True, start_date=start, stop_date=stop)


def test_a_clean_liver_report_maps_to_certain() -> None:
    facts = facts_from_report(report=report_with())

    assert facts.time_relationship is TimeRelationship.PLAUSIBLE
    assert facts.other_explanation is OtherExplanation.NONE
    assert facts.event_definitive is True
    assert assess(facts=facts) is CausalityLevel.CERTAIN


@pytest.mark.parametrize(
    ("answer", "dechallenge", "rechallenge"),
    [
        (FormAnswer.YES, Dechallenge.IMPROVED, Rechallenge.POSITIVE),
        (FormAnswer.NO, Dechallenge.NOT_IMPROVED, Rechallenge.NEGATIVE),
        (FormAnswer.NOT_APPLICABLE, Dechallenge.NOT_DONE, Rechallenge.NOT_DONE),
        (FormAnswer.UNKNOWN, Dechallenge.UNKNOWN, Rechallenge.UNKNOWN),
    ],
)
def test_the_four_form_answers_map_to_dechallenge_and_rechallenge(
    answer: FormAnswer, dechallenge: Dechallenge, rechallenge: Rechallenge
) -> None:
    facts = facts_from_report(report=report_with(dechallenge=answer, rechallenge=answer))

    assert facts.dechallenge is dechallenge
    assert facts.rechallenge is rechallenge


def test_an_onset_before_the_start_is_improbable() -> None:
    report = report_with(onset_date=START - timedelta(days=1))

    assert time_relationship_of(report=report) is TimeRelationship.IMPROBABLE


def test_an_onset_long_after_the_stop_is_improbable() -> None:
    report = report_with(exposures=[exposure(drug=DrugName.PYRAZINAMIDE, start=START, stop=START + timedelta(days=5))])

    assert time_relationship_of(report=report) is TimeRelationship.IMPROBABLE


def test_a_liver_reaction_after_one_day_is_reasonable_not_plausible() -> None:
    report = report_with(onset_date=START + timedelta(days=1))

    assert time_relationship_of(report=report) is TimeRelationship.REASONABLE


def test_a_reaction_that_the_drug_does_not_cause_is_never_plausible() -> None:
    report = report_with(
        reaction_terms=["optic neuritis"],
        exposures=[exposure(drug=DrugName.PYRAZINAMIDE, start=START)],
        onset_date=START + timedelta(days=60),
    )

    assert time_relationship_of(report=report) is TimeRelationship.REASONABLE


def test_a_nonspecific_term_is_never_plausible() -> None:
    report = report_with(reaction_terms=["fatigue"], exposures=[exposure(drug=DrugName.RIFAMPICIN, start=START)])

    assert time_relationship_of(report=report) is TimeRelationship.REASONABLE


def test_a_missing_start_date_gives_an_unknown_time() -> None:
    report = report_with(exposures=[exposure(drug=DrugName.PYRAZINAMIDE, start=None)])

    assert time_relationship_of(report=report) is TimeRelationship.UNKNOWN


def test_a_missing_onset_gives_an_unknown_time() -> None:
    assert time_relationship_of(report=report_with(onset_date=None)) is TimeRelationship.UNKNOWN


def test_the_best_suspected_drug_decides_the_time() -> None:
    report = report_with(
        exposures=[
            exposure(drug=DrugName.ETHAMBUTOL, start=START + timedelta(days=29)),
            exposure(drug=DrugName.PYRAZINAMIDE, start=START),
        ]
    )

    assert time_relationship_of(report=report) is TimeRelationship.PLAUSIBLE


def test_one_other_cause_is_possible_and_two_are_plausible() -> None:
    one = report_with(history=clean_history().model_copy(update={"alcohol_use": True}))
    two = report_with(history=clean_history().model_copy(update={"alcohol_use": True, "hepatitis_b_or_c": True}))

    assert other_explanation_of(report=one) is OtherExplanation.POSSIBLE
    assert other_explanation_of(report=two) is OtherExplanation.PLAUSIBLE


def test_a_history_that_was_not_recorded_gives_unknown() -> None:
    history = clean_history().model_copy(update={"hepatitis_b_or_c": None})

    assert other_explanation_of(report=report_with(history=history)) is OtherExplanation.UNKNOWN


def test_an_nnrti_antiretroviral_is_another_cause_of_liver_injury() -> None:
    medicines = clean_medicines().model_copy(update={"antiretroviral": Antiretroviral.NNRTI_BASED})

    assert other_explanation_of(report=report_with(other_medicines=medicines)) is OtherExplanation.POSSIBLE


def test_dolutegravir_alone_is_not_another_cause_of_liver_injury() -> None:
    medicines = clean_medicines().model_copy(update={"antiretroviral": Antiretroviral.DOLUTEGRAVIR_BASED})

    assert other_explanation_of(report=report_with(other_medicines=medicines)) is OtherExplanation.NONE


def test_a_liver_event_is_definitive_by_alt_or_by_bilirubin() -> None:
    by_alt = report_with(labs=LabResults(alt_multiple_of_upper_limit=5.0, bilirubin_umol_per_l=None, visual_exam=VisualExam.NOT_DONE))
    by_bilirubin = report_with(labs=LabResults(alt_multiple_of_upper_limit=1.0, bilirubin_umol_per_l=51.0, visual_exam=VisualExam.NOT_DONE))
    below = report_with(labs=LabResults(alt_multiple_of_upper_limit=4.9, bilirubin_umol_per_l=50.0, visual_exam=VisualExam.NOT_DONE))

    assert is_event_definitive(report=by_alt) is True
    assert is_event_definitive(report=by_bilirubin) is True
    assert is_event_definitive(report=below) is False


def test_an_optic_event_is_definitive_by_an_abnormal_eye_exam() -> None:
    labs = LabResults(alt_multiple_of_upper_limit=None, bilirubin_umol_per_l=None, visual_exam=VisualExam.ABNORMAL)

    assert is_event_definitive(report=report_with(reaction_terms=["optic neuritis"], labs=labs)) is True
    assert is_event_definitive(report=report_with(reaction_terms=["jaundice"], labs=labs)) is False


def test_a_high_alt_does_not_make_a_skin_reaction_definitive() -> None:
    assert is_event_definitive(report=report_with(reaction_terms=["rash"])) is False


def test_information_is_cannot_be_judged_without_a_suspected_drug_or_a_reaction() -> None:
    no_drug = report_with(exposures=[MedicineExposure(drug=DrugName.ETHAMBUTOL, suspected=False, start_date=START, stop_date=None)])
    no_reaction = report_with(reaction_terms=[])

    assert information_of(report=no_drug) is Information.CANNOT_BE_JUDGED
    assert information_of(report=no_reaction) is Information.CANNOT_BE_JUDGED


def test_information_is_more_data_needed_without_an_onset_or_a_start_date() -> None:
    no_onset = report_with(onset_date=None)
    no_start = report_with(exposures=[exposure(drug=DrugName.PYRAZINAMIDE, start=None)])

    assert information_of(report=no_onset) is Information.MORE_DATA_NEEDED
    assert information_of(report=no_start) is Information.MORE_DATA_NEEDED


def test_the_mapping_gives_the_same_facts_twice() -> None:
    report = report_with()

    assert facts_from_report(report=report) == facts_from_report(report=report)
