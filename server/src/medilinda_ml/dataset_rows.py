"""The rows of the dataset: one sampled case as a flat row, and the way back to the report fields.

The words of the categorical columns are the words that the app and the old data.csv use.
The columns of data.csv come first, in their old order. The new columns of decision DR-8 come after them.
The diagnostic columns are written to a separate file, so that training cannot read them.
"""

import random
from datetime import date, timedelta
from typing import Final

from medilinda_ml.case_facts import CausalityLevel
from medilinda_ml.case_sampler import DrugDetails, SampledCase
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

TARGET_COLUMN: Final[str] = "causality_assessment_level"
DIAGNOSTIC_COLUMNS: Final[list[str]] = ["causality_by_rule", "is_drug_related", "regimen"]

DRUG_FIELDS: Final[list[str]] = [
    "suspected",
    "start_date",
    "stop_date",
    "dose_amount",
    "frequency_number",
    "route",
    "batch_no",
    "manufacturer",
]

OLD_COLUMNS: Final[list[str]] = [
    "patient_name",
    "inpatient_or_outpatient_number",
    "patient_date_of_birth",
    "patient_age",
    "patient_address",
    "ward_or_clinic",
    "patient_gender",
    "known_allergy",
    "pregnancy_status",
    "patient_weight_kg",
    "patient_height_cm",
    "date_of_onset_of_reaction",
    "description_of_reaction",
    *[f"{drug.value}_{field}" for drug in DrugName for field in DRUG_FIELDS],
    "dechallenge",
    "rechallenge",
    "severity",
    "is_serious",
    "criteria_for_seriousness",
    "action_taken",
    "outcome",
    "created_at",
]

NEW_COLUMNS: Final[list[str]] = [
    "alcohol_use",
    "hepatic_dysfunction",
    "renal_dysfunction",
    "hiv_positive",
    "hepatitis_b_or_c",
    "antiretroviral",
    "on_cotrimoxazole",
    "other_hepatotoxic_medicine",
    "alt_multiple_of_upper_limit",
    "bilirubin_umol_per_l",
    "visual_exam",
]

DATASET_COLUMNS: Final[list[str]] = [*OLD_COLUMNS, *NEW_COLUMNS, TARGET_COLUMN]

ANSWER_WORDS: Final[dict[FormAnswer, str]] = {
    FormAnswer.YES: "yes",
    FormAnswer.NO: "no",
    FormAnswer.UNKNOWN: "unknown",
    FormAnswer.NOT_APPLICABLE: "na",
}
WORDS_ANSWER: Final[dict[str, FormAnswer]] = {word: answer for answer, word in ANSWER_WORDS.items()}

ACTION_WORDS: Final[dict[str, str]] = {
    "drug_withdrawn": "drug withdrawn",
    "dose_reduced": "dose reduced",
    "dose_increased": "dose increased",
    "dose_not_changed": "dose not changed",
    "not_applicable": "not applicable",
    "unknown": "unknown",
}
CRITERIA_WORDS: Final[dict[str, str]] = {
    "hospitalization": "hospitalisation",
    "life_threatening": "life-threatening",
    "disability": "disability",
    "death": "death",
}
OUTCOME_WORDS: Final[dict[str, str]] = {
    "recovering": "recovering",
    "recovered": "recovered",
    "not_recovered": "not recovered",
    "unknown": "unknown",
    "death": "death",
}
PREGNANCY_WORDS: Final[dict[str, str]] = {
    "not_pregnant": "not pregnant",
    "not_applicable": "not applicable",
    "first_trimester": "1st trimester",
    "second_trimester": "2nd trimester",
    "third_trimester": "3rd trimester",
}

# The four levels that the model predicts, from least to most certain. Label noise moves along this scale.
ORDERED_LEVELS: Final[list[CausalityLevel]] = [
    CausalityLevel.UNLIKELY,
    CausalityLevel.POSSIBLE,
    CausalityLevel.LIKELY,
    CausalityLevel.CERTAIN,
]


def _iso(value: date | None) -> str | None:
    """Return the ISO text of a date, or None."""
    return value.isoformat() if value is not None else None


def case_to_row(*, case: SampledCase, level: CausalityLevel) -> dict[str, object]:
    """Return the flat row of a case, without the diagnostic columns. Pure."""
    patient = case.patient
    report = case.report
    dob = case.report_date - timedelta(days=round(patient.age_years * 365.25))
    row: dict[str, object] = {
        "patient_name": "Synthetic patient",
        "inpatient_or_outpatient_number": None,
        "patient_date_of_birth": _iso(dob),
        "patient_age": float(patient.age_years),
        "patient_address": None,
        "ward_or_clinic": None,
        "patient_gender": patient.gender,
        "known_allergy": patient.known_allergy or "no",
        "pregnancy_status": PREGNANCY_WORDS[patient.pregnancy_status or "not_applicable"],
        "patient_weight_kg": patient.weight_kg,
        "patient_height_cm": patient.height_cm,
        "date_of_onset_of_reaction": _iso(report.onset_date),
        "description_of_reaction": case.reaction_description,
    }
    details_by_drug = {details.drug: details for details in case.drug_details}
    for exposure in report.exposures:
        row.update(_drug_columns(exposure=exposure, details=details_by_drug.get(exposure.drug)))
    row.update(
        {
            "dechallenge": ANSWER_WORDS[report.dechallenge],
            "rechallenge": ANSWER_WORDS[report.rechallenge],
            "severity": case.grading.severity,
            "is_serious": "yes" if case.grading.is_serious else "no",
            "criteria_for_seriousness": CRITERIA_WORDS.get(case.grading.criteria_for_seriousness or ""),
            "action_taken": ACTION_WORDS[case.grading.action_taken],
            "outcome": OUTCOME_WORDS[case.grading.outcome],
            "created_at": _iso(case.report_date),
            **_new_columns(report=report),
            TARGET_COLUMN: level.value,
        }
    )
    return row


def _drug_columns(*, exposure: MedicineExposure, details: DrugDetails | None) -> dict[str, object]:
    """Return the eight columns of one drug. A drug that is not suspected has empty details, as in the app."""
    prefix = exposure.drug.value
    empty: dict[str, object] = {f"{prefix}_{field}": None for field in DRUG_FIELDS}
    empty[f"{prefix}_suspected"] = False
    if not exposure.suspected or details is None:
        return empty
    return {
        f"{prefix}_suspected": True,
        f"{prefix}_start_date": _iso(exposure.start_date),
        f"{prefix}_stop_date": _iso(exposure.stop_date),
        f"{prefix}_dose_amount": float(details.dose_mg),
        f"{prefix}_frequency_number": float(details.frequency_per_day),
        f"{prefix}_route": details.route,
        f"{prefix}_batch_no": details.batch_number,
        f"{prefix}_manufacturer": details.manufacturer,
    }


def _new_columns(*, report: ReportFields) -> dict[str, object]:
    """Return the columns of decision DR-8."""
    history = report.history
    medicines = report.other_medicines
    labs = report.labs
    return {
        "alcohol_use": history.alcohol_use,
        "hepatic_dysfunction": history.hepatic_dysfunction,
        "renal_dysfunction": history.renal_dysfunction,
        "hiv_positive": history.hiv_positive,
        "hepatitis_b_or_c": history.hepatitis_b_or_c,
        "antiretroviral": medicines.antiretroviral.value,
        "on_cotrimoxazole": medicines.on_cotrimoxazole,
        "other_hepatotoxic_medicine": medicines.other_hepatotoxic_medicine,
        "alt_multiple_of_upper_limit": labs.alt_multiple_of_upper_limit,
        "bilirubin_umol_per_l": labs.bilirubin_umol_per_l,
        "visual_exam": labs.visual_exam.value,
    }


def apply_label_noise(*, level: CausalityLevel, random_source: random.Random, rate: float) -> CausalityLevel:
    """Move a level one step along the scale with the given probability (decision DR-6).

    The levels unclassified and unclassifiable do not move. At the end of the scale the step goes inward.
    """
    if level not in ORDERED_LEVELS or random_source.random() >= rate:
        return level
    position = ORDERED_LEVELS.index(level)
    if position == 0:
        return ORDERED_LEVELS[1]
    if position == len(ORDERED_LEVELS) - 1:
        return ORDERED_LEVELS[-2]
    return ORDERED_LEVELS[position + random_source.choice([-1, 1])]


def _blank(value: object) -> bool:
    """Return True for a missing value of a row (None or NaN)."""
    return value is None or (isinstance(value, float) and value != value)


def _date_or_none(value: object) -> date | None:
    """Parse an ISO date of a row, or return None for a missing value."""
    return None if _blank(value) else date.fromisoformat(str(value))


def _flag_or_none(value: object) -> bool | None:
    """Read a True, False or missing flag of a row."""
    return None if _blank(value) else str(value).lower() == "true"


def report_from_row(*, row: dict[str, object]) -> ReportFields:
    """Rebuild the report fields from a row. This is the inverse of case_to_row for the fields that the rules read."""
    exposures = [
        MedicineExposure(
            drug=drug,
            suspected=_flag_or_none(row[f"{drug.value}_suspected"]) is True,
            start_date=_date_or_none(row[f"{drug.value}_start_date"]),
            stop_date=_date_or_none(row[f"{drug.value}_stop_date"]),
        )
        for drug in DrugName
    ]
    description = row["description_of_reaction"]
    return ReportFields(
        onset_date=_date_or_none(row["date_of_onset_of_reaction"]),
        reaction_terms=[] if _blank(description) else [term.strip() for term in str(description).split(",")],
        exposures=exposures,
        history=MedicalHistory(
            alcohol_use=_flag_or_none(row["alcohol_use"]),
            hepatic_dysfunction=_flag_or_none(row["hepatic_dysfunction"]),
            renal_dysfunction=_flag_or_none(row["renal_dysfunction"]),
            hiv_positive=_flag_or_none(row["hiv_positive"]),
            hepatitis_b_or_c=_flag_or_none(row["hepatitis_b_or_c"]),
        ),
        other_medicines=OtherMedicines(
            antiretroviral=Antiretroviral(str(row["antiretroviral"])),
            on_cotrimoxazole=_flag_or_none(row["on_cotrimoxazole"]),
            other_hepatotoxic_medicine=_flag_or_none(row["other_hepatotoxic_medicine"]),
        ),
        labs=LabResults(
            alt_multiple_of_upper_limit=None if _blank(row["alt_multiple_of_upper_limit"]) else float(str(row["alt_multiple_of_upper_limit"])),
            bilirubin_umol_per_l=None if _blank(row["bilirubin_umol_per_l"]) else float(str(row["bilirubin_umol_per_l"])),
            visual_exam=VisualExam(str(row["visual_exam"])),
        ),
        dechallenge=WORDS_ANSWER[str(row["dechallenge"])],
        rechallenge=WORDS_ANSWER[str(row["rechallenge"])],
    )
