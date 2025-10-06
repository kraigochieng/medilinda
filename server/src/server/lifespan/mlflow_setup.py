import os
from typing import TypedDict

import joblib
import mlflow
from mlflow.pyfunc import PyFuncModel
from sklearn.preprocessing import OrdinalEncoder


class MLEnsemble(TypedDict):
    model: PyFuncModel
    encoder: OrdinalEncoder


def mlflow_setup(
    databricks_host: str,
    databricks_token: str,
    mlflow_tracking_uri: str,
    mlflow_artifact_path: str,
    mlflow_experiment_path: str,
    mlflow_model_name: str,
    mlflow_model_version: str,
    local_artifacts_path: str = "./artifacts",
) -> MLEnsemble:
    os.environ["DATABRICKS_HOST"] = databricks_host
    os.environ["DATABRICKS_TOKEN"] = databricks_token

    os.environ["MLFLOW_TRACKING_URI"] = mlflow_tracking_uri

    # Set tracking URI
    mlflow.set_tracking_uri(mlflow_tracking_uri)

    if mlflow.get_experiment_by_name(mlflow_experiment_path) is None:
        mlflow.create_experiment(
            name=mlflow_experiment_path,
            artifact_location=mlflow_artifact_path,
        )

    mlflow.set_experiment(mlflow_experiment_path)

    model_uri = f"models:/{mlflow_model_name}/{mlflow_model_version}"

    model = mlflow.pyfunc.load_model(model_uri)

    run_id = model.metadata.run_id
    encoder_path_on_server = f"encoders/ordinal_encoder.pkl"

    if not os.path.exists(local_artifacts_path):
        os.mkdir(local_artifacts_path)

    local_encoder_path = mlflow.artifacts.download_artifacts(
        run_id=run_id,
        artifact_path=encoder_path_on_server,
        dst_path=local_artifacts_path,
    )

    ordinal_encoder: OrdinalEncoder = joblib.load(local_encoder_path)

    return {"model": model, "encoder": ordinal_encoder}


# # --- Example Usage ---
# if __name__ == "__main__":
#     from server.settings import settings

#     # Call the setup function
#     ml_ensemble: MLEnsemble = mlflow_setup(
#         databricks_host=settings.databricks_host,
#         databricks_token=settings.databricks_token,
#         mlflow_tracking_uri=settings.mlflow_tracking_uri,
#         mlflow_experiment_path=settings.mlflow_experiment_path,
#         mlflow_artifact_path=settings.mlflow_artifact_path,
#         mlflow_model_name=settings.mlflow_model_name,
#         mlflow_model_version=settings.mlflow_model_version,
#     )

#     # Now you can use both objects
#     print("Model:", ml_ensemble["model"])
#     print("Encoder Categories:", ml_ensemble["encoder"])
