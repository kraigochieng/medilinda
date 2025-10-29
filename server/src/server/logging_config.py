import logging
import sys  # <-- 1. Import sys to get stdout
from pathlib import Path


def setup_logging():
    """
    Configures the root logger for the entire application.
    """
    current_file = Path(__file__).resolve()
    BASE_DIR = current_file.parent.parent
    LOG_FILE_PATH = BASE_DIR / "basic.log"

    log_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(LOG_FILE_PATH)
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
    logger.debug(
        f"Logging configured. File: {LOG_FILE_PATH}, Console: True"
    )
