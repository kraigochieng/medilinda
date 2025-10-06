from pathlib import Path

ARTIFACTS_DIR = Path(__file__).resolve().parent

# These paths rely on what is in MLFlow, change accordingly if required
ML_MODEL_PATH = f"{ARTIFACTS_DIR}/model/model.pkl"
SCALERS_PATH = f"{ARTIFACTS_DIR}/scalers/minmax_scaler.pkl"
ENCODERS_PATH = f"{ARTIFACTS_DIR}/encoders"
METADATA_PATH = f"{ARTIFACTS_DIR}/metadata/model_columns.json"