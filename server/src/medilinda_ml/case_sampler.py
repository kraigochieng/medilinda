"""Sample one synthetic report in causal order.

The order is: patient, history, medicines, the event and its cause, the timeline, the follow-up
(dechallenge, rechallenge, action), the labs, the grading, and last the missing information.
This module never reads the WHO-UMC level. The level comes only from who_umc.assess, applied to the
facts of the report. A test checks that this module does not import who_umc.

Side-effect free: the random source is a parameter, so the same random source state gives the same case.
The totals come from marginals.py. The numbers that no source gives are in sampler_assumptions.py.
"""

import math
import random
from datetime import date, timedelta
from typing import Final

from medilinda_ml import marginals
from medilinda_ml.marginals import CountedDistribution
from medilinda_ml.reaction_knowledge import (
    KNOWN_CATEGORIES_BY_DRUG,
    REACTION_CATEGORY_BY_TERM,
    TIME_WINDOW_BY_CATEGORY,
    ReactionCategory,
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
from medilinda_ml.sampler_assumptions import DEFAULT_ASSUMPTIONS, SamplerAssumptions
from pydantic import BaseModel, ConfigDict

AGE_RANGE_BY_GROUP: Final[dict[str, tuple[int, int]]] = {
    "neonate": (0, 0),
    "infant": (0, 0),
    "child": (1, 11),
    "adolescent": (12, 17),
    "adult": (18, 64),
    "elderly": (65, 85),
}

DRUGS_BY_REGIMEN: Final[dict[str, list[DrugName]]] = {
    "rhze": [DrugName.RIFAMPICIN, DrugName.ISONIAZID, DrugName.PYRAZINAMIDE, DrugName.ETHAMBUTOL],
    "rhz": [DrugName.RIFAMPICIN, DrugName.ISONIAZID, DrugName.PYRAZINAMIDE],
    "rh": [DrugName.RIFAMPICIN, DrugName.ISONIAZID],
}

TERMS_BY_CATEGORY: Final[dict[ReactionCategory, list[str]]] = {
    **{
        category: [term for term, term_category in REACTION_CATEGORY_BY_TERM.items() if term_category is category]
        for category in ReactionCategory
        if category is not ReactionCategory.NONSPECIFIC
    },
    ReactionCategory.NONSPECIFIC: ["fatigue", "headache", "fever", "dizziness"],
}

# Dose in mg for each kg of body weight, with the lowest and highest dose, and the step of rounding.
DOSE_RULES_MG: Final[dict[DrugName, tuple[float, int, int, int]]] = {
    DrugName.RIFAMPICIN: (10, 150, 600, 25),
    DrugName.ISONIAZID: (5, 100, 300, 25),
    DrugName.PYRAZINAMIDE: (25, 500, 2000, 50),
    DrugName.ETHAMBUTOL: (15, 400, 1200, 50),
}

MANUFACTURERS: Final[list[str]] = [
    "PharmaHealth Ltd",
    "Global Meds Inc",
    "Kenya Drug Co",
    "MedLife Pharmaceuticals",
    "HealthPlus Labs",
]

CRITERIA_LEGEND: Final[dict[str, str]] = {
    "hospitalization": "Hospitalization/Prolonged Hospitalization",
    "life_threatening": "Life threatening",
    "disability": "Disability",
    "death": "Death",
}


class PatientDetails(BaseModel):
    """The patient of a sampled report."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    age_years: int
    gender: str  # "male" or "female"
    known_allergy: str | None  # "yes", "no", or None when the form did not record it
    pregnancy_status: str | None
    weight_kg: float
    height_cm: float


class DrugDetails(BaseModel):
    """The dose, route, frequency, batch and maker of one medicine that the patient took."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    drug: DrugName
    dose_mg: int
    frequency_per_day: int
    route: str
    batch_number: str
    manufacturer: str


class Grading(BaseModel):
    """Section 9 of the form: severity, seriousness, action taken and outcome."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    severity: str
    is_serious: bool
    criteria_for_seriousness: str | None
    action_taken: str
    outcome: str


class SampledCase(BaseModel):
    """One sampled report with its details. The level is not part of it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    report: ReportFields
    patient: PatientDetails
    drug_details: list[DrugDetails]
    grading: Grading
    reaction_description: str
    report_date: date
    is_drug_related: bool  # the latent cause, kept for checks only. It is not a feature of the model.
    regimen: str


def choose_category(*, random_source: random.Random, distribution: CountedDistribution, excluded: set[str] | None = None) -> str:
    """Draw one category of a distribution, leaving out the excluded ones."""
    skipped = excluded or set()
    categories = [name for name in distribution.counts if name not in skipped]
    weights = [distribution.counts[name] for name in categories]
    return random_source.choices(categories, weights=weights, k=1)[0]


def _chance(*, random_source: random.Random, probability: float) -> bool:
    """Return True with the given probability."""
    return random_source.random() < probability


def sample_patient(*, random_source: random.Random, assumptions: SamplerAssumptions) -> PatientDetails:
    """Sample the age, gender, allergy, pregnancy status and body size of the patient."""
    age_group = choose_category(random_source=random_source, distribution=marginals.AGE_GROUP)
    low, high = AGE_RANGE_BY_GROUP[age_group]
    age_years = random_source.randint(low, high)
    gender = choose_category(random_source=random_source, distribution=marginals.GENDER)
    height_cm = _height_cm(random_source=random_source, age_group=age_group, gender=gender)
    body_mass_index = (
        random_source.gauss(assumptions.adult_bmi_mean, assumptions.adult_bmi_deviation)
        if age_group in {"adult", "elderly", "adolescent"}
        else random_source.gauss(16.0, 2.0)
    )
    body_mass_index = min(max(body_mass_index, 12.0), 35.0)
    allergy = choose_category(random_source=random_source, distribution=marginals.KNOWN_ALLERGY)
    return PatientDetails(
        age_years=age_years,
        gender=gender,
        known_allergy=None if allergy == "not_indicated" else allergy,
        pregnancy_status=_pregnancy_status(random_source=random_source, gender=gender, age_group=age_group),
        weight_kg=round(body_mass_index * (height_cm / 100) ** 2, 1),
        height_cm=round(height_cm, 1),
    )


def _height_cm(*, random_source: random.Random, age_group: str, gender: str) -> float:
    """Sample a height in cm that fits the age group and the gender."""
    heights = {
        "neonate": (50.0, 2.0),
        "infant": (70.0, 5.0),
        "child": (110.0, 15.0),
        "adolescent": (155.0, 10.0),
        "elderly": (158.0 if gender == "female" else 166.0, 7.0),
        "adult": (158.0 if gender == "female" else 168.0, 7.0),
    }
    mean, deviation = heights[age_group]
    return max(random_source.gauss(mean, deviation), 40.0)


def _pregnancy_status(*, random_source: random.Random, gender: str, age_group: str) -> str | None:
    """Sample the pregnancy status. Males, children and elderly women get "not_applicable"."""
    if gender == "male" or age_group not in {"adult", "adolescent"}:
        return "not_applicable"
    status = choose_category(random_source=random_source, distribution=marginals.PREGNANCY_STATUS_OF_FEMALES)
    return None if status == "not_indicated" else status


def sample_history(
    *, random_source: random.Random, assumptions: SamplerAssumptions
) -> tuple[MedicalHistory, OtherMedicines]:
    """Sample the medical history and the other medicines. The form can leave each box empty."""
    history_is_empty = _chance(random_source=random_source, probability=assumptions.history_not_recorded)
    medicines_are_empty = _chance(random_source=random_source, probability=assumptions.medicines_not_recorded)

    def drawn(*, probability: float, is_empty: bool) -> bool | None:
        return None if is_empty else _chance(random_source=random_source, probability=probability)

    hiv = drawn(probability=assumptions.hiv_positive, is_empty=history_is_empty)
    history = MedicalHistory(
        alcohol_use=drawn(probability=assumptions.alcohol_use, is_empty=history_is_empty),
        hepatic_dysfunction=drawn(probability=assumptions.hepatic_dysfunction, is_empty=history_is_empty),
        renal_dysfunction=drawn(probability=assumptions.renal_dysfunction, is_empty=history_is_empty),
        hiv_positive=hiv,
        hepatitis_b_or_c=drawn(probability=assumptions.hepatitis_b_or_c, is_empty=history_is_empty),
    )
    # The treatment of HIV is known to the reporter from the medicines list, even if the history is empty.
    has_hiv = bool(hiv) if hiv is not None else _chance(random_source=random_source, probability=assumptions.hiv_positive)
    medicines = OtherMedicines(
        antiretroviral=Antiretroviral.UNKNOWN
        if medicines_are_empty
        else _antiretroviral(random_source=random_source, hiv=has_hiv, assumptions=assumptions),
        on_cotrimoxazole=drawn(
            probability=assumptions.cotrimoxazole_with_hiv if has_hiv else assumptions.cotrimoxazole_without_hiv,
            is_empty=medicines_are_empty,
        ),
        other_hepatotoxic_medicine=drawn(
            probability=assumptions.other_hepatotoxic_medicine, is_empty=medicines_are_empty
        ),
    )
    return history, medicines


def _antiretroviral(*, random_source: random.Random, hiv: bool | None, assumptions: SamplerAssumptions) -> Antiretroviral:
    """Sample the antiretroviral type. Without HIV it is none. With HIV not recorded it is unknown."""
    if hiv is None:
        return Antiretroviral.UNKNOWN
    if not hiv:
        return Antiretroviral.NONE
    draw = random_source.random()
    if draw < assumptions.dolutegravir_share:
        return Antiretroviral.DOLUTEGRAVIR_BASED
    if draw < assumptions.dolutegravir_share + assumptions.nnrti_share:
        return Antiretroviral.NNRTI_BASED
    return Antiretroviral.UNKNOWN


class RegimenChoice(BaseModel):
    """The medicines that the patient took, and the ones that the reporter ticked as suspected."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str  # "rhze", "rhz", "rh", or "separate"
    taken: list[DrugName]
    suspected: list[DrugName]


def sample_regimen(*, random_source: random.Random) -> RegimenChoice:
    """Sample the regimen. A combination medicine is one exposure to all its drugs (DR-7)."""
    if _chance(random_source=random_source, probability=marginals.SEPARATE_DRUGS_SHARE):
        every_drug = list(DrugName)
        taken = random_source.sample(every_drug, k=random_source.randint(1, len(every_drug)))
        suspected = random_source.sample(taken, k=random_source.randint(1, min(2, len(taken))))
        return RegimenChoice(name="separate", taken=taken, suspected=suspected)
    name = choose_category(random_source=random_source, distribution=marginals.TB_COMBINATION_MENTIONS)
    drugs = DRUGS_BY_REGIMEN[name]
    return RegimenChoice(name=name, taken=drugs, suspected=drugs)


class EventChoice(BaseModel):
    """The reaction of the report and its latent cause."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    category: ReactionCategory
    terms: list[str]
    is_drug_related: bool


def sample_event(
    *, random_source: random.Random, assumptions: SamplerAssumptions, suspected: list[DrugName]
) -> EventChoice:
    """Sample the reaction category and terms, and whether the drug truly caused the event.

    A drug cannot truly cause a category that it is not known to cause, so that event is unrelated.
    """
    known = {ReactionCategory.NONSPECIFIC}.union(*(KNOWN_CATEGORIES_BY_DRUG[drug] for drug in suspected))
    all_categories = {ReactionCategory(name) for name in marginals.REACTION_CATEGORY_COUNTS.counts}
    allowed = known if _chance(random_source=random_source, probability=assumptions.known_category_share) else all_categories
    excluded = {category.value for category in all_categories - allowed}
    category = ReactionCategory(
        choose_category(random_source=random_source, distribution=marginals.REACTION_CATEGORY_COUNTS, excluded=excluded)
    )
    terms_for_category = TERMS_BY_CATEGORY[category]
    terms = random_source.sample(terms_for_category, k=random_source.randint(1, min(2, len(terms_for_category))))
    is_known_to_a_suspected_drug = category in known
    is_drug_related = is_known_to_a_suspected_drug and _chance(
        random_source=random_source, probability=assumptions.drug_related_share
    )
    return EventChoice(category=category, terms=terms, is_drug_related=is_drug_related)


def sample_latency_days(
    *, random_source: random.Random, assumptions: SamplerAssumptions, category: ReactionCategory, is_drug_related: bool
) -> int:
    """Sample the days from the start of the drug to the onset of the reaction."""
    window = TIME_WINDOW_BY_CATEGORY[category]
    if not is_drug_related:
        return random_source.randint(0, window.reasonable_to_days + 120)
    if _chance(random_source=random_source, probability=assumptions.outside_window_share):
        return random_source.randint(window.plausible_to_days + 1, window.reasonable_to_days)
    span = window.plausible_to_days - window.plausible_from_days
    mode = window.plausible_from_days + 0.3 * span
    return round(random_source.triangular(window.plausible_from_days, window.plausible_to_days, mode))


def sample_exposures(
    *, regimen: RegimenChoice, start_date: date, stop_date: date | None
) -> list[MedicineExposure]:
    """Build the four exposures. The drugs of a combination share one start and one stop."""
    return [
        MedicineExposure(
            drug=drug,
            suspected=drug in regimen.suspected,
            start_date=start_date if drug in regimen.taken else None,
            stop_date=stop_date if drug in regimen.taken else None,
        )
        for drug in DrugName
    ]


def sample_follow_up(
    *, random_source: random.Random, assumptions: SamplerAssumptions, is_drug_related: bool, action_taken: str
) -> tuple[FormAnswer, FormAnswer]:
    """Sample the dechallenge and rechallenge answers of the form."""
    was_stopped_or_reduced = action_taken in {"drug_withdrawn", "dose_reduced"}
    if not was_stopped_or_reduced or _chance(random_source=random_source, probability=assumptions.answer_unknown):
        dechallenge = FormAnswer.UNKNOWN if was_stopped_or_reduced else FormAnswer.NOT_APPLICABLE
    else:
        improved = (
            assumptions.dechallenge_improved_if_related
            if is_drug_related
            else assumptions.dechallenge_improved_if_unrelated
        )
        dechallenge = FormAnswer.YES if _chance(random_source=random_source, probability=improved) else FormAnswer.NO
    return dechallenge, _sample_rechallenge(
        random_source=random_source, assumptions=assumptions, is_drug_related=is_drug_related, action_taken=action_taken
    )


def _sample_rechallenge(
    *, random_source: random.Random, assumptions: SamplerAssumptions, is_drug_related: bool, action_taken: str
) -> FormAnswer:
    """Sample the rechallenge answer. Only a withdrawn drug can be given again."""
    was_withdrawn = action_taken == "drug_withdrawn"
    if was_withdrawn and _chance(random_source=random_source, probability=assumptions.rechallenge_done_after_withdrawal):
        reappeared = assumptions.rechallenge_positive_if_related if is_drug_related else 0.1
        return FormAnswer.YES if _chance(random_source=random_source, probability=reappeared) else FormAnswer.NO
    if _chance(random_source=random_source, probability=assumptions.answer_unknown):
        return FormAnswer.UNKNOWN
    return FormAnswer.NOT_APPLICABLE


def sample_labs(
    *, random_source: random.Random, assumptions: SamplerAssumptions, category: ReactionCategory, is_drug_related: bool
) -> LabResults:
    """Sample the lab results and the eye exam. A test that was not done stays empty."""
    is_liver = category is ReactionCategory.LIVER
    alt_measured = assumptions.alt_measured_if_liver if is_liver else assumptions.alt_measured_other
    bilirubin_measured = assumptions.bilirubin_measured_if_liver if is_liver else assumptions.bilirubin_measured_other
    alt_median = (6.0 if is_drug_related else 1.5) if is_liver else 1.0
    bilirubin_median = (45.0 if is_drug_related else 15.0) if is_liver else 12.0
    alt = (
        round(random_source.lognormvariate(_log(alt_median), 0.7), 1)
        if _chance(random_source=random_source, probability=alt_measured)
        else None
    )
    bilirubin = (
        round(random_source.lognormvariate(_log(bilirubin_median), 0.6), 1)
        if _chance(random_source=random_source, probability=bilirubin_measured)
        else None
    )
    return LabResults(
        alt_multiple_of_upper_limit=alt,
        bilirubin_umol_per_l=bilirubin,
        visual_exam=_sample_visual_exam(
            random_source=random_source, assumptions=assumptions, category=category, is_drug_related=is_drug_related
        ),
    )


def _log(value: float) -> float:
    """Return the natural logarithm of a positive number."""
    return math.log(value)


def _sample_visual_exam(
    *, random_source: random.Random, assumptions: SamplerAssumptions, category: ReactionCategory, is_drug_related: bool
) -> VisualExam:
    """Sample the eye exam. It is done mostly for an optic reaction."""
    is_optic = category is ReactionCategory.OPTIC
    done_probability = assumptions.exam_done_if_optic if is_optic else 0.03
    if not _chance(random_source=random_source, probability=done_probability):
        return VisualExam.NOT_DONE
    abnormal_probability = (
        assumptions.exam_abnormal_if_related if is_drug_related else assumptions.exam_abnormal_if_unrelated
    )
    return (
        VisualExam.ABNORMAL
        if is_optic and _chance(random_source=random_source, probability=abnormal_probability)
        else VisualExam.NORMAL
    )


def sample_grading(*, random_source: random.Random, action_taken: str) -> Grading:
    """Sample severity, seriousness and outcome from the PPB totals, and keep death consistent."""
    severity = choose_category(random_source=random_source, distribution=marginals.SEVERITY)
    if severity == "fatal":
        return Grading(
            severity="fatal", is_serious=True, criteria_for_seriousness="death", action_taken=action_taken, outcome="death"
        )
    outcome = choose_category(random_source=random_source, distribution=marginals.OUTCOME, excluded={"death"})
    is_serious = choose_category(random_source=random_source, distribution=marginals.IS_SERIOUS) == "yes"
    criteria = (
        choose_category(
            random_source=random_source, distribution=marginals.CRITERIA_FOR_SERIOUSNESS, excluded={"death"}
        )
        if is_serious
        else None
    )
    return Grading(
        severity=severity, is_serious=is_serious, criteria_for_seriousness=criteria, action_taken=action_taken, outcome=outcome
    )


def sample_drug_details(
    *, random_source: random.Random, regimen: RegimenChoice, weight_kg: float
) -> list[DrugDetails]:
    """Sample the dose, route, frequency, batch and maker of each drug that the patient took."""
    details: list[DrugDetails] = []
    for drug in DrugName:
        if drug not in regimen.taken:
            continue
        per_kg, lowest, highest, step = DOSE_RULES_MG[drug]
        dose = round(min(max(per_kg * weight_kg, lowest), highest) / step) * step
        details.append(
            DrugDetails(
                drug=drug,
                dose_mg=dose,
                frequency_per_day=1,
                route="oral",
                batch_number="B" + "".join(random_source.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=6)),
                manufacturer=random_source.choice(MANUFACTURERS),
            )
        )
    return details


def apply_missing_information(
    *, random_source: random.Random, assumptions: SamplerAssumptions, report: ReportFields
) -> ReportFields:
    """Leave out some information, as real reports do: the onset, a start date, or the suspected tick."""
    onset = None if _chance(random_source=random_source, probability=assumptions.onset_missing) else report.onset_date
    unticked = _chance(random_source=random_source, probability=assumptions.no_suspected_drug_ticked)
    exposures = [
        exposure.model_copy(
            update={
                "suspected": exposure.suspected and not unticked,
                "start_date": None
                if exposure.suspected and _chance(random_source=random_source, probability=assumptions.start_date_missing)
                else exposure.start_date,
            }
        )
        for exposure in report.exposures
    ]
    return report.model_copy(update={"onset_date": onset, "exposures": exposures})


def sample_case(
    *,
    random_source: random.Random,
    reference_date: date,
    assumptions: SamplerAssumptions = DEFAULT_ASSUMPTIONS,
) -> SampledCase:
    """Sample one report in causal order. The WHO-UMC level is not read or set here."""
    patient = sample_patient(random_source=random_source, assumptions=assumptions)
    history, other_medicines = sample_history(random_source=random_source, assumptions=assumptions)
    regimen = sample_regimen(random_source=random_source)
    event = sample_event(random_source=random_source, assumptions=assumptions, suspected=regimen.suspected)
    action_taken = choose_category(random_source=random_source, distribution=marginals.ACTION_TAKEN)

    report_date = reference_date - timedelta(days=random_source.randint(0, 180))
    onset_date = report_date - timedelta(days=random_source.randint(8, 60))
    latency = sample_latency_days(
        random_source=random_source, assumptions=assumptions, category=event.category, is_drug_related=event.is_drug_related
    )
    start_date = onset_date - timedelta(days=latency)
    stop_date = onset_date + timedelta(days=random_source.randint(0, 7)) if action_taken == "drug_withdrawn" else None

    dechallenge, rechallenge = sample_follow_up(
        random_source=random_source, assumptions=assumptions, is_drug_related=event.is_drug_related, action_taken=action_taken
    )
    labs = sample_labs(
        random_source=random_source, assumptions=assumptions, category=event.category, is_drug_related=event.is_drug_related
    )
    report = ReportFields(
        onset_date=onset_date,
        reaction_terms=event.terms,
        exposures=sample_exposures(regimen=regimen, start_date=start_date, stop_date=stop_date),
        history=history,
        other_medicines=other_medicines,
        labs=labs,
        dechallenge=dechallenge,
        rechallenge=rechallenge,
    )
    return SampledCase(
        report=apply_missing_information(random_source=random_source, assumptions=assumptions, report=report),
        patient=patient,
        drug_details=sample_drug_details(random_source=random_source, regimen=regimen, weight_kg=patient.weight_kg),
        grading=sample_grading(random_source=random_source, action_taken=action_taken),
        reaction_description=", ".join(event.terms),
        report_date=report_date,
        is_drug_related=event.is_drug_related,
        regimen=regimen.name,
    )
