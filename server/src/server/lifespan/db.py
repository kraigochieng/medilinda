import datetime
import logging
import os
import random
from uuid import uuid4

import pandas as pd
from mlflow.pyfunc import PyFuncModel
from shap import KernelExplainer
from sklearn.preprocessing import OrdinalEncoder
from sqlalchemy.orm import Session

from server.basemodels.adverse_drug_reaction_report import (
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
from server.config import (
    ADR_CSV_PATH,
    MEDICAL_INSTITUTIONS_CSV_PATH,
    USERS_CSV_PATH,
)
from server.db.base import Base
from server.db.engine import engine
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.causality_assessment_level import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelModel,
)
from server.models.medical_institution import (
    MedicalInstitutionModel,
    MedicalInstitutionTelephoneModel,
)
from server.models.review import ReviewModel
from server.models.sms import SMSMessageModel, SMSMessageTypeEnum
from server.models.user import UserModel
from server.utils import (
    bool_cols,
    format_dataframe_for_model,
    get_shap_values,
    model_cols,
    numeric_cols,
    safe_date_parse,
    string_cols,
)


def setup_db():
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logging.error(f"Error creating tables: {e}")


def insert_medical_institutions(session: Session):
    # Add institutions
    institution_count = session.query(MedicalInstitutionModel).count()

    if institution_count != 0:
        logging.info("Medical Institutions already inserted")
        return

    if not os.path.exists(MEDICAL_INSTITUTIONS_CSV_PATH):
        logging.warning("Medical Institutions CSV path does not exist")
        return

    institution_df = pd.read_csv(MEDICAL_INSTITUTIONS_CSV_PATH)

    institution_entries = []

    for record in institution_df.to_dict(orient="records"):
        institution_entry = MedicalInstitutionModel(
            mfl_code=record["MFL Code"],
            dhis_code=record["DHIS Code"],
            name=record["Name"],
            county=record["County"],
            sub_county=record["Subcounty"],
        )

        institution_entries.append(institution_entry)

    session.add_all(institution_entries)
    session.commit()
    logging.info("Medical Institutions inserted")


def insert_medical_institution_telephones(session: Session):
    institution_telephones_count = session.query(
        MedicalInstitutionTelephoneModel
    ).count()

    if institution_telephones_count != 0:
        logging.info("Medical Institution Telephones already inserted")
        return

    institutions = session.query(MedicalInstitutionModel).all()

    institution_telephone_entries = []

    for institution in institutions:
        if not institution.telephones:  # If no telephone entries yet
            institution_telephone_entry = MedicalInstitutionTelephoneModel(
                medical_institution_id=institution.id, telephone="+254777529295"
            )

            institution_telephone_entries.append(institution_telephone_entry)

    session.add_all(institution_telephone_entries)
    session.commit()

    logging.info("Medical Institution Telephones inserted")


def insert_users(session: Session):
    user_count = session.query(UserModel).count()

    if user_count != 0:
        logging.info("Users already inserted")
        return

    if not os.path.exists(USERS_CSV_PATH):
        logging.warning("Users CSV path does not exist")
        return

    users_df = pd.read_csv(USERS_CSV_PATH)
    session.bulk_insert_mappings(UserModel, users_df.to_dict(orient="records"))
    session.commit()
    logging.info("User data inserted successfully.")


def insert_adverse_drug_reaction_reports(session: Session) -> list[ADRModel]:
    user_a = session.query(UserModel).filter(UserModel.username == "A").first()

    if not user_a:
        logging.error("User with username 'A' not found! ADR insertion aborted.")
        return

    user_a_id = user_a.id  # Get user ID

    adr_count = session.query(ADRModel).count()

    if adr_count != 0:
        logging.info("ADR already inserted")
        adr_entries = session.query(ADRModel).all()
        return adr_entries

    if not os.path.exists(ADR_CSV_PATH):
        logging.warning("ADR CSV not found")
        return

    adr_df = pd.read_csv(ADR_CSV_PATH)

    adr_entries: list[ADRModel] = []

    facility_ids = session.query(MedicalInstitutionModel.id).limit(20).all()
    facility_ids = [id_tuple[0] for id_tuple in facility_ids]

    for record in adr_df.to_dict(orient="records"):
        adr_entry = ADRModel(
            # Institution Details
            medical_institution_id=random.choice(facility_ids),
            # Personal Details
            patient_name=record["patient_name"],
            inpatient_or_outpatient_number=record["inpatient_or_outpatient_number"],
            patient_date_of_birth=safe_date_parse(record["patient_date_of_birth"]),
            patient_age=record["patient_age"]
            if pd.notna(record["patient_age"])
            else None,
            patient_address=record["patient_address"],
            ward_or_clinic=record["ward_or_clinic"],
            patient_gender=GenderEnum(record["patient_gender"]),
            known_allergy=KnownAllergyEnum(record["known_allergy"]),
            pregnancy_status=PregnancyStatusEnum(record["pregnancy_status"]),
            patient_weight_kg=record["patient_weight_kg"],
            patient_height_cm=record["patient_height_cm"],
            # Suspected Adverse Reaction
            date_of_onset_of_reaction=safe_date_parse(
                record["date_of_onset_of_reaction"]
            ),
            description_of_reaction=record["description_of_reaction"],
            # Medicine Columns (Rifampicin)
            rifampicin_suspected=record["rifampicin_suspected"],
            rifampicin_start_date=safe_date_parse(record["rifampicin_start_date"]),
            rifampicin_stop_date=safe_date_parse(record["rifampicin_stop_date"]),
            rifampicin_dose_amount=record["rifampicin_dose_amount"],
            rifampicin_frequency_number=record["rifampicin_frequency_number"],
            rifampicin_route=record["rifampicin_route"],
            rifampicin_batch_no=record["rifampicin_batch_no"],
            rifampicin_manufacturer=record["rifampicin_manufacturer"],
            # Medicine Columns (Isoniazid)
            isoniazid_suspected=record["isoniazid_suspected"],
            isoniazid_start_date=safe_date_parse(record["isoniazid_start_date"]),
            isoniazid_stop_date=safe_date_parse(record["isoniazid_stop_date"]),
            isoniazid_dose_amount=record["isoniazid_dose_amount"],
            isoniazid_frequency_number=record["isoniazid_frequency_number"],
            isoniazid_route=record["isoniazid_route"],
            isoniazid_batch_no=record["isoniazid_batch_no"],
            isoniazid_manufacturer=record["isoniazid_manufacturer"],
            # Medicine Columns (Pyrazinamide)
            pyrazinamide_suspected=record["pyrazinamide_suspected"],
            pyrazinamide_start_date=safe_date_parse(record["pyrazinamide_start_date"]),
            pyrazinamide_stop_date=safe_date_parse(record["pyrazinamide_stop_date"]),
            pyrazinamide_dose_amount=record["pyrazinamide_dose_amount"],
            pyrazinamide_frequency_number=record["pyrazinamide_frequency_number"],
            pyrazinamide_route=record["pyrazinamide_route"],
            pyrazinamide_batch_no=record["pyrazinamide_batch_no"],
            pyrazinamide_manufacturer=record["pyrazinamide_manufacturer"],
            # Medicine Columns (Ethambutol)
            ethambutol_suspected=record["ethambutol_suspected"],
            ethambutol_start_date=safe_date_parse(record["ethambutol_start_date"]),
            ethambutol_stop_date=safe_date_parse(record["ethambutol_stop_date"]),
            ethambutol_dose_amount=record["ethambutol_dose_amount"],
            ethambutol_frequency_number=record["ethambutol_frequency_number"],
            ethambutol_route=record["ethambutol_route"],
            ethambutol_batch_no=record["ethambutol_batch_no"],
            ethambutol_manufacturer=record["ethambutol_manufacturer"],
            # Rechallenge/Dechallenge, etc.
            rechallenge=RechallengeEnum(record["rechallenge"]),
            dechallenge=DechallengeEnum(record["dechallenge"]),
            severity=SeverityEnum(record["severity"]),
            is_serious=IsSeriousEnum(record["is_serious"]),
            criteria_for_seriousness=CriteriaForSeriousnessEnum(
                record["criteria_for_seriousness"]
            ),
            action_taken=ActionTakenEnum(record["action_taken"]),
            outcome=OutcomeEnum(record["outcome"]),
            created_at=safe_date_parse(record["created_at"]),
            # Relationships
            user_id=user_a_id,
        )
        adr_entries.append(adr_entry)

    session.add_all(adr_entries)
    session.commit()  # This assigns IDs via flush

    for adr_entry in adr_entries:
        session.refresh(adr_entry)

    logging.info("ADR inserted successfully.")
    return adr_entries


def insert_causality_assessment_levels(
    session: Session,
    ml_model: PyFuncModel,
    encoder: OrdinalEncoder,
    explainer: KernelExplainer,
    adr_entries: list[ADRModel],
):
    causality_assessment_level_count = session.query(
        CausalityAssessmentLevelModel
    ).count()

    if causality_assessment_level_count != 0:
        logging.info("Causality Assessment Levels already inserted")
        return

    if not os.path.exists(ADR_CSV_PATH):
        logging.warning("ADR CSV not found")
        return

    causality_entries: list[CausalityAssessmentLevelModel] = []

    # new_data_df = pd.read_csv(
    #     ADR_CSV_PATH,
    # )

    # for adr_entry, record in zip(adr_entries, new_data_df.to_dict(orient="records")):
    for adr_entry in adr_entries:
        # Load and preprocess new data
        record_dict = {
            c.name: getattr(adr_entry, c.name) for c in adr_entry.__table__.columns
        }
        adr_data_df = pd.DataFrame([record_dict])

        formatted_df = format_dataframe_for_model(
            adr_data_df,
            model_cols=model_cols,
            numeric_cols=numeric_cols,
            bool_cols=bool_cols,
            string_cols=string_cols,
        )
        # Predict using the ML model
        prediction = ml_model.predict(formatted_df)

        decoded_prediction = encoder.inverse_transform(prediction.reshape(-1, 1))[0][0]

        logging.info("Generation SHAP value...")
        shap_values = explainer(formatted_df)

        broken_down_shap_values = get_shap_values(shap_values)

        base_values = broken_down_shap_values["base_values"]
        shap_values_matrix = broken_down_shap_values["shap_values_matrix"]
        shap_values_sum_per_class = broken_down_shap_values["shap_values_sum_per_class"]
        shap_values_and_base_values_sum_per_class = broken_down_shap_values[
            "shap_values_and_base_values_sum_per_class"
        ]

        # Add causality assessment level
        causality_entry = CausalityAssessmentLevelModel(
            adr_id=adr_entry.id,
            causality_assessment_level_value=CausalityAssessmentLevelEnum(
                decoded_prediction
            ),
            base_values=base_values,
            shap_values_matrix=shap_values_matrix,
            shap_values_sum_per_class=shap_values_sum_per_class,
            shap_values_and_base_values_sum_per_class=shap_values_and_base_values_sum_per_class,
            feature_names=None,
            feature_values=None,
        )

        causality_entries.append(causality_entry)

    session.add_all(causality_entries)
    session.commit()

    logging.info("Causality Assessment inserted successfully.")


def insert_reviews(session: Session):
    review_count = session.query(ReviewModel).count()

    if review_count != 0:
        logging.info("Review data already inserted")
        return

    causality_entries = session.query(CausalityAssessmentLevelModel).all()

    users = session.query(UserModel).all()
    user_ids = [u.id for u in users]

    for causality_entry in causality_entries:
        # Ensure 20 unique users per causality assessment
        # selected_user_ids = random.sample(user_ids, min(20, len(user_ids)))
        selected_user_ids = user_ids

        for user_id in selected_user_ids:
            approved = random.choices(
                population=[
                    True,
                    False,
                ],
                weights=[0.65, 0.35],
                k=1,
            )[0]
            proposed_level = (
                random.choice(list(CausalityAssessmentLevelEnum))
                if not approved
                else None
            )
            reason = (
                random.choice(
                    [
                        "Sufficient evidence provided.",
                        "Missing key symptom analysis.",
                        "Reviewed and agreed.",
                        "Contradicts known patterns.",
                        "Needs expert second opinion.",
                        "",
                    ]
                )
                if not approved
                else None
            )

            review = ReviewModel(
                causality_assessment_level_id=causality_entry.id,
                user_id=user_id,
                approved=approved,
                proposed_causality_level=proposed_level,
                reason=reason,
            )
            session.add(review)

    session.commit()
    logging.info("Reviews inserted.")


def insert_sms_messages(session: Session):
    # Add SMS messages for each ADR
    sms_message_count = session.query(SMSMessageModel).count()

    # if sms_message_count == 0:
    #     sms_messages = []
    #     for adr in session.query(ADRModel).all():
    #         for sms_type in SMSMessageTypeEnum:
    #             number_of_messages = random.randint(0, 5)

    #             if (
    #                 sms_type == SMSMessageTypeEnum.individual_alert
    #                 and number_of_messages == 0
    #             ):
    #                 print(f"{adr.patient_name} - {sms_type} - {number_of_messages}")

    #             for _ in range(number_of_messages):
    #                 sms_message = SMSMessageModel(
    #                     message_id=f"ATXid_{uuid4()}",
    #                     sms_type=sms_type,
    #                     number="+254777529295",
    #                     content=f"{adr.medical_institution.name} - {sms_type.value} - {adr.patient_name}",
    #                     cost="KES 0.8000",
    #                     status="Success",
    #                     status_code=100,
    #                     adr_id=adr.id,
    #                 )
    #                 sms_messages.append(sms_message)

    #     session.add_all(sms_messages)
    #     session.commit()
    #     logging.info("SMS messages inserted successfully.")
    # else:
    #     logging.info("SMS messages already successfully.")

    if sms_message_count != 0:
        logging.info("SMS messages already exist. Skipping creation.")
        return

    sms_messages = []

    # Get all causality assessments that are CERTAIN
    certain_assessments = (
        session.query(CausalityAssessmentLevelModel)
        .filter(
            CausalityAssessmentLevelModel.causality_assessment_level_value
            == CausalityAssessmentLevelEnum.certain
        )
        .all()
    )

    for cal in certain_assessments:
        adr = session.query(ADRModel).filter(ADRModel.id == cal.adr_id).first()
        reviews = (
            session.query(ReviewModel)
            .filter(ReviewModel.causality_assessment_level_id == cal.id)
            .all()
        )

        if not reviews:
            continue

        approvals = sum(1 for r in reviews if r.approved)
        denials = len(reviews) - approvals

        if approvals > denials:
            # Add a random number of messages
            for _ in range(random.randint(0, 3)):
                sms_message = SMSMessageModel(
                    message_id=f"ATXid_{uuid4()}",
                    sms_type=SMSMessageTypeEnum.individual_alert,
                    number="+254777529295",
                    content=f"{adr.medical_institution.name} - individual alert - {adr.patient_name}",
                    cost="KES 0.8000",
                    status="Success",
                    status_code=100,
                    adr_id=adr.id,
                )
                sms_messages.append(sms_message)
                logging.info(
                    f"✅ SMS alert created for ADR {adr.id} ({adr.patient_name})"
                )

    if sms_messages:
        session.add_all(sms_messages)
        session.commit()
        logging.info("Filtered SMS messages inserted successfully.")
    else:
        logging.info("No ADRs met criteria for SMS message creation.")
