"""Generate the synthetic dataset: sample cases, apply the WHO-UMC rules, add label noise, write the files.

Run from the server folder:

    PYTHONPATH=src uv run python -m medilinda_ml.data_generation --rows 30000 --seed 42 \\
        --output src/medilinda_ml/data/data_who_umc.csv

It writes two files. The dataset has the columns that training may read. The diagnostics file
(same name with _diagnostics) has the rule label without noise, the latent cause and the regimen.
Training must never read the diagnostics file.

The level of each row is the output of who_umc.assess on the facts of the report (decision DR-1).
"""

import argparse
import gzip
import random
from datetime import date
from pathlib import Path
from typing import Final

import pandas as pd
from medilinda_ml.case_facts import CausalityLevel
from medilinda_ml.case_sampler import sample_case
from medilinda_ml.dataset_rows import (
    DATASET_COLUMNS,
    DIAGNOSTIC_COLUMNS,
    TARGET_COLUMN,
    apply_label_noise,
    case_to_row,
)
from medilinda_ml.paths import DATA_DIR
from medilinda_ml.who_umc import assess
from medilinda_ml.yellow_form_mapping import facts_from_report

DEFAULT_ROWS: Final[int] = 30_000
DEFAULT_SEED: Final[int] = 42
DEFAULT_LABEL_NOISE: Final[float] = 0.05
# One fixed "today", so the generated data repeats on every run.
REFERENCE_DATE: Final[date] = date(2026, 11, 1)
DEFAULT_OUTPUT: Final[Path] = DATA_DIR / "data_who_umc.csv.gz"


def generate_tables(
    *, rows: int, seed: int, label_noise: float, reference_date: date = REFERENCE_DATE
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return the dataset and the diagnostics. Pure: the same arguments always give the same tables."""
    sampling_source = random.Random(seed)
    noise_source = random.Random(seed + 1)
    dataset_rows: list[dict[str, object]] = []
    diagnostic_rows: list[dict[str, object]] = []
    for _ in range(rows):
        case = sample_case(random_source=sampling_source, reference_date=reference_date)
        rule_level = assess(facts=facts_from_report(report=case.report))
        final_level = apply_label_noise(level=rule_level, random_source=noise_source, rate=label_noise)
        dataset_rows.append(case_to_row(case=case, level=final_level))
        diagnostic_rows.append(
            {
                "causality_by_rule": rule_level.value,
                "is_drug_related": case.is_drug_related,
                "regimen": case.regimen,
            }
        )
    return (
        pd.DataFrame(dataset_rows, columns=DATASET_COLUMNS),
        pd.DataFrame(diagnostic_rows, columns=DIAGNOSTIC_COLUMNS),
    )


def diagnostics_path_for(*, dataset_path: Path) -> Path:
    """Return the path of the diagnostics file that goes with a dataset file (name.csv.gz gives name_diagnostics.csv.gz)."""
    base_name = dataset_path.name.removesuffix(".gz").removesuffix(".csv")
    suffix = ".csv.gz" if dataset_path.name.endswith(".gz") else ".csv"
    return dataset_path.with_name(f"{base_name}_diagnostics{suffix}")


def write_tables(*, dataset: pd.DataFrame, diagnostics: pd.DataFrame, dataset_path: Path) -> None:
    """Side effect (disk): write the dataset and the diagnostics as CSV files.

    A name that ends in .gz is compressed with a fixed header time and no file name, so the same data gives the same bytes.
    """
    diagnostics_path = diagnostics_path_for(dataset_path=dataset_path)
    for table, path in ((dataset, dataset_path), (diagnostics, diagnostics_path)):
        content = table.to_csv(index=False).encode()
        path.write_bytes(gzip.compress(content, mtime=0) if path.name.endswith(".gz") else content)


def trainable_levels() -> list[str]:
    """Return the levels that the model predicts. The server sets the other two by rule."""
    return [
        CausalityLevel.CERTAIN.value,
        CausalityLevel.LIKELY.value,
        CausalityLevel.POSSIBLE.value,
        CausalityLevel.UNLIKELY.value,
    ]


def main() -> None:
    """Side effect (disk): read the arguments and write the two files."""
    parser = argparse.ArgumentParser(description="Generate the synthetic dataset (issue #164).")
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS, help="the number of rows, for example 30000")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="the random seed, for example 42")
    parser.add_argument("--label-noise", type=float, default=DEFAULT_LABEL_NOISE, help="the share of labels that move one step, for example 0.05")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="the dataset file")
    arguments = parser.parse_args()
    dataset, diagnostics = generate_tables(rows=arguments.rows, seed=arguments.seed, label_noise=arguments.label_noise)
    write_tables(dataset=dataset, diagnostics=diagnostics, dataset_path=arguments.output)
    print(dataset[TARGET_COLUMN].value_counts().to_string())


if __name__ == "__main__":
    main()
