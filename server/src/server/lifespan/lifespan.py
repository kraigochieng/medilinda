import datetime
import logging
import os
import random
import shutil
from contextlib import asynccontextmanager
from datetime import datetime
from uuid import uuid4

import pandas as pd
import shap
from fastapi import FastAPI
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
from server.db import DB_PATH
from server.db.base import Base
from server.db.engine import engine
from server.lifespan.mlflow_setup import MLEnsemble, mlflow_setup
# from server.ml.artifacts import (
#     ENCODERS_PATH,
#     METADATA_PATH,
#     SCALERS_PATH,
# )
# from server.ml.utils import (
#     format_feature_values,
#     get_column_metadata,
#     get_encoders,
#     get_scalers,
#     get_shap_values,
# )
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
from server.settings import settings


def safe_date_parse(date_str):
    """
    Safely parses a date string into a datetime.date object.
    Returns None if the input is empty, invalid, or causes an error.
    """
    if pd.isna(date_str) or not date_str:
        return None
    try:
        # pd.to_datetime is flexible and can handle many formats
        return pd.to_datetime(date_str).date()
    except (ValueError, TypeError):
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ML Model Artifacts
    ml_ensemble: MLEnsemble = mlflow_setup(
        databricks_host=settings.databricks_host,
        databricks_token=settings.databricks_token,
        mlflow_tracking_uri=settings.mlflow_tracking_uri,
        mlflow_experiment_path=settings.mlflow_experiment_path,
        mlflow_artifact_path=settings.mlflow_artifact_path,
        mlflow_model_name=settings.mlflow_model_name,
        mlflow_model_version=settings.mlflow_model_version,
    )

    app.state.ml_model = ml_ensemble["model"]
    app.state.encoder = ml_ensemble["encoder"]
    app.state.explainer = ml_ensemble["explainer"]

    ml_model: PyFuncModel = app.state.ml_model
    encoder: OrdinalEncoder = app.state.encoder
    explainer: KernelExplainer = app.state.explainer

    # Load and preprocess new data
    new_data_df = pd.read_csv(ADR_CSV_PATH)

    # Create tables once before the app starts
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logging.error(f"Error creating tables: {e}")

    session = Session(bind=engine)

    # Add institutions
    institution_count = session.query(MedicalInstitutionModel).count()

    if institution_count == 0 and os.path.exists(MEDICAL_INSTITUTIONS_CSV_PATH):
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
    else:
        logging.info("Medical Institutions already inserted")

    # Add telelphones to the institutions
    institution_telephones_count = session.query(
        MedicalInstitutionTelephoneModel
    ).count()

    if institution_telephones_count == 0:
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
    else:
        logging.info("Medical Institution Telephones already inserted")

    # Add users
    user_count = session.query(UserModel).count()

    if user_count == 0 and os.path.exists(USERS_CSV_PATH):
        users_df = pd.read_csv(USERS_CSV_PATH)
        session.bulk_insert_mappings(UserModel, users_df.to_dict(orient="records"))
        session.commit()
        logging.info("User data inserted successfully.")
    else:
        logging.info("User data already exists. Skipping CSV insertion.")

    # Retrieve User ID for username "A"
    user_a = session.query(UserModel).filter(UserModel.username == "A").first()

    if not user_a:
        logging.error("User with username 'A' not found! ADR insertion aborted.")
        session.close()
        yield
        return

    user_a_id = user_a.id  # Get user ID

    # # Add ADRs using current user
    # adr_count = session.query(ADRModel).count()

    # if adr_count == 0 and os.path.exists(ADR_CSV_PATH):
    #     adr_df = pd.read_csv(ADR_CSV_PATH)

    #     adr_entries = []
    #     causality_entries = []

    #     facility_ids = session.query(MedicalInstitutionModel.id).limit(20).all()
    #     facility_ids = [id_tuple[0] for id_tuple in facility_ids]

    #     for record in adr_df.to_dict(orient="records"):
    #         adr_entry = ADRModel(
    #             # Institution Details
    #             medical_institution_id=random.choice(facility_ids),
    #             # Personal Details
    #             patient_name=record["patient_name"],
    #             inpatient_or_outpatient_number=record["inpatient_or_outpatient_number"],
    #             # patient_date_of_birth=datetime.datetime.strptime(
    #             #     record["patient_date_of_birth"], "%Y-%m-%d"
    #             # ).date()
    #             # if pd.notna(record["patient_date_of_birth"])
    #             # else None,
    #             patient_date_of_birth=safe_date_parse(record["patient_date_of_birth"]),
    #             patient_age=record["patient_age"]
    #             if pd.notna(record["patient_age"])
    #             else None,
    #             patient_address=record["patient_address"],
    #             ward_or_clinic=record["ward_or_clinic"],
    #             patient_gender=GenderEnum(record["patient_gender"]),
    #             known_allergy=KnownAllergyEnum(record["known_allergy"]),
    #             pregnancy_status=PregnancyStatusEnum(record["pregnancy_status"]),
    #             patient_weight_kg=record["patient_weight_kg"],
    #             patient_height_cm=record["patient_height_cm"],
    #             # Suspected Adverse Reaction
    #             date_of_onset_of_reaction=safe_date_parse(
    #                 record["date_of_onset_of_reaction"]
    #             ),
    #             description_of_reaction=record["description_of_reaction"],
    #             # Medicine Columns
    #             rifampicin_suspected=record["rifampicin_suspected"],
    #             rifampicin_start_date=safe_date_parse(record["rifampicin_start_date"]),
    #             rifampicin_stop_date=safe_date_parse(record["rifampicin_stop_date"]),
    #             rifampicin_dose_amount=record["rifampicin_dose_amount"],
    #             rifampicin_frequency_number=record["rifampicin_frequency_number"],
    #             rifampicin_route=record["rifampicin_route"],
    #             rifampicin_batch_no=record["rifampicin_batch_no"],
    #             rifampicin_manufacturer=record["rifampicin_manufacturer"],
    #             isoniazid_suspected=record["isoniazid_suspected"],
    #             isoniazid_start_date=safe_date_parse(record["isoniazid_start_date"]),
    #             isoniazid_stop_date=safe_date_parse(record["isoniazid_stop_date"]),
    #             isoniazid_dose_amount=record["isoniazid_dose_amount"],
    #             isoniazid_frequency_number=record["isoniazid_frequency_number"],
    #             isoniazid_route=record["isoniazid_route"],
    #             isoniazid_batch_no=record["isoniazid_batch_no"],
    #             isoniazid_manufacturer=record["isoniazid_manufacturer"],
    #             pyrazinamide_suspected=record["pyrazinamide_suspected"],
    #             pyrazinamide_start_date=safe_date_parse(
    #                 record["pyrazinamide_start_date"]
    #             ),
    #             pyrazinamide_stop_date=safe_date_parse(
    #                 record["pyrazinamide_stop_date"]
    #             ),
    #             pyrazinamide_dose_amount=record["pyrazinamide_dose_amount"],
    #             pyrazinamide_frequency_number=record["pyrazinamide_frequency_number"],
    #             pyrazinamide_route=record["pyrazinamide_route"],
    #             pyrazinamide_batch_no=record["pyrazinamide_batch_no"],
    #             pyrazinamide_manufacturer=record["pyrazinamide_manufacturer"],
    #             ethambutol_suspected=record["ethambutol_suspected"],
    #             ethambutol_start_date=safe_date_parse(record["ethambutol_start_date"]),
    #             ethambutol_stop_date=safe_date_parse(record["ethambutol_stop_date"]),
    #             ethambutol_dose_amount=record["ethambutol_dose_amount"],
    #             ethambutol_frequency_number=record["ethambutol_frequency_number"],
    #             ethambutol_route=record["ethambutol_route"],
    #             ethambutol_batch_no=record["ethambutol_batch_no"],
    #             ethambutol_manufacturer=record["ethambutol_manufacturer"],
    #             # Rechallenge/Dechallenge
    #             rechallenge=RechallengeEnum(record["rechallenge"]),
    #             dechallenge=DechallengeEnum(record["dechallenge"]),
    #             # Grading of Reaction/Event
    #             severity=SeverityEnum(record["severity"]),
    #             is_serious=IsSeriousEnum(record["is_serious"]),
    #             criteria_for_seriousness=CriteriaForSeriousnessEnum(
    #                 record["criteria_for_seriousness"]
    #             ),
    #             action_taken=ActionTakenEnum(record["action_taken"]),
    #             outcome=OutcomeEnum(record["outcome"]),
    #             created_at=datetime.datetime.strptime(
    #                 record["created_at"], "%Y-%m-%d"
    #             ).date(),
    #             # Relationships
    #             user_id=user_a_id,
    #         )
    #         adr_entries.append(adr_entry)

    #     session.add_all(adr_entries)
    #     session.commit()  # This assigns IDs via flush
    #     for adr_entry in adr_entries:
    #         session.refresh(adr_entry)

    #     logging.info("ADR inserted successfully.")
    #     # Now that adr_entries have IDs, link them to causality entries
    #     for adr_entry, record in zip(
    #         adr_entries, new_data_df.to_dict(orient="records")
    #     ):
    #         _, ordinal_encoder = get_encoders(ENCODERS_PATH)

    #         minmax_scaler = get_scalers(SCALERS_PATH)

    #         # Load and preprocess new data
    #         adr_data_df = pd.DataFrame([record])

    #         column_metadata = get_column_metadata(METADATA_PATH)

    #         final_input_df = input_to_prediction_format(
    #             input_df=adr_data_df,
    #             column_metadata=column_metadata,
    #             scalers_path=SCALERS_PATH,
    #             encoders_path=ENCODERS_PATH,
    #         )

    #         # Predict using the ML model
    #         prediction = ml_model.predict(final_input_df)

    #         decoded_prediction = ordinal_encoder.inverse_transform(
    #             prediction.reshape(-1, 1)
    #         )[0][0]

    #         logging.info("Generation SHAP value...")
    #         shap_values = app.state.explainer(final_input_df)

    #         broken_down_shap_values = get_shap_values(shap_values)

    #         base_values = broken_down_shap_values["base_values"]
    #         shap_values_matrix = broken_down_shap_values["shap_values_matrix"]
    #         shap_values_sum_per_class = broken_down_shap_values[
    #             "shap_values_sum_per_class"
    #         ]
    #         shap_values_and_base_values_sum_per_class = broken_down_shap_values[
    #             "shap_values_and_base_values_sum_per_class"
    #         ]

    #         feature_names = final_input_df.columns.tolist()
    #         feature_values = final_input_df.iloc[0].tolist()

    #         # Add causality assessment level
    #         causality_entry = CausalityAssessmentLevelModel(
    #             adr_id=adr_entry.id,
    #             causality_assessment_level_value=CausalityAssessmentLevelEnum(
    #                 decoded_prediction
    #             ),
    #             base_values=base_values,
    #             shap_values_matrix=shap_values_matrix,
    #             shap_values_sum_per_class=shap_values_sum_per_class,
    #             shap_values_and_base_values_sum_per_class=shap_values_and_base_values_sum_per_class,
    #             feature_names=feature_names,
    #             feature_values=format_feature_values(
    #                 feature_values=feature_values, scalers_path=SCALERS_PATH
    #             ),
    #         )

    #         causality_entries.append(causality_entry)

    #     session.add_all(causality_entries)
    #     session.commit()

    #     logging.info("Causality Assessment inserted successfully.")
    # else:
    #     logging.info("ADR and Causality data already exists. Skipping CSV insertion.")

    # # Add reviews
    # review_count = session.query(ReviewModel).count()

    # if review_count == 0:
    #     # causality_entries = session.query(CausalityAssessmentLevelModel).limit(20).all()

    #     causality_entries = session.query(CausalityAssessmentLevelModel).all()
    #     users = session.query(UserModel).all()
    #     user_ids = [u.id for u in users]

    #     for causality_entry in causality_entries:
    #         # Ensure 20 unique users per causality assessment
    #         # selected_user_ids = random.sample(user_ids, min(20, len(user_ids)))
    #         selected_user_ids = user_ids

    #         for user_id in selected_user_ids:
    #             approved = random.choices(
    #                 population=[
    #                     True,
    #                     False,
    #                 ],
    #                 weights=[0.65, 0.35],
    #                 k=1,
    #             )[0]
    #             proposed_level = (
    #                 random.choice(list(CausalityAssessmentLevelEnum))
    #                 if not approved
    #                 else None
    #             )
    #             reason = (
    #                 random.choice(
    #                     [
    #                         "Sufficient evidence provided.",
    #                         "Missing key symptom analysis.",
    #                         "Reviewed and agreed.",
    #                         "Contradicts known patterns.",
    #                         "Needs expert second opinion.",
    #                         "",
    #                     ]
    #                 )
    #                 if not approved
    #                 else None
    #             )

    #             review = ReviewModel(
    #                 causality_assessment_level_id=causality_entry.id,
    #                 user_id=user_id,
    #                 approved=approved,
    #                 proposed_causality_level=proposed_level,
    #                 reason=reason,
    #             )
    #             session.add(review)

    #     session.commit()
    #     logging.info("Reviews inserted.")
    # else:
    #     logging.info("Review data already inserted")

    #     # Add SMS messages for each ADR
    # sms_message_count = session.query(SMSMessageModel).count()

    # # if sms_message_count == 0:
    # #     sms_messages = []
    # #     for adr in session.query(ADRModel).all():
    # #         for sms_type in SMSMessageTypeEnum:
    # #             number_of_messages = random.randint(0, 5)

    # #             if (
    # #                 sms_type == SMSMessageTypeEnum.individual_alert
    # #                 and number_of_messages == 0
    # #             ):
    # #                 print(f"{adr.patient_name} - {sms_type} - {number_of_messages}")

    # #             for _ in range(number_of_messages):
    # #                 sms_message = SMSMessageModel(
    # #                     message_id=f"ATXid_{uuid4()}",
    # #                     sms_type=sms_type,
    # #                     number="+254777529295",
    # #                     content=f"{adr.medical_institution.name} - {sms_type.value} - {adr.patient_name}",
    # #                     cost="KES 0.8000",
    # #                     status="Success",
    # #                     status_code=100,
    # #                     adr_id=adr.id,
    # #                 )
    # #                 sms_messages.append(sms_message)

    # #     session.add_all(sms_messages)
    # #     session.commit()
    # #     logging.info("SMS messages inserted successfully.")
    # # else:
    # #     logging.info("SMS messages already successfully.")
    # if sms_message_count == 0:
    #     sms_messages = []

    #     # Get all causality assessments that are CERTAIN
    #     certain_assessments = (
    #         session.query(CausalityAssessmentLevelModel)
    #         .filter(
    #             CausalityAssessmentLevelModel.causality_assessment_level_value
    #             == CausalityAssessmentLevelEnum.certain
    #         )
    #         .all()
    #     )

    #     for cal in certain_assessments:
    #         adr = session.query(ADRModel).filter(ADRModel.id == cal.adr_id).first()
    #         reviews = (
    #             session.query(ReviewModel)
    #             .filter(ReviewModel.causality_assessment_level_id == cal.id)
    #             .all()
    #         )

    #         if not reviews:
    #             continue

    #         approvals = sum(1 for r in reviews if r.approved)
    #         denials = len(reviews) - approvals

    #         if approvals > denials:
    #             # Add a random number of messages
    #             for _ in range(random.randint(0, 3)):
    #                 sms_message = SMSMessageModel(
    #                     message_id=f"ATXid_{uuid4()}",
    #                     sms_type=SMSMessageTypeEnum.individual_alert,
    #                     number="+254777529295",
    #                     content=f"{adr.medical_institution.name} - individual alert - {adr.patient_name}",
    #                     cost="KES 0.8000",
    #                     status="Success",
    #                     status_code=100,
    #                     adr_id=adr.id,
    #                 )
    #                 sms_messages.append(sms_message)
    #                 logging.info(
    #                     f"✅ SMS alert created for ADR {adr.id} ({adr.patient_name})"
    #                 )

    #     if sms_messages:
    #         session.add_all(sms_messages)
    #         session.commit()
    #         logging.info("Filtered SMS messages inserted successfully.")
    #     else:
    #         logging.info("No ADRs met criteria for SMS message creation.")
    # else:
    #     logging.info("SMS messages already exist. Skipping creation.")

    session.close()

    yield

    # # Delete the SQLite database after shutdown
    # if os.path.exists(DB_PATH):
    #     try:
    #         os.remove(DB_PATH)
    #         logging.info("Database deleted successfully.")
    #     except Exception as e:
    #         logging.error(f"Error deleting database: {e}")

    # # Delete the SQLite database after shutdown
    # for filename in os.listdir(ARTIFACTS_DIR):
    #     file_path = os.path.join(ARTIFACTS_DIR, filename)
    #     if filename != "__init__.py":
    #         try:
    #             if os.path.isfile(file_path) or os.path.islink(file_path):
    #                 os.unlink(file_path)  # delete file or symlink
    #             elif os.path.isdir(file_path):
    #                 shutil.rmtree(file_path)  # delete folder
    #         except Exception as e:
    #             logging.error(f"Error deleting {file_path}: {e}")
