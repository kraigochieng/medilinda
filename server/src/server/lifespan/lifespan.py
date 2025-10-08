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

from server.config import (
    ADR_CSV_PATH,
    MEDICAL_INSTITUTIONS_CSV_PATH,
    USERS_CSV_PATH,
)
from server.db.engine import engine
from server.lifespan.db import (
    insert_adverse_drug_reaction_reports,
    insert_causality_assessment_levels,
    insert_medical_institution_telephones,
    insert_medical_institutions,
    insert_reviews,
    insert_sms_messages,
    insert_users,
    setup_db,
)
from server.lifespan.mlflow_setup import MLEnsemble, mlflow_setup
from server.models.adverse_drug_reaction_report import ADRModel
from server.settings import settings

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
    setup_db()

    session = Session(bind=engine)

    # Add institutions
    insert_medical_institutions(session=session)

    # Add telelphones to the institutions
    insert_medical_institution_telephones(session=session)

    # Add users
    insert_users(session=session)

    # Add ADRs
    adr_entries = insert_adverse_drug_reaction_reports(session=session)

    insert_causality_assessment_levels(
        session=session,
        ml_model=ml_model,
        encoder=encoder,
        explainer=explainer,
        adr_entries=adr_entries,
    )

    # Add reviews
    insert_reviews(session=session)

    # Add SMS messages
    insert_sms_messages(session=session)
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
