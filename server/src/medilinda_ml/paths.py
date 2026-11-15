from pathlib import Path

# The training data is in the package. The Dockerfile leaves the CSV files and the
# notebooks of the package out of the server image (see server/.dockerignore).
PACKAGE_DIR = Path(__file__).resolve().parent

DATA_DIR = PACKAGE_DIR / "data"

# The model store is in the server folder, so that the server image holds the models.
MODELS_DIR = Path(__file__).resolve().parents[2] / "models"
