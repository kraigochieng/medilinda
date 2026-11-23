"""The fields of one report that decide the WHO-UMC facts, named after the PPB yellow form.

The history, medicines and lab fields follow sections 4 to 8 of the form. The decisions
DR-7 and DR-8 of issue #164 add the typed history, antiretroviral, lab and eye fields.
"""

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class DrugName(StrEnum):
    """The four first-line TB medicines of the project."""

    RIFAMPICIN = "rifampicin"
    ISONIAZID = "isoniazid"
    PYRAZINAMIDE = "pyrazinamide"
    ETHAMBUTOL = "ethambutol"


class FormAnswer(StrEnum):
    """The four answers that the yellow form gives to the dechallenge and rechallenge questions."""

    YES = "yes"
    NO = "no"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


class Antiretroviral(StrEnum):
    """The antiretroviral treatment of the patient, as far as it matters for another cause."""

    NONE = "none"
    DOLUTEGRAVIR_BASED = "dolutegravir_based"
    NNRTI_BASED = "nnrti_based"  # nevirapine or efavirenz: named as a cause of liver injury in the Kenya guideline
    UNKNOWN = "unknown"


class VisualExam(StrEnum):
    """The result of an eye examination."""

    ABNORMAL = "abnormal"
    NORMAL = "normal"
    NOT_DONE = "not_done"


class MedicineExposure(BaseModel):
    """One TB medicine of the patient: was it suspected, and when was it taken."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    drug: DrugName
    suspected: bool
    start_date: date | None
    stop_date: date | None


class MedicalHistory(BaseModel):
    """Section 4 of the form, typed. A value of None means that the form did not record it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    alcohol_use: bool | None
    hepatic_dysfunction: bool | None
    renal_dysfunction: bool | None
    hiv_positive: bool | None
    hepatitis_b_or_c: bool | None


class OtherMedicines(BaseModel):
    """Sections 5 and 6 of the form, typed: the medicines that can be another cause."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    antiretroviral: Antiretroviral
    on_cotrimoxazole: bool | None
    other_hepatotoxic_medicine: bool | None


class LabResults(BaseModel):
    """Section 8 of the form, typed. A value of None means that the test was not done."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    alt_multiple_of_upper_limit: float | None
    bilirubin_umol_per_l: float | None
    visual_exam: VisualExam


class ReportFields(BaseModel):
    """The fields of one report that the mapping to the WHO-UMC facts reads."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    onset_date: date | None
    reaction_terms: list[str]
    exposures: list[MedicineExposure]
    history: MedicalHistory
    other_medicines: OtherMedicines
    labs: LabResults
    dechallenge: FormAnswer
    rechallenge: FormAnswer
