from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest
from server.basemodels.adverse_drug_reaction_report import MLModelOutput
from server.models.causality_assessment_level import CausalityAssessmentLevelEnum
from server.services.adverse_drug_reaction_report import (
    AdverseDrugReactionReportService,
)

Level = CausalityAssessmentLevelEnum


@pytest.fixture
def adr_data(sample_adverse_drug_reaction_report_post_request):
    return sample_adverse_drug_reaction_report_post_request


def test_predict_is_called_with_the_arguments_it_accepts(db, adr_data, mocker):
    """Regression: the service called `_predict(adr_model=...)` but `_predict`
    also required a `data` argument, so every prediction raised a TypeError."""
    from server.repositories.adverse_drug_reaction_report import (
        AdverseDrugReactionReportRepository,
    )

    service = AdverseDrugReactionReportService(
        db=db, ml_model=Mock(), encoder=Mock(), explainer=Mock()
    )
    adr = AdverseDrugReactionReportRepository(db).create(data=adr_data)
    shap = SimpleNamespace(feature_names=["f1"], data=[np.array([1.0])])
    predict = mocker.patch.object(
        AdverseDrugReactionReportService,
        "_predict",
        autospec=True,  # enforces the real signature
        return_value=MLModelOutput.model_construct(
            prediction=Level.likely, shap_values=shap
        ),
    )
    mocker.patch(
        "server.services.adverse_drug_reaction_report.get_shap_values",
        return_value={
            "base_values": [0.1],
            "shap_values_matrix": [[0.2]],
            "shap_values_sum_per_class": [0.2],
            "shap_values_and_base_values_sum_per_class": [0.3],
        },
    )

    result = service._generate_causality_assessment_data(adr_model=adr)

    predict.assert_called_once_with(service, adr_model=adr)
    assert result.causality_assessment_level_value == Level.likely
    assert result.feature_names == ["f1"]
