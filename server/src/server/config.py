from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parent


DATA_DIR = SERVER_DIR / "data"

ADR_CSV_PATH = DATA_DIR / "adr.csv"
MEDICAL_INSTITUTIONS_CSV_PATH = DATA_DIR / "medical_institution.csv"
USERS_CSV_PATH = DATA_DIR / "users.csv"
