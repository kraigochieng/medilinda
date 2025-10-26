import pytest
from fastapi import status


@pytest.fixture
def sample_telephone_payload():
    """Fixture for creating a telephone record."""
    return {
        "medical_institution_id": "institution-1",
        "telephone": "+254712345678",
    }


@pytest.fixture
def sample_telephone_payload_updated():
    """Fixture for updating a telephone record."""
    return {
        "medical_institution_id": "institution-1",
        "telephone": "+254700000000",
    }


@pytest.fixture
def multiple_telephones_payload(sample_telephone_payload):
    """Fixture for creating multiple telephone records at once."""
    return {
        "telephones": [
            sample_telephone_payload,
            {
                "medical_institution_id": "institution-2",
                "telephone": "+254711111111",
            },
        ]
    }


def test_create_telephone(client, multiple_telephones_payload):
    """POST /api/v1/telephones/ - create multiple telephone records."""
    response = client.post("/api/v1/telephones", json=multiple_telephones_payload)
    assert response.status_code == status.HTTP_201_CREATED

    data = [d for d in response.json() if d]  # filter out empty objects
    assert len(data) >= 1

    first = data[0]
    assert "telephone" in first
    assert first["telephone"].startswith("+254")


def test_get_all_telephones(client):
    """GET /api/v1/telephones/ - fetch paginated telephones."""
    response = client.get("/api/v1/telephones/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)


# def test_get_telephone_by_id(client, multiple_telephones_payload):
#     """GET /api/v1/telephones/{id} - retrieve a specific record."""
#     create_resp = client.post("/api/v1/telephones/", json=multiple_telephones_payload)
#     data = [d for d in create_resp.json() if isinstance(d, dict) and d.get("id")]
#     assert data, (
#         f"Expected at least one valid telephone object, got: {create_resp.json()}"
#     )

#     telephone_id = data[0]["id"]

#     response = client.get(f"/api/v1/telephones/{telephone_id}")
#     assert response.status_code == status.HTTP_200_OK

#     tele_data = response.json()
#     assert tele_data["id"] == telephone_id
#     assert "telephone" in tele_data


def test_update_telephone(
    client, multiple_telephones_payload, sample_telephone_payload_updated
):
    """PUT /api/v1/telephones/{id} - update an existing telephone."""
    create_resp = client.post("/api/v1/telephones/", json=multiple_telephones_payload)
    data = [d for d in create_resp.json() if d]
    assert len(data) >= 1

    telephone_id = data[0].get("id")
    assert telephone_id is not None, "Expected created telephone to have an 'id'"

    update_resp = client.put(
        f"/api/v1/telephones/{telephone_id}",
        json=sample_telephone_payload_updated,
    )
    assert update_resp.status_code == status.HTTP_200_OK

    updated_data = update_resp.json()
    assert updated_data["telephone"] == sample_telephone_payload_updated["telephone"]


def test_delete_telephone(client, multiple_telephones_payload):
    """DELETE /api/v1/telephones/{id} - delete a telephone record."""
    create_resp = client.post("/api/v1/telephones/", json=multiple_telephones_payload)
    data = [d for d in create_resp.json() if d]
    assert len(data) >= 1

    telephone_id = data[0].get("id")
    assert telephone_id is not None, "Expected created telephone to have an 'id'"

    delete_resp = client.delete(f"/api/v1/telephones/{telephone_id}")
    assert delete_resp.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's deleted
    get_resp = client.get(f"/api/v1/telephones/{telephone_id}")
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND
