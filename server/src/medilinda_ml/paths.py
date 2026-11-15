from pathlib import Path

# The training data is in the package. The Dockerfile leaves the CSV files and the
# notebooks of the package out of the server image (see server/.dockerignore).
PACKAGE_DIR = Path(__file__).resolve().parent

DATA_DIR = PACKAGE_DIR / "data"

SERVER_DIR = Path(__file__).resolve().parents[2]
REPOSITORY_ROOT = SERVER_DIR.parent

# The model store is in the server folder, so that the server image holds the models.
MODELS_DIR = SERVER_DIR / "models"

# MLflow keeps the runs of the experiments in this folder. It is in git, with relative
# paths (see tracking_store.py), and not in the server image. Open it from the server
# folder with `mlflow ui --backend-store-uri mlruns`.
TRACKING_DIR = SERVER_DIR / "mlruns"
