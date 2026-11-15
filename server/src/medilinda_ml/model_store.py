"""Write, read and verify versions of the model on disk.

A version is a folder. It holds the pipeline, the encoder, the explainer and a
manifest with the hash of each file. The folder name holds the creation time and
the start of the content hash, so the name sorts by time and proves the content.
A folder is never edited after it is written. A new model is a new folder.
"""

import hashlib
import io
import json
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import joblib
from imblearn.pipeline import Pipeline as ImbalancedLearnPipeline
from medilinda_ml.errors import (
    ModelIntegrityError,
    ModelNotFoundError,
    ModelVersionExistsError,
    ModelVersionNameError,
)
from pydantic import BaseModel, ConfigDict
from shap import KernelExplainer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

LATEST_FILE_NAME = "LATEST"
LATEST_ALIAS = "latest"
MANIFEST_FILE_NAME = "manifest.json"
PIPELINE_FILE_NAME = "pipeline.pkl"
ENCODER_FILE_NAME = "encoder.pkl"
EXPLAINER_FILE_NAME = "explainer.pkl"
VERSION_FILE_NAMES: tuple[str, ...] = (
    PIPELINE_FILE_NAME,
    ENCODER_FILE_NAME,
    EXPLAINER_FILE_NAME,
)
DIGEST_LENGTH_IN_NAME = 12

_SAFE_VERSION_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class ModelManifest(BaseModel):
    """The record of one model version, saved next to its files."""

    model_name: str
    version: str
    created_at: datetime
    source: str
    library_versions: dict[str, str]
    file_hashes: dict[str, str]
    digest: str


class ModelEnsemble(BaseModel):
    """What the server needs to answer a prediction request."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    version: str
    pipeline: Pipeline | ImbalancedLearnPipeline
    encoder: OrdinalEncoder
    explainer: KernelExplainer


def hash_bytes(*, content: bytes) -> str:
    """Return the SHA-256 of the content as hex digits."""
    return hashlib.sha256(content).hexdigest()


def digest_contents(*, contents: list[bytes]) -> str:
    """Return one digest for the contents of several files, in the given order."""
    outer_hash = hashlib.sha256()
    for content in contents:
        outer_hash.update(hash_bytes(content=content).encode("ascii"))
    return outer_hash.hexdigest()


def version_name(*, model_name: str, created_at: datetime, digest: str) -> str:
    """Build the folder name: model name, UTC time, and the start of the digest."""
    if created_at.tzinfo is None:
        raise ModelVersionNameError("created_at must have a time zone.")
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ModelVersionNameError("digest must be 64 lowercase hex digits.")
    if not _SAFE_VERSION_NAME.match(model_name):
        raise ModelVersionNameError(f"model_name '{model_name}' is not a safe name.")

    created_at_utc = created_at.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{model_name}-{created_at_utc}-{digest[:DIGEST_LENGTH_IN_NAME]}"


def _serialize(*, value: object) -> bytes:
    """Turn an object into the bytes of a joblib file."""
    buffer = io.BytesIO()
    joblib.dump(value, buffer)
    return buffer.getvalue()


def write_version(
    *,
    root: Path,
    model_name: str,
    pipeline: Pipeline | ImbalancedLearnPipeline,
    encoder: OrdinalEncoder,
    explainer: KernelExplainer,
    created_at: datetime,
    source: str,
    library_versions: dict[str, str],
) -> Path:
    """Side effect (disk): save a new version and point LATEST at it.

    The folder appears all at once, because the files go to a temporary folder
    first. Raise ModelVersionExistsError if the folder already exists.
    """
    contents: dict[str, bytes] = {
        PIPELINE_FILE_NAME: _serialize(value=pipeline),
        ENCODER_FILE_NAME: _serialize(value=encoder),
        EXPLAINER_FILE_NAME: _serialize(value=explainer),
    }
    digest = digest_contents(
        contents=[contents[file_name] for file_name in VERSION_FILE_NAMES]
    )
    version = version_name(model_name=model_name, created_at=created_at, digest=digest)
    version_folder = root / version

    if version_folder.exists():
        raise ModelVersionExistsError(version=version)

    manifest = ModelManifest(
        model_name=model_name,
        version=version,
        created_at=created_at,
        source=source,
        library_versions=library_versions,
        file_hashes={
            file_name: hash_bytes(content=content)
            for file_name, content in contents.items()
        },
        digest=digest,
    )

    root.mkdir(parents=True, exist_ok=True)
    temporary_folder = Path(tempfile.mkdtemp(prefix=".writing-", dir=root))
    try:
        for file_name, content in contents.items():
            (temporary_folder / file_name).write_bytes(content)
        (temporary_folder / MANIFEST_FILE_NAME).write_text(
            manifest.model_dump_json(indent=2), encoding="utf-8"
        )
        temporary_folder.chmod(0o755)
        temporary_folder.rename(version_folder)
    except BaseException:
        shutil.rmtree(temporary_folder, ignore_errors=True)
        raise

    latest_temporary = root / f".{LATEST_FILE_NAME}.writing"
    latest_temporary.write_text(version + "\n", encoding="utf-8")
    latest_temporary.replace(root / LATEST_FILE_NAME)

    return version_folder


def resolve_version(*, root: Path, version: str) -> str:
    """Side effect (disk): turn `latest` into a folder name, and check the name."""
    if version == LATEST_ALIAS:
        latest_file = root / LATEST_FILE_NAME
        if not latest_file.is_file():
            raise ModelNotFoundError(version=version)
        version = latest_file.read_text(encoding="utf-8").strip()

    if not version or not _SAFE_VERSION_NAME.match(version):
        raise ModelNotFoundError(version=version)
    if not (root / version).is_dir():
        raise ModelNotFoundError(version=version)

    return version


def read_manifest(*, root: Path, version: str) -> ModelManifest:
    """Side effect (disk): read and check the manifest of a version."""
    manifest_path = root / version / MANIFEST_FILE_NAME
    if not manifest_path.is_file():
        raise ModelIntegrityError(
            version=version, file_name=MANIFEST_FILE_NAME, reason="the file is missing"
        )
    try:
        manifest = ModelManifest.model_validate(
            json.loads(manifest_path.read_text(encoding="utf-8"))
        )
    except ValueError as error:
        raise ModelIntegrityError(
            version=version, file_name=MANIFEST_FILE_NAME, reason="the file is invalid"
        ) from error

    if manifest.version != version or not version.endswith(
        manifest.digest[:DIGEST_LENGTH_IN_NAME]
    ):
        raise ModelIntegrityError(
            version=version,
            file_name=MANIFEST_FILE_NAME,
            reason="the manifest does not match the folder name",
        )
    return manifest


def read_version(*, root: Path, version: str) -> ModelEnsemble:
    """Side effect (disk): load a version after every file hash matches its manifest."""
    folder_name = resolve_version(root=root, version=version)
    manifest = read_manifest(root=root, version=folder_name)

    contents: dict[str, bytes] = {}
    for file_name in VERSION_FILE_NAMES:
        file_path = root / folder_name / file_name
        if not file_path.is_file():
            raise ModelIntegrityError(
                version=folder_name, file_name=file_name, reason="the file is missing"
            )
        contents[file_name] = file_path.read_bytes()
        if hash_bytes(content=contents[file_name]) != manifest.file_hashes.get(
            file_name
        ):
            raise ModelIntegrityError(
                version=folder_name,
                file_name=file_name,
                reason="the hash does not match the manifest",
            )

    return ModelEnsemble(
        version=folder_name,
        pipeline=joblib.load(io.BytesIO(contents[PIPELINE_FILE_NAME])),
        encoder=joblib.load(io.BytesIO(contents[ENCODER_FILE_NAME])),
        explainer=joblib.load(io.BytesIO(contents[EXPLAINER_FILE_NAME])),
    )
