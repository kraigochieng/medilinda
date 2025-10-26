import pytest
from fastapi import HTTPException
from fastapi_pagination import Params
from server.basemodels.medical_institution import (
    MedicalInstitutionPostRequest,
)
from server.models.medical_institution import (
    MedicalInstitutionModel,
    MedicalInstitutionTelephoneModel,
)
from server.repositories.medical_institution import MedicalInstitutionRepository


@pytest.fixture
def institution_repository(db):
    return MedicalInstitutionRepository(db)


@pytest.fixture
def sample_institution_request():
    """Fixture for creating a sample medical institution."""
    return MedicalInstitutionPostRequest(
        name="Nairobi Hospital",
        mfl_code="MFL001",
        dhis_code="DHIS001",
        county="Nairobi",
        sub_county="Upper Hill",
    )


@pytest.fixture
def sample_institution_request_updated():
    """Fixture for updating a medical institution."""
    return MedicalInstitutionPostRequest(
        name="Updated Nairobi Hospital",
        mfl_code="MFL002",
        dhis_code="DHIS002",
        county="Nairobi",
        sub_county="Upper Hill",
    )


def test_create_institution(institution_repository, sample_institution_request):
    created = institution_repository.create(sample_institution_request)

    assert created.id is not None
    assert created.name == "Nairobi Hospital"
    assert created.mfl_code == "MFL001"
    assert created.dhis_code == "DHIS001"
    assert created.county == "Nairobi"
    assert created.sub_county == "Upper Hill"


def test_get_institution(institution_repository, sample_institution_request):
    created = institution_repository.create(sample_institution_request)
    fetched = institution_repository.get(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "Nairobi Hospital"


def test_update_institution(
    institution_repository,
    sample_institution_request,
    sample_institution_request_updated,
):
    created = institution_repository.create(sample_institution_request)
    updated = institution_repository.update(
        sample_institution_request_updated, created.id
    )

    assert updated is not None
    assert updated.name == "Updated Nairobi Hospital"
    assert updated.mfl_code == "MFL002"
    assert updated.dhis_code == "DHIS002"


def test_update_institution_not_found(
    institution_repository, sample_institution_request_updated
):
    with pytest.raises(HTTPException) as exc:
        institution_repository.update(
            sample_institution_request_updated, "non-existent-id"
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Medical Institution not found"


def test_delete_institution(institution_repository, sample_institution_request):
    created = institution_repository.create(sample_institution_request)
    institution_repository.delete(created.id)

    # After deletion, fetching should return None
    assert institution_repository.get(created.id) is None


def test_delete_institution_not_found(institution_repository):
    with pytest.raises(HTTPException) as exc:
        institution_repository.delete("non-existent-id")

    assert exc.value.status_code == 404
    assert exc.value.detail == "Medical Institution not found"


def test_get_all_and_filter(institution_repository, sample_institution_request):
    # Create multiple institutions
    institution_repository.create(sample_institution_request)
    institution_repository.create(
        MedicalInstitutionPostRequest(
            name="Mombasa Hospital",
            mfl_code="MFL003",
            dhis_code="DHIS003",
            county="Mombasa",
            sub_county="Kizingo",
        )
    )

    # Test without query
    page = institution_repository.get_all()
    assert len(page.items) == 2
    assert page.total == 2

    # Test with filter query
    filtered = institution_repository.get_all(query="Nairobi")
    assert len(filtered.items) == 1
    assert filtered.items[0].name == "Nairobi Hospital"
