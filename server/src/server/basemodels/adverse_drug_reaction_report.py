import enum
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from server.basemodels.causality_asssessment_level import CausalityAssessmentLevelEnum


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"


class PregnancyStatusEnum(str, enum.Enum):
    not_applicable = "not applicable"
    not_pregnant = "not pregnant"
    first_trimester = "1st trimester"
    second_trimester = "2nd trimester"
    third_trimester = "3rd trimester"


class KnownAllergyEnum(str, enum.Enum):
    yes = "yes"
    no = "no"


class RechallengeEnum(str, enum.Enum):
    yes = "yes"
    no = "no"
    unknown = "unknown"
    na = "na"


class DechallengeEnum(str, enum.Enum):
    yes = "yes"
    no = "no"
    unknown = "unknown"
    na = "na"


class SeverityEnum(str, enum.Enum):
    mild = "mild"
    moderate = "moderate"
    severe = "severe"
    fatal = "fatal"
    unknown = "unknown"


class IsSeriousEnum(str, enum.Enum):
    yes = "yes"
    no = "no"


class CriteriaForSeriousnessEnum(str, enum.Enum):
    hospitalisation = "hospitalisation"
    disability = "disability"
    congenital_anomaly = "congenital anomaly"
    life_threatening = "life-threatening"
    death = "death"


class ActionTakenEnum(str, enum.Enum):
    drug_withdrawn = "drug withdrawn"
    dose_reduced = "dose reduced"
    dose_increased = "dose increased"
    dose_not_changed = "dose not changed"
    not_applicable = "not applicable"
    unknown = "unknown"


class OutcomeEnum(str, enum.Enum):
    recovered = "recovered"
    recovered_with_sequelae = "recovered with sequelae"
    recovering = "recovering"
    not_recovered = "not recovered"
    death = "death"
    unknown = "unknown"


# ADR
class ADRPostRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Institution Details
    medical_institution_id: str | None = (
        "8ade772c-0808-4681-a22c-34f99cb742e5"  # Not in ML model
    )

    # User Submitted Details
    user_id: str = "804911e1-c1df-4e45-ae3c-de62104903f7"

    # Personal Details
    patient_name: str
    inpatient_or_outpatient_number: str | None = None
    patient_age: float | None = None
    patient_date_of_birth: date | None = None
    patient_address: str | None = None
    patient_weight_kg: float | None = None
    patient_height_cm: float | None = None
    ward_or_clinic: str | None = None
    patient_gender: GenderEnum
    pregnancy_status: PregnancyStatusEnum
    known_allergy: KnownAllergyEnum

    # Suspected Adverse Reaction
    date_of_onset_of_reaction: date | None = None
    description_of_reaction: str | None = None

    # Medicine fields - Rifampicin
    rifampicin_suspected: bool | None = None
    rifampicin_start_date: date | None = None
    rifampicin_stop_date: date | None = None
    rifampicin_dose_amount: float | None = None
    rifampicin_frequency_number: float | None = None
    rifampicin_route: str | None = None
    rifampicin_batch_no: str | None = None
    rifampicin_manufacturer: str | None = None

    # Isoniazid
    isoniazid_suspected: bool | None = None
    isoniazid_start_date: date | None = None
    isoniazid_stop_date: date | None = None
    isoniazid_dose_amount: float | None = None
    isoniazid_frequency_number: float | None = None
    isoniazid_route: str | None = None
    isoniazid_batch_no: str | None = None
    isoniazid_manufacturer: str | None = None

    # Pyrazinamide
    pyrazinamide_suspected: bool | None = None
    pyrazinamide_start_date: date | None = None
    pyrazinamide_stop_date: date | None = None
    pyrazinamide_dose_amount: float | None = None
    pyrazinamide_frequency_number: float | None = None
    pyrazinamide_route: str | None = None
    pyrazinamide_batch_no: str | None = None
    pyrazinamide_manufacturer: str | None = None

    # Ethambutol
    ethambutol_suspected: bool | None = None
    ethambutol_start_date: date | None = None
    ethambutol_stop_date: date | None = None
    ethambutol_dose_amount: float | None = None
    ethambutol_frequency_number: float | None = None
    ethambutol_route: str | None = None
    ethambutol_batch_no: str | None = None
    ethambutol_manufacturer: str | None = None

    # Rechallenge/Dechallenge
    rechallenge: RechallengeEnum = RechallengeEnum.unknown
    dechallenge: DechallengeEnum = DechallengeEnum.unknown

    # Grading of Reaction/Event
    severity: SeverityEnum = SeverityEnum.unknown
    is_serious: IsSeriousEnum
    criteria_for_seriousness: CriteriaForSeriousnessEnum
    action_taken: ActionTakenEnum = ActionTakenEnum.unknown
    outcome: OutcomeEnum = OutcomeEnum.unknown

    # Additional
    comments: str | None = None  # Not in ML model

    # created_at: date | None = None


class MLModelInput(BaseModel):
    # Order columns to match the model input schema and training dataset in order for SHAP to work
    model_config = ConfigDict(from_attributes=True)

    # Personal Details
    patient_name: str
    inpatient_or_outpatient_number: str | None = None
    patient_date_of_birth: date | None = None
    patient_age: float | None = None
    patient_address: str | None = None
    ward_or_clinic: str | None = None
    patient_gender: GenderEnum
    known_allergy: KnownAllergyEnum
    pregnancy_status: PregnancyStatusEnum
    patient_weight_kg: float | None = None
    patient_height_cm: float | None = None

    # Suspected Adverse Reaction
    date_of_onset_of_reaction: date | None = None
    description_of_reaction: str | None = None

    # Medicine fields - Rifampicin
    rifampicin_suspected: bool | None = None
    rifampicin_start_date: date | None = None
    rifampicin_stop_date: date | None = None
    rifampicin_dose_amount: float | None = None
    rifampicin_frequency_number: float | None = None
    rifampicin_route: str | None = None
    rifampicin_batch_no: str | None = None
    rifampicin_manufacturer: str | None = None

    # Isoniazid
    isoniazid_suspected: bool | None = None
    isoniazid_start_date: date | None = None
    isoniazid_stop_date: date | None = None
    isoniazid_dose_amount: float | None = None
    isoniazid_frequency_number: float | None = None
    isoniazid_route: str | None = None
    isoniazid_batch_no: str | None = None
    isoniazid_manufacturer: str | None = None

    # Pyrazinamide
    pyrazinamide_suspected: bool | None = None
    pyrazinamide_start_date: date | None = None
    pyrazinamide_stop_date: date | None = None
    pyrazinamide_dose_amount: float | None = None
    pyrazinamide_frequency_number: float | None = None
    pyrazinamide_route: str | None = None
    pyrazinamide_batch_no: str | None = None
    pyrazinamide_manufacturer: str | None = None

    # Ethambutol
    ethambutol_suspected: bool | None = None
    ethambutol_start_date: date | None = None
    ethambutol_stop_date: date | None = None
    ethambutol_dose_amount: float | None = None
    ethambutol_frequency_number: float | None = None
    ethambutol_route: str | None = None
    ethambutol_batch_no: str | None = None
    ethambutol_manufacturer: str | None = None

    # Rechallenge/Dechallenge
    dechallenge: DechallengeEnum = DechallengeEnum.unknown
    rechallenge: RechallengeEnum = RechallengeEnum.unknown

    # Grading of Reaction/Event
    severity: SeverityEnum = SeverityEnum.unknown
    is_serious: IsSeriousEnum
    criteria_for_seriousness: CriteriaForSeriousnessEnum
    action_taken: ActionTakenEnum = ActionTakenEnum.unknown
    outcome: OutcomeEnum = OutcomeEnum.unknown

    # Metadata
    created_at: date | None = None


class ADRGetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    # User
    user_id: str
    # Institution Details
    medical_institution_id: str | None = None
    # Personal Details
    patient_name: str
    inpatient_or_outpatient_number: str
    patient_age: int | None = None
    patient_date_of_birth: date | None = None
    patient_address: str | None = None
    patient_weight_kg: float | None = None
    patient_height_cm: float | None = None
    ward_or_clinic: str | None = None
    patient_gender: GenderEnum
    pregnancy_status: PregnancyStatusEnum
    known_allergy: KnownAllergyEnum
    # Suspected Adverse Reaction
    date_of_onset_of_reaction: date | None = None
    description_of_reaction: str | None = None
    # Rechallenge/Dechallenge
    rechallenge: RechallengeEnum
    dechallenge: DechallengeEnum
    # Grading of Reaction/Event
    severity: SeverityEnum
    is_serious: IsSeriousEnum
    criteria_for_seriousness: CriteriaForSeriousnessEnum
    action_taken: ActionTakenEnum
    outcome: OutcomeEnum
    comments: str | None = None

    # causality_assessment_levels: List[CausalityAssessmentLevelGetResponse] = []


class ADRWithReviewsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    adr_id: str
    patient_name: str
    created_by: str
    created_at: datetime

    causality_assessment_level_value: CausalityAssessmentLevelEnum | None = None

    approved_reviews: int
    unapproved_reviews: int
