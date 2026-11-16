"""The MLflow tracking that the experiment and the training share."""

import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Final

import mlflow
import mlflow.sklearn
from medilinda_ml.paths import REPOSITORY_ROOT, SERVER_DIR, TRACKING_DIR
from medilinda_ml.tracking_store import make_absolute, make_relative

EXPERIMENT_NAME: Final[str] = "medilinda-causality"

LIBRARIES_TO_RECORD: Final[tuple[str, ...]] = (
    "scikit-learn",
    "imbalanced-learn",
    "numpy",
    "pandas",
    "scipy",
    "shap",
    "joblib",
    "mlflow",
)


def current_git_commit() -> str | None:
    """Side effect (runs git): the commit of the code that trains, or None if unknown."""
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).parent,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return completed.stdout.strip()


def start_local_tracking(*, tracking_dir: Path = TRACKING_DIR) -> None:
    """Side effect (disk): send MLflow runs to a local folder, and pick the experiment."""
    mlflow.set_tracking_uri(tracking_dir.as_uri())
    mlflow.set_experiment(EXPERIMENT_NAME)
    # The search and its candidates are logged. The model goes to the model store.
    mlflow.sklearn.autolog(log_models=False, log_datasets=False, silent=True)


@contextmanager
def portable_runs_folder() -> Iterator[None]:
    """Side effect (disk): keep the runs folder in the relative form outside the block.

    The folder is made absolute for MLflow, and relative again when the block ends,
    also after a failure. So git sees no path of this machine.
    """
    TRACKING_DIR.mkdir(parents=True, exist_ok=True)
    make_absolute(tracking_dir=TRACKING_DIR, server_dir=SERVER_DIR)
    try:
        yield
    finally:
        make_relative(
            tracking_dir=TRACKING_DIR,
            server_dir=SERVER_DIR,
            repository_root=REPOSITORY_ROOT,
        )
