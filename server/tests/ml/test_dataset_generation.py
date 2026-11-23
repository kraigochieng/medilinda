"""Tests of the dataset rows, the generator, and the validation."""

import random
from datetime import date
from pathlib import Path

import pandas as pd
import pytest
from medilinda_ml.case_facts import CausalityLevel
from medilinda_ml.case_sampler import sample_case
from medilinda_ml.data_generation import diagnostics_path_for, generate_tables, write_tables
from medilinda_ml.dataset_rows import (
    DATASET_COLUMNS,
    DIAGNOSTIC_COLUMNS,
    TARGET_COLUMN,
    apply_label_noise,
    case_to_row,
    report_from_row,
)
from medilinda_ml.dataset_validation import (
    check_consistency,
    check_label_is_rule_output,
    check_label_noise,
    render_markdown,
    validate_dataset,
)
from medilinda_ml.selection import hash_data_file
from medilinda_ml.who_umc import assess
from medilinda_ml.yellow_form_mapping import facts_from_report

REFERENCE_DATE = date(2026, 11, 1)


@pytest.fixture(scope="module")
def tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    """A small generated dataset and its diagnostics, shared by the tests."""
    return generate_tables(rows=1500, seed=3, label_noise=0.05)


def test_the_row_has_the_dataset_columns_in_order() -> None:
    case = sample_case(random_source=random.Random(1), reference_date=REFERENCE_DATE)
    row = case_to_row(case=case, level=CausalityLevel.POSSIBLE)

    assert list(row) == DATASET_COLUMNS
    assert row[TARGET_COLUMN] == "possible"


def test_the_row_uses_the_words_of_the_app() -> None:
    random_source = random.Random(2)
    rows = [case_to_row(case=sample_case(random_source=random_source, reference_date=REFERENCE_DATE), level=CausalityLevel.LIKELY) for _ in range(300)]
    frame = pd.DataFrame(rows)

    assert set(frame["dechallenge"]) <= {"yes", "no", "unknown", "na"}
    assert set(frame["action_taken"]) <= {"drug withdrawn", "dose reduced", "dose increased", "dose not changed", "not applicable", "unknown"}
    assert set(frame["pregnancy_status"]) <= {"not applicable", "not pregnant", "1st trimester", "2nd trimester", "3rd trimester"}
    assert set(frame["known_allergy"]) <= {"yes", "no"}


def test_the_report_rebuilt_from_a_row_gives_the_same_level() -> None:
    random_source = random.Random(4)
    for _ in range(300):
        case = sample_case(random_source=random_source, reference_date=REFERENCE_DATE)
        expected = assess(facts=facts_from_report(report=case.report))
        row = case_to_row(case=case, level=expected)
        rebuilt = assess(facts=facts_from_report(report=report_from_row(row=row)))

        assert rebuilt is expected


def test_label_noise_moves_one_step_and_leaves_the_two_unclassified_levels() -> None:
    random_source = random.Random(5)
    moved = {apply_label_noise(level=CausalityLevel.POSSIBLE, random_source=random_source, rate=1.0) for _ in range(100)}

    assert moved == {CausalityLevel.UNLIKELY, CausalityLevel.LIKELY}
    assert apply_label_noise(level=CausalityLevel.UNCLASSIFIED, random_source=random_source, rate=1.0) is CausalityLevel.UNCLASSIFIED
    assert apply_label_noise(level=CausalityLevel.UNCLASSIFIABLE, random_source=random_source, rate=1.0) is CausalityLevel.UNCLASSIFIABLE
    assert apply_label_noise(level=CausalityLevel.CERTAIN, random_source=random_source, rate=1.0) is CausalityLevel.LIKELY
    assert apply_label_noise(level=CausalityLevel.UNLIKELY, random_source=random_source, rate=1.0) is CausalityLevel.POSSIBLE
    assert apply_label_noise(level=CausalityLevel.POSSIBLE, random_source=random_source, rate=0.0) is CausalityLevel.POSSIBLE


def test_the_same_seed_gives_the_same_tables(tables: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    again = generate_tables(rows=1500, seed=3, label_noise=0.05)

    pd.testing.assert_frame_equal(tables[0], again[0])
    pd.testing.assert_frame_equal(tables[1], again[1])


def test_the_dataset_has_no_diagnostic_column(tables: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    dataset, diagnostics = tables

    assert list(dataset.columns) == DATASET_COLUMNS
    assert list(diagnostics.columns) == DIAGNOSTIC_COLUMNS
    assert not set(DIAGNOSTIC_COLUMNS) & set(dataset.columns)


def test_the_compressed_file_has_the_same_bytes_every_time(tmp_path: Path, tables: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    first = tmp_path / "first.csv.gz"
    second = tmp_path / "second.csv.gz"
    write_tables(dataset=tables[0], diagnostics=tables[1], dataset_path=first)
    write_tables(dataset=tables[0], diagnostics=tables[1], dataset_path=second)

    assert hash_data_file(path=first) == hash_data_file(path=second)
    assert diagnostics_path_for(dataset_path=first).name == "first_diagnostics.csv.gz"
    pd.testing.assert_frame_equal(pd.read_csv(first)[["patient_age", TARGET_COLUMN]], tables[0][["patient_age", TARGET_COLUMN]])


def test_a_generated_dataset_passes_the_validation(tables: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    dataset, diagnostics = tables
    report = validate_dataset(dataset=dataset, diagnostics=diagnostics, label_noise=0.05, minimum_rows_per_level=1)

    failed = [check for check in report.checks if not check.passed]
    assert not failed, failed
    assert "# Report on the synthetic data" in render_markdown(report=report, seed=3, label_noise=0.05)


def test_the_validation_catches_a_label_that_the_rules_did_not_give(tables: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    dataset, diagnostics = tables
    tampered = diagnostics.copy()
    tampered.loc[0, "causality_by_rule"] = "certain" if tampered.loc[0, "causality_by_rule"] != "certain" else "likely"

    assert not check_label_is_rule_output(dataset=dataset, diagnostics=tampered).passed


def test_the_validation_catches_a_death_without_a_fatal_severity(tables: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    dataset = tables[0].copy()
    dataset.loc[dataset["severity"] != "fatal", "outcome"] = "death"

    assert not [check for check in check_consistency(dataset=dataset) if check.name.startswith("fatal")][0].passed


def test_the_validation_catches_the_wrong_noise_rate(tables: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    dataset, diagnostics = tables

    assert not check_label_noise(dataset=dataset, diagnostics=diagnostics, expected_rate=0.5).passed
