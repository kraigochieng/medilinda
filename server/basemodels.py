import enum
from datetime import date, datetime
from typing import List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


# Define Enums for each field
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


class CausalityAssessmentLevelEnum(str, enum.Enum):
    certain = "certain"
    likely = "likely"
    possible = "possible"
    unlikely = "unlikely"
    unclassified = "unclassified"
    unclassifiable = "unclassifiable"


class ReviewEnum(str, enum.Enum):
    approved = "approved"
    denied = "denied"


class SMSMessageTypeEnum(str, enum.Enum):
    individual_alert = "individual alert"
    # bulk_alert = "bulk alert"
    additional_info = "additional info"


# Users
class User(BaseModel):
    username: str
    email: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserSignupBaseModel(BaseModel):
    username: str
    password: str
    first_name: str | None = None
    last_name: str | None = None


class UserDetailsBaseModel(BaseModel):
    id: str | None = None
    username: str
    first_name: str | None = None
    last_name: str | None = None


class UserLoginBaseModel(BaseModel):
    username: str
    password: str


class UserGetResponse(BaseModel):
    id: str
    username: str
    first_name: str
    last_name: str


# Review
class ReviewGetResponse(BaseModel):
    id: str
    causality_assessment_level_id: str
    user_id: str
    user: UserGetResponse
    approved: bool
    proposed_causality_level: CausalityAssessmentLevelEnum | None = None
    reason: str | None
    created_at: datetime


# class ReviewGetResponse(BaseModel):
#     causality_assessment_level_id: str
#     # causality_assessment_level: model
#     user_id = str
#     # user: model
#     approved: bool
#     proposed_causality_level = CausalityAssessmentLevelEnum
#     reason: str | None = None


# CAL
# class CausalityAssessmentLevelGetResponse2(BaseModel):
#     id: str
#     adr_id: str
#     ml_model_id: str
#     causality_assessment_level_value: CausalityAssessmentLevelEnum
#     prediction_reason: str | None = None


# class CausalityAssessmentLevelGetResponse(BaseModel):
#     id: str
#     adr_id: str
#     ml_model_id: str
#     causality_assessment_level_value: CausalityAssessmentLevelEnum
#     prediction_reason: str | None = None
#     reviews: List[ReviewGetResponse] = []


class CausalityAssessmentLevelGetResponse(BaseModel):
    id: str
    adr_id: str
    ml_model_id: str = "final_ml_model@champion"
    causality_assessment_level_value: CausalityAssessmentLevelEnum

    base_values: Optional[List[float]] = None
    shap_values_matrix: Optional[List[List[float]]] = None
    shap_values_sum_per_class: Optional[List[float]] = None
    shap_values_and_base_values_sum_per_class: Optional[List[float]] = None
    feature_names: Optional[List[str]] = None
    feature_values: Optional[List[Any]] = None


# ADR
class ADRPostRequest(BaseModel):
    # Institution Details
    medical_institution_id: str | None = None

    # Personal Details
    patient_name: str
    inpatient_or_outpatient_number: str | None = None
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

    # Medicine fields - Rifampicin
    rifampicin_suspected: bool | None = None
    rifampicin_start_date: date | None = None
    rifampicin_stop_date: date | None = None
    rifampicin_dose_amount: int | None = None
    rifampicin_frequency_number: int | None = None
    rifampicin_route: str | None = None
    rifampicin_batch_no: str | None = None
    rifampicin_manufacturer: str | None = None

    # Isoniazid
    isoniazid_suspected: bool | None = None
    isoniazid_start_date: date | None = None
    isoniazid_stop_date: date | None = None
    isoniazid_dose_amount: int | None = None
    isoniazid_frequency_number: int | None = None
    isoniazid_route: str | None = None
    isoniazid_batch_no: str | None = None
    isoniazid_manufacturer: str | None = None

    # Pyrazinamide
    pyrazinamide_suspected: bool | None = None
    pyrazinamide_start_date: date | None = None
    pyrazinamide_stop_date: date | None = None
    pyrazinamide_dose_amount: int | None = None
    pyrazinamide_frequency_number: int | None = None
    pyrazinamide_route: str | None = None
    pyrazinamide_batch_no: str | None = None
    pyrazinamide_manufacturer: str | None = None

    # Ethambutol
    ethambutol_suspected: bool | None = None
    ethambutol_start_date: date | None = None
    ethambutol_stop_date: date | None = None
    ethambutol_dose_amount: int | None = None
    ethambutol_frequency_number: int | None = None
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
    comments: str | None = None


class ADRGetResponse(BaseModel):
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


class ADRReviewCreateRequest(BaseModel):
    approved: bool
    proposed_causality_level: CausalityAssessmentLevelEnum | None = None
    reason: str | None = None


class ADRReviewSchema(BaseModel):
    review_id: str
    user_id: str
    approved: bool
    proposed_causality_level: CausalityAssessmentLevelEnum | None = None
    reason: str | None = None
    created_at: datetime


class ADRReviewGetResponse(BaseModel):
    adr_id: str
    patient_id: str
    user_id: str
    patient_gender: str
    pregnancy_status: str
    known_allergy: str
    rechallenge: str
    dechallenge: str
    severity: str
    is_serious: str
    criteria_for_seriousness: str
    action_taken: str
    outcome: str
    causality_assessment_level: str | None = None
    reviews: List[ADRReviewSchema] = []


# Medical Institution
class MedicalInstitutionGetResponse(BaseModel):
    id: str
    name: str
    mfl_code: str | None = None
    dhis_code: str | None = None
    county: str | None = None
    sub_county: str | None = None


class MedicalInstitutionPostRequest(BaseModel):
    name: str
    mfl_code: str | None = None
    dhis_code: str | None = None
    county: str | None = None
    sub_county: str | None = None


# Medical Institution Telephone
class MedicalInstitutionTelephoneGetResponse(BaseModel):
    medical_institution_id: str
    telephone: str


class MedicalInstitutionTelephonePostRequest(BaseModel):
    medical_institution_id: str
    telephone: str


class MultipleMedicalInstitutionTelephonePostRequest(BaseModel):
    telephones: List[MedicalInstitutionTelephonePostRequest]


# SMS Message
class SMSMessageGetResponse(BaseModel):
    id: str
    adr_id: str
    content: str
    sms_type: SMSMessageTypeEnum
    cost: str | None = None
    message_id: str | None = None
    message_parts: int | None = None
    number: str | None = None
    status: str
    status_code: int
    created_at: datetime


class IndividualAlertPostRequest(BaseModel):
    adr_id: str


class AdditionalInfoPostRequest(BaseModel):
    adr_id: str


class UnclassifiablePostRequest(BaseModel):
    adr_ids: List[str]
