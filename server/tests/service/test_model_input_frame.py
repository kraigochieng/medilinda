"""The model input frame follows the pydantic schema MLModelInput (issue #121).

The MLflow model coerced the input to its signature. The raw pipeline does not,
so the frame must carry the right types itself.
"""

import numpy as np
import pandas as pd
import pytest
from server.basemodels.adverse_drug_reaction_report import MLModelInput
from server.services.adverse_drug_reaction_report import (
    AdverseDrugReactionReportService,
)

FLOAT_FIELDS: list[str] = [
    "patient_age",
    "patient_weight_kg",
    "patient_height_cm",
    "rifampicin_dose_amount",
    "rifampicin_frequency_number",
    "isoniazid_dose_amount",
    "isoniazid_frequency_number",
    "pyrazinamide_dose_amount",
    "pyrazinamide_frequency_number",
    "ethambutol_dose_amount",
    "ethambutol_frequency_number",
]


@pytest.fixture
def model_input(sample_adverse_drug_reaction_report_post_request) -> MLModelInput:
    request = sample_adverse_drug_reaction_report_post_request
    return MLModelInput.model_validate(
        {**request.model_dump(), "created_at": "2025-10-08T13:35:00"}
    )


def build(model_input: MLModelInput) -> pd.DataFrame:
    return AdverseDrugReactionReportService.build_model_frame(
        model_inputs=[model_input]
    )


def test_the_columns_are_the_fields_of_the_schema_in_order(model_input):
    assert list(build(model_input).columns) == list(MLModelInput.model_fields)


@pytest.mark.parametrize("field", FLOAT_FIELDS)
def test_a_float_field_is_a_float64_column(model_input, field):
    assert build(model_input)[field].dtype == np.float64


def test_a_missing_float_value_is_nan_in_a_float64_column(model_input):
    frame = build(model_input.model_copy(update={"patient_weight_kg": None}))

    assert frame["patient_weight_kg"].dtype == np.float64
    assert np.isnan(frame["patient_weight_kg"].iloc[0])


def test_created_at_is_a_string_in_the_same_format_as_before(model_input):
    assert build(model_input)["created_at"].iloc[0] == "2025-10-08 13:35:00"


def test_every_float_field_of_the_schema_is_checked_here():
    float_fields = [
        name
        for name, field in MLModelInput.model_fields.items()
        if field.annotation in (float, float | None)
    ]

    assert sorted(float_fields) == sorted(FLOAT_FIELDS)
