import pytest
from fastapi import status
from server.basemodels.causality_asssessment_level import CausalityAssessmentLevelEnum

path = "/api/v1/causality-assessment-levels"


@pytest.fixture
def sample_causality_assessment_level_payload():
    """Fixture for creating or updating a Causality Assessment Level record."""
    return {
        "adr_id": "adr-12345",
        "ml_model_id": "final_ml_model@champion",
        "causality_assessment_level_value": CausalityAssessmentLevelEnum.likely.value,
        # These can be updated later to real SHAP data; for now they’re None
        "base_values": None,
        "shap_values_matrix": None,
        "shap_values_sum_per_class": None,
        "shap_values_and_base_values_sum_per_class": None,
        "feature_names": None,
        "feature_values": None,
    }


@pytest.fixture
def sample_causality_assessment_level_updated_payload():
    """Fixture for updating an existing Causality Assessment Level record."""
    return {
        "adr_id": "adr-12345",
        "ml_model_id": "final_ml_model@champion",
        "causality_assessment_level_value": CausalityAssessmentLevelEnum.certain.value,
        "base_values": None,
        "shap_values_matrix": None,
        "shap_values_sum_per_class": None,
        "shap_values_and_base_values_sum_per_class": None,
        "feature_names": None,
        "feature_values": None,
    }


def test_get_causality_assessment_level_by_id_not_found(client):
    """GET /api/v1/causality-assessment-levels/{id} - should 400 if not found"""
    response = client.get(f"/{path}/nonexistent-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# def test_create_and_get_causality_assessment_level(
#     client, sample_causality_assessment_level_payload
# ):
#     """
#     Simulate creation (via service that auto-creates with ADR)
#     and then fetch by ID.
#     """
#     # Create the record via POST (if exposed by another endpoint)
#     create_resp = client.post(
#         "/api/v1/adrs/adr-12345/causality-assessment-level",
#         json=sample_causality_assessment_level_payload,
#     )

#     # Some setups might not have a POST route here;
#     # adapt to your actual endpoint structure.
#     assert create_resp.status_code in [
#         status.HTTP_201_CREATED,
#         status.HTTP_200_OK,
#     ], create_resp.text

#     created = create_resp.json()
#     cal_id = created.get("id") or created.get("cal_id")

#     # Now fetch it by ID
#     get_resp = client.get(f"{path}/{cal_id}")
#     assert get_resp.status_code == status.HTTP_200_OK

#     data = get_resp.json()
#     assert data["id"] == cal_id
#     assert (
#         data["causality_assessment_level_value"]
#         == sample_causality_assessment_level_payload["causality_assessment_level_value"]
#     )
#     assert "approved_count" in data
#     assert "not_approved_count" in data


# def test_update_causality_assessment_level(
#     client,
#     sample_causality_assessment_level_payload,
#     sample_causality_assessment_level_updated_payload,
# ):
#     """PUT /api/v1/causality-assessment-levels/{id} - update"""
#     # Create one first (simulate ADR-linked creation)
#     create_resp = client.post(
#         "/api/v1/adrs/adr-12345/causality-assessment-level",
#         json=sample_causality_assessment_level_payload,
#     )
#     assert create_resp.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
#     cal_id = create_resp.json().get("id")

#     update_resp = client.put(
#         f"{path}/{cal_id}", json=sample_causality_assessment_level_updated_payload
#     )
#     assert update_resp.status_code == status.HTTP_200_OK, update_resp.text

#     updated = update_resp.json()
#     assert (
#         updated["causality_assessment_level_value"]
#         == sample_causality_assessment_level_updated_payload[
#             "causality_assessment_level_value"
#         ]
#     )


def test_update_causality_assessment_level_not_found(
    client, sample_causality_assessment_level_updated_payload
):
    """PUT /api/v1/causality-assessment-levels/{id} - not found"""
    response = client.put(
        f"{path}/nonexistent-id", json=sample_causality_assessment_level_updated_payload
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


# def test_delete_causality_assessment_level(
#     client, sample_causality_assessment_level_payload
# ):
#     """DELETE /api/v1/causality-assessment-levels/{id}"""
#     create_resp = client.post(
#         "/api/v1/adrs/adr-12345/causality-assessment-level",
#         json=sample_causality_assessment_level_payload,
#     )
#     assert create_resp.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]
#     cal_id = create_resp.json()["id"]

#     delete_resp = client.delete(f"{path}/{cal_id}")
#     assert delete_resp.status_code == status.HTTP_204_NO_CONTENT

#     # confirm deletion
#     get_resp = client.get(f"{path}/{cal_id}")
#     assert get_resp.status_code in [
#         status.HTTP_404_NOT_FOUND,
#         status.HTTP_400_BAD_REQUEST,
#     ]


def test_delete_causality_assessment_level_not_found(client):
    """DELETE /api/v1/causality-assessment-levels/{id} - not found"""
    response = client.delete(f"{path}/nonexistent-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND
