"""The model in server/models gives the outputs saved in its golden file (#123).

The golden file holds sample inputs and the outputs of the model when it was
added. A new model version needs a new golden file, so a change in behavior is
a visible change in the repository.
"""

import json

import numpy as np
import pandas as pd
import pytest
from medilinda_ml.model_store import ModelEnsemble, read_version
from server.basemodels.adverse_drug_reaction_report import MLModelInput
from server.config import MODELS_DIR
from server.models.causality_assessment_level import CausalityAssessmentLevelEnum
from server.services.adverse_drug_reaction_report import (
    AdverseDrugReactionReportService,
)


@pytest.fixture(scope="module")
def ensemble() -> ModelEnsemble:
    return read_version(root=MODELS_DIR, version="latest")


@pytest.fixture(scope="module")
def golden(ensemble: ModelEnsemble) -> dict[str, list]:
    return json.loads((MODELS_DIR / ensemble.version / "golden.json").read_text())


@pytest.fixture(scope="module")
def golden_frame(golden: dict[str, list]) -> pd.DataFrame:
    return AdverseDrugReactionReportService.build_model_frame(
        model_inputs=[MLModelInput.model_validate(row) for row in golden["inputs"]]
    )


def test_the_pipeline_gives_the_golden_outputs(ensemble, golden, golden_frame):
    outputs = np.asarray(ensemble.pipeline.predict(golden_frame))

    assert outputs.tolist() == golden["outputs"]


def test_every_golden_output_decodes_to_a_causality_level(
    ensemble, golden, golden_frame
):
    outputs = np.asarray(ensemble.pipeline.predict(golden_frame))

    levels = ensemble.encoder.inverse_transform(outputs.reshape(-1, 1)).ravel()

    assert {CausalityAssessmentLevelEnum(level) for level in levels}


def test_the_explainer_explains_one_golden_row(ensemble, golden_frame):
    explanation = ensemble.explainer(golden_frame.iloc[:1])

    assert explanation.feature_names is not None
    assert explanation.values.shape[0] == 1
