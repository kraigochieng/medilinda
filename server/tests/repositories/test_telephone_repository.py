import pytest
from fastapi_pagination import Params
from server.basemodels.medical_institution import MedicalInstitutionTelephonePostRequest
from server.models.medical_institution import MedicalInstitutionTelephoneModel
from server.repositories.telephone import TelephoneRepository


@pytest.fixture
def telephone_repository(db):
    return TelephoneRepository(db)


@pytest.fixture
def sample_telephone_request():
    return MedicalInstitutionTelephonePostRequest(
        medical_institution_id="inst-1",
        telephone="+254700000001",
    )


@pytest.fixture
def sample_telephone_request_updated():
    return MedicalInstitutionTelephonePostRequest(
        medical_institution_id="inst-1",
        telephone="+254700000002",
    )


def test_create_telephone(telephone_repository, sample_telephone_request):
    created = telephone_repository.create(sample_telephone_request)

    assert created.id is not None
    assert created.telephone == "+254700000001"


def test_get_by_id(telephone_repository, sample_telephone_request):
    created = telephone_repository.create(sample_telephone_request)
    fetched = telephone_repository.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.telephone == created.telephone


def test_update_telephone(
    telephone_repository, sample_telephone_request, sample_telephone_request_updated
):
    created = telephone_repository.create(sample_telephone_request)
    updated = telephone_repository.update(created.id, sample_telephone_request_updated)

    assert updated is not None
    assert updated.telephone == "+254700000002"


def test_delete_telephone(telephone_repository, sample_telephone_request):
    created = telephone_repository.create(sample_telephone_request)
    deleted = telephone_repository.delete(created.id)

    assert deleted is True
    assert telephone_repository.get_by_id(created.id) is None


def test_get_all_pagination(telephone_repository, sample_telephone_request):
    # Create multiple telephones
    for i in range(3):
        telephone_repository.create(
            MedicalInstitutionTelephonePostRequest(
                medical_institution_id=f"inst-{i}",
                telephone=f"+25470000000{i}",
            )
        )

    page = telephone_repository.get_all(medical_institution_id=None)
    assert page is not None
    assert len(page.items) == 3
    assert page.total == 3
