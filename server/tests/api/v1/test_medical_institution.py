from fastapi import status
from server.basemodels.medical_institution import MedicalInstitutionPostRequest
from server.models.medical_institution import (
    MedicalInstitutionModel,
    MedicalInstitutionTelephoneModel,
)

path = "/api/v1/medical-institutions"


def test_post_medical_institution(client, db):
    institution_basemodel = MedicalInstitutionPostRequest(
        name="Test Medical Institution",
        mfl_code="123456",
        dhis_code="123456",
        county="Kenya",
        sub_county="Nairobi",
    )

    response = client.post(path, json=institution_basemodel.model_dump())

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert "id" in data

    db_obj = (
        db.query(MedicalInstitutionModel)
        .filter_by(name="Test Medical Institution")
        .first()
    )
    assert db_obj is not None


def test_get_medical_institution_list(client, db):
    db.add(
        MedicalInstitutionModel(
            name="County Hospital",
            mfl_code="111",
            dhis_code="222",
            county="Kisumu",
            sub_county="Central",
        )
    )
    db.commit()

    response = client.get(path)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert any("County Hospital" in inst["name"] for inst in data["items"])


def test_get_medical_institution_by_id(client, db):
    institution = MedicalInstitutionModel(
        name="Special Hospital",
        mfl_code="333",
        dhis_code="444",
        county="Nakuru",
        sub_county="Town",
    )
    db.add(institution)
    db.commit()
    db.refresh(institution)

    response = client.get(f"{path}/{institution.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Special Hospital"


def test_get_medical_institution_by_id_not_found(client):
    response = client.get(f"{path}/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_medical_institution(client, db):
    institution = MedicalInstitutionModel(
        name="Old Name",
        mfl_code="555",
        dhis_code="666",
        county="Kiambu",
        sub_county="Thika",
    )
    db.add(institution)
    db.commit()
    db.refresh(institution)

    payload = {
        "id": institution.id,
        "name": "New Name",
        "mfl_code": "555",
        "dhis_code": "666",
        "county": "Kiambu",
        "sub_county": "Thika",
    }

    response = client.put(f"{path}/{institution.id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "New Name"


def test_update_medical_institution_not_found(client):
    payload = {
        "id": "nonexistent",
        "name": "Nope",
        "mfl_code": "000",
        "dhis_code": "000",
        "county": "None",
        "sub_county": "None",
    }

    response = client.put(f"{path}/nonexistent", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_medical_institution(client, db):
    institution = MedicalInstitutionModel(
        name="To Delete",
        mfl_code="777",
        dhis_code="888",
        county="Eldoret",
        sub_county="Langas",
    )
    db.add(institution)
    db.commit()
    db.refresh(institution)

    response = client.delete(f"{path}/{institution.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert (
        db.query(MedicalInstitutionModel).filter_by(id=institution.id).first() is None
    )


def test_delete_medical_institution_not_found(client):
    response = client.delete(f"{path}/doesnotexist")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_telephones_for_medical_institution(client, db):
    

    institution = MedicalInstitutionModel(
        name="With Phones",
        mfl_code="999",
        dhis_code="888",
        county="Kisii",
        sub_county="Central",
    )
    db.add(institution)
    db.commit()
    db.refresh(institution)

    phone = MedicalInstitutionTelephoneModel(
        medical_institution_id=institution.id,
        telephone="0712345678",
    )
    db.add(phone)
    db.commit()

    response = client.get(f"{path}/{institution.id}/telephone")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "items" in data
    assert any("0712345678" in tel["telephone"] for tel in data["items"])
