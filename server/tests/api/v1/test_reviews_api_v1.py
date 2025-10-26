import pytest
from fastapi import status
from server.basemodels.causality_asssessment_level import CausalityAssessmentLevelEnum


@pytest.fixture
def sample_review_payload():
    """Sample payload for creating a review."""
    return {
        "adr_id": "adr-1",
        "causality_assessment_level_id": "level-1",
        "user_id": "user-1",
        "proposed_causality_level": CausalityAssessmentLevelEnum.possible.value,
        "reason": "This is my review reason",
        "approved": True,
    }


@pytest.fixture
def sample_review_payload_updated():
    """Sample payload for updating a review."""
    return {
        "adr_id": "adr-1",
        "causality_assessment_level_id": "level-1",
        "user_id": "user-1",
        "proposed_causality_level": CausalityAssessmentLevelEnum.possible.value,
        "reason": "Updated reason",
        "approved": False,
    }


def test_create_review(client, sample_review_payload):
    """POST /api/v1/reviews"""
    response = client.post("/api/v1/reviews/", json=sample_review_payload)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["reason"] == sample_review_payload["reason"]
    assert data["user_id"] == sample_review_payload["user_id"]
    assert (
        data["causality_assessment_level_id"]
        == sample_review_payload["causality_assessment_level_id"]
    )
    assert "id" in data


def test_get_all_reviews(client):
    """GET /api/v1/reviews"""
    response = client.get("/api/v1/reviews/")
    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()
    assert "items" in json_data
    assert isinstance(json_data["items"], list)


def test_get_review_by_id(client, sample_review_payload):
    """GET /api/v1/reviews/{id}"""
    # First create one
    create_resp = client.post("/api/v1/reviews/", json=sample_review_payload)
    review_id = create_resp.json()["id"]

    # Then retrieve it
    response = client.get(f"/api/v1/reviews/{review_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == review_id
    assert data["reason"] == sample_review_payload["reason"]


def test_update_review_by_id(
    client, sample_review_payload, sample_review_payload_updated
):
    """PUT /api/v1/reviews/{id}"""
    create_resp = client.post("/api/v1/reviews/", json=sample_review_payload)
    review_id = create_resp.json()["id"]

    update_resp = client.put(
        f"/api/v1/reviews/{review_id}", json=sample_review_payload_updated
    )
    assert update_resp.status_code == status.HTTP_200_OK

    updated_data = update_resp.json()
    assert updated_data["reason"] == sample_review_payload_updated["reason"]
    assert updated_data["approved"] == sample_review_payload_updated["approved"]


def test_delete_review_by_id(client, sample_review_payload):
    """DELETE /api/v1/reviews/{id}"""
    create_resp = client.post("/api/v1/reviews/", json=sample_review_payload)
    review_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/api/v1/reviews/{review_id}")
    assert delete_resp.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's gone
    get_resp = client.get(f"/api/v1/reviews/{review_id}")
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND
