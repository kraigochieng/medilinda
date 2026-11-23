"""The mapping from the fields of a yellow form report to the facts of the WHO-UMC rules.

Pure functions. The mapping table is in docs/yellow-form-mapping.md. The reaction knowledge
(categories, time windows, known reactions of each drug) is in reaction_knowledge.py.
"""

from typing import Final

from medilinda_ml.case_facts import (
    CaseFacts,
    Dechallenge,
    Information,
    OtherExplanation,
    Rechallenge,
    TimeRelationship,
)
from medilinda_ml.reaction_knowledge import (
    DEFINITIVE_ALT_MULTIPLE,
    DEFINITIVE_BILIRUBIN_UMOL_PER_L,
    KNOWN_CATEGORIES_BY_DRUG,
    TIME_WINDOW_BY_CATEGORY,
    ReactionCategory,
    categories_of,
)
from medilinda_ml.report_fields import (
    Antiretroviral,
    FormAnswer,
    MedicineExposure,
    ReportFields,
    VisualExam,
)

# A reaction that starts more than this many days after the stop is improbable.
AFTER_STOP_GRACE_DAYS: Final[int] = 14

# The most specific category comes first. It decides the other causes.
CATEGORY_PRIORITY: Final[list[ReactionCategory]] = [
    ReactionCategory.LIVER,
    ReactionCategory.OPTIC,
    ReactionCategory.NEUROPATHY,
    ReactionCategory.SKIN,
    ReactionCategory.JOINT,
    ReactionCategory.GASTROINTESTINAL,
    ReactionCategory.NONSPECIFIC,
]

# A higher number is a better time relationship. Unknown beats improbable: no information is
# not evidence against the drug.
TIME_RANK: Final[dict[TimeRelationship, int]] = {
    TimeRelationship.PLAUSIBLE: 3,
    TimeRelationship.REASONABLE: 2,
    TimeRelationship.UNKNOWN: 1,
    TimeRelationship.IMPROBABLE: 0,
}

DECHALLENGE_BY_ANSWER: Final[dict[FormAnswer, Dechallenge]] = {
    FormAnswer.YES: Dechallenge.IMPROVED,
    FormAnswer.NO: Dechallenge.NOT_IMPROVED,
    FormAnswer.NOT_APPLICABLE: Dechallenge.NOT_DONE,
    FormAnswer.UNKNOWN: Dechallenge.UNKNOWN,
}

RECHALLENGE_BY_ANSWER: Final[dict[FormAnswer, Rechallenge]] = {
    FormAnswer.YES: Rechallenge.POSITIVE,
    FormAnswer.NO: Rechallenge.NEGATIVE,
    FormAnswer.NOT_APPLICABLE: Rechallenge.NOT_DONE,
    FormAnswer.UNKNOWN: Rechallenge.UNKNOWN,
}


def facts_from_report(*, report: ReportFields) -> CaseFacts:
    """Return the WHO-UMC facts of a report. Pure: the same report always gives the same facts."""
    return CaseFacts(
        time_relationship=time_relationship_of(report=report),
        other_explanation=other_explanation_of(report=report),
        dechallenge=DECHALLENGE_BY_ANSWER[report.dechallenge],
        rechallenge=RECHALLENGE_BY_ANSWER[report.rechallenge],
        event_definitive=is_event_definitive(report=report),
        information=information_of(report=report),
    )


def _suspected(*, report: ReportFields) -> list[MedicineExposure]:
    """Return the exposures that the reporter ticked as suspected."""
    return [exposure for exposure in report.exposures if exposure.suspected]


def _time_relationship_for(
    *, exposure: MedicineExposure, category: ReactionCategory, report: ReportFields
) -> TimeRelationship:
    """Judge the time from one suspected drug to the event, for one reaction category."""
    if report.onset_date is None or exposure.start_date is None:
        return TimeRelationship.UNKNOWN
    days_from_start = (report.onset_date - exposure.start_date).days
    if days_from_start < 0:
        return TimeRelationship.IMPROBABLE
    if exposure.stop_date is not None and (report.onset_date - exposure.stop_date).days > AFTER_STOP_GRACE_DAYS:
        return TimeRelationship.IMPROBABLE
    window = TIME_WINDOW_BY_CATEGORY[category]
    is_known_reaction = category in KNOWN_CATEGORIES_BY_DRUG[exposure.drug]
    in_plausible_window = window.plausible_from_days <= days_from_start <= window.plausible_to_days
    if in_plausible_window and is_known_reaction:
        return TimeRelationship.PLAUSIBLE
    if days_from_start <= window.reasonable_to_days:
        return TimeRelationship.REASONABLE
    return TimeRelationship.IMPROBABLE


def time_relationship_of(*, report: ReportFields) -> TimeRelationship:
    """Return the best time relationship over the suspected drugs and the reaction categories."""
    categories = categories_of(terms=report.reaction_terms)
    judgements = [
        _time_relationship_for(exposure=exposure, category=category, report=report)
        for exposure in _suspected(report=report)
        for category in categories
    ]
    if not judgements:
        return TimeRelationship.UNKNOWN
    return max(judgements, key=lambda judgement: TIME_RANK[judgement])


def _primary_category(*, report: ReportFields) -> ReactionCategory:
    """Return the most specific reaction category of the report."""
    categories = categories_of(terms=report.reaction_terms)
    return next(
        (category for category in CATEGORY_PRIORITY if category in categories),
        ReactionCategory.NONSPECIFIC,
    )


def _other_cause_factors(*, report: ReportFields, category: ReactionCategory) -> list[bool | None]:
    """Return the other-cause factors for a category. None means that the form did not record it."""
    history = report.history
    medicines = report.other_medicines
    on_nnrti = medicines.antiretroviral is Antiretroviral.NNRTI_BASED
    on_any_antiretroviral = medicines.antiretroviral in {Antiretroviral.DOLUTEGRAVIR_BASED, Antiretroviral.NNRTI_BASED}
    unknown_antiretroviral = None if medicines.antiretroviral is Antiretroviral.UNKNOWN else False
    factors_by_category: dict[ReactionCategory, list[bool | None]] = {
        ReactionCategory.LIVER: [
            history.hepatitis_b_or_c,
            history.alcohol_use,
            history.hepatic_dysfunction,
            on_nnrti if unknown_antiretroviral is not None else None,
            medicines.on_cotrimoxazole,
            medicines.other_hepatotoxic_medicine,
        ],
        ReactionCategory.OPTIC: [history.alcohol_use],
        ReactionCategory.NEUROPATHY: [history.hiv_positive, history.alcohol_use, history.renal_dysfunction],
        ReactionCategory.SKIN: [
            medicines.on_cotrimoxazole,
            history.hiv_positive,
            on_nnrti if unknown_antiretroviral is not None else None,
        ],
        ReactionCategory.JOINT: [history.alcohol_use],
        ReactionCategory.GASTROINTESTINAL: [
            history.alcohol_use,
            on_any_antiretroviral if unknown_antiretroviral is not None else None,
            medicines.on_cotrimoxazole,
        ],
        ReactionCategory.NONSPECIFIC: [history.hiv_positive, history.hepatitis_b_or_c, history.alcohol_use],
    }
    return factors_by_category[category]


def other_explanation_of(*, report: ReportFields) -> OtherExplanation:
    """Count the other causes: none is "none", one is "possible", two or more is "plausible".

    With no cause present, a factor that the form did not record makes the answer "unknown".
    """
    factors = _other_cause_factors(report=report, category=_primary_category(report=report))
    present = sum(1 for factor in factors if factor is True)
    not_recorded = sum(1 for factor in factors if factor is None)
    if present >= 2:
        return OtherExplanation.PLAUSIBLE
    if present == 1:
        return OtherExplanation.POSSIBLE
    return OtherExplanation.UNKNOWN if not_recorded else OtherExplanation.NONE


def is_event_definitive(*, report: ReportFields) -> bool:
    """Return True for an objective event: a liver injury by the lab limits, or an abnormal eye exam."""
    categories = categories_of(terms=report.reaction_terms)
    labs = report.labs
    liver_by_alt = (
        labs.alt_multiple_of_upper_limit is not None
        and labs.alt_multiple_of_upper_limit >= DEFINITIVE_ALT_MULTIPLE
    )
    liver_by_bilirubin = (
        labs.bilirubin_umol_per_l is not None
        and labs.bilirubin_umol_per_l >= DEFINITIVE_BILIRUBIN_UMOL_PER_L
    )
    is_definitive_liver = ReactionCategory.LIVER in categories and (liver_by_alt or liver_by_bilirubin)
    is_definitive_optic = ReactionCategory.OPTIC in categories and labs.visual_exam is VisualExam.ABNORMAL
    return is_definitive_liver or is_definitive_optic


def information_of(*, report: ReportFields) -> Information:
    """Judge whether the report holds enough information: no suspected drug or no reaction cannot be judged."""
    suspected = _suspected(report=report)
    if not suspected or not report.reaction_terms:
        return Information.CANNOT_BE_JUDGED
    has_start_date = any(exposure.start_date is not None for exposure in suspected)
    if report.onset_date is None or not has_start_date:
        return Information.MORE_DATA_NEEDED
    return Information.SUFFICIENT
