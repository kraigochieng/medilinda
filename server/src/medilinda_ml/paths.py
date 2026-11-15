from pathlib import Path

# This file is at <repository>/server/src/medilinda_ml/paths.py. The training data
# and the notebooks stay in the top-level medilinda_ml folder, outside the server image.
PROJ_ROOT_DIR = Path(__file__).resolve().parents[3] / "medilinda_ml"

DATA_DIR = PROJ_ROOT_DIR / "data"

# The model store is in the server folder, so that the server image holds the models.
MODELS_DIR = Path(__file__).resolve().parents[2] / "models"
