from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parent


DATA_DIR = SERVER_DIR / "data"

# The model store is in the server folder, next to src. The Dockerfile copies it.
MODELS_DIR = SERVER_DIR.parents[1] / "models"

ADR_CSV_PATH = DATA_DIR / "adr.csv"
MEDICAL_INSTITUTIONS_CSV_PATH = DATA_DIR / "medical_institutions.csv"
USERS_CSV_PATH = DATA_DIR / "users.csv"
