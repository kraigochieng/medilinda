import matplotlib

matplotlib.use("agg")

import json
import logging
from datetime import datetime, timezone
from importlib.metadata import version as installed_version
from pathlib import Path

import mlflow
import mlflow.data
import mlflow.sklearn
import numpy as np
import pandas as pd
import shap
from medilinda_ml.columns import TARGET_COLUMN, TARGET_LEVELS
from medilinda_ml.candidates import candidate_named
from medilinda_ml.logging_config import setup_logging
from medilinda_ml.pipeline import build_pipeline
from medilinda_ml.tracking import (
    EXPERIMENT_NAME,
    LIBRARIES_TO_RECORD,
    current_git_commit,
    portable_runs_folder,
    start_local_tracking,
)
from medilinda_ml.data_split import (
    SPLIT_SEED,
    TEST_FRACTION,
    VALIDATION_FRACTION,
    split_dataset,
)
from medilinda_ml.evaluation import classify, headline_metrics, max_additivity_error
from medilinda_ml.model_store import write_version
from medilinda_ml.paths import MODELS_DIR, SELECTION_PATH, TRAINING_DATA_PATH
from medilinda_ml.selection import check_data_matches, read_selection
from medilinda_ml.training_data import load_training_frame
from medilinda_ml.utils import ShapModelWrapper
# The model goes to the model store. MLflow tracks the experiment in a local folder.
# MLFLOW-DISABLED (#119): the Databricks and model logging code below stays off.
# import joblib
# import mlflow
# from medilinda_ml.settings import settings
# from medilinda_ml.signature import signature
# from mlflow.models import infer_signature
from sklearn.metrics import classification_report

# from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

# MLFLOW-DISABLED (#119): these lines set up MLflow. They start MLflow when the module loads.
# os.environ["DATABRICKS_HOST"] = settings.databricks_host
# os.environ["DATABRICKS_TOKEN"] = settings.databricks_token
# os.environ["MLFLOW_RECORD_ENV_VARS_IN_MODEL_LOGGING"] = "false"

setup_logging()
# # To allow uv to be used
# os.environ["MLFLOW_LOCK_MODEL_DEPENDENCIES"] = "true"

# Set MLFlow Tracking URI
# mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

# Create MLFlow Experiment if not created
# if mlflow.get_experiment_by_name(settings.mlflow_experiment_path) is None:
#     mlflow.create_experiment(
#         name=settings.mlflow_experiment_path,
#         artifact_location=settings.mlflow_artifact_path,
#     )

# Set MLFlow Experiment if not created
# mlflow.set_experiment(settings.mlflow_experiment_path)



SHAP_BACKGROUND_ROWS = 100
SHAP_SEED = 42
SHAP_ADDITIVITY_ROWS = 5


def train_model(df_path: str) -> None:
    """Side effect (disk): train, and keep the runs folder in the relative form."""
    with portable_runs_folder():
        run_training(df_path=df_path)


def run_training(df_path: str) -> None:
    """Side effect (disk): train the model that selection.json names and save it."""
    start_local_tracking()
    selection = read_selection(path=SELECTION_PATH)
    check_data_matches(selection=selection, data_path=Path(df_path))
    df = load_training_frame(path=Path(df_path), feature_set=selection.feature_set)

    data_split = split_dataset(df=df)
    X_train, X_val, X_test = data_split.X_train, data_split.X_val, data_split.X_test
    y_train, y_val, y_test = data_split.y_train, data_split.y_val, data_split.y_test

    ordinal_encoder = OrdinalEncoder(categories=[TARGET_LEVELS])

    y_train_enc = ordinal_encoder.fit_transform(y_train.to_frame()).ravel()
    y_val_enc = ordinal_encoder.transform(y_val.to_frame()).ravel()

    print("✅ Train shape:", X_train.shape)
    print("✅ Validation shape:", X_val.shape)
    print("✅ Test shape:", X_test.shape)

    # The experiment (notebook 3.3) chose the estimator, the params and the features.
    # This training fits that choice once on all training rows. It does not search.
    name = selection.estimator
    candidate = candidate_named(name=name)
    estimator = candidate.estimator.set_params(**selection.params)
    best_estimator = build_pipeline(
        estimator=estimator,
        final_columns=selection.features,
        include_history=selection.feature_set == "full",
    )
    print(f"\n🧠 Training model: {name}")
    print("—" * 80)

    with mlflow.start_run(run_name=f"{name}") as run:
        mlflow.log_input(
            mlflow.data.from_pandas(
                df, source=str(df_path), name=Path(df_path).name, targets=TARGET_COLUMN
            ),
            context="training",
        )
        mlflow.log_params(
            {
                "estimator": name,
                "split_seed": SPLIT_SEED,
                "test_fraction": TEST_FRACTION,
                "validation_fraction": VALIDATION_FRACTION,
                "stratified": True,
                "train_rows": len(X_train),
                "validation_rows": len(X_val),
                "test_rows": len(X_test),
                "shap_background_rows": SHAP_BACKGROUND_ROWS,
                "shap_seed": SHAP_SEED,
                "selected_params": json.dumps(selection.params, sort_keys=True),
                "selected_feature_count": len(selection.features),
            }
        )
        mlflow.set_tags(
            {
                "stage": "production",
                "experiment_run_id": selection.experiment_run_id,
                "data_sha256": selection.data_sha256,
                "git_commit": current_git_commit() or "unknown",
                **{
                    f"library.{library}": installed_version(library)
                    for library in LIBRARIES_TO_RECORD
                },
            }
        )

        best_estimator.fit(X_train, y_train_enc)

        # --- Evaluate on validation data ---
        y_pred = best_estimator.predict(X_val)

        decoded_y_val = ordinal_encoder.inverse_transform(
            y_val_enc.reshape(-1, 1)
        ).ravel()
        decoded_y_pred = ordinal_encoder.inverse_transform(
            y_pred.reshape(-1, 1)
        ).ravel()

        print("\n📊 Validation Results:")
        print(classification_report(decoded_y_val, decoded_y_pred))

        labels: list[str] = ordinal_encoder.categories_[0].tolist()
        validation_result = classify(
            true_labels=decoded_y_val.tolist(),
            predicted_labels=decoded_y_pred.tolist(),
            labels=labels,
        )
        mlflow.log_metrics(headline_metrics(split="validation", result=validation_result))
        mlflow.log_dict(validation_result.model_dump(), "validation_result.json")

        # --- Evaluate once on the held-out test data ---
        decoded_test_prediction = ordinal_encoder.inverse_transform(
            best_estimator.predict(X_test).reshape(-1, 1)
        ).ravel()
        test_result = classify(
            true_labels=y_test.tolist(),
            predicted_labels=decoded_test_prediction.tolist(),
            labels=labels,
        )
        mlflow.log_metrics(headline_metrics(split="test", result=test_result))
        mlflow.log_dict(test_result.model_dump(), "test_result.json")

        print("\n🧪 Test Results (held-out, evaluated once):")
        print(classification_report(y_test.tolist(), decoded_test_prediction))

        print("═" * 80)

        model_name = f"medilinda_rf_smote_pipeline_{name}"

        # Disable verbose params
        print("📦 Disabling verbose logging for production artifact...")

        verbose_params_to_disable = {
            key: False
            for key in best_estimator.get_params().keys()
            if key.endswith("__verbose")
        }

        if verbose_params_to_disable:
            best_estimator.set_params(**verbose_params_to_disable)

            logging.info(f"Disabled {len(verbose_params_to_disable)} verbose flags.")
        else:
            logging.info("No verbose flags found.")

            # MLFLOW-DISABLED (#119): the lines below logged the model, the encoder and the explainer to MLflow.
#             mlflow.sklearn.log_model(
#                 sk_model=best_estimator,
#                 name=model_name,
#                 # input_example=input_example,
#                 registered_model_name=registered_model_name,
#                 signature=signature,
#             )
#             print("📦 Model logged to MLflow successfully.")

#             encoder_path = "ordinal_encoder.pkl"

#             try:
#                 joblib.dump(ordinal_encoder, encoder_path)
#                 mlflow.log_artifact(encoder_path, artifact_path="encoders")
#                 print("📦 Ordinal encoder logged to MLflow successfully.")
#             finally:
#                 if os.path.exists(encoder_path):
#                     os.remove(encoder_path)

#             print("📦 Creating and logging SHAP explainer...")

#             # Temporarily disable autologging to prevent conflicts
#             mlflow.autolog(disable=True)

#             explainer_path = "shap_explainer.pkl"

#             try:
#                 # preprocessed_X_train, _ = best_estimator[:-1].fit_resample(
#                 #     X_train, y_train_enc
#                 # )
#                 background_data = X_train.sample(100, random_state=42)

#                 predict_fn = ShapModelWrapper(best_estimator, X_train.columns)

#                 explainer = shap.KernelExplainer(predict_fn, background_data)

#                 joblib.dump(explainer, explainer_path)
#                 mlflow.log_artifact(explainer_path, artifact_path="explainers")
#                 print("📦 SHAP explainer logged to MLflow successfully.")
#             finally:
#                 if os.path.exists(explainer_path):
#                     os.remove(explainer_path)
#                     print("🧹 Cleaned up local explainer file.")

        print("📦 Creating the SHAP explainer...")

        background_data = X_train.sample(
            SHAP_BACKGROUND_ROWS, random_state=SHAP_SEED
        )
        predict_function = ShapModelWrapper(best_estimator, X_train.columns)
        explainer = shap.KernelExplainer(predict_function, background_data)

        # The SHAP values plus the base value must add up to the model output.
        # Use a second explainer: after a call, an explainer cannot be pickled.
        checking_explainer = shap.KernelExplainer(predict_function, background_data)
        additivity_rows = X_test.iloc[:SHAP_ADDITIVITY_ROWS]
        explanation = checking_explainer(additivity_rows)
        additivity_error = max_additivity_error(
            shap_values=np.asarray(explanation.values),
            base_values=np.asarray(explanation.base_values),
            model_output=best_estimator.predict_proba(additivity_rows),
        )
        mlflow.log_metric("shap_max_additivity_error", additivity_error)
        print(f"🔎 Largest SHAP additivity error: {additivity_error:.6f}")

        version_folder = write_version(
            root=MODELS_DIR,
            model_name=model_name,
            pipeline=best_estimator,
            encoder=ordinal_encoder,
            explainer=explainer,
            created_at=datetime.now(timezone.utc),
            source=f"trained locally; MLflow experiment {EXPERIMENT_NAME}, run {run.info.run_id}; experiment run {selection.experiment_run_id}",
            library_versions={
                library: installed_version(library)
                for library in LIBRARIES_TO_RECORD
            },
        )
        mlflow.set_tag("model_version", version_folder.name)
        print(f"📦 Model saved to {version_folder}")

    print("DONE")


if __name__ == "__main__":
    train_model(str(TRAINING_DATA_PATH))
