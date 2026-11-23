"""Check a generated dataset against the PPB totals and against the rules, and write the report.

Pure functions work on data frames. Only main() reads and writes files.

Run from the server folder:

    PYTHONPATH=src uv run python -m medilinda_ml.dataset_validation \\
        --dataset src/medilinda_ml/data/data_who_umc.csv --output ../docs/synthetic-data-report.md
"""

import argparse
from pathlib import Path
from typing import Final

import pandas as pd
from medilinda_ml import marginals
from medilinda_ml.data_generation import diagnostics_path_for, trainable_levels
from medilinda_ml.dataset_rows import ORDERED_LEVELS, TARGET_COLUMN, report_from_row
from medilinda_ml.marginals import CountedDistribution, proportions
from medilinda_ml.report_fields import DrugName
from medilinda_ml.who_umc import assess
from medilinda_ml.yellow_form_mapping import facts_from_report
from pydantic import BaseModel, ConfigDict

TOTALS_TOLERANCE: Final[float] = 0.03
NOISE_TOLERANCE: Final[float] = 0.01


class Check(BaseModel):
    """The result of one check, with the numbers that a reader needs."""

    model_config = ConfigDict(frozen=True)

    name: str
    passed: bool
    detail: str


class ValidationReport(BaseModel):
    """All checks, and the class counts of the rule label and of the final label."""

    model_config = ConfigDict(frozen=True)

    rows: int
    checks: list[Check]
    rule_label_counts: dict[str, int]
    final_label_counts: dict[str, int]

    @property
    def passed(self) -> bool:
        """True when every check passed."""
        return all(check.passed for check in self.checks)


def _share_check(*, name: str, observed: float, distribution: CountedDistribution, category: str) -> Check:
    """Compare the share of one category with the share of the PPB report."""
    expected = proportions(distribution=distribution)[category]
    return Check(
        name=name,
        passed=abs(observed - expected) <= TOTALS_TOLERANCE,
        detail=f"observed {observed:.3f}, PPB report {expected:.3f}, tolerance {TOTALS_TOLERANCE}",
    )


def check_totals(*, dataset: pd.DataFrame) -> list[Check]:
    """Compare the main totals of the dataset with the PPB report."""
    age = dataset["patient_age"]
    return [
        _share_check(name="female share", observed=float((dataset["patient_gender"] == "female").mean()), distribution=marginals.GENDER, category="female"),
        _share_check(name="adult share (18 to 64)", observed=float(((age >= 18) & (age <= 64)).mean()), distribution=marginals.AGE_GROUP, category="adult"),
        _share_check(name="elderly share (65 and over)", observed=float((age >= 65).mean()), distribution=marginals.AGE_GROUP, category="elderly"),
        _share_check(name="mild severity share", observed=float((dataset["severity"] == "mild").mean()), distribution=marginals.SEVERITY, category="mild"),
        _share_check(name="serious share", observed=float((dataset["is_serious"] == "yes").mean()), distribution=marginals.IS_SERIOUS, category="yes"),
        _share_check(name="drug withdrawn share", observed=float((dataset["action_taken"] == "drug withdrawn").mean()), distribution=marginals.ACTION_TAKEN, category="drug_withdrawn"),
    ]


def _dates(*, dataset: pd.DataFrame, column: str) -> pd.Series:
    """Parse a date column. A missing or bad value becomes NaT."""
    return pd.to_datetime(dataset[column], errors="coerce")


def check_consistency(*, dataset: pd.DataFrame) -> list[Check]:
    """Check the rules of causal order and of the form on every row."""
    onset = _dates(dataset=dataset, column="date_of_onset_of_reaction")
    created = _dates(dataset=dataset, column="created_at")
    start_before_onset = True
    stop_after_start = True
    for drug in DrugName:
        start = _dates(dataset=dataset, column=f"{drug.value}_start_date")
        stop = _dates(dataset=dataset, column=f"{drug.value}_stop_date")
        start_before_onset &= bool(((start <= onset) | start.isna() | onset.isna()).all())
        stop_after_start &= bool(((stop >= start) | stop.isna() | start.isna()).all())
    male_pregnant = dataset["patient_gender"].eq("male") & dataset["pregnancy_status"].str.contains("trimester", na=False)
    criteria_without_serious = dataset["is_serious"].eq("no") & dataset["criteria_for_seriousness"].notna()
    return [
        Check(name="onset on or after every start date", passed=start_before_onset, detail="checked for the four drugs"),
        Check(name="stop on or after start", passed=stop_after_start, detail="checked for the four drugs"),
        Check(name="report date on or after onset", passed=bool(((created >= onset) | onset.isna()).all()), detail="every row"),
        Check(name="fatal severity if and only if death outcome", passed=bool((dataset["severity"].eq("fatal") == dataset["outcome"].eq("death")).all()), detail="every row"),
        Check(name="no pregnant male", passed=not bool(male_pregnant.any()), detail=f"{int(male_pregnant.sum())} rows"),
        Check(name="seriousness criteria only for serious reports", passed=not bool(criteria_without_serious.any()), detail=f"{int(criteria_without_serious.sum())} rows"),
    ]


def check_label_is_rule_output(*, dataset: pd.DataFrame, diagnostics: pd.DataFrame) -> Check:
    """Rebuild each report from its row, apply the rules, and compare with the rule label (decision DR-1)."""
    records = dataset.to_dict("records")
    rebuilt = [assess(facts=facts_from_report(report=report_from_row(row=record))).value for record in records]
    mismatches = int((pd.Series(rebuilt, index=diagnostics.index) != diagnostics["causality_by_rule"]).sum())
    return Check(
        name="the rule label is a function of the visible fields",
        passed=mismatches == 0,
        detail=f"{mismatches} of {len(records)} rows differ when the rules are applied to the row again",
    )


def check_label_noise(*, dataset: pd.DataFrame, diagnostics: pd.DataFrame, expected_rate: float) -> Check:
    """Check that the share of moved labels is the stated rate (decision DR-6)."""
    ordered = {level.value for level in ORDERED_LEVELS}
    in_scale = diagnostics["causality_by_rule"].isin(ordered)
    moved = float((dataset.loc[in_scale, TARGET_COLUMN] != diagnostics.loc[in_scale, "causality_by_rule"]).mean())
    return Check(
        name="label noise equals the stated rate",
        passed=abs(moved - expected_rate) <= NOISE_TOLERANCE,
        detail=f"moved {moved:.4f}, stated {expected_rate}, tolerance {NOISE_TOLERANCE}",
    )


def check_class_floor(*, dataset: pd.DataFrame, minimum_total: int) -> Check:
    """Check that each trainable level has at least the given number of rows (decision DR-4)."""
    counts = dataset[TARGET_COLUMN].value_counts()
    smallest = min((int(counts.get(level, 0)), level) for level in trainable_levels())
    return Check(
        name="each trainable level has the floor of rows",
        passed=smallest[0] >= minimum_total,
        detail=f"the smallest is {smallest[1]} with {smallest[0]} rows, the floor is {minimum_total}",
    )


def validate_dataset(
    *, dataset: pd.DataFrame, diagnostics: pd.DataFrame, label_noise: float, minimum_rows_per_level: int
) -> ValidationReport:
    """Run all checks. Pure: it reads only the two tables."""
    checks = [
        *check_totals(dataset=dataset),
        *check_consistency(dataset=dataset),
        check_label_is_rule_output(dataset=dataset, diagnostics=diagnostics),
        check_label_noise(dataset=dataset, diagnostics=diagnostics, expected_rate=label_noise),
        check_class_floor(dataset=dataset, minimum_total=minimum_rows_per_level),
    ]
    return ValidationReport(
        rows=len(dataset),
        checks=checks,
        rule_label_counts={str(key): int(value) for key, value in diagnostics["causality_by_rule"].value_counts().items()},
        final_label_counts={str(key): int(value) for key, value in dataset[TARGET_COLUMN].value_counts().items()},
    )


def render_markdown(*, report: ValidationReport, seed: int, label_noise: float) -> str:
    """Return the report as Markdown text. Pure."""
    check_lines = "\n".join(
        f"| {check.name} | {'passed' if check.passed else 'FAILED'} | {check.detail} |" for check in report.checks
    )
    levels = ["certain", "likely", "possible", "unlikely", "unclassified", "unclassifiable"]
    count_lines = "\n".join(
        f"| {level} | {report.rule_label_counts.get(level, 0)} | {report.rule_label_counts.get(level, 0) / report.rows:.2%} | {report.final_label_counts.get(level, 0)} |"
        for level in levels
    )
    return f"""# Report on the synthetic data

Generated by `python -m medilinda_ml.dataset_validation`. Rows: {report.rows}. Seed: {seed}. Label noise: {label_noise}.
Issue #164 explains the design. The data is synthetic. The scores of a model on this data do not show clinical accuracy.

## Checks

| Check | Result | Detail |
|---|---|---|
{check_lines}

## Class mix

The mix is the output of the rules (decision DR-4). It does not copy real-world frequencies. No source gives them.

| Level | Rule label (rows) | Share | Final label with noise (rows) |
|---|---|---|---|
{count_lines}

The model trains on certain, likely, possible and unlikely. The server sets unclassified and unclassifiable by its own rule.
"""


def main() -> None:
    """Side effect (disk): read the dataset and the diagnostics, write the Markdown report, and exit 1 if a check failed."""
    parser = argparse.ArgumentParser(description="Validate the synthetic dataset (issue #164).")
    parser.add_argument("--dataset", type=Path, required=True, help="the dataset file")
    parser.add_argument("--output", type=Path, required=True, help="the Markdown report to write")
    parser.add_argument("--seed", type=int, default=42, help="the seed that made the dataset, for the report")
    parser.add_argument("--label-noise", type=float, default=0.05, help="the label noise of the dataset")
    parser.add_argument("--minimum-rows-per-level", type=int, default=200, help="the floor for each trainable level")
    arguments = parser.parse_args()
    dataset = pd.read_csv(arguments.dataset)
    diagnostics = pd.read_csv(diagnostics_path_for(dataset_path=arguments.dataset))
    report = validate_dataset(
        dataset=dataset,
        diagnostics=diagnostics,
        label_noise=arguments.label_noise,
        minimum_rows_per_level=arguments.minimum_rows_per_level,
    )
    arguments.output.write_text(render_markdown(report=report, seed=arguments.seed, label_noise=arguments.label_noise))
    raise SystemExit(0 if report.passed else 1)


if __name__ == "__main__":
    main()
