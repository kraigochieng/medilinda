import pytest
from fastapi import status

path = "/api/v1/medical-institutions"


@pytest.fixture
def sample_medical_institution_payload():
    """Fixture for creating a medical institution."""
    return {
        "name": "Test Medical Institution",
        "mfl_code": "123456",
        "dhis_code": "123456",
        "county": "Kenya",
        "sub_county": "Nairobi",
    }


@pytest.fixture
def sample_medical_institution_updated_payload():
    """Fixture for updating a medical institution."""
    return {
        "name": "Updated Medical Institution",
        "mfl_code": "123456",
        "dhis_code": "123456",
        "county": "Kenya",
        "sub_county": "Nairobi",
    }


def test_post_medical_institution(client, sample_medical_institution_payload):
    """POST /api/v1/medical-institutions - create"""
    response = client.post(path, json=sample_medical_institution_payload)
    assert response.status_code == status.HTTP_201_CREATED, response.text

    data = response.json()
    assert "id" in data
    assert data["name"] == sample_medical_institution_payload["name"]


def test_get_medical_institution_list(client, sample_medical_institution_payload):
    """GET /api/v1/medical-institutions - list"""
    create_resp = client.post(path, json=sample_medical_institution_payload)
    assert create_resp.status_code == status.HTTP_201_CREATED
    created_id = create_resp.json()["id"]

    response = client.get(path)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "items" in data
    assert any(inst["id"] == created_id for inst in data["items"])


def test_get_medical_institution_by_id(client, sample_medical_institution_payload):
    """GET /api/v1/medical-institutions/{id}"""
    create_resp = client.post(path, json=sample_medical_institution_payload)
    created = create_resp.json()
    inst_id = created["id"]

    response = client.get(f"{path}/{inst_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == sample_medical_institution_payload["name"]


def test_get_medical_institution_by_id_not_found(client):
    """GET /api/v1/medical-institutions/{id} - not found"""
    response = client.get(f"{path}/nonexistent")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_medical_institution(
    client,
    sample_medical_institution_payload,
    sample_medical_institution_updated_payload,
):
    """PUT /api/v1/medical-institutions/{id}"""
    create_resp = client.post(path, json=sample_medical_institution_payload)
    inst_id = create_resp.json()["id"]

    response = client.put(
        f"{path}/{inst_id}", json=sample_medical_institution_updated_payload
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == sample_medical_institution_updated_payload["name"]


def test_update_medical_institution_not_found(
    client, sample_medical_institution_updated_payload
):
    """PUT /api/v1/medical-institutions/{id} - not found"""
    response = client.put(
        f"{path}/doesnotexist", json=sample_medical_institution_updated_payload
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_medical_institution(client, sample_medical_institution_payload):
    """DELETE /api/v1/medical-institutions/{id}"""
    create_resp = client.post(path, json=sample_medical_institution_payload)
    inst_id = create_resp.json()["id"]

    response = client.delete(f"{path}/{inst_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # confirm deletion
    get_resp = client.get(f"{path}/{inst_id}")
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND


def test_delete_medical_institution_not_found(client):
    """DELETE /api/v1/medical-institutions/{id} - not found"""
    response = client.delete(f"{path}/doesnotexist")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# def test_get_telephones_for_medical_institution(
#     client, sample_medical_institution_payload
# ):
#     """GET /api/v1/medical-institutions/{id}/telephone"""
#     # create institution
#     create_resp = client.post(path, json=sample_medical_institution_payload)
#     inst_id = create_resp.json()["id"]

#     # create telephone via its endpoint
#     tel_payload = {"telephone": "0712345678"}
#     tel_resp = client.post(f"{path}/{inst_id}/telephone", json=tel_payload)
#     assert tel_resp.status_code == status.HTTP_201_CREATED, tel_resp.text

#     # retrieve telephones
#     get_resp = client.get(f"{path}/{inst_id}/telephone")
#     assert get_resp.status_code == status.HTTP_200_OK

#     data = get_resp.json()
#     assert "items" in data
#     assert any(t["telephone"] == "0712345678" for t in data["items"])
