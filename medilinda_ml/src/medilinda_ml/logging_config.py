import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from medilinda_ml.settings import settings


def setup_logging():
    """
    Configures the root logger for the entire application.
    """
    current_file = Path(__file__).resolve()
    BASE_DIR = current_file.parent.parent.parent
    LOG_FILE_PATH = BASE_DIR / "basic.log"

    # if settings.environment == "development":
    #     logging_level = logging.DEBUG
    # elif settings.environment == "production":
    #     logging_level = logging.INFO
    # else:
    #     logging_level = logging.INFO

    log_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # file_handler = logging.FileHandler(LOG_FILE_PATH)

    MAX_LOG_SIZE = 10 * 1024 * 1024
    BACKUP_COUNT = 3

    file_handler = RotatingFileHandler(
        LOG_FILE_PATH, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT
    )
    file_handler.setFormatter(log_formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler],  # <-- Pass both handlers
        force=True,
    )

    # Add a log message to confirm setup
    logger = logging.getLogger(__name__)
    logger.debug(f"Logging configured. File: {LOG_FILE_PATH}, Console: True")
