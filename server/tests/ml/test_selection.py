"""The selection file (#143): one test for each row of the contract."""

from pathlib import Path

import pytest
from medilinda_ml.errors import (
    MedilindaMlError,
    SelectionDataMismatchError,
    SelectionError,
    SelectionInvalidError,
    SelectionNotFoundError,
)
from medilinda_ml.model_store import hash_bytes
from medilinda_ml.selection import (
    ModelSelection,
    check_data_matches,
    hash_data_file,
    read_selection,
    write_selection,
)
from pydantic import ValidationError


def make_selection(*, data_sha256: str = "a" * 64) -> ModelSelection:
    return ModelSelection(
        estimator="random_forest",
        params={"max_depth": 10, "max_features": "sqrt", "n_estimators": 100},
        features=["dechallenge_yes", "patient_bmi"],
        data_sha256=data_sha256,
        split_seed=42,
        experiment_run_id="abc123",
        cv_weighted_f1=0.87,
    )


def test_a_selection_survives_a_write_and_a_read(tmp_path: Path):
    path = tmp_path / "selection.json"
    selection = make_selection()

    write_selection(path=path, selection=selection)

    assert read_selection(path=path) == selection


def test_a_write_leaves_no_temporary_file(tmp_path: Path):
    write_selection(path=tmp_path / "selection.json", selection=make_selection())

    assert [file.name for file in tmp_path.iterdir()] == ["selection.json"]


def test_a_write_replaces_an_older_selection(tmp_path: Path):
    path = tmp_path / "selection.json"
    write_selection(path=path, selection=make_selection())
    newer = make_selection().model_copy(update={"estimator": "decision_tree"})

    write_selection(path=path, selection=newer)

    assert read_selection(path=path).estimator == "decision_tree"


def test_a_missing_file_raises_not_found_with_the_path(tmp_path: Path):
    path = tmp_path / "selection.json"

    with pytest.raises(SelectionNotFoundError) as error:
        read_selection(path=path)

    assert error.value.path == path


def test_text_that_is_not_json_raises_invalid_and_keeps_the_cause(tmp_path: Path):
    path = tmp_path / "selection.json"
    path.write_text("not json")

    with pytest.raises(SelectionInvalidError) as error:
        read_selection(path=path)

    assert error.value.path == path
    assert isinstance(error.value.__cause__, ValidationError)


def test_a_missing_field_raises_invalid(tmp_path: Path):
    path = tmp_path / "selection.json"
    path.write_text('{"estimator": "random_forest"}')

    with pytest.raises(SelectionInvalidError):
        read_selection(path=path)


def test_an_unknown_key_raises_invalid(tmp_path: Path):
    path = tmp_path / "selection.json"
    write_selection(path=path, selection=make_selection())
    path.write_text(path.read_text().replace("{", '{"surprise": 1,', 1))

    with pytest.raises(SelectionInvalidError):
        read_selection(path=path)


def test_an_empty_feature_list_is_not_valid():
    with pytest.raises(ValidationError):
        ModelSelection.model_validate(make_selection().model_dump() | {"features": []})


def test_a_data_hash_that_is_not_64_hex_digits_is_not_valid():
    with pytest.raises(ValidationError):
        ModelSelection.model_validate(make_selection().model_dump() | {"data_sha256": "xyz"})


def test_the_data_hash_is_the_sha256_of_the_file_bytes(tmp_path: Path):
    data_path = tmp_path / "data.csv"
    data_path.write_bytes(b"a,b\n1,2\n")

    assert hash_data_file(path=data_path) == hash_bytes(content=b"a,b\n1,2\n")


def test_data_that_matches_the_selection_passes(tmp_path: Path):
    data_path = tmp_path / "data.csv"
    data_path.write_bytes(b"a,b\n1,2\n")
    selection = make_selection(data_sha256=hash_data_file(path=data_path))

    check_data_matches(selection=selection, data_path=data_path)


def test_changed_data_raises_a_mismatch_with_both_hashes(tmp_path: Path):
    data_path = tmp_path / "data.csv"
    data_path.write_bytes(b"a,b\n1,2\n")
    selection = make_selection(data_sha256=hash_data_file(path=data_path))
    data_path.write_bytes(b"a,b\n1,3\n")

    with pytest.raises(SelectionDataMismatchError) as error:
        check_data_matches(selection=selection, data_path=data_path)

    assert error.value.expected == selection.data_sha256
    assert error.value.actual == hash_data_file(path=data_path)


def test_every_selection_error_derives_from_the_selection_base():
    for error_type in (
        SelectionNotFoundError,
        SelectionInvalidError,
        SelectionDataMismatchError,
    ):
        assert issubclass(error_type, SelectionError)
    assert issubclass(SelectionError, MedilindaMlError)
