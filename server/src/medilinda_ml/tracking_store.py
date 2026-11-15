"""Make the MLflow runs folder portable, so that it can be kept in git.

MLflow writes absolute paths into the run files. A copy of the folder on another
machine cannot open its artifacts. In the relative form, the artifact locations
are `mlruns/...` and MLflow must run from the `server` folder. Other absolute paths
(the training script, the data file) become paths from the repository root.
"""

import re
from collections.abc import Callable
from pathlib import Path

TRACKING_FOLDER_NAME = "mlruns"
ARTIFACTS_FOLDER_NAME = "artifacts"
_ARTIFACT_LOCATION_LINE = re.compile(
    rf"^(artifact_uri|artifact_location): {TRACKING_FOLDER_NAME}", flags=re.MULTILINE
)


def to_relative_text(*, text: str, server_dir: Path, repository_root: Path) -> str:
    """Pure: replace the absolute paths of this machine in the text of a run file."""
    tracking_uri = f"{server_dir.resolve().as_uri()}/{TRACKING_FOLDER_NAME}"
    converted = text.replace(tracking_uri, TRACKING_FOLDER_NAME)

    return converted.replace(f"{repository_root.resolve().as_posix()}/", "")


def to_absolute_text(*, text: str, server_dir: Path) -> str:
    """Pure: give the artifact locations in the text of a run file their full path."""
    tracking_uri = f"{server_dir.resolve().as_uri()}/{TRACKING_FOLDER_NAME}"

    return _ARTIFACT_LOCATION_LINE.sub(
        lambda match: f"{match.group(1)}: {tracking_uri}", text
    )


def _rewrite_run_files(*, tracking_dir: Path, convert: Callable[[str], str]) -> int:
    """Side effect (disk): rewrite each text file that the conversion changes.

    The artifacts of the runs stay as they are. Return the number of files changed.
    """
    changed_files = 0
    for path in tracking_dir.rglob("*"):
        is_artifact = ARTIFACTS_FOLDER_NAME in path.relative_to(tracking_dir).parts
        if not path.is_file() or is_artifact:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        converted = convert(text)
        if converted != text:
            path.write_text(converted, encoding="utf-8")
            changed_files += 1

    return changed_files


def make_relative(
    *, tracking_dir: Path, server_dir: Path, repository_root: Path
) -> int:
    """Side effect (disk): rewrite the folder to the relative form."""
    return _rewrite_run_files(
        tracking_dir=tracking_dir,
        convert=lambda text: to_relative_text(
            text=text, server_dir=server_dir, repository_root=repository_root
        ),
    )


def make_absolute(*, tracking_dir: Path, server_dir: Path) -> int:
    """Side effect (disk): give the artifact locations their full path on this machine."""
    return _rewrite_run_files(
        tracking_dir=tracking_dir,
        convert=lambda text: to_absolute_text(text=text, server_dir=server_dir),
    )
