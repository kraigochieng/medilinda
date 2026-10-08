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
from server.services.adverse_drug_reaction_report import (
    AdverseDrugReactionReportService,
)

Level = CausalityAssessmentLevelEnum


@pytest.fixture
def adr_payload(sample_adverse_drug_reaction_report_post_request):
    return sample_adverse_drug_reaction_report_post_request.model_dump(mode="json")


@pytest.fixture(autouse=True)
def fake_ml_service(client, db, mocker):
    """The real service, with the ML prediction replaced by a fixed sequence."""
    service = AdverseDrugReactionReportService(
        db=db, ml_model=Mock(), encoder=Mock(), explainer=Mock()
    )
    levels = iter([Level.likely, Level.certain, Level.possible, Level.unlikely])
    mocker.patch.object(
        service,
        "_generate_causality_assessment_data",
        side_effect=lambda adr_model: CausalityAssessmentLevelPostRequest(
            adr_id=adr_model.id, causality_assessment_level_value=next(levels)
        ),
    )
    app.dependency_overrides[get_adverse_drug_reaction_report_service] = lambda: service


def create_adr(client, payload):
    response = client.post("/api/v1/adrs/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED, response.text
    return response.json()["id"]


def test_the_full_lifecycle_is_recorded(client, adr_payload):
    adr_id = create_adr(client, adr_payload)

    edited = {**adr_payload, "patient_name": "Renamed Patient"}
    assert client.put(f"/api/v1/adrs/{adr_id}", json=edited).status_code == 200

    versions = client.get(f"/api/v1/adrs/{adr_id}/versions").json()
    assert [(v["version"], v["action"]) for v in versions] == [(2, "update"), (1, "create")]
    assert versions[0]["actor_username"] == "testuser"
    assert {"field": "patient_name", "old": "Jane Smith", "new": "Renamed Patient"} in versions[0]["changes"]
    assert "snapshot" not in versions[0]  # lists stay small

    assert client.delete(f"/api/v1/adrs/{adr_id}").status_code == status.HTTP_204_NO_CONTENT
    assert client.get(f"/api/v1/adrs/{adr_id}").status_code == status.HTTP_404_NOT_FOUND

    # History outlives the record.
    versions = client.get(f"/api/v1/adrs/{adr_id}/versions").json()
    assert versions[0]["action"] == "delete"

    restored = client.post(f"/api/v1/adrs/{adr_id}/restore")
    assert restored.status_code == status.HTTP_200_OK
    assert restored.json()["patient_name"] == "Renamed Patient"
    assert client.get(f"/api/v1/adrs/{adr_id}").status_code == status.HTTP_200_OK

    versions = client.get(f"/api/v1/adrs/{adr_id}/versions").json()
    assert [v["action"] for v in versions] == ["restore", "delete", "update", "create"]


def test_one_version_returns_the_record_as_it_was(client, adr_payload):
    adr_id = create_adr(client, adr_payload)
    client.put(f"/api/v1/adrs/{adr_id}", json={**adr_payload, "patient_name": "Renamed"})

    first = client.get(f"/api/v1/adrs/{adr_id}/versions/1").json()
    second = client.get(f"/api/v1/adrs/{adr_id}/versions/2").json()

    assert first["snapshot"]["patient_name"] == "Jane Smith"
    assert second["snapshot"]["patient_name"] == "Renamed"


def test_an_unknown_version_is_a_404(client, adr_payload):
    adr_id = create_adr(client, adr_payload)

    assert client.get(f"/api/v1/adrs/{adr_id}/versions/99").status_code == 404
    assert client.get("/api/v1/adrs/never-existed/versions/1").status_code == 404


def test_an_adr_with_no_history_has_an_empty_version_list(client):
    assert client.get("/api/v1/adrs/never-existed/versions").json() == []


def test_activity_shows_assessments_alongside_edits(client, adr_payload):
    adr_id = create_adr(client, adr_payload)
    client.put(
        f"/api/v1/adrs/{adr_id}", json={**adr_payload, "rifampicin_suspected": False}
    )

    activity = client.get(f"/api/v1/adrs/{adr_id}/activity").json()

    kinds = [(e["entity_type"], e["action"]) for e in activity["items"]]
    assert ("adr", "create") in kinds
    assert ("adr", "update") in kinds
    # One assessment when created, a second one after the model input changed.
    assert kinds.count(("causality_assessment_level", "create")) == 2
    assert all("snapshot" not in e for e in activity["items"])


def test_restoring_something_never_deleted_is_a_404(client, adr_payload):
    adr_id = create_adr(client, adr_payload)

    assert client.post(f"/api/v1/adrs/{adr_id}/restore").status_code == 404
    assert client.post("/api/v1/adrs/never-existed/restore").status_code == 404


def test_restoring_twice_is_a_conflict(client, adr_payload):
    adr_id = create_adr(client, adr_payload)
    client.delete(f"/api/v1/adrs/{adr_id}")
    assert client.post(f"/api/v1/adrs/{adr_id}/restore").status_code == 200

    assert client.post(f"/api/v1/adrs/{adr_id}/restore").status_code == 409


def test_audit_logs_can_be_filtered(client, adr_payload):
    first = create_adr(client, adr_payload)
    create_adr(client, adr_payload)
    client.delete(f"/api/v1/adrs/{first}")

    deleted = client.get(
        "/api/v1/audit-logs/", params={"entity_type": "adr", "action": "delete"}
    ).json()

    assert deleted["total"] == 1
    assert deleted["items"][0]["entity_id"] == first
    assert "snapshot" not in deleted["items"][0]

    with_snapshot = client.get(
        "/api/v1/audit-logs/",
        params={"entity_type": "adr", "action": "delete", "include_snapshot": True},
    ).json()
    assert with_snapshot["items"][0]["snapshot"]["patient_name"] == "Jane Smith"


def test_audit_logs_can_be_filtered_by_actor(client, adr_payload):
    create_adr(client, adr_payload)

    mine = client.get("/api/v1/audit-logs/", params={"actor_id": "1"}).json()
    nobody = client.get("/api/v1/audit-logs/", params={"actor_id": "someone-else"}).json()

    assert mine["total"] > 0
    assert nobody["total"] == 0
