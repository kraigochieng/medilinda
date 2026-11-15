from pathlib import Path

import pytest
from medilinda_ml.tracking_store import (
    make_absolute,
    make_relative,
    to_absolute_text,
    to_relative_text,
)


@pytest.fixture
def server_dir(tmp_path: Path) -> Path:
    return tmp_path / "repo" / "server"


@pytest.fixture
def repository_root(server_dir: Path) -> Path:
    return server_dir.parent


def absolute_location(server_dir: Path, tail: str) -> str:
    return f"{server_dir.resolve().as_uri()}/mlruns/{tail}"


def test_relative_text_replaces_the_artifact_location(server_dir, repository_root):
    text = f"artifact_uri: {absolute_location(server_dir, '1/abc/artifacts')}\n"

    converted = to_relative_text(
        text=text, server_dir=server_dir, repository_root=repository_root
    )

    assert converted == "artifact_uri: mlruns/1/abc/artifacts\n"


def test_relative_text_makes_other_paths_start_at_the_repository_root(
    server_dir, repository_root
):
    text = f"source: {repository_root.resolve()}/server/src/train.py\n"

    converted = to_relative_text(
        text=text, server_dir=server_dir, repository_root=repository_root
    )

    assert converted == "source: server/src/train.py\n"


def test_relative_text_leaves_a_text_without_paths_unchanged(
    server_dir, repository_root
):
    text = "metric 0.9 1\n"

    assert (
        to_relative_text(
            text=text, server_dir=server_dir, repository_root=repository_root
        )
        == text
    )


def test_absolute_text_restores_the_artifact_location(server_dir):
    converted = to_absolute_text(
        text="artifact_location: mlruns/1\nname: x\n", server_dir=server_dir
    )

    assert converted == f"artifact_location: {absolute_location(server_dir, '1')}\nname: x\n"


def test_absolute_text_leaves_a_parameter_that_starts_with_mlruns_unchanged(server_dir):
    text = "source: mlruns/1\n"

    assert to_absolute_text(text=text, server_dir=server_dir) == text


def write_store(tracking_dir: Path, server_dir: Path, repository_root: Path) -> None:
    run_dir = tracking_dir / "1" / "abc"
    (run_dir / "artifacts").mkdir(parents=True)
    (run_dir / "tags").mkdir()
    (run_dir / "meta.yaml").write_text(
        f"artifact_uri: {absolute_location(server_dir, '1/abc/artifacts')}\n"
    )
    (run_dir / "tags" / "mlflow.source.name").write_text(
        f"{repository_root.resolve()}/server/src/train.py"
    )
    (run_dir / "artifacts" / "report.json").write_text(
        f'{{"path": "{repository_root.resolve()}/data.csv"}}'
    )
    (run_dir / "artifacts" / "plot.png").write_bytes(b"\x89PNG\xff\xfe")


def test_make_relative_leaves_no_path_of_this_machine_outside_the_artifacts(
    tmp_path, server_dir, repository_root
):
    tracking_dir = server_dir / "mlruns"
    write_store(tracking_dir, server_dir, repository_root)

    changed = make_relative(
        tracking_dir=tracking_dir,
        server_dir=server_dir,
        repository_root=repository_root,
    )

    assert changed == 2
    leaked = [
        path
        for path in tracking_dir.rglob("*")
        if path.is_file()
        and "artifacts" not in path.parts
        and str(tmp_path) in path.read_text()
    ]
    assert leaked == []


def test_make_relative_does_not_touch_the_artifacts(
    server_dir, repository_root
):
    tracking_dir = server_dir / "mlruns"
    write_store(tracking_dir, server_dir, repository_root)
    artifacts = tracking_dir / "1" / "abc" / "artifacts"
    before = {path.name: path.read_bytes() for path in artifacts.iterdir()}

    make_relative(
        tracking_dir=tracking_dir, server_dir=server_dir, repository_root=repository_root
    )

    assert {path.name: path.read_bytes() for path in artifacts.iterdir()} == before


def test_a_second_make_relative_changes_nothing(server_dir, repository_root):
    tracking_dir = server_dir / "mlruns"
    write_store(tracking_dir, server_dir, repository_root)
    make_relative(
        tracking_dir=tracking_dir, server_dir=server_dir, repository_root=repository_root
    )

    assert (
        make_relative(
            tracking_dir=tracking_dir,
            server_dir=server_dir,
            repository_root=repository_root,
        )
        == 0
    )


def test_relative_then_absolute_restores_the_artifact_location(
    server_dir, repository_root
):
    tracking_dir = server_dir / "mlruns"
    write_store(tracking_dir, server_dir, repository_root)
    make_relative(
        tracking_dir=tracking_dir, server_dir=server_dir, repository_root=repository_root
    )

    make_absolute(tracking_dir=tracking_dir, server_dir=server_dir)

    meta = (tracking_dir / "1" / "abc" / "meta.yaml").read_text()
    assert meta == f"artifact_uri: {absolute_location(server_dir, '1/abc/artifacts')}\n"


def test_the_folder_functions_skip_a_binary_file(server_dir, repository_root):
    tracking_dir = server_dir / "mlruns"
    tracking_dir.mkdir(parents=True)
    (tracking_dir / "binary.dat").write_bytes(b"\xff\xfe\x00")

    assert (
        make_relative(
            tracking_dir=tracking_dir,
            server_dir=server_dir,
            repository_root=repository_root,
        )
        == 0
    )
