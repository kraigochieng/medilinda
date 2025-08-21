from pathlib import Path
from sqlalchemy import create_engine

# Path to the SQLite DB file (next to this file)
DB_PATH = Path(__file__).resolve().parent / "db.sqlite"