"""Sample inputs and outputs that fix the behavior of one model version.

Side effects: disk. Run it from the `server` folder:

    PYTHONPATH=src uv run python -m medilinda_ml.golden <version folder>
"""

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from server.basemodels.adverse_drug_reaction_report import MLModelInput
from server.config import ADR_CSV_PATH
from server.services.adverse_drug_reaction_report import (
    AdverseDrugReactionReportService,
)

GOLDEN_FILE_NAME = "golden.json"
GOLDEN_ROW_COUNT = 8
GOLDEN_CREATED_AT = "2025-10-08T13:35:00"


def build_golden_inputs(*, adr_csv_path: Path, row_count: int) -> list[dict[str, object]]:
    """Read sample rows from the seed CSV as model inputs, as JSON-ready records."""
    adr_frame = pd.read_csv(adr_csv_path).head(row_count)
    records: list[dict[str, object]] = []
    for row in adr_frame.to_dict(orient="records"):
        cleaned_row = {
            field: (None if pd.isna(row.get(field)) else row.get(field))
            for field in MLModelInput.model_fields
            if field != "created_at"
        }
        model_input = MLModelInput.model_validate(
            {**cleaned_row, "created_at": GOLDEN_CREATED_AT}
        )
        records.append(model_input.model_dump(mode="json"))
    return records


def inputs_to_frame(*, records: list[dict[str, object]]) -> pd.DataFrame:
    """Build the data frame that the server gives the model: one row for each record."""
    return AdverseDrugReactionReportService.build_model_frame(
        model_inputs=[MLModelInput.model_validate(record) for record in records]
    )


def write_golden(*, version_folder: Path, expected_outputs: list[float] | None = None) -> Path:
    """Side effect (disk): save sample inputs and outputs in the version folder.

    Without `expected_outputs`, the outputs come from the pipeline in the folder.
    """
    records = build_golden_inputs(adr_csv_path=ADR_CSV_PATH, row_count=GOLDEN_ROW_COUNT)
    if expected_outputs is None:
        pipeline = joblib.load(version_folder / "pipeline.pkl")
        expected_outputs = np.asarray(
            pipeline.predict(inputs_to_frame(records=records))
        ).tolist()

    golden_path = version_folder / GOLDEN_FILE_NAME
    golden_path.write_text(
        json.dumps({"inputs": records, "outputs": expected_outputs}, indent=2),
        encoding="utf-8",
    )
    return golden_path


if __name__ == "__main__":
    print(f"Saved {write_golden(version_folder=Path(sys.argv[1]))}")
