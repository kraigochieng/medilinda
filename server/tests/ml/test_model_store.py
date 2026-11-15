from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import shap
from medilinda_ml.errors import (
    ModelIntegrityError,
    ModelNotFoundError,
    ModelStoreError,
    ModelVersionExistsError,
    ModelVersionNameError,
)
from medilinda_ml.model_store import (
    digest_contents,
    read_version,
    version_name,
    write_version,
)
from medilinda_ml.utils import ShapModelWrapper
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OrdinalEncoder

CREATED_AT = datetime(2025, 10, 8, 13, 35, 0, tzinfo=timezone.utc)
DIGEST = "3f9a1c2b7d4e" + "0" * 52
LIBRARY_VERSIONS: dict[str, str] = {"scikit-learn": "1.7.2"}


class Parts:
    """The three objects of one model, built small and fast."""

    def __init__(self, *, shift: float = 0.0) -> None:
        frame = pd.DataFrame({"a": [0.0, 1.0, 2.0, 3.0], "b": [1.0, 0.0, 1.0, 0.0]})
        frame["a"] = frame["a"] + shift
        labels = np.array([0, 0, 1, 1])
        self.pipeline = Pipeline(
            [("scale", MinMaxScaler()), ("model", LogisticRegression())]
        ).fit(frame, labels)
        self.encoder = OrdinalEncoder().fit(
            pd.DataFrame({"level": ["likely", "possible"]})
        )
        self.explainer = shap.KernelExplainer(
            ShapModelWrapper(self.pipeline, frame.columns), frame
        )
        self.frame = frame


def save(root: Path, parts: Parts, *, created_at: datetime = CREATED_AT) -> Path:
    return write_version(
        root=root,
        model_name="demo",
        pipeline=parts.pipeline,
        encoder=parts.encoder,
        explainer=parts.explainer,
        created_at=created_at,
        source="test",
        library_versions=LIBRARY_VERSIONS,
    )


def test_version_name_holds_the_time_and_the_start_of_the_digest():
    name = version_name(model_name="m", created_at=CREATED_AT, digest=DIGEST)

    assert name == "m-20251008T133500Z-3f9a1c2b7d4e"


def test_version_name_converts_the_time_to_utc():
    nairobi_time = CREATED_AT.astimezone(timezone(timedelta(hours=3)))

    name = version_name(model_name="m", created_at=nairobi_time, digest=DIGEST)

    assert name == "m-20251008T133500Z-3f9a1c2b7d4e"


@pytest.mark.parametrize(
    ("created_at", "digest", "model_name"),
    [
        (datetime(2025, 10, 8), DIGEST, "m"),
        (CREATED_AT, "abc", "m"),
        (CREATED_AT, DIGEST, "../m"),
    ],
)
def test_version_name_refuses_invalid_input(created_at, digest, model_name):
    with pytest.raises(ModelVersionNameError):
        version_name(model_name=model_name, created_at=created_at, digest=digest)


def test_the_digest_is_the_same_for_the_same_bytes():
    assert digest_contents(contents=[b"a", b"b"]) == digest_contents(
        contents=[b"a", b"b"]
    )


def test_the_digest_changes_when_one_byte_changes():
    assert digest_contents(contents=[b"a", b"b"]) != digest_contents(
        contents=[b"a", b"c"]
    )


def test_the_digest_changes_when_the_order_changes():
    assert digest_contents(contents=[b"a", b"b"]) != digest_contents(
        contents=[b"b", b"a"]
    )


def test_a_written_version_reads_back_and_predicts_the_same(tmp_path: Path):
    parts = Parts()
    save(tmp_path, parts)

    ensemble = read_version(root=tmp_path, version="latest")

    np.testing.assert_array_equal(
        ensemble.pipeline.predict(parts.frame), parts.pipeline.predict(parts.frame)
    )
    assert ensemble.encoder.categories_[0].tolist() == ["likely", "possible"]
    assert ensemble.version.startswith("demo-20251008T133500Z-")


def test_latest_points_to_the_newest_version(tmp_path: Path):
    save(tmp_path, Parts())
    newer = save(tmp_path, Parts(shift=5.0), created_at=CREATED_AT + timedelta(days=1))

    assert read_version(root=tmp_path, version="latest").version == newer.name


def test_an_older_version_still_reads_by_name(tmp_path: Path):
    older = save(tmp_path, Parts())
    save(tmp_path, Parts(shift=5.0), created_at=CREATED_AT + timedelta(days=1))

    assert read_version(root=tmp_path, version=older.name).version == older.name


def test_a_changed_file_fails_the_integrity_check(tmp_path: Path):
    folder = save(tmp_path, Parts())
    pipeline_file = folder / "pipeline.pkl"
    content = bytearray(pipeline_file.read_bytes())
    content[-1] ^= 1
    pipeline_file.write_bytes(bytes(content))

    with pytest.raises(ModelIntegrityError) as raised:
        read_version(root=tmp_path, version="latest")

    assert raised.value.file_name == "pipeline.pkl"


def test_a_missing_file_fails_the_integrity_check(tmp_path: Path):
    folder = save(tmp_path, Parts())
    (folder / "explainer.pkl").unlink()

    with pytest.raises(ModelIntegrityError) as raised:
        read_version(root=tmp_path, version="latest")

    assert raised.value.file_name == "explainer.pkl"


def test_a_missing_manifest_fails_the_integrity_check(tmp_path: Path):
    folder = save(tmp_path, Parts())
    (folder / "manifest.json").unlink()

    with pytest.raises(ModelIntegrityError):
        read_version(root=tmp_path, version="latest")


def test_an_unknown_version_is_not_found(tmp_path: Path):
    save(tmp_path, Parts())

    with pytest.raises(ModelNotFoundError):
        read_version(root=tmp_path, version="missing")


@pytest.mark.parametrize("version", ["../outside", "/etc", "a/b", ""])
def test_a_version_name_that_leaves_the_store_is_not_found(tmp_path: Path, version):
    with pytest.raises(ModelNotFoundError):
        read_version(root=tmp_path, version=version)


def test_latest_is_not_found_when_the_store_is_empty(tmp_path: Path):
    with pytest.raises(ModelNotFoundError):
        read_version(root=tmp_path, version="latest")


def test_latest_is_not_found_when_the_file_is_empty(tmp_path: Path):
    (tmp_path / "LATEST").write_text("\n")

    with pytest.raises(ModelNotFoundError):
        read_version(root=tmp_path, version="latest")


def test_writing_the_same_model_twice_is_refused(tmp_path: Path):
    parts = Parts()
    save(tmp_path, parts)

    with pytest.raises(ModelVersionExistsError):
        save(tmp_path, parts)


def test_every_store_error_derives_from_one_base_error():
    for error_type in (
        ModelIntegrityError,
        ModelNotFoundError,
        ModelVersionExistsError,
        ModelVersionNameError,
    ):
        assert issubclass(error_type, ModelStoreError)


def test_a_failed_write_leaves_no_folder_behind(tmp_path: Path):
    parts = Parts()

    with pytest.raises(ModelVersionNameError):
        write_version(
            root=tmp_path,
            model_name="../bad",
            pipeline=parts.pipeline,
            encoder=parts.encoder,
            explainer=parts.explainer,
            created_at=CREATED_AT,
            source="test",
            library_versions=LIBRARY_VERSIONS,
        )

    assert list(tmp_path.iterdir()) == []
