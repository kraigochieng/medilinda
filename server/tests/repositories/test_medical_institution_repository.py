import pytest
from fastapi import HTTPException
from fastapi_pagination import Params
from server.basemodels.medical_institution import (
    MedicalInstitutionPostRequest,
)
from server.exceptions import ResourceNotFoundError
from server.models.medical_institution import (
    MedicalInstitutionModel,
    MedicalInstitutionTelephoneModel,
)
from server.repositories.medical_institution import MedicalInstitutionRepository


@pytest.fixture
def institution_repository(db):
    return MedicalInstitutionRepository(db)


@pytest.fixture
def sample_medical_institution_post_request() -> MedicalInstitutionPostRequest:
    """Fixture for creating a sample medical institution."""
    return MedicalInstitutionPostRequest(
        name="Nairobi Hospital",
        mfl_code="MFL001",
        dhis_code="DHIS001",
        county="Nairobi",
        sub_county="Upper Hill",
    )


@pytest.fixture
def sample_medical_institution_post_request_updated(
    sample_medical_institution_post_request: MedicalInstitutionPostRequest,
) -> MedicalInstitutionPostRequest:
    """Fixture for updating a medical institution."""
    updated = sample_medical_institution_post_request.model_copy()

    updated.name = "Updated Nairobi Hospital"

    return updated


def test_create_institution(
    institution_repository, sample_medical_institution_post_request
):
    created = institution_repository.create(
        data=sample_medical_institution_post_request
    )

    assert created.id is not None
    assert created.name == sample_medical_institution_post_request.name
    assert created.mfl_code == sample_medical_institution_post_request.mfl_code
    assert created.dhis_code == sample_medical_institution_post_request.dhis_code
    assert created.county == sample_medical_institution_post_request.county
    assert created.sub_county == sample_medical_institution_post_request.sub_county


def test_get_institution(
    institution_repository, sample_medical_institution_post_request
):
    created = institution_repository.create(
        data=sample_medical_institution_post_request
    )
    fetched = institution_repository.get(id=created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == created.name


def test_update_institution(
    institution_repository,
    sample_medical_institution_post_request,
    sample_medical_institution_post_request_updated,
):
    created = institution_repository.create(
        data=sample_medical_institution_post_request
    )
    updated = institution_repository.update(
        data=sample_medical_institution_post_request_updated, id=created.id
    )

    assert updated is not None
    assert updated.name == sample_medical_institution_post_request_updated.name
    assert updated.mfl_code == sample_medical_institution_post_request_updated.mfl_code
    assert (
        updated.dhis_code == sample_medical_institution_post_request_updated.dhis_code
    )


def test_update_institution_not_found(
    institution_repository, sample_medical_institution_post_request_updated
):
    with pytest.raises(ResourceNotFoundError):
        institution_repository.update(
            data=sample_medical_institution_post_request_updated, id="non-existent-id"
        )


def test_delete_institution(
    institution_repository, sample_medical_institution_post_request
):
    created = institution_repository.create(
        data=sample_medical_institution_post_request
    )

    institution_repository.delete(created.id)

    with pytest.raises(ResourceNotFoundError):
        institution_repository.get(id=created.id)


def test_delete_institution_not_found(institution_repository):
    with pytest.raises(ResourceNotFoundError):
        institution_repository.delete(id="non-existent-id")


def test_get_all_and_filter(
    institution_repository, sample_medical_institution_post_request
):
    for i in range(2):
        institution_repository.create(data=sample_medical_institution_post_request)

    # Test without query
    page = institution_repository.get_all(pagination_params=Params(page=1, size=50))
    assert len(page.items) == 2
    assert page.total == 2
