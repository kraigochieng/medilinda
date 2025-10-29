from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Float
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from ..basemodels.adverse_drug_reaction_report import (
    ActionTakenEnum,
    CriteriaForSeriousnessEnum,
    DechallengeEnum,
    GenderEnum,
    IsSeriousEnum,
    KnownAllergyEnum,
    OutcomeEnum,
    PregnancyStatusEnum,
    RechallengeEnum,
    SeverityEnum,
)
from ..db.base import Base
from ._mixins import IDMixin, TimestampMixin


class ADRModel(Base, IDMixin, TimestampMixin):
    __tablename__ = "adr"
    # Institution Details
    medical_institution_id = Column(
        String, ForeignKey("medical_institution.id"), nullable=False
    )
    medical_institution = relationship("MedicalInstitutionModel", back_populates="adrs")

    # Personal Details
    patient_name = Column(String, nullable=False)
    inpatient_or_outpatient_number = Column(String, nullable=True)
    patient_date_of_birth = Column(Date, nullable=True)
    patient_age = Column(Integer, nullable=True)
    patient_address = Column(String, nullable=True)
    ward_or_clinic = Column(String, nullable=True)
    patient_gender = Column(SQLAlchemyEnum(GenderEnum), nullable=False)
    known_allergy = Column(SQLAlchemyEnum(KnownAllergyEnum), nullable=False)
    pregnancy_status = Column(SQLAlchemyEnum(PregnancyStatusEnum), nullable=False)
    patient_weight_kg = Column(Float, nullable=True)
    patient_height_cm = Column(Float, nullable=True)

    # Suspected Adverse Reaction
    date_of_onset_of_reaction = Column(Date, nullable=True)
    description_of_reaction = Column(String, nullable=True)

    # Medicine Columns
    rifampicin_suspected = Column(Boolean, nullable=True)
    rifampicin_start_date = Column(Date, nullable=True)
    rifampicin_stop_date = Column(Date, nullable=True)
    rifampicin_dose_amount = Column(Integer, nullable=True)
    rifampicin_frequency_number = Column(Integer, nullable=True)
    rifampicin_route = Column(String(20), nullable=True)
    rifampicin_batch_no = Column(String(50), nullable=True)
    rifampicin_manufacturer = Column(String(100), nullable=True)

    isoniazid_suspected = Column(Boolean, nullable=True)
    isoniazid_start_date = Column(Date, nullable=True)
    isoniazid_stop_date = Column(Date, nullable=True)
    isoniazid_dose_amount = Column(Integer, nullable=True)
    isoniazid_frequency_number = Column(Integer, nullable=True)
    isoniazid_route = Column(String(20), nullable=True)
    isoniazid_batch_no = Column(String(50), nullable=True)
    isoniazid_manufacturer = Column(String(100), nullable=True)

    pyrazinamide_suspected = Column(Boolean, nullable=True)
    pyrazinamide_start_date = Column(Date, nullable=True)
    pyrazinamide_stop_date = Column(Date, nullable=True)
    pyrazinamide_dose_amount = Column(Integer, nullable=True)
    pyrazinamide_frequency_number = Column(Integer, nullable=True)
    pyrazinamide_route = Column(String(20), nullable=True)
    pyrazinamide_batch_no = Column(String(50), nullable=True)
    pyrazinamide_manufacturer = Column(String(100), nullable=True)

    ethambutol_suspected = Column(Boolean, nullable=True)
    ethambutol_start_date = Column(Date, nullable=True)
    ethambutol_stop_date = Column(Date, nullable=True)
    ethambutol_dose_amount = Column(Integer, nullable=True)
    ethambutol_frequency_number = Column(Integer, nullable=True)
    ethambutol_route = Column(String(20), nullable=True)
    ethambutol_batch_no = Column(String(50), nullable=True)
    ethambutol_manufacturer = Column(String(100), nullable=True)

    # Rechallenge/Dechallenge
    rechallenge = Column(
        SQLAlchemyEnum(RechallengeEnum), nullable=False, default=RechallengeEnum.unknown
    )
    dechallenge = Column(
        SQLAlchemyEnum(DechallengeEnum), nullable=False, default=DechallengeEnum.unknown
    )
    # Grading of Reaction/Event
    severity = Column(
        SQLAlchemyEnum(SeverityEnum), nullable=False, default=SeverityEnum.unknown
    )
    is_serious = Column(SQLAlchemyEnum(IsSeriousEnum), nullable=False)
    criteria_for_seriousness = Column(
        SQLAlchemyEnum(CriteriaForSeriousnessEnum), nullable=False
    )
    action_taken = Column(
        SQLAlchemyEnum(ActionTakenEnum), nullable=False, default=ActionTakenEnum.unknown
    )
    outcome = Column(
        SQLAlchemyEnum(OutcomeEnum), nullable=False, default=OutcomeEnum.unknown
    )
    # causality_assessment_level = Column(
    #     SQLAlchemyEnum(CausalityAssessmentLevelEnum), nullable=True
    # )
    comments = Column(String, nullable=True)

    # Relationships
    causality_assessment_levels = relationship(
        "CausalityAssessmentLevelModel",
        back_populates="adr",
        cascade="all, delete-orphan",
    )

    sms_messages = relationship(
        "SMSMessageModel",
        back_populates="adr",
    )

    # User Tracking
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    user = relationship(
        "UserModel",
        back_populates="adrs",
    )
