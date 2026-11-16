import matplotlib

matplotlib.use("agg")

import logging
from datetime import datetime, timezone
from importlib.metadata import version as installed_version
from pathlib import Path
from pprint import pprint

import mlflow
import mlflow.data
import mlflow.sklearn
import numpy as np
import pandas as pd
import shap
from medilinda_ml.columns import FINAL_COLUMNS, TARGET_COLUMN
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
from medilinda_ml.evaluation import classify, headline_metrics, max_additivity_error
from medilinda_ml.model_store import write_version
from medilinda_ml.paths import DATA_DIR, MODELS_DIR
from medilinda_ml.utils import ShapModelWrapper
# The model goes to the model store. MLflow tracks the experiment in a local folder.
# MLFLOW-DISABLED (#119): the Databricks and model logging code below stays off.
# import joblib
# import mlflow
# from medilinda_ml.settings import settings
# from medilinda_ml.signature import signature
# from mlflow.models import infer_signature
from sklearn.metrics import classification_report
from sklearn.model_selection import (
    RandomizedSearchCV,
    RepeatedStratifiedKFold,
    train_test_split,
)

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


SPLIT_SEED = 42
TEST_FRACTION = 0.25
VALIDATION_FRACTION = 0.2
CV_SPLITS = 5
CV_REPEATS = 3
SCORING = "f1_weighted"
MAX_SEARCH_DRAWS = 20
SHAP_BACKGROUND_ROWS = 100
SHAP_SEED = 42
SHAP_ADDITIVITY_ROWS = 5


def train_model(df_path: str) -> None:
    """Side effect (disk): train, and keep the runs folder in the relative form."""
    with portable_runs_folder():
        run_training(df_path=df_path)


def run_training(df_path: str) -> None:
    start_local_tracking()
    df = pd.read_csv(df_path)

    X = df.drop(columns=[TARGET_COLUMN], axis=1)
    y = df[TARGET_COLUMN]

    X_train_and_val, X_test, y_train_and_val, y_test = train_test_split(
        X, y, stratify=y, test_size=TEST_FRACTION, random_state=SPLIT_SEED
    )

    X_train, X_val, y_train, y_val = train_test_split(
        X_train_and_val,
        y_train_and_val,
        stratify=y_train_and_val,
        test_size=VALIDATION_FRACTION,
        random_state=SPLIT_SEED,
    )

    ordinal_encoder = OrdinalEncoder(
        categories=[["certain", "likely", "possible", "unlikely"]]
    )

    y_train_enc = ordinal_encoder.fit_transform(y_train.to_frame()).ravel()
    y_val_enc = ordinal_encoder.transform(y_val.to_frame()).ravel()
    y_test_enc = ordinal_encoder.transform(y_test.to_frame()).ravel()

    print("✅ Train shape:", X_train.shape)
    print("✅ Validation shape:", X_val.shape)
    print("✅ Test shape:", X_test.shape)

    # The experiment (notebook 3.3) compares all candidates. This training still
    # trains the decision tree only.
    selected_candidate = candidate_named(name="decision_tree")
    estimators_and_param_grids = {
        selected_candidate.name: (selected_candidate.estimator, selected_candidate.param_grid),
    }
    # --- Cross-validation setup ---
    cv = RepeatedStratifiedKFold(
        n_splits=CV_SPLITS, n_repeats=CV_REPEATS, random_state=SPLIT_SEED
    )

    best_estimators_and_best_param_grids = {}

    for name, (estimator, param_grid) in estimators_and_param_grids.items():
        print(f"\n🧠 Training model: {name}")
        print("—" * 80)

        # --- Build full pipeline for this estimator ---
        pipeline = build_pipeline(estimator=estimator, final_columns=FINAL_COLUMNS)

        # # --- Run pipeline on training data ---
        # print("\n🚀 Running pipeline...")
        # X_train_resampled, y_train_resampled = pipeline.fit_resample(
        #     X_train, y_train_enc
        # )

        # # --- Display results ---
        # print("\n✅ Pipeline output:")
        # print(pd.DataFrame(X_train_resampled).info())
        # print("\nOutput shape:", X_train_resampled.shape)

        # # --- Check class balance ---
        # print("Before SMOTE:")
        # print(pd.Series(y_train_enc).value_counts(normalize=True))
        # print("\nAfter SMOTE:")
        # print(pd.Series(y_train_resampled).value_counts(normalize=True))

        # Prefix param grid keys with "classifier__"
        tuned_params = {f"classifier__{k}": v for k, v in param_grid.items()}

        # --- RandomizedSearchCV ---
        search = RandomizedSearchCV(
            estimator=pipeline,
            param_distributions=tuned_params,
            cv=cv,
            n_iter=int(
                min(MAX_SEARCH_DRAWS, np.prod([len(v) for v in tuned_params.values()]))
            ),
            scoring=SCORING,
            random_state=SPLIT_SEED,
            verbose=2,
            n_jobs=-1,
        )

        with mlflow.start_run(run_name=f"{name}") as run:
            mlflow.log_input(
                mlflow.data.from_pandas(
                    df, source=str(df_path), name=Path(df_path).name, targets=TARGET_COLUMN
                ),
                context="training",
            )
            mlflow.log_params(
                {
                    "split_seed": SPLIT_SEED,
                    "test_fraction": TEST_FRACTION,
                    "validation_fraction": VALIDATION_FRACTION,
                    "stratified": True,
                    "cv_splits": CV_SPLITS,
                    "cv_repeats": CV_REPEATS,
                    "scoring": SCORING,
                    "train_rows": len(X_train),
                    "validation_rows": len(X_val),
                    "test_rows": len(X_test),
                    "shap_background_rows": SHAP_BACKGROUND_ROWS,
                    "shap_seed": SHAP_SEED,
                }
            )
            mlflow.set_tags(
                {
                    "git_commit": current_git_commit() or "unknown",
                    **{
                        f"library.{library}": installed_version(library)
                        for library in LIBRARIES_TO_RECORD
                    },
                }
            )

            search.fit(X_train, y_train_enc)

            # --- Results ---
            best_estimator = search.best_estimator_
            best_params = search.best_params_

            best_estimators_and_best_param_grids[name] = (best_estimator, best_params)

            print("\n✅ Best params:")
            pprint(best_params)

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

            # --- Log model ---
            # signature = infer_signature(X_test, y_pred)

            # input_example = X_test.iloc[:1]

            model_name = f"medilinda_rf_smote_pipeline_{name}"

            registered_model_name = f"workspace.default.{model_name}"

            # Disable verbose params
            print("📦 Disabling verbose logging for production artifact...")

            verbose_params_to_disable = {
                key: False
                for key in best_estimator.get_params().keys()
                if key.endswith("__verbose")
            }

            if verbose_params_to_disable:
                best_estimator.set_params(**verbose_params_to_disable)

                logging.info(
                    f"Disabled {len(verbose_params_to_disable)} verbose flags."
                )
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
                source=f"trained locally; MLflow experiment {EXPERIMENT_NAME}, run {run.info.run_id}",
                library_versions={
                    library: installed_version(library)
                    for library in LIBRARIES_TO_RECORD
                },
            )
            mlflow.set_tag("model_version", version_folder.name)
            print(f"📦 Model saved to {version_folder}")

        print("DONE")


if __name__ == "__main__":
    train_model(f"{DATA_DIR}/data.csv")
