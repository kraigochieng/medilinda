from unittest.mock import Mock

import pytest
from fastapi import status
from server.api.v1.endpoints.adverse_drug_reaction_reports import (
    get_adverse_drug_reaction_report_service,
)
from server.basemodels.causality_asssessment_level import (
    CausalityAssessmentLevelPostRequest,
)
from server.main import app
from server.models.causality_assessment_level import CausalityAssessmentLevelEnum
from server.repositories.adverse_drug_reaction_report import (
    AdverseDrugReactionReportRepository,
)
from server.services.adverse_drug_reaction_report import (
    AdverseDrugReactionReportService,
)

MEDICINES = ["rifampicin", "isoniazid", "pyrazinamide", "ethambutol"]
FIELDS = [
    "suspected",
    "start_date",
    "stop_date",
    "dose_amount",
    "frequency_number",
    "route",
    "batch_no",
    "manufacturer",
]


@pytest.fixture(autouse=True)
def fake_ml_service(client, db, mocker):
    """The real service, with the ML prediction replaced by a fixed level."""
    service = AdverseDrugReactionReportService(
        db=db, ml_model=Mock(), encoder=Mock(), explainer=Mock()
    )
    mocker.patch.object(
        service,
        "_generate_causality_assessment_data",
        side_effect=lambda adr_model: CausalityAssessmentLevelPostRequest(
            adr_id=adr_model.id,
            causality_assessment_level_value=CausalityAssessmentLevelEnum.likely,
        ),
    )
    app.dependency_overrides[get_adverse_drug_reaction_report_service] = lambda: service


@pytest.fixture
def adr_id(db, sample_adverse_drug_reaction_report_post_request):
    model = AdverseDrugReactionReportRepository(db).create(
        data=sample_adverse_drug_reaction_report_post_request
    )
    return model.id


def test_a_report_comes_back_with_its_medicines(client, adr_id):
    body = client.get(f"/api/v1/adrs/{adr_id}").json()

    missing = [f"{m}_{f}" for m in MEDICINES for f in FIELDS if f"{m}_{f}" not in body]
    assert missing == []
    assert body["rifampicin_suspected"] is True
    assert body["rifampicin_dose_amount"] == 600.0
    assert body["rifampicin_batch_no"] == "RF-BATCH-001"
    assert body["rifampicin_start_date"] == "2025-10-01"
    assert body["rifampicin_stop_date"] == "2025-10-16"


def test_saving_a_loaded_report_unchanged_keeps_its_medicines(
    client, adr_id, sample_adverse_drug_reaction_report_post_request
):
    """The edit form fills itself from this response and saves all of it back."""
    loaded = client.get(f"/api/v1/adrs/{adr_id}").json()
    payload = {
        **sample_adverse_drug_reaction_report_post_request.model_dump(mode="json"),
        **{k: v for k, v in loaded.items() if k.split("_")[0] in MEDICINES},
    }
    payload.pop("user_id", None)

    saved = client.put(f"/api/v1/adrs/{adr_id}", json=payload)
    assert saved.status_code == status.HTTP_200_OK, saved.text

    after = client.get(f"/api/v1/adrs/{adr_id}").json()
    for m in MEDICINES:
        for f in FIELDS:
            assert after[f"{m}_{f}"] == loaded[f"{m}_{f}"], f"{m}_{f}"
