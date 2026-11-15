"""One-off export of the current model from Databricks MLflow into a version folder.

Side effects: network (Databricks), disk (the model store).
Run it from the `server` folder with the Databricks settings in `.env`:

    uv sync --group train
    PYTHONPATH=src uv run python ../medilinda_ml/export_from_databricks.py \
        --model-uri models:/<name>/<version> --model-name medilinda_rf_smote_pipeline

The script checks that the raw pipeline gives the same output as the MLflow model
on sample rows. It stops if the two differ. It saves the sample rows and the
outputs in `golden.json` inside the version folder.
"""

import argparse
import os
import tempfile
from datetime import datetime, timezone
from importlib.metadata import version as installed_version
from pathlib import Path

import joblib
import mlflow
import numpy as np
from golden import GOLDEN_ROW_COUNT, build_golden_inputs, inputs_to_frame, write_golden
from medilinda_ml.model_store import write_version
from medilinda_ml.settings import settings
from server.config import ADR_CSV_PATH

LIBRARIES_TO_RECORD: tuple[str, ...] = (
    "scikit-learn",
    "imbalanced-learn",
    "numpy",
    "pandas",
    "scipy",
    "shap",
    "joblib",
    "mlflow",
)
ENCODER_ARTIFACT_PATH = "encoders/ordinal_encoder.pkl"
EXPLAINER_ARTIFACT_PATH = "explainers/shap_explainer.pkl"


def record_library_versions() -> dict[str, str]:
    """Return the installed version of each library that a pickle depends on."""
    return {name: installed_version(name) for name in LIBRARIES_TO_RECORD}


def export_model(*, model_uri: str, model_name: str, root: Path) -> Path:
    """Download the model, check it against the MLflow output, and save a version."""
    os.environ["DATABRICKS_HOST"] = settings.databricks_host
    os.environ["DATABRICKS_TOKEN"] = settings.databricks_token
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

    pyfunc_model = mlflow.pyfunc.load_model(model_uri)
    pipeline = mlflow.sklearn.load_model(model_uri)
    run_id: str = pyfunc_model.metadata.run_id

    with tempfile.TemporaryDirectory() as download_folder:
        encoder = joblib.load(
            mlflow.artifacts.download_artifacts(
                run_id=run_id,
                artifact_path=ENCODER_ARTIFACT_PATH,
                dst_path=download_folder,
            )
        )
        explainer = joblib.load(
            mlflow.artifacts.download_artifacts(
                run_id=run_id,
                artifact_path=EXPLAINER_ARTIFACT_PATH,
                dst_path=download_folder,
            )
        )

    golden_records = build_golden_inputs(
        adr_csv_path=ADR_CSV_PATH, row_count=GOLDEN_ROW_COUNT
    )
    golden_frame = inputs_to_frame(records=golden_records)
    expected_outputs: np.ndarray = np.asarray(pyfunc_model.predict(golden_frame))
    raw_outputs: np.ndarray = np.asarray(pipeline.predict(golden_frame))
    if not np.array_equal(expected_outputs, raw_outputs):
        raise SystemExit(
            "The raw pipeline and the MLflow model give different outputs. "
            f"MLflow: {expected_outputs.tolist()}. Raw: {raw_outputs.tolist()}. "
            "Nothing was saved."
        )

    version_folder = write_version(
        root=root,
        model_name=model_name,
        pipeline=pipeline,
        encoder=encoder,
        explainer=explainer,
        created_at=datetime.now(timezone.utc),
        source=f"databricks run {run_id}, {model_uri}",
        library_versions=record_library_versions(),
    )
    write_golden(version_folder=version_folder, expected_outputs=expected_outputs.tolist())
    return version_folder


def main() -> None:
    """Parse the command line and run the export."""
    parser = argparse.ArgumentParser(
        description="Export the model from Databricks MLflow into a version folder.",
        epilog="Example: --model-uri models:/workspace.default.m/3 --model-name m",
    )
    parser.add_argument("--model-uri", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--root", type=Path, default=Path("models"))
    arguments = parser.parse_args()

    version_folder = export_model(
        model_uri=arguments.model_uri,
        model_name=arguments.model_name,
        root=arguments.root,
    )
    print(f"Saved {version_folder}")


if __name__ == "__main__":
    main()
