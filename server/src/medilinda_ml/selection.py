"""The selection file: the decision of the experiment, read by the production training.

The experiment (notebook 3.3) writes `selection.json`. The training reads it, so
the model in production is the model that the experiment chose.
"""

import os
from pathlib import Path

from medilinda_ml.errors import (
    SelectionDataMismatchError,
    SelectionInvalidError,
    SelectionNotFoundError,
)
from medilinda_ml.model_store import hash_bytes
from pydantic import BaseModel, ConfigDict, Field, JsonValue, ValidationError


class ModelSelection(BaseModel):
    """What the experiment chose, and what it needs to prove where the choice came from."""

    model_config = ConfigDict(extra="forbid")

    estimator: str = Field(min_length=1)
    params: dict[str, JsonValue]
    features: list[str] = Field(min_length=1)
    data_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    split_seed: int
    experiment_run_id: str = Field(min_length=1)
    cv_weighted_f1: float


def hash_data_file(*, path: Path) -> str:
    """Side effect (disk): return the SHA-256 of the data file as hex digits."""
    return hash_bytes(content=path.read_bytes())


def write_selection(*, path: Path, selection: ModelSelection) -> None:
    """Side effect (disk): write the selection, so a reader sees all of it or none of it."""
    temporary_path = path.with_name(f"{path.name}.tmp")
    temporary_path.write_text(selection.model_dump_json(indent=2) + "\n")
    os.replace(temporary_path, path)


def read_selection(*, path: Path) -> ModelSelection:
    """Side effect (disk): read and check the selection.

    Raises SelectionNotFoundError if the file is missing, and SelectionInvalidError
    if its content is not a valid selection.
    """
    try:
        text = path.read_text()
    except FileNotFoundError as error:
        raise SelectionNotFoundError(path=path) from error
    try:
        return ModelSelection.model_validate_json(text)
    except ValidationError as error:
        raise SelectionInvalidError(path=path, reason=str(error)) from error


def check_data_matches(*, selection: ModelSelection, data_path: Path) -> None:
    """Side effect (disk): raise SelectionDataMismatchError if the data changed since the experiment."""
    actual = hash_data_file(path=data_path)
    if actual != selection.data_sha256:
        raise SelectionDataMismatchError(
            data_path=data_path, expected=selection.data_sha256, actual=actual
        )
