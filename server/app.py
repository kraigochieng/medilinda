import calendar
import datetime
import json
import logging
import math
import os
import random
import shutil
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import List, Tuple
from uuid import uuid4

import africastalking
import boto3
import joblib
import jwt
import mlflow
import numpy as np
import pandas as pd
import shap
from auth import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from basemodels import (
    ActionTakenEnum,
    AdditionalInfoPostRequest,
    ADRGetResponse,
    ADRPostRequest,
    ADRReviewCreateRequest,
    ADRReviewGetResponse,
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelGetResponse,
    CriteriaForSeriousnessEnum,
    DechallengeEnum,
    GenderEnum,
    IndividualAlertPostRequest,
    IsSeriousEnum,
    KnownAllergyEnum,
    MedicalInstitutionGetResponse,
    MedicalInstitutionPostRequest,
    MedicalInstitutionTelephoneGetResponse,
    MedicalInstitutionTelephonePostRequest,
    MultipleMedicalInstitutionTelephonePostRequest,
    OutcomeEnum,
    PregnancyStatusEnum,
    RechallengeEnum,
    ReviewGetResponse,
    SeverityEnum,
    SMSMessageGetResponse,
    SMSMessageTypeEnum,
    Token,
    UnclassifiablePostRequest,
    UserDetailsBaseModel,
    UserGetResponse,
    UserSignupBaseModel,
)
from config import settings
from dependencies import get_db
from engines import engine
from fastapi import Depends, FastAPI, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate
from mlflow.tracking import MlflowClient
from models import (
    ADRModel,
    Base,
    CausalityAssessmentLevelModel,
    MedicalInstitutionModel,
    MedicalInstitutionTelephoneModel,
    ReviewModel,
    SMSMessageModel,
    UserModel,
)
from shap import Explainer, Explanation, KernelExplainer
from sklearn.base import BaseEstimator
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sqlalchemy import case, desc, func, text
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session, joinedload, load_only
from typing_extensions import Annotated, Dict

DB_PATH = "db.sqlite"
ADR_CSV_PATH = "data.csv"  # Path to the CSV file
USERS_CSV_PATH = "users.csv"
REVIEWS_CSV_PATH = "reviews.csv"
ARTIFACTS_DIR = f"./{settings.mlflow_model_artifacts_path}"
MEDICAL_INSTITUTION_CSV_PATH = "medical_institutions.csv"

logging.basicConfig(level=logging.INFO)
logging.getLogger("shap").setLevel(logging.WARNING)

explainer: KernelExplainer = None


def safe_date_parse(value):
    try:
        if pd.isna(value):
            return None
        if isinstance(value, datetime.datetime):
            return value.date()
        return pd.to_datetime(value).date()
    except Exception:
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ML Model Artifacts
    if not os.path.exists(ARTIFACTS_DIR):
        try:
            logging.info("Downloading ML Model Artifacts")

            # Tracking URI
            mlflow.set_tracking_uri(
                f"http://{settings.mlflow_tracking_server_host}:{settings.mlflow_tracking_server_port}"
            )

            # Credentials
            # Set MinIO Credentials
            os.environ["AWS_ACCESS_KEY_ID"] = settings.minio_access_key
            os.environ["AWS_SECRET_ACCESS_KEY"] = settings.minio_secret_access_key
            os.environ["AWS_DEFAULT_REGION"] = settings.aws_region

            os.environ["MLFLOW_S3_ENDPOINT_URL"] = (
                f"http://{settings.minio_host}:{settings.minio_api_port}"
            )

            # Test if credentials are set correctly
            boto3.client(
                "s3",
                endpoint_url=os.getenv("MLFLOW_S3_ENDPOINT_URL"),
            )

            mlflow_client = MlflowClient()

            ml_model_version = mlflow_client.get_model_version_by_alias(
                settings.mlflow_model_name, settings.mlflow_model_alias
            )

            ml_model_run_id = ml_model_version.run_id

            logging.info(
                f"✅ Retrieved model version {ml_model_version.version} (run_id: {ml_model_run_id})"
            )

            # 2️⃣ List available artifacts
            artifacts = mlflow_client.list_artifacts(ml_model_run_id)
            if not artifacts:
                logging.warning("No artifacts found for this model.")
            else:
                logging.info(
                    f"Available artifacts: {[artifact.path for artifact in artifacts]}"
                )

            # 3️⃣ Ensure local artifacts directory exists
            os.makedirs(ARTIFACTS_DIR, exist_ok=True)
            mlflow_client.download_artifacts(
                ml_model_run_id,
                "",
                dst_path=ARTIFACTS_DIR,
            )
            logging.info("Downloaded ML Model Artifacts")

        except Exception as e:
            logging.error(f"Error during ML model retrieval: {e}")

    else:
        logging.info("Skipping artifact download")

    # Explain with SHAP
    logging.info("SHAP Explainer Setup Started...")

    ml_model = get_ml_model()

    # Load and preprocess new data
    new_data_df = pd.read_csv("data.csv")

    final_input_df = input_to_prediction_format(new_data_df)

    global explainer

    explainer = shap.KernelExplainer(
        ml_model.predict_proba, shap.kmeans(final_input_df, 10)
    )

    logging.info("SHAP Explainer Setup Finished...")

    # Create tables once before the app starts
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logging.error(f"Error creating tables: {e}")

    session = Session(bind=engine)

    # Add institutions
    institution_count = session.query(MedicalInstitutionModel).count()

    if institution_count == 0 and os.path.exists(MEDICAL_INSTITUTION_CSV_PATH):
        institution_df = pd.read_csv(MEDICAL_INSTITUTION_CSV_PATH)

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

    # Add ADRs using current user
    adr_count = session.query(ADRModel).count()

    if adr_count == 0 and os.path.exists(ADR_CSV_PATH):
        adr_df = pd.read_csv(ADR_CSV_PATH)

        adr_entries = []
        causality_entries = []

        facility_ids = session.query(MedicalInstitutionModel.id).limit(20).all()
        facility_ids = [id_tuple[0] for id_tuple in facility_ids]

        for record in adr_df.to_dict(orient="records"):
            adr_entry = ADRModel(
                # Institution Details
                medical_institution_id=random.choice(facility_ids),
                # Personal Details
                patient_name=record["patient_name"],
                inpatient_or_outpatient_number=record["inpatient_or_outpatient_number"],
                # patient_date_of_birth=datetime.datetime.strptime(
                #     record["patient_date_of_birth"], "%Y-%m-%d"
                # ).date()
                # if pd.notna(record["patient_date_of_birth"])
                # else None,
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
                # Medicine Columns
                rifampicin_suspected=record["rifampicin_suspected"],
                rifampicin_start_date=safe_date_parse(record["rifampicin_start_date"]),
                rifampicin_stop_date=safe_date_parse(record["rifampicin_stop_date"]),
                rifampicin_dose_amount=record["rifampicin_dose_amount"],
                rifampicin_frequency_number=record["rifampicin_frequency_number"],
                rifampicin_route=record["rifampicin_route"],
                rifampicin_batch_no=record["rifampicin_batch_no"],
                rifampicin_manufacturer=record["rifampicin_manufacturer"],
                isoniazid_suspected=record["isoniazid_suspected"],
                isoniazid_start_date=safe_date_parse(record["isoniazid_start_date"]),
                isoniazid_stop_date=safe_date_parse(record["isoniazid_stop_date"]),
                isoniazid_dose_amount=record["isoniazid_dose_amount"],
                isoniazid_frequency_number=record["isoniazid_frequency_number"],
                isoniazid_route=record["isoniazid_route"],
                isoniazid_batch_no=record["isoniazid_batch_no"],
                isoniazid_manufacturer=record["isoniazid_manufacturer"],
                pyrazinamide_suspected=record["pyrazinamide_suspected"],
                pyrazinamide_start_date=safe_date_parse(
                    record["pyrazinamide_start_date"]
                ),
                pyrazinamide_stop_date=safe_date_parse(
                    record["pyrazinamide_stop_date"]
                ),
                pyrazinamide_dose_amount=record["pyrazinamide_dose_amount"],
                pyrazinamide_frequency_number=record["pyrazinamide_frequency_number"],
                pyrazinamide_route=record["pyrazinamide_route"],
                pyrazinamide_batch_no=record["pyrazinamide_batch_no"],
                pyrazinamide_manufacturer=record["pyrazinamide_manufacturer"],
                ethambutol_suspected=record["ethambutol_suspected"],
                ethambutol_start_date=safe_date_parse(record["ethambutol_start_date"]),
                ethambutol_stop_date=safe_date_parse(record["ethambutol_stop_date"]),
                ethambutol_dose_amount=record["ethambutol_dose_amount"],
                ethambutol_frequency_number=record["ethambutol_frequency_number"],
                ethambutol_route=record["ethambutol_route"],
                ethambutol_batch_no=record["ethambutol_batch_no"],
                ethambutol_manufacturer=record["ethambutol_manufacturer"],
                # Rechallenge/Dechallenge
                rechallenge=RechallengeEnum(record["rechallenge"]),
                dechallenge=DechallengeEnum(record["dechallenge"]),
                # Grading of Reaction/Event
                severity=SeverityEnum(record["severity"]),
                is_serious=IsSeriousEnum(record["is_serious"]),
                criteria_for_seriousness=CriteriaForSeriousnessEnum(
                    record["criteria_for_seriousness"]
                ),
                action_taken=ActionTakenEnum(record["action_taken"]),
                outcome=OutcomeEnum(record["outcome"]),
                created_at=datetime.datetime.strptime(
                    record["created_at"], "%Y-%m-%d"
                ).date(),
                # Relationships
                user_id=user_a_id,
            )
            adr_entries.append(adr_entry)

        session.add_all(adr_entries)
        session.commit()  # This assigns IDs via flush
        for adr_entry in adr_entries:
            session.refresh(adr_entry)

        logging.info("ADR inserted successfully.")
        # Now that adr_entries have IDs, link them to causality entries
        for adr_entry, record in zip(
            adr_entries, new_data_df.to_dict(orient="records")
        ):
            ml_model = get_ml_model()

            _, ordinal_encoder = get_encoders()

            minmax_scaler = get_scalers()

            # Load and preprocess new data
            adr_data_df = pd.DataFrame([record])

            final_input_df = input_to_prediction_format(adr_data_df)

            # Predict using the ML model
            prediction = ml_model.predict(final_input_df)

            decoded_prediction = ordinal_encoder.inverse_transform(
                prediction.reshape(-1, 1)
            )[0][0]

            logging.info("Generation SHAP value...")
            shap_values = explainer(final_input_df)

            broken_down_shap_values = get_shap_values(shap_values)

            base_values = broken_down_shap_values["base_values"]
            shap_values_matrix = broken_down_shap_values["shap_values_matrix"]
            shap_values_sum_per_class = broken_down_shap_values[
                "shap_values_sum_per_class"
            ]
            shap_values_and_base_values_sum_per_class = broken_down_shap_values[
                "shap_values_and_base_values_sum_per_class"
            ]

            feature_names = final_input_df.columns.tolist()
            feature_values = final_input_df.iloc[0].tolist()

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
                feature_names=feature_names,
                feature_values=format_feature_values(feature_values),
            )

            causality_entries.append(causality_entry)

        session.add_all(causality_entries)
        session.commit()

        logging.info("Causality Assessment inserted successfully.")
    else:
        logging.info("ADR and Causality data already exists. Skipping CSV insertion.")

    # Add reviews
    review_count = session.query(ReviewModel).count()

    if review_count == 0:
        # causality_entries = session.query(CausalityAssessmentLevelModel).limit(20).all()

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
    else:
        logging.info("Review data already inserted")

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
    if sms_message_count == 0:
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
    else:
        logging.info("SMS messages already exist. Skipping creation.")

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
    # if os.path.exists(ARTIFACTS_DIR):
    #     try:
    #         shutil.rmtree(ARTIFACTS_DIR)
    #         logging.info("Artifacts deleted successfully.")
    #     except Exception as e:
    #         logging.error(f"Error deleting artifacts: {e}")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_pagination(app)


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    # lhreje
    return "test"


@app.post("/api/v1/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserSignupBaseModel, db: Session = Depends(get_db)):
    existing_user = (
        db.query(UserModel).filter(UserModel.username == user.username).first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    new_user = UserModel(
        username=user.username,
        password=get_password_hash(user.username),
        first_name=user.first_name,
        last_name=user.last_name,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    user_basemodel = UserDetailsBaseModel(
        id=new_user.id,
        username=new_user.username,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
    )
    return JSONResponse(
        content=jsonable_encoder(user_basemodel), status_code=status.HTTP_200_OK
    )


@app.post("/api/v1/token", status_code=status.HTTP_201_CREATED)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    existing_user = (
        db.query(UserModel).filter(UserModel.username == form_data.username).first()
    )

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, existing_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = datetime.timedelta(
        minutes=settings.server_access_token_expire_minutes
    )

    access_token = create_access_token(
        data={"sub": existing_user.username}, expires_delta=access_token_expires
    )

    refresh_token_expires = datetime.timedelta(
        days=settings.server_refresh_token_expire_days
    )

    refresh_token = create_refresh_token(
        data={"sub": existing_user.username}, expires_delta=refresh_token_expires
    )

    return JSONResponse(
        content=jsonable_encoder(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
        ),
        status_code=status.HTTP_200_OK,
    )


@app.post("/api/v1/token/refresh", status_code=status.HTTP_201_CREATED)
async def refresh_access_token(refresh_token: str):
    try:
        payload = jwt.decode(
            refresh_token,
            settings.server_refresh_secret_key,
            algorithms=[settings.server_refresh_algorithm],
        )
        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        # Generate new access token
        new_access_token = create_access_token(
            data={"sub": username},
            expires_delta=datetime.timedelta(
                minutes=settings.server_access_token_expire_minutes
            ),
        )
        return {"access_token": new_access_token, "token_type": "bearer"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )


@app.get("/api/v1/users/me", status_code=status.HTTP_201_CREATED)
async def read_users_me(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    db_user = (
        db.query(UserModel)
        .options(
            load_only(
                UserModel.id,
                UserModel.username,
                UserModel.first_name,
                UserModel.last_name,
            )
        )
        .filter(UserModel.username == current_user.username)
        .first()
    )

    return db_user


@app.get(
    "/api/v1/adr", response_model=Page[ADRGetResponse], status_code=status.HTTP_200_OK
)
def get_adrs(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    query: str = Query("", description="Search query(optional)"),
    db: Session = Depends(get_db),
):
    if query:
        content = db.query(ADRModel).filter(
            ADRModel.patient_name.ilike(f"%{query}%")
            | ADRModel.patient_address.ilike(f"%{query}%")
            | ADRModel.inpatient_or_outpatient_number.ilike(f"%{query}%")
            | ADRModel.ward_or_clinic.ilike(f"%{query}%")
        )

    else:
        content = db.query(ADRModel)

    content = content.order_by(desc(ADRModel.created_at))

    return paginate(content)


@app.get(
    "/api/v1/adrs_with_causality_and_review_count",
    response_model=Page[dict],
    status_code=status.HTTP_200_OK,
)
def get_adrs_with_causality_and_review_count(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    query: str = Query("", description="Search query (optional)"),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * size
    search_term = f"%{query}%" if query else None

    # Total count query
    total_sql = text("""
        SELECT COUNT(*) FROM adr
        WHERE (:query IS NULL OR LOWER(patient_name) LIKE LOWER(:query));
    """)
    total_result = db.execute(total_sql, {"query": search_term})
    total = total_result.scalar_one()
    pages = math.ceil(total / size) if total > 0 else 1

    # Main query using ROW_NUMBER and CTE for SQLite compatibility
    main_sql = text("""
        WITH ranked_causality AS (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY adr_id ORDER BY created_at ASC) AS rn
            FROM causality_assessment_level
        )
        SELECT
            a.id AS adr_id,
            a.patient_name,
            u.first_name || ' ' || u.last_name AS created_by,
            a.created_at,
            cal.causality_assessment_level_value,
            COUNT(CASE WHEN r.approved = 1 THEN 1 END) AS approved_reviews,
            COUNT(CASE WHEN r.approved = 0 THEN 1 END) AS unapproved_reviews
        FROM adr a
        JOIN "user" u ON a.user_id = u.id
        LEFT JOIN ranked_causality cal ON cal.adr_id = a.id AND cal.rn = 1
        LEFT JOIN review r ON r.causality_assessment_level_id = cal.id
        WHERE (:query IS NULL OR LOWER(a.patient_name) LIKE LOWER(:query))
        GROUP BY a.id, a.patient_name, u.first_name, u.last_name, cal.causality_assessment_level_value
        ORDER BY a.created_at DESC
        LIMIT :limit OFFSET :offset;
    """)

    result = db.execute(
        main_sql,
        {
            "query": search_term,
            "limit": size,
            "offset": offset,
        },
    )

    items = [dict(row._mapping) for row in result.fetchall()]

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
    }


@app.get("/api/v1/adr/{adr_id}", status_code=status.HTTP_200_OK)
def get_adr_by_id(
    adr_id: str = Path(..., description="ID of ADR to read"),
    db: Session = Depends(get_db),
):
    adr = db.query(ADRModel).filter(ADRModel.id == adr_id).first()

    if not adr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="ADR record not found"
        )
    return JSONResponse(content=jsonable_encoder(adr), status_code=status.HTTP_200_OK)


@app.post("/api/v1/adr", status_code=status.HTTP_201_CREATED)
async def post_adr(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    adr: ADRPostRequest,
    db: Session = Depends(get_db),
):
    # Get user id
    db_user = (
        db.query(UserModel).filter(UserModel.username == current_user.username).first()
    )

    adr_model = ADRModel(
        **adr.model_dump(),
        user_id=db_user.id,
    )

    db.add(adr_model)
    db.commit()
    db.refresh(adr_model)

    # Check if ADR has the appropriate fields present.
    # If not, set the causality level to unclassified and just return immediately
    if (
        adr.rifampicin_suspected is None
        and adr.isoniazid_suspected is None
        and adr.pyrazinamide_suspected is None
        and adr.ethambutol_suspected is None
    ) or (
        adr.rechallenge is RechallengeEnum.unknown
        and adr.dechallenge is DechallengeEnum.unknown
    ):
        casuality_assessment_level_model = CausalityAssessmentLevelModel(
            adr_id=adr_model.id,
            causality_assessment_level_value=CausalityAssessmentLevelEnum.unclassified,
            base_values=None,
            shap_values_matrix=None,
            shap_values_sum_per_class=None,
            shap_values_and_base_values_sum_per_class=None,
            feature_names=None,
            feature_values=None,
        )

        db.add(casuality_assessment_level_model)
        db.commit()
        db.refresh(casuality_assessment_level_model)

        # To load the causality assessment levels
        content = db.query(ADRModel).filter(ADRModel.id == adr_model.id).first()

        return JSONResponse(
            content=jsonable_encoder(content),
            status_code=status.HTTP_201_CREATED,
        )

    # Get ML Model
    ml_model = get_ml_model()

    # Get encoders
    _, ordinal_encoder = get_encoders()

    # Save data as temp df
    temp_df = pd.DataFrame([adr.model_dump()])

    # Extract prediction input
    prediction_input = input_to_prediction_format(temp_df)

    # Predict using the ML model
    prediction = ml_model.predict(prediction_input)

    decoded_prediction = ordinal_encoder.inverse_transform(prediction.reshape(-1, 1))[
        0
    ][0]

    global explainer

    shap_values = explainer(prediction_input)

    broken_down_shap_values = get_shap_values(shap_values)

    base_values = broken_down_shap_values["base_values"]
    shap_values_matrix = broken_down_shap_values["shap_values_matrix"]
    shap_values_sum_per_class = broken_down_shap_values["shap_values_sum_per_class"]
    shap_values_and_base_values_sum_per_class = broken_down_shap_values[
        "shap_values_and_base_values_sum_per_class"
    ]

    feature_names = prediction_input.columns.tolist()
    feature_values = prediction_input.iloc[0].tolist()

    # Add causality assessment level
    casuality_assessment_level_model = CausalityAssessmentLevelModel(
        adr_id=adr_model.id,
        causality_assessment_level_value=CausalityAssessmentLevelEnum(
            decoded_prediction
        ),
        base_values=base_values,
        shap_values_matrix=shap_values_matrix,
        shap_values_sum_per_class=shap_values_sum_per_class,
        shap_values_and_base_values_sum_per_class=shap_values_and_base_values_sum_per_class,
        feature_names=feature_names,
        feature_values=format_feature_values(feature_values),
    )

    db.add(casuality_assessment_level_model)
    db.commit()
    db.refresh(casuality_assessment_level_model)

    # To load the causality assessment levels
    content = db.query(ADRModel).filter(ADRModel.id == adr_model.id).first()

    return JSONResponse(
        content=jsonable_encoder(content),
        status_code=status.HTTP_201_CREATED,
    )


@app.put("/api/v1/adr/{adr_id}", status_code=status.HTTP_200_OK)
async def update_adr(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    updated_adr: ADRPostRequest,
    adr_id: str = Path(..., description="ID of the ADR record to update"),
    db: Session = Depends(get_db),
):
    # Get existing ADR record
    adr_model = db.query(ADRModel).filter(ADRModel.id == adr_id).first()
    if not adr_model:
        raise HTTPException(status_code=404, detail="ADR record not found")

    # Update ADR fields
    for key, value in updated_adr.model_dump().items():
        setattr(adr_model, key, value)

    db.commit()
    db.refresh(adr_model)

    if (
        adr_model.rifampicin_suspected is None
        and adr_model.isoniazid_suspected is None
        and adr_model.pyrazinamide_suspected is None
        and adr_model.ethambutol_suspected is None
    ) or (
        adr_model.rechallenge is RechallengeEnum.unknown
        and adr_model.dechallenge is DechallengeEnum.unknown
    ):
        casuality_assessment_level_model = CausalityAssessmentLevelModel(
            adr_id=adr_model.id,
            causality_assessment_level_value=CausalityAssessmentLevelEnum.unclassified,
            base_values=None,
            shap_values_matrix=None,
            shap_values_sum_per_class=None,
            shap_values_and_base_values_sum_per_class=None,
            feature_names=None,
            feature_values=None,
        )

        db.add(casuality_assessment_level_model)
        db.commit()
        db.refresh(casuality_assessment_level_model)

        # To load the causality assessment levels
        content = db.query(ADRModel).filter(ADRModel.id == adr_model.id).first()

        return JSONResponse(
            content=jsonable_encoder(content),
            status_code=status.HTTP_201_CREATED,
        )

    # Step 3: Load ML model and encoders
    ml_model = get_ml_model()

    _, ordinal_encoder = get_encoders()

    temp_df = pd.DataFrame([updated_adr.model_dump()])

    prediction_input = input_to_prediction_format(temp_df)

    # Predict and decode
    prediction = ml_model.predict(prediction_input)
    decoded_prediction = ordinal_encoder.inverse_transform(prediction.reshape(-1, 1))[
        0
    ][0]

    global explainer

    shap_values = explainer(prediction_input)

    broken_down_shap_values = get_shap_values(shap_values)

    base_values = broken_down_shap_values["base_values"]
    shap_values_matrix = broken_down_shap_values["shap_values_matrix"]
    shap_values_sum_per_class = broken_down_shap_values["shap_values_sum_per_class"]
    shap_values_and_base_values_sum_per_class = broken_down_shap_values[
        "shap_values_and_base_values_sum_per_class"
    ]

    feature_names = prediction_input.columns.tolist()
    feature_values = prediction_input.iloc[0].tolist()

    # Update causality assessment model
    causality_record = (
        db.query(CausalityAssessmentLevelModel)
        .filter(CausalityAssessmentLevelModel.adr_id == adr_model.id)
        .first()
    )

    if causality_record:
        causality_record.causality_assessment_level_value = (
            CausalityAssessmentLevelEnum(decoded_prediction)
        )
        causality_record.base_values = base_values
        causality_record.shap_values_matrix = shap_values_matrix
        causality_record.shap_values_sum_per_class = shap_values_sum_per_class
        causality_record.shap_values_and_base_values_sum_per_class = (
            shap_values_and_base_values_sum_per_class
        )
        causality_record.feature_names = feature_names
        causality_record.feature_values = format_feature_values(feature_values)

        db.commit()
        db.refresh(causality_record)
    else:
        new_causality = CausalityAssessmentLevelModel(
            adr_id=adr_model.id,
            causality_assessment_level_value=CausalityAssessmentLevelEnum(
                decoded_prediction
            ),
            base_values=base_values,
            shap_values_matrix=shap_values_matrix,
            shap_values_sum_per_class=shap_values_sum_per_class,
            shap_values_and_base_values_sum_per_class=shap_values_and_base_values_sum_per_class,
            feature_names=feature_names,
            feature_values=format_feature_values(feature_values),
        )
        db.add(new_causality)
        db.commit()
        db.refresh(new_causality)

    # Step 8: Return updated record with causality details
    content = db.query(ADRModel).filter(ADRModel.id == adr_model.id).first()

    return JSONResponse(
        content=jsonable_encoder(content),
        status_code=status.HTTP_200_OK,
    )


@app.delete("/api/v1/adr/{adr_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_adr_by_id(
    adr_id: str = Path(..., description="ID of ADR to delete"),
    db: Session = Depends(get_db),
):
    adr = db.query(ADRModel).filter(ADRModel.id == adr_id).first()

    if not adr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="ADR record not found"
        )

    db.delete(adr)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/api/v1/causality_assessment_level/{causality_assessment_level_id}",
    status_code=status.HTTP_200_OK,
)
async def get_causality_assessment_level_by_id(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    causality_assessment_level_id: str = Path(
        ..., description="ID of Causality Assessment to read"
    ),
    db: Session = Depends(get_db),
):
    causality_assessment_level = (
        db.query(CausalityAssessmentLevelModel)
        .filter(CausalityAssessmentLevelModel.id == causality_assessment_level_id)
        .first()
    )

    if not causality_assessment_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Causality Assessment Level record not found",
        )

    approved_count = sum(1 for r in causality_assessment_level.reviews if r.approved)
    not_approved_count = sum(
        1 for r in causality_assessment_level.reviews if not r.approved
    )

    content = {
        **jsonable_encoder(causality_assessment_level),
        "approved_count": approved_count,
        "not_approved_count": not_approved_count,
    }
    return JSONResponse(
        content=content,
        status_code=status.HTTP_200_OK,
    )


@app.get(
    "/api/v1/specific_adr/{adr_id}/causality_assessment_level",
    status_code=status.HTTP_200_OK,
)
async def get_causality_assessment_level_by_adr_id(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    adr_id: str = Path(..., description="ID of Causality Assessment to read"),
    db: Session = Depends(get_db),
):
    causality_assessment_level = (
        db.query(CausalityAssessmentLevelModel)
        .filter(CausalityAssessmentLevelModel.adr_id == adr_id)
        .first()
    )

    if not causality_assessment_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Causality Assessment Level record not found",
        )

    approved_count = sum(1 for r in causality_assessment_level.reviews if r.approved)
    not_approved_count = sum(
        1 for r in causality_assessment_level.reviews if not r.approved
    )

    content = {
        **jsonable_encoder(causality_assessment_level),
        "approved_count": approved_count,
        "not_approved_count": not_approved_count,
    }
    return JSONResponse(
        content=content,
        status_code=status.HTTP_200_OK,
    )


@app.get(
    "/api/v1/adr/{adr_id}/causality_assessment_level",
    response_model=Page[CausalityAssessmentLevelGetResponse],
    status_code=status.HTTP_200_OK,
)
def get_causality_assessment_levels_for_adr(
    adr_id: str = Path(..., description="ID of ADR to read"),
    db: Session = Depends(get_db),
):
    adr = db.query(ADRModel).filter(ADRModel.id == adr_id).first()

    if not adr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="ADR record not found"
        )

    content = (
        db.query(CausalityAssessmentLevelModel)
        .filter(CausalityAssessmentLevelModel.adr_id == adr_id)
        .order_by(desc(CausalityAssessmentLevelModel.created_at))
    )

    return paginate(content)


@app.put(
    "/api/v1/causality_assessment_level/{causality_assessment_level_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def update_causality_assessment_level_by_id(
    causality_assessment_level_id: str = Path(..., description="ID of CAL to update"),
    db: Session = Depends(get_db),
):
    cal_model = (
        db.query(ADRModel)
        .filter(CausalityAssessmentLevelModel.id == causality_assessment_level_id)
        .first()
    )

    if not cal_model:
        raise HTTPException(status_code=404, detail="CAL record not found")

    # Update ADR fields
    for key, value in cal_model.model_dump().items():
        setattr(cal_model, key, value)

    db.commit()
    db.refresh()

    content = jsonable_encoder(cal_model)

    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


@app.delete(
    "/api/v1/causality_assessment_level/{causality_assessment_level_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_causality_assessment_level_by_id(
    causality_assessment_level_id: str = Path(..., description="ID of CAL to delete"),
    db: Session = Depends(get_db),
):
    cal = (
        db.query(CausalityAssessmentLevelModel)
        .filter(CausalityAssessmentLevelModel.id == causality_assessment_level_id)
        .first()
    )

    if not cal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="CAL record not found"
        )

    db.delete(cal)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/api/v1/review",
    response_model=Page[ReviewGetResponse],
    status_code=status.HTTP_200_OK,
)
async def get_reviews(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    query: str = Query("", description="Search query(optional)"),
    db: Session = Depends(get_db),
):
    if query:
        content = db.query(ReviewModel).order_by(desc(ReviewModel.created_at))
    else:
        content = db.query(ReviewModel).order_by(desc(ReviewModel.created_at))

    return paginate(content)


@app.get(
    "/api/v1/review/{review_id}",
    response_model=Page[ReviewGetResponse],
    status_code=status.HTTP_200_OK,
)
async def get_reviews_by_id(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    review_id: str = Path(..., description="Review ID"),
    db: Session = Depends(get_db),
):
    review = db.query(ReviewModel).filter(ReviewModel.id == review_id).first()

    if not review:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )
    content = jsonable_encoder(review)

    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


@app.get(
    "/api/v1/review_for_specific_user_and_causality_assessment_level",
    status_code=status.HTTP_200_OK,
)
async def get_review_for_specific_user_and_causality_assessment_level(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    causality_assessment_level_id: str = Query(
        ..., description="ID of Causality Assessment to read"
    ),
    db: Session = Depends(get_db),
):
    db_user = (
        db.query(UserModel).filter(UserModel.username == current_user.username).first()
    )

    review = (
        db.query(ReviewModel)
        .filter(
            ReviewModel.causality_assessment_level_id == causality_assessment_level_id,
            ReviewModel.user_id == db_user.id,
        )
        .first()
    )

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    return review


@app.get(
    "/api/v1/causality_assessment_level/{causality_assessment_level_id}/review",
    response_model=Page[ReviewGetResponse],
    status_code=status.HTTP_200_OK,
)
async def get_reviews_for_causality_assessment_level(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    causality_assessment_level_id: str = Path(
        ..., description="ID of Causality Assessment to read"
    ),
    db: Session = Depends(get_db),
):
    causality_assessment_level = (
        db.query(CausalityAssessmentLevelModel)
        .filter(CausalityAssessmentLevelModel.id == causality_assessment_level_id)
        .first()
    )

    if not causality_assessment_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Causality Assessment Level record not found",
        )

    content = (
        db.query(ReviewModel)
        .options(
            joinedload(ReviewModel.user).load_only(
                UserModel.id,
                UserModel.username,
                UserModel.first_name,
                UserModel.last_name,
            )
        )
        .filter(
            ReviewModel.causality_assessment_level_id == causality_assessment_level_id
        )
        .order_by(desc(ReviewModel.created_at))
    )

    return paginate(content)


@app.post(
    "/api/v1/causality_assessment_level/{causality_assessment_level_id}/review",
    status_code=status.HTTP_201_CREATED,
)
async def post_review(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    review: ADRReviewCreateRequest,
    causality_assessment_level_id: str = Path(
        ..., description="ID of Causality Assessment to read"
    ),
    db: Session = Depends(get_db),
):
    causality_assessment_level = (
        db.query(CausalityAssessmentLevelModel)
        .filter(CausalityAssessmentLevelModel.id == causality_assessment_level_id)
        .first()
    )

    if not causality_assessment_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Causality Level not found"
        )

    db_user = (
        db.query(UserModel).filter(UserModel.username == current_user.username).first()
    )

    review_model = ReviewModel(
        **review.model_dump(),
        user_id=db_user.id,
        causality_assessment_level_id=causality_assessment_level_id,
    )

    db.add(review_model)
    db.commit()
    db.refresh(review_model)
    # content = ADRCreateResponse.model_validate(adr_model)
    return JSONResponse(
        content=jsonable_encoder(review_model),
        status_code=status.HTTP_201_CREATED,
    )


@app.put("/api/v1/review/{review_id}", status_code=status.HTTP_200_OK)
async def update_review_by_id(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    review_update: ADRReviewCreateRequest,
    review_id: str = Path(..., description="ID of review to update"),
    db: Session = Depends(get_db),
):
    # Step 1: Get the existing review
    review = db.query(ReviewModel).filter(ReviewModel.id == review_id).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    # Step 2: Update the fields
    for key, value in review_update.model_dump().items():
        setattr(review, key, value)

    db.commit()
    db.refresh(review)

    return JSONResponse(
        content=jsonable_encoder(review),
        status_code=status.HTTP_200_OK,
    )


@app.delete(
    "/api/v1/review/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_review_by_id(
    review_id: str = Path(..., description="ID of review to delete"),
    db: Session = Depends(get_db),
):
    review = db.query(ReviewModel).filter(ReviewModel.id == review_id).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review record not found"
        )

    db.delete(review)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/v1/adr_monitoring", status_code=status.HTTP_200_OK)
def get_adr_monitoring(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    start: str = Query(...),
    end: str = Query(...),
    db: Session = Depends(get_db),
):
    # Parse date strings
    start_date = datetime.datetime.strptime(start, "%Y-%m-%d").replace(
        tzinfo=datetime.timezone.utc
    )
    # Include the full day by setting end time to 23:59:59.999999
    end_date = (
        datetime.datetime.strptime(end, "%Y-%m-%d").replace(
            tzinfo=datetime.timezone.utc
        )
        + datetime.timedelta(days=1)
        - datetime.timedelta(microseconds=1)
    )

    def query_proportion_data(db: Session, column):
        return (
            db.query(column, func.count(ADRModel.id))
            .filter(ADRModel.created_at >= start_date)
            .filter(ADRModel.created_at <= end_date)
            .group_by(column)
            .all()
        )

    def format_proportion_data(raw_data):
        return {
            "series": [label.value for label, _ in raw_data],
            "data": [count for _, count in raw_data],
        }

    # Gender Proportion
    gender_proportions_data = query_proportion_data(db, ADRModel.patient_gender)
    gender_proportions_content = format_proportion_data(gender_proportions_data)

    # Pregnancy Status Proportion
    pregnancy_status_proportions_data = query_proportion_data(
        db, ADRModel.pregnancy_status
    )
    pregnancy_status_proportions_content = format_proportion_data(
        pregnancy_status_proportions_data
    )

    # Known Allergy Proportion
    known_allergy_proportions_data = query_proportion_data(db, ADRModel.known_allergy)
    known_allergy_proportions_content = format_proportion_data(
        known_allergy_proportions_data
    )

    # Rechallenge Proportion
    rechallenge_proportions_data = query_proportion_data(db, ADRModel.rechallenge)
    rechallenge_proportions_content = format_proportion_data(
        rechallenge_proportions_data
    )

    # Dechallenge Proportion (fixed column name)
    dechallenge_proportions_data = query_proportion_data(db, ADRModel.dechallenge)
    dechallenge_proportions_content = format_proportion_data(
        dechallenge_proportions_data
    )

    # Severity Proportion
    severity_proportions_data = query_proportion_data(db, ADRModel.severity)
    severity_proportions_content = format_proportion_data(severity_proportions_data)

    # Criteria For Seriousness Proportion
    criteria_for_seriousness_proportions_data = query_proportion_data(
        db, ADRModel.criteria_for_seriousness
    )
    criteria_for_seriousness_proportions_content = format_proportion_data(
        criteria_for_seriousness_proportions_data
    )

    # Is Serious Proportion
    is_serious_proportions_data = query_proportion_data(db, ADRModel.is_serious)
    is_serious_proportions_content = format_proportion_data(is_serious_proportions_data)

    # Outcome Proportion
    outcome_proportions_data = query_proportion_data(db, ADRModel.outcome)
    outcome_proportions_content = format_proportion_data(outcome_proportions_data)

    content = {
        "gender_proportions": gender_proportions_content,
        "pregnancy_status_proportions": pregnancy_status_proportions_content,
        "known_allergy_proportions": known_allergy_proportions_content,
        "dechallenge_proportions": dechallenge_proportions_content,
        "rechallenge_proportions": rechallenge_proportions_content,
        "severity_proportions": severity_proportions_content,
        "criteria_for_seriousness_proportions": criteria_for_seriousness_proportions_content,
        "is_serious_proportions": is_serious_proportions_content,
        "outcome_proportions": outcome_proportions_content,
    }

    print(content)

    return JSONResponse(
        content=jsonable_encoder(content),
        status_code=status.HTTP_200_OK,
    )


#  Summary Cards
@app.get("/api/v1/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    return {
        "total_adrs": db.query(func.count(ADRModel.id)).scalar(),
        "total_institutions": db.query(
            func.count(func.distinct(ADRModel.medical_institution_id))
        ).scalar(),
    }


#  Reviewed vs Unreviewed
@app.get("/api/v1/dashboard/reviewed-unreviewed")
def reviewed_vs_unreviewed(db: Session = Depends(get_db)):
    total = db.query(ADRModel.id).count()
    reviewed = (
        db.query(func.count(func.distinct(CausalityAssessmentLevelModel.id)))
        .join(CausalityAssessmentLevelModel.reviews)
        .scalar()
    )
    return {"series": [reviewed, total - reviewed], "data": ["Reviewed", "Unreviewed"]}


#  Causality Distribution
@app.get("/api/v1/dashboard/causality-distribution")
def causality_distribution(db: Session = Depends(get_db)):
    rows = (
        db.query(
            CausalityAssessmentLevelModel.causality_assessment_level_value, func.count()
        )
        .group_by(CausalityAssessmentLevelModel.causality_assessment_level_value)
        .all()
    )
    # return {"series": [r[1] for r in rows], "data": [str(r[0]) for r in rows]}
    counts = {str(r[0]): r[1] for r in rows}

    # Ensure all enum values are included
    all_values = [str(val) for val in CausalityAssessmentLevelEnum]
    series = []
    data = []
    for val in all_values:
        data.append(val)
        series.append(counts.get(val, 0))

    return {"series": series, "data": data}


#  Approval Status
@app.get("/api/v1/dashboard/approval-status")
def approval_status(db: Session = Depends(get_db)):
    sql = text("""
        SELECT status, COUNT(*) as count FROM (
            SELECT
                cal.id AS cal_id,
                SUM(CASE WHEN r.approved = 1 THEN 1 ELSE 0 END) AS approved_count,
                SUM(CASE WHEN r.approved = 0 THEN 1 ELSE 0 END) AS unapproved_count,
                CASE
                    WHEN SUM(CASE WHEN r.approved = 1 THEN 1 ELSE 0 END) >
                         SUM(CASE WHEN r.approved = 0 THEN 1 ELSE 0 END)
                    THEN 'Approved'
                    ELSE 'Unapproved'
                END AS status
            FROM causality_assessment_level cal
            JOIN review r ON cal.id = r.causality_assessment_level_id
            GROUP BY cal.id
        ) AS sub
        GROUP BY status
    """)
    result = db.execute(sql).fetchall()
    return {"series": [r[1] for r in result], "data": [r[0] for r in result]}


#  Categorical Field Distribution
@app.get("/api/v1/dashboard/categorical-field/{field_name}")
def categorical_distribution(field_name: str, db: Session = Depends(get_db)):
    field = getattr(ADRModel, field_name, None)
    if not field:
        return {"error": "Invalid field name"}
    rows = db.query(field, func.count()).group_by(field).all()
    return {"series": [r[1] for r in rows], "data": [str(r[0]) for r in rows]}


#  Top Institutions
@app.get("/api/v1/dashboard/top-institutions")
def top_reporting_institutions(db: Session = Depends(get_db)):
    rows = (
        db.query(MedicalInstitutionModel.name, func.count(ADRModel.id))
        .join(ADRModel, MedicalInstitutionModel.id == ADRModel.medical_institution_id)
        .group_by(MedicalInstitutionModel.name)
        .order_by(func.count(ADRModel.id).desc())
        .limit(5)
        .all()
    )
    return {"series": [r[1] for r in rows], "data": [r[0] for r in rows]}


#  ADRs Weekly (Raw SQL with structured output)
@app.get("/api/v1/dashboard/adrs-weekly")
def adrs_weekly(db: Session = Depends(get_db)):
    sql = text("""
        SELECT strftime('%Y-W%W', created_at) AS week_label, COUNT(*) AS count
        FROM adr
        GROUP BY week_label
        ORDER BY week_label
    """)
    result = db.execute(sql).fetchall()
    return {"series": [r[1] for r in result], "data": [r[0] for r in result]}


#  ADRs Monthly (Raw SQL with structured output)
@app.get("/api/v1/dashboard/adrs-monthly")
def adrs_monthly(db: Session = Depends(get_db)):
    sql = text("""
        SELECT
            strftime('%Y', created_at) AS year,
            strftime('%m', created_at) AS month,
            COUNT(*) AS count
        FROM adr
        GROUP BY year, month
        ORDER BY year, month
    """)
    result = db.execute(sql).fetchall()

    data_by_year = defaultdict(lambda: {"series": [], "data": []})

    for row in result:
        year, month, count = row
        # Convert month number to short month name
        month_int = int(month)
        month_label = f"{calendar.month_abbr[month_int]}"
        data_by_year[year]["data"].append(month_label)
        data_by_year[year]["series"].append(count)

    return data_by_year


#  SMS Summary
@app.get("/api/v1/dashboard/sms-summary")
def sms_summary(db: Session = Depends(get_db)):
    total_sms = db.query(func.count(SMSMessageModel.id)).scalar()
    total_cost = db.query(func.sum(SMSMessageModel.cost)).scalar()
    success_rate = (
        db.query(func.count()).filter(SMSMessageModel.status == "Delivered").scalar()
    )
    return {
        "total_sms": total_sms,
        "total_cost": total_cost,
        "delivered": success_rate,
        "average_cost": round(float(total_cost or 0) / total_sms, 4)
        if total_sms
        else 0,
    }


#  SMS Status Distribution
@app.get("/api/v1/dashboard/sms-status")
def sms_status_distribution(db: Session = Depends(get_db)):
    rows = (
        db.query(SMSMessageModel.status, func.count())
        .group_by(SMSMessageModel.status)
        .all()
    )
    return [{"series": r[0], "data": r[1]} for r in rows]


#  SMS Type Distribution
@app.get("/api/v1/dashboard/sms-type")
def sms_type_distribution(db: Session = Depends(get_db)):
    rows = (
        db.query(SMSMessageModel.sms_type, func.count())
        .group_by(SMSMessageModel.sms_type)
        .all()
    )
    return [{"type": r[0], "count": r[1]} for r in rows]


#  SMS Count Over Time
@app.get("/api/v1/dashboard/sms-weekly")
def sms_weekly(db: Session = Depends(get_db)):
    sql = text("""
        SELECT strftime('%Y-W%W', created_at) AS week_label, COUNT(*) AS count
        FROM sms_message
        GROUP BY week_label
        ORDER BY week_label
    """)
    result = db.execute(sql).fetchall()
    return {"series": [r[1] for r in result], "data": [r[0] for r in result]}


def get_sms_monthly_by_type(db: Session, sms_type: str):
    sql = text("""
        SELECT
            strftime('%Y', created_at) AS year,
            strftime('%m', created_at) AS month,
            COUNT(*) AS count
        FROM sms_message
        WHERE sms_type = :sms_type
        GROUP BY year, month
        ORDER BY year, month
    """)
    result = db.execute(sql, {"sms_type": sms_type}).fetchall()

    data_by_year = defaultdict(lambda: {"series": [], "data": []})

    for row in result:
        year, month, count = row
        month_int = int(month)
        month_label = calendar.month_abbr[month_int]
        data_by_year[year]["data"].append(month_label)
        data_by_year[year]["series"].append(count)

    return data_by_year


@app.get("/api/v1/dashboard/sms-monthly/individual-alert")
def sms_monthly_individual_alert(db: Session = Depends(get_db)):
    return get_sms_monthly_by_type(db, "individual alert")


# Uncomment and add more routes if you add more message types in the future
# @app.get("/api/v1/dashboard/sms-monthly/bulk-alert")
# def sms_monthly_bulk_alert(db: Session = Depends(get_db)):
#     return get_sms_monthly_by_type(db, "bulk alert")


@app.get("/api/v1/dashboard/sms-monthly/additional-info")
def sms_monthly_additional_info(db: Session = Depends(get_db)):
    return get_sms_monthly_by_type(db, "additional info")


#  SMS Monthly (Raw SQL with structured output)
@app.get("/api/v1/dashboard/sms-monthly")
def sms_monthly(db: Session = Depends(get_db)):
    sql = text("""
        SELECT strftime('%Y-%m', created_at) AS month_label, COUNT(*) AS count
        FROM sms_message
        GROUP BY month_label
        ORDER BY month_label
    """)
    result = db.execute(sql).fetchall()
    return {"series": [r[1] for r in result], "data": [r[0] for r in result]}


@app.get(
    "/api/v1/medical_institution",
    response_model=Page[MedicalInstitutionGetResponse],
)
async def get_medical_institution(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    query: str = Query("", description="Search query(optional)"),
    db: Session = Depends(get_db),
):
    if query:
        content = (
            db.query(MedicalInstitutionModel)
            .filter(
                MedicalInstitutionModel.name.ilike(f"%{query}%")
                | MedicalInstitutionModel.county.ilike(f"%{query}%")
                | MedicalInstitutionModel.sub_county.ilike(f"%{query}%")
            )
            .order_by(desc(MedicalInstitutionModel.created_at))
        )
    else:
        content = db.query(MedicalInstitutionModel).order_by(
            desc(MedicalInstitutionModel.created_at)
        )

    return paginate(content)


@app.get("/api/v1/medical_institution/{institution_id}", status_code=status.HTTP_200_OK)
async def get_medical_institution_by_id(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    institution_id: str = Path(..., description="ID of Medical Institution to delete"),
    query: str = Query("", description="Search query(optional)"),
    db: Session = Depends(get_db),
):
    db_institution = (
        db.query(MedicalInstitutionModel)
        .filter(MedicalInstitutionModel.id == institution_id)
        .first()
    )

    if not db_institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical Institution not found",
        )

    return JSONResponse(
        content=jsonable_encoder(db_institution), status_code=status.HTTP_200_OK
    )


@app.post("/api/v1/medical_institution", status_code=status.HTTP_201_CREATED)
async def post_medical_institution(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    institution: MedicalInstitutionPostRequest,
    db: Session = Depends(get_db),
):
    new_institution = MedicalInstitutionModel(**institution.model_dump())

    db.add(new_institution)
    db.commit()
    db.refresh(new_institution)

    return JSONResponse(
        content=jsonable_encoder(new_institution),
        status_code=status.HTTP_201_CREATED,
    )


@app.put("/api/v1/medical_institution/{institution_id}", status_code=status.HTTP_200_OK)
async def update_medical_institution(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    institution: MedicalInstitutionGetResponse,
    institution_id: str = Path(..., description="ID of Medical Institution to update"),
    db: Session = Depends(get_db),
):
    db_institution = (
        db.query(MedicalInstitutionModel)
        .filter(MedicalInstitutionModel.id == institution_id)
        .first()
    )

    if not db_institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical Institution not found",
        )

    for key, value in institution.model_dump().items():
        setattr(db_institution, key, value)

    db.commit()
    db.refresh(db_institution)

    return JSONResponse(
        content=jsonable_encoder(db_institution),
        status_code=status.HTTP_200_OK,
    )


@app.delete(
    "/api/v1/medical_institution/{institution_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_medical_institution(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    institution_id: str = Path(..., description="ID of Medical Institution to delete"),
    db: Session = Depends(get_db),
):
    db_institution = (
        db.query(MedicalInstitutionModel)
        .filter(MedicalInstitutionModel.id == institution_id)
        .first()
    )

    if not db_institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical Institution not found",
        )

    db.delete(db_institution)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/api/v1/medical_institution/{institution_id}/telephone",
    response_model=Page[MedicalInstitutionTelephoneGetResponse],
)
async def get_telephones_for_medical_institution(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    institution_id: str = Path(..., description="ID of the Medical Institution"),
    db: Session = Depends(get_db),
):
    # Check if the medical institution exists first (optional but good)
    institution = (
        db.query(MedicalInstitutionModel)
        .filter(MedicalInstitutionModel.id == institution_id)
        .first()
    )

    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical Institution not found",
        )

    # Query all telephone numbers for the given institution
    telephones = db.query(MedicalInstitutionTelephoneModel).filter(
        MedicalInstitutionTelephoneModel.medical_institution_id == institution_id
    )

    return paginate(telephones)


@app.get(
    "/api/v1/medical_institution_telephone",
    response_model=Page[MedicalInstitutionTelephoneGetResponse],
)
async def get_medical_institution_telephones(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    content = db.query(MedicalInstitutionTelephoneModel).order_by(
        desc(MedicalInstitutionTelephoneModel.created_at)
    )
    return paginate(content)


@app.post("/api/v1/medical_institution_telephone", status_code=status.HTTP_201_CREATED)
async def create_medical_institution_telephone(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    data: MultipleMedicalInstitutionTelephonePostRequest,
    db: Session = Depends(get_db),
):
    # Create a list of MedicalInstitutionTelephoneModel instances
    new_telephones = [
        MedicalInstitutionTelephoneModel(
            medical_institution_id=telephone.medical_institution_id,
            telephone=telephone.telephone,
        )
        for telephone in data.telephones
    ]

    db.add_all(new_telephones)  # Add all telephones to the session
    db.commit()  # Commit the changes

    for telephone in new_telephones:
        db.refresh(telephone)

    return JSONResponse(
        content=jsonable_encoder(new_telephones),
        status_code=status.HTTP_201_CREATED,
    )


@app.put(
    "/api/v1/medical_institution_telephone/{telephone_id}",
    status_code=status.HTTP_200_OK,
)
async def update_medical_institution_telephone(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    telephone_update: MedicalInstitutionTelephonePostRequest,
    telephone_id: str = Path(..., description="ID of Telephone record to update"),
    db: Session = Depends(get_db),
):
    db_telephone = (
        db.query(MedicalInstitutionTelephoneModel)
        .filter(MedicalInstitutionTelephoneModel.id == telephone_id)
        .first()
    )

    if not db_telephone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telephone record not found",
        )

    for key, value in telephone_update.model_dump().items():
        setattr(db_telephone, key, value)

    db.commit()
    db.refresh(db_telephone)

    return JSONResponse(
        content=jsonable_encoder(db_telephone),
        status_code=status.HTTP_200_OK,
    )


@app.delete(
    "/api/v1/medical_institution_telephone/{telephone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_medical_institution_telephone(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    telephone_id: str = Path(..., description="ID of Telephone record to delete"),
    db: Session = Depends(get_db),
):
    db_telephone = (
        db.query(MedicalInstitutionTelephoneModel)
        .filter(MedicalInstitutionTelephoneModel.id == telephone_id)
        .first()
    )

    if not db_telephone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telephone record not found",
        )

    db.delete(db_telephone)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/api/v1/sms_message",
    response_model=Page[SMSMessageGetResponse],
)
async def get_sms_messages(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    sms_type: SMSMessageTypeEnum | None = Query(None, description="Filter by SMS type"),
    adr_id: str | None = Query(None, description="Filter by ADR ID"),
    db: Session = Depends(get_db),
):
    if sms_type:
        content = db.query(SMSMessageModel).filter(SMSMessageModel.sms_type == sms_type)
    elif adr_id:
        content = db.query(SMSMessageModel).filter(SMSMessageModel.adr_id == adr_id)
    else:
        content = db.query(SMSMessageModel)

    content = content.order_by(desc(SMSMessageModel.created_at))

    return paginate(content)


@app.get("/api/v1/sms_message/{sms_message_id}", status_code=status.HTTP_200_OK)
async def get_sms_message_by_id(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    sms_message_id: str = Path(..., description="ID of Medical Institution to delete"),
    db: Session = Depends(get_db),
):
    db_sms_message = (
        db.query(SMSMessageModel).filter(SMSMessageModel.id == sms_message_id).first()
    )

    if not db_sms_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMS Message not found",
        )

    return JSONResponse(
        content=jsonable_encoder(db_sms_message), status_code=status.HTTP_200_OK
    )


@app.get("/api/v1/sms_message_count", response_model=Page[dict])
async def get_sms_message_with_adr_and_counts(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    sms_type: SMSMessageTypeEnum | None = Query(None, description="Filter by SMS type"),
    db: Session = Depends(get_db),
):
    # Calculate offset and limit based on page and size
    offset = (page - 1) * size
    limit = size

    # Query to count rows grouped by adr_id, sms_type, and include medical institution name
    if sms_type:
        query = (
            db.query(
                SMSMessageModel.adr_id,
                SMSMessageModel.sms_type,
                MedicalInstitutionModel.mfl_code.label("medical_institution_mfl_code"),
                MedicalInstitutionModel.name.label("medical_institution_name"),
                ADRModel.patient_name.label("patient_name"),
                func.count().label("sms_count"),
            )
            .filter(SMSMessageModel.sms_type == sms_type)
            .join(
                ADRModel,
                ADRModel.id == SMSMessageModel.adr_id,
            )
            .join(
                MedicalInstitutionModel,
                MedicalInstitutionModel.id == ADRModel.medical_institution_id,
            )
            .group_by(
                SMSMessageModel.adr_id,
                SMSMessageModel.sms_type,
                MedicalInstitutionModel.name,
                MedicalInstitutionModel.mfl_code,
                ADRModel.patient_name,
            )
            .offset(offset)
            .limit(limit)
        )
    else:
        query = (
            db.query(
                SMSMessageModel.adr_id,
                SMSMessageModel.sms_type,
                MedicalInstitutionModel.mfl_code.label("medical_institution_mfl_code"),
                MedicalInstitutionModel.name.label("medical_institution_name"),
                ADRModel.patient_name.label("patient_name"),
                func.count().label("sms_count"),
            )
            .join(
                ADRModel,
                ADRModel.id == SMSMessageModel.adr_id,
            )
            .join(
                MedicalInstitutionModel,
                MedicalInstitutionModel.id == ADRModel.medical_institution_id,
            )
            .group_by(
                SMSMessageModel.adr_id,
                SMSMessageModel.sms_type,
                MedicalInstitutionModel.name,
                MedicalInstitutionModel.mfl_code,
                ADRModel.patient_name,
            )
            .offset(offset)
            .limit(limit)
        )

    # Query to get the total count of records
    if sms_type:
        total_query = (
            db.query(func.count().label("total"))
            .select_from(SMSMessageModel)
            .filter(SMSMessageModel.sms_type == sms_type)
            .join(
                ADRModel,
                ADRModel.id == SMSMessageModel.adr_id,
            )
            .join(
                MedicalInstitutionModel,
                MedicalInstitutionModel.id == ADRModel.medical_institution_id,
            )
        )
    else:
        total_query = (
            db.query(func.count().label("total"))
            .select_from(SMSMessageModel)
            .join(
                ADRModel,
                ADRModel.id == SMSMessageModel.adr_id,
            )
            .join(
                MedicalInstitutionModel,
                MedicalInstitutionModel.id == ADRModel.medical_institution_id,
            )
        )
    # Get total count
    total_result = (
        total_query.scalar()
    )  # Executes the query and gets the scalar value (total count)

    # Calculate the total number of pages
    pages = (total_result + size - 1) // size  # Equivalent to math.ceil(total / size)

    # Execute the query and get the results
    result = query.all()

    items = [
        {
            "adr_id": row.adr_id,
            "sms_type": row.sms_type,
            "medical_institution_mfl_code": row.medical_institution_mfl_code,
            "medical_institution_name": row.medical_institution_name,
            "patient_name": row.patient_name,
            "sms_count": row.sms_count,
        }
        for row in result
    ]

    return {
        "items": items,
        "total": total_result,
        "page": page,
        "size": size,
        "pages": pages,
    }


@app.get("/api/v1/adrs_with_individual_alerts", response_model=Page[dict])
async def get_adrs_with_individual_alerts(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    query: str = Query("", description="Search query (optional)"),
    db: Session = Depends(get_db),
):
    # Calculate offset and limit based on page and size
    offset = (page - 1) * size
    limit = size

    search_term = f"%{query}%" if query else None

    result_sql = text("""
    SELECT
        adr.id AS adr_id,
        adr.patient_name AS patient_name,
        mi.name AS medical_institution_name,
        mi.mfl_code AS medical_institution_mfl_code,
        adr.created_at AS created_at,
        GROUP_CONCAT(DISTINCT mit.telephone) AS telephones,
        COUNT(DISTINCT sms.id) AS sms_count,
        COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) AS approved_reviews,
        COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END) AS unapproved_reviews
        
    FROM adr
    JOIN causality_assessment_level cal ON adr.id = cal.adr_id
    JOIN medical_institution mi ON adr.medical_institution_id = mi.id
    LEFT JOIN medical_institution_telephone mit ON mi.id = mit.medical_institution_id
    LEFT JOIN review ON cal.id = review.causality_assessment_level_id
    LEFT JOIN sms_message sms ON adr.id = sms.adr_id
    WHERE cal.causality_assessment_level_value = :level_value
        AND (:query IS NULL OR LOWER(adr.patient_name) LIKE LOWER(:query))
    GROUP BY adr.id, adr.patient_name, mi.name, mi.mfl_code, adr.created_at
    HAVING COUNT(DISTINCT sms.id) != 0
        AND COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) >
        COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END)
    ORDER BY adr.created_at DESC
    LIMIT :limit OFFSET :offset
    """)

    result_params = {
        "level_value": "certain",
        "limit": limit,
        "offset": offset,
        "query": search_term,
    }

    result = db.execute(result_sql, result_params)

    rows = result.fetchall()

    items = [
        {
            "adr_id": row.adr_id,
            "patient_name": row.patient_name,
            "medical_institution_mfl_code": row.medical_institution_mfl_code,
            "medical_institution_name": row.medical_institution_name,
            "created_at": row.created_at,
            "telephones": row.telephones.split(",") if row.telephones else [],
            "sms_count": row.sms_count,
        }
        for row in rows
    ]

    total_sql = text("""
    SELECT COUNT(*) FROM (
        SELECT
            adr.id,
            COUNT(DISTINCT sms.id) AS sms_count
        FROM adr
        JOIN causality_assessment_level cal ON adr.id = cal.adr_id
        LEFT JOIN review ON cal.id = review.causality_assessment_level_id
        LEFT JOIN sms_message sms ON adr.id = sms.adr_id
        WHERE cal.causality_assessment_level_value = :level_value
            AND (:query IS NULL OR LOWER(adr.patient_name) LIKE LOWER(:query))
        GROUP BY adr.id
        HAVING COUNT(DISTINCT sms.id) != 0
            AND COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) >
            COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END)
    ) AS sub
    """)

    total_result_params = {"level_value": "certain", "query": search_term}
    total_result = db.execute(total_sql, total_result_params).scalar()
    # Calculate the total number of pages
    pages = (total_result + size - 1) // size  # Equivalent to math.ceil(total / size)

    return {
        "items": items,
        "total": total_result,
        "page": page,
        "size": size,
        "pages": pages,
    }


@app.get("/api/v1/adrs_to_be_sent_individual_alerts", response_model=Page[dict])
async def get_adrs_to_be_sent_for_individual_alerts(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    query: str = Query("", description="Search query (optional)"),
    db: Session = Depends(get_db),
):
    # Calculate offset and limit based on page and size
    offset = (page - 1) * size
    limit = size

    search_term = f"%{query}%" if query else None

    result_sql = text("""
    SELECT
        adr.id AS adr_id,
        adr.patient_name AS patient_name,
        mi.name AS medical_institution_name,
        mi.mfl_code AS medical_institution_mfl_code,
        adr.created_at AS created_at,
        GROUP_CONCAT(DISTINCT mit.telephone) AS telephones,
        COUNT(DISTINCT sms.id) AS sms_count,
        COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) AS approved_reviews,
        COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END) AS unapproved_reviews
    FROM adr
    JOIN causality_assessment_level cal ON adr.id = cal.adr_id
    JOIN medical_institution mi ON adr.medical_institution_id = mi.id
    LEFT JOIN medical_institution_telephone mit ON mi.id = mit.medical_institution_id
    LEFT JOIN review ON cal.id = review.causality_assessment_level_id
    LEFT JOIN sms_message sms ON adr.id = sms.adr_id
    WHERE cal.causality_assessment_level_value = :level_value
        AND (:query IS NULL OR LOWER(adr.patient_name) LIKE LOWER(:query))
    GROUP BY adr.id, adr.patient_name, mi.name, mi.mfl_code, adr.created_at
    HAVING COUNT(DISTINCT sms.id) = 0
        AND COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) >
        COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END)
    ORDER BY adr.created_at DESC
    LIMIT :limit OFFSET :offset
    """)

    result_params = {
        "level_value": "certain",
        "limit": limit,
        "offset": offset,
        "query": search_term,
    }

    result = db.execute(result_sql, result_params)

    rows = result.fetchall()

    items = [
        {
            "adr_id": row.adr_id,
            "patient_name": row.patient_name,
            "medical_institution_mfl_code": row.medical_institution_mfl_code,
            "medical_institution_name": row.medical_institution_name,
            "created_at": row.created_at,
            "telephones": row.telephones.split(",") if row.telephones else [],
            "sms_count": row.sms_count,
        }
        for row in rows
    ]

    total_sql = text("""
    SELECT COUNT(*) FROM (
        SELECT
            adr.id,
            COUNT(DISTINCT sms.id) AS sms_count
        FROM adr
        JOIN causality_assessment_level cal ON adr.id = cal.adr_id
        LEFT JOIN review ON cal.id = review.causality_assessment_level_id
        LEFT JOIN sms_message sms ON adr.id = sms.adr_id
        WHERE cal.causality_assessment_level_value = :level_value
            AND (:query IS NULL OR LOWER(adr.patient_name) LIKE LOWER(:query))
        GROUP BY adr.id
        HAVING COUNT(DISTINCT sms.id) = 0
            AND COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) >
            COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END)
    ) AS sub
    """)

    total_result_params = {"level_value": "certain", "query": search_term}

    total_result = db.execute(total_sql, total_result_params).scalar()
    # Calculate the total number of pages
    pages = (total_result + size - 1) // size  # Equivalent to math.ceil(total / size)

    return {
        "items": items,
        "total": total_result,
        "page": page,
        "size": size,
        "pages": pages,
    }


@app.get("/api/v1/adrs_with_additional_info_requests", response_model=Page[dict])
async def get_adrs_with_additional_info_requests(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    query: str = Query("", description="Search query (optional)"),
    db: Session = Depends(get_db),
):
    # Calculate offset and limit based on page and size
    offset = (page - 1) * size
    limit = size

    search_term = f"%{query}%" if query else None

    result_sql = text("""
    SELECT
        adr.id AS adr_id,
        adr.patient_name AS patient_name,
        mi.name AS medical_institution_name,
        mi.mfl_code AS medical_institution_mfl_code,
        adr.created_at AS created_at,
        GROUP_CONCAT(DISTINCT mit.telephone) AS telephones,
        COUNT(DISTINCT sms.id) AS sms_count,
        COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) AS approved_reviews,
        COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END) AS unapproved_reviews
        
    FROM adr
    JOIN causality_assessment_level cal ON adr.id = cal.adr_id
    JOIN medical_institution mi ON adr.medical_institution_id = mi.id
    LEFT JOIN medical_institution_telephone mit ON mi.id = mit.medical_institution_id
    LEFT JOIN review ON cal.id = review.causality_assessment_level_id
    LEFT JOIN sms_message sms ON adr.id = sms.adr_id
    WHERE cal.causality_assessment_level_value = :level_value
        AND (:query IS NULL OR LOWER(adr.patient_name) LIKE LOWER(:query))
    GROUP BY adr.id, adr.patient_name, mi.name, mi.mfl_code, adr.created_at
    HAVING COUNT(DISTINCT sms.id) != 0
        AND COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) >
        COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END)
    ORDER BY adr.created_at DESC
    LIMIT :limit OFFSET :offset
    """)

    result_params = {
        "level_value": "unclassified",
        "limit": limit,
        "offset": offset,
        "query": search_term,
    }

    result = db.execute(result_sql, result_params)

    rows = result.fetchall()

    items = [
        {
            "adr_id": row.adr_id,
            "patient_name": row.patient_name,
            "medical_institution_mfl_code": row.medical_institution_mfl_code,
            "medical_institution_name": row.medical_institution_name,
            "created_at": row.created_at,
            "telephones": row.telephones.split(",") if row.telephones else [],
            "sms_count": row.sms_count,
        }
        for row in rows
    ]

    total_sql = text("""
    SELECT COUNT(*) FROM (
        SELECT
            adr.id,
            COUNT(DISTINCT sms.id) AS sms_count
        FROM adr
        JOIN causality_assessment_level cal ON adr.id = cal.adr_id
        LEFT JOIN review ON cal.id = review.causality_assessment_level_id
        LEFT JOIN sms_message sms ON adr.id = sms.adr_id
        WHERE cal.causality_assessment_level_value = :level_value
            AND (:query IS NULL OR LOWER(adr.patient_name) LIKE LOWER(:query))
        GROUP BY adr.id
        HAVING COUNT(DISTINCT sms.id) != 0
            AND COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) >
            COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END)
    ) AS sub
    """)

    total_result_params = {"level_value": "unclassifiable", "query": search_term}

    total_result = db.execute(total_sql, total_result_params).scalar()
    # Calculate the total number of pages
    pages = (total_result + size - 1) // size  # Equivalent to math.ceil(total / size)

    return {
        "items": items,
        "total": total_result,
        "page": page,
        "size": size,
        "pages": pages,
    }


@app.get("/api/v1/adrs_to_be_sent_additional_info_requests", response_model=Page[dict])
async def get_adrs_to_be_sent_for_additional_info_requests(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    query: str = Query("", description="Search query (optional)"),
    db: Session = Depends(get_db),
):
    # Calculate offset and limit based on page and size
    offset = (page - 1) * size
    limit = size

    search_term = f"%{query}%" if query else None

    result_sql = text("""
    SELECT
        adr.id AS adr_id,
        adr.patient_name AS patient_name,
        mi.name AS medical_institution_name,
        mi.mfl_code AS medical_institution_mfl_code,
        adr.created_at AS created_at,
        GROUP_CONCAT(DISTINCT mit.telephone) AS telephones,
        COUNT(DISTINCT sms.id) AS sms_count,
        COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) AS approved_reviews,
        COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END) AS unapproved_reviews
    FROM adr
    JOIN causality_assessment_level cal ON adr.id = cal.adr_id
    JOIN medical_institution mi ON adr.medical_institution_id = mi.id
    LEFT JOIN medical_institution_telephone mit ON mi.id = mit.medical_institution_id
    LEFT JOIN review ON cal.id = review.causality_assessment_level_id
    LEFT JOIN sms_message sms ON adr.id = sms.adr_id
    WHERE cal.causality_assessment_level_value = :level_value
        AND (:query IS NULL OR LOWER(adr.patient_name) LIKE LOWER(:query))
    GROUP BY adr.id, adr.patient_name, mi.name, mi.mfl_code, adr.created_at
    HAVING COUNT(DISTINCT sms.id) = 0
        AND COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) >
        COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END)
    ORDER BY adr.created_at DESC
    LIMIT :limit OFFSET :offset
    """)

    result_params = {
        "level_value": "unclassified",
        "limit": limit,
        "offset": offset,
        "query": search_term,
    }

    result = db.execute(result_sql, result_params)

    rows = result.fetchall()

    items = [
        {
            "adr_id": row.adr_id,
            "patient_name": row.patient_name,
            "medical_institution_mfl_code": row.medical_institution_mfl_code,
            "medical_institution_name": row.medical_institution_name,
            "created_at": row.created_at,
            "telephones": row.telephones.split(",") if row.telephones else [],
            "sms_count": row.sms_count,
        }
        for row in rows
    ]

    total_sql = text("""
    SELECT COUNT(*) FROM (
        SELECT
            adr.id,
            COUNT(DISTINCT sms.id) AS sms_count
        FROM adr
        JOIN causality_assessment_level cal ON adr.id = cal.adr_id
        LEFT JOIN review ON cal.id = review.causality_assessment_level_id
        LEFT JOIN sms_message sms ON adr.id = sms.adr_id
        WHERE cal.causality_assessment_level_value = :level_value
            AND (:query IS NULL OR LOWER(adr.patient_name) LIKE LOWER(:query))
        GROUP BY adr.id
        HAVING COUNT(DISTINCT sms.id) = 0
            AND COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) >
            COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END)
    ) AS sub
    """)

    total_result_params = {"level_value": "unclassified", "query": search_term}

    total_result = db.execute(total_sql, total_result_params).scalar()
    # Calculate the total number of pages
    pages = (total_result + size - 1) // size  # Equivalent to math.ceil(total / size)

    return {
        "items": items,
        "total": total_result,
        "page": page,
        "size": size,
        "pages": pages,
    }


@app.put("api/v1/update_causalities_to_unclassifiable")
def update_causalities_to_unclassifiable(
    data: UnclassifiablePostRequest,
    db: Session = Depends(get_db),
):
    for adr_id in data.adr_ids:
        cals = (
            db.query(CausalityAssessmentLevelModel)
            .filter(CausalityAssessmentLevelModel.adr_id == adr_id)
            .all()
        )

        for cal in cals:
            cal.causality_assessment_level_value = (
                CausalityAssessmentLevelEnum.unclassifiable
            )

    db.commit()
    db.refresh()

    return JSONResponse(
        content="ADR models with unclassifiable set", status_code=status.HTTP_200_OK
    )


@app.get("/api/v1/adrs_with_unclassifiable_causality", response_model=Page[dict])
async def get_adrs_with_unclassifiable_causality(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    # Calculate offset and limit based on page and size
    offset = (page - 1) * size
    limit = size

    result_sql = text("""
    SELECT
        adr.id AS adr_id,
        adr.patient_name AS patient_name,
        mi.name AS medical_institution_name,
        mi.mfl_code AS medical_institution_mfl_code,
        adr.created_at AS created_at,
        GROUP_CONCAT(DISTINCT mit.telephone) AS telephones,
        COUNT(DISTINCT sms.id) AS sms_count,
        COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) AS approved_reviews,
        COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END) AS unapproved_reviews
        
    FROM adr
    JOIN causality_assessment_level cal ON adr.id = cal.adr_id
    JOIN medical_institution mi ON adr.medical_institution_id = mi.id
    LEFT JOIN medical_institution_telephone mit ON mi.id = mit.medical_institution_id
    LEFT JOIN review ON cal.id = review.causality_assessment_level_id
    LEFT JOIN sms_message sms ON adr.id = sms.adr_id
    WHERE cal.causality_assessment_level_value = :level_value
    GROUP BY adr.id, adr.patient_name, mi.name, mi.mfl_code, adr.created_at
    HAVING COUNT(DISTINCT sms.id) != 0
        AND COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) >
        COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END)
    ORDER BY adr.created_at DESC
    LIMIT :limit OFFSET :offset
    """)

    result_params = {"level_value": "unclassifiable", "limit": limit, "offset": offset}

    result = db.execute(result_sql, result_params)

    rows = result.fetchall()

    items = [
        {
            "adr_id": row.adr_id,
            "patient_name": row.patient_name,
            "medical_institution_mfl_code": row.medical_institution_mfl_code,
            "medical_institution_name": row.medical_institution_name,
            "created_at": row.created_at,
            "telephones": row.telephones.split(",") if row.telephones else [],
            "sms_count": row.sms_count,
        }
        for row in rows
    ]

    total_sql = text("""
    SELECT COUNT(*) FROM (
        SELECT
            adr.id,
            COUNT(DISTINCT sms.id) AS sms_count
        FROM adr
        JOIN causality_assessment_level cal ON adr.id = cal.adr_id
        LEFT JOIN review ON cal.id = review.causality_assessment_level_id
        LEFT JOIN sms_message sms ON adr.id = sms.adr_id
        WHERE cal.causality_assessment_level_value = :level_value
        GROUP BY adr.id
        HAVING COUNT(DISTINCT sms.id) != 0
            AND COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) >
            COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END)
    ) AS sub
    """)

    total_result_params = {
        "level_value": "unclassifiable",
    }

    total_result = db.execute(total_sql, total_result_params).scalar()
    # Calculate the total number of pages
    pages = (total_result + size - 1) // size  # Equivalent to math.ceil(total / size)

    return {
        "items": items,
        "total": total_result,
        "page": page,
        "size": size,
        "pages": pages,
    }


@app.post("/api/v1/send_individual_alert")
def send_individual_alert(
    data: IndividualAlertPostRequest, db: Session = Depends(get_db)
):
    try:
        africastalking.initialize(
            settings.africas_talking_username, settings.africas_talking_api_key
        )
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to initialize Africa's Talking: " + str(e),
        )

    sms = africastalking.SMS

    adr_model = db.query(ADRModel).filter(ADRModel.id == data.adr_id).first()

    medical_institution_model = (
        db.query(MedicalInstitutionModel)
        .filter(MedicalInstitutionModel.id == adr_model.medical_institution_id)
        .first()
    )

    telephone_number_model = (
        db.query(MedicalInstitutionTelephoneModel)
        .filter(
            MedicalInstitutionTelephoneModel.medical_institution_id
            == adr_model.medical_institution_id
        )
        .first()
    )

    message_content = (
        f"URGENT ADR ALERT: {adr_model.patient_name} at {medical_institution_model.name} "
        f"has a causality assessment of CERTAIN. We are further investigating this as the Pharmacy and Poisons Board (PPB) for further guidance. Call +254795743049 for further information."
    )

    message_type = SMSMessageTypeEnum.individual_alert

    recipients = [telephone_number_model.telephone]

    response: Dict = sms.send(message_content, recipients)

    sms_messages = []

    for message in response.get("SMSMessageData").get("Recipients"):
        sms_message = SMSMessageModel(
            adr_id=adr_model.id,
            content=message_content,
            sms_type=message_type,
            cost=message.get("cost", None),
            message_id=message.get("messageId", None),
            message_parts=message.get("messageParts", None),
            number=message.get("number", None),
            status=message.get("status"),
            status_code=message.get("statusCode"),
        )

        sms_messages.append(sms_message)

    db.add_all(sms_messages)
    db.commit()

    for sms_message in sms_messages:
        db.refresh(sms_message)

    content = jsonable_encoder(sms_messages)

    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


@app.post("/api/v1/send_additional_info_request")
def send_additional_info_request(
    data: AdditionalInfoPostRequest, db: Session = Depends(get_db)
):
    try:
        africastalking.initialize(
            settings.africas_talking_username, settings.africas_talking_api_key
        )
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to initialize Africa's Talking: " + str(e),
        )

    sms = africastalking.SMS

    adr_model = db.query(ADRModel).filter(ADRModel.id == data.adr_id).first()

    medical_institution_model = (
        db.query(MedicalInstitutionModel)
        .filter(MedicalInstitutionModel.id == adr_model.medical_institution_id)
        .first()
    )

    telephone_number_model = (
        db.query(MedicalInstitutionTelephoneModel)
        .filter(
            MedicalInstitutionTelephoneModel.medical_institution_id
            == adr_model.medical_institution_id
        )
        .first()
    )

    message_content = (
        f"ADR FOLLOW-UP: An ADR case involving {adr_model.patient_name} from {medical_institution_model.name} requires additional clinical details. "
        f"Kindly review and submit supporting information to the Pharmacy and Poisons Board (PPB)."
    )

    message_type = SMSMessageTypeEnum.additional_info

    recipients = [telephone_number_model.telephone]

    response: Dict = sms.send(message_content, recipients)

    sms_messages = []

    for message in response.get("SMSMessageData").get("Recipients"):
        sms_message = SMSMessageModel(
            adr_id=adr_model.id,
            content=message_content,
            sms_type=message_type,
            cost=message.get("cost", None),
            message_id=message.get("messageId", None),
            message_parts=message.get("messageParts", None),
            number=message.get("number", None),
            status=message.get("status"),
            status_code=message.get("statusCode"),
        )

        sms_messages.append(sms_message)

    db.add_all(sms_messages)
    db.commit()

    for sms_message in sms_messages:
        db.refresh(sms_message)

    content = jsonable_encoder(sms_messages)

    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


# Utility functions
def get_ml_model() -> BaseEstimator:
    """Load the trained ML model."""
    model_path = f"{settings.mlflow_model_artifacts_path}/model/model.pkl"
    return joblib.load(model_path)


def get_scalers() -> BaseEstimator:
    """Load the trained ML model."""
    minmax_scaler_path = (
        f"{settings.mlflow_model_artifacts_path}/scalers/minmax_scaler.pkl"
    )
    return joblib.load(minmax_scaler_path)


def get_encoders() -> Tuple[OneHotEncoder, OrdinalEncoder]:
    """Load the one-hot and ordinal encoders."""
    encoders_path = f"{settings.mlflow_model_artifacts_path}/encoders"
    one_hot_encoder = joblib.load(f"{encoders_path}/one_hot_encoder.pkl")
    ordinal_encoder = joblib.load(f"{encoders_path}/ordinal_encoder.pkl")
    return one_hot_encoder, ordinal_encoder


def get_column_metadata() -> dict:
    """Return list of categorical fields used for encoding."""
    """Load the one-hot and ordinal encoders."""
    column_metadata_path = (
        f"{settings.mlflow_model_artifacts_path}/metadata/model_columns.json"
    )
    with open(column_metadata_path, "r") as f:
        column_metadata = json.load(f)

    categorical_columns = column_metadata["categorical_columns"]
    numerical_columns = column_metadata["numerical_columns"]
    date_columns = column_metadata["date_columns"]
    boolean_columns = column_metadata["boolean_columns"]
    prediction_columns = column_metadata["prediction_columns"]
    columns_to_drop = column_metadata["columns_to_drop"]

    return {
        "categorical_columns": categorical_columns,
        "numerical_columns": numerical_columns,
        "date_columns": date_columns,
        "boolean_columns": boolean_columns,
        "prediction_columns": prediction_columns,
        "columns_to_drop": columns_to_drop,
    }


def input_to_prediction_format(input_df: pd.DataFrame) -> pd.DataFrame:
    """
    This function returns for a proper dataframe for the ML model and SHAP model
    """

    column_metadata = get_column_metadata()

    categorical_columns = column_metadata["categorical_columns"]
    numerical_columns = column_metadata["numerical_columns"]
    date_columns = column_metadata["date_columns"]
    boolean_columns = column_metadata["boolean_columns"]
    prediction_columns = column_metadata["prediction_columns"]
    columns_to_drop = column_metadata["columns_to_drop"]

    # Create all the columns not originally in dataset
    ## Num suspected drugs
    input_df["num_suspected_drugs"] = input_df[boolean_columns].sum(axis=1)

    for column in categorical_columns:
        input_df[column] = input_df[column].astype("category")

    ## Patient Age and Patient Date of Birth
    date_columns_without_created_at = date_columns
    date_columns_without_created_at.remove("created_at")

    for column in date_columns:
        input_df[column] = pd.to_datetime(input_df[column], errors="coerce")

    today = pd.to_datetime("today")

    missing_age_mask = (
        input_df["patient_age"].isnull() & input_df["patient_date_of_birth"].notnull()
    )

    input_df.loc[missing_age_mask, "patient_age"] = (
        today - input_df.loc[missing_age_mask, "patient_date_of_birth"]
    ).dt.days // 365

    input_df["patient_age"] = input_df["patient_age"].fillna(
        input_df["patient_age"].median()
    )

    ## Patient BMI
    input_df["patient_bmi"] = input_df["patient_weight_kg"] / (
        input_df["patient_height_cm"] * input_df["patient_height_cm"]
    )

    ## Drug columns
    drug_names = ["rifampicin", "isoniazid", "pyrazinamide", "ethambutol"]

    for drug in drug_names:
        start_col = f"{drug}_start_to_onset_days"
        stop_col = f"{drug}_stop_to_onset_days"
        start_stop_col = f"{drug}_start_stop_difference"

        input_df[start_col] = (
            input_df["date_of_onset_of_reaction"] - input_df[f"{drug}_start_date"]
        ).dt.days
        input_df[stop_col] = (
            input_df["date_of_onset_of_reaction"] - input_df[f"{drug}_stop_date"]
        ).dt.days
        input_df[start_stop_col] = (
            input_df[f"{drug}_stop_date"] - input_df[f"{drug}_start_date"]
        ).dt.days

    # Drop date columns
    input_df = input_df.drop(columns=date_columns)

    input_df = input_df.drop(columns=columns_to_drop)

    # Fill null valuea
    input_df[numerical_columns] = input_df[numerical_columns].fillna(-1)

    # Scale numerical columns
    minmax_scaler = get_scalers()
    scaled_numericals = minmax_scaler.transform(input_df[numerical_columns])
    scaled_numericals_df = pd.DataFrame(scaled_numericals, columns=numerical_columns)

    # Encode categorical columns

    one_hot_encoder, _ = get_encoders()

    cat_encoded = one_hot_encoder.transform(input_df[categorical_columns])
    cat_encoded_df = pd.DataFrame(
        cat_encoded, columns=one_hot_encoder.get_feature_names_out(categorical_columns)
    )

    # Merge all features
    final_input_df = pd.concat(
        [
            cat_encoded_df,
            input_df[boolean_columns].reset_index(drop=True),
            scaled_numericals_df,
        ],
        axis=1,
    )

    # Reorder to match training time
    final_input_df = final_input_df[prediction_columns]

    return final_input_df


def get_shap_values(shap_values: Explainer):
    base_values = list(shap_values.base_values[0])
    shap_values_matrix = shap_values.values[0].tolist()
    shap_values_sum_per_class = np.sum(shap_values.values[0], axis=0).tolist()
    shap_values_and_base_values_sum_per_class = list(
        np.sum(shap_values.values[0], axis=0) + shap_values.base_values[0]
    )

    return {
        "base_values": base_values,
        "shap_values_matrix": shap_values_matrix,
        "shap_values_sum_per_class": shap_values_sum_per_class,
        "shap_values_and_base_values_sum_per_class": shap_values_and_base_values_sum_per_class,
    }


def format_feature_values(feature_values: List[any]) -> List[any]:
    minmax_scaler = get_scalers()

    reversed_values = []

    for i, value in enumerate(feature_values):
        # Handle logical encoding: 0 → False, 1 → True, -1 → None
        if value == 0:
            reversed_values.append(False)
        elif value == 1:
            reversed_values.append(True)

        # Reverse min-max scaling for decimal floats
        elif isinstance(value, float) and not value.is_integer():
            min_val = minmax_scaler.data_min_[i]
            max_val = minmax_scaler.data_max_[i]
            original = round(value * (max_val - min_val) + min_val)
            if original == -1:
                reversed_values.append(None)
            else:
                reversed_values.append(original)

        # Leave all other values as-is
        else:
            reversed_values.append(value)

    return reversed_values
