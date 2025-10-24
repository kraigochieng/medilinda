from fastapi import status
from server.models.medical_institution import MedicalInstitutionTelephoneModel
from server.basemodels.medical_institution import MedicalInstitutionTelephonePostRequest

path = "/api/v1/telephones"


def test_create_telephone(client, db):
    telephone_data = {"medical_institution_id": "1", "telephone": "1234567890"}
    response = client.post(path, json={"telephones": [telephone_data]})
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["telephone"] == "1234567890"
    db_obj = (
        db.query(MedicalInstitutionTelephoneModel)
        .filter_by(telephone="1234567890")
        .first()
    )
    assert db_obj is not None


def test_get_telephone_list(client, db):
    db.add(
        MedicalInstitutionTelephoneModel(
            medical_institution_id="1", telephone="2223334444"
        )
    )
    db.commit()
    response = client.get(path)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert any("2223334444" in tel["telephone"] for tel in data["items"])


def test_get_telephone_by_id(client, db):
    telephone = MedicalInstitutionTelephoneModel(
        medical_institution_id="1", telephone="3334445555"
    )
    db.add(telephone)
    db.commit()
    response = client.get(f"{path}/{telephone.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["telephone"] == "3334445555"


def test_update_telephone(client, db):
    obj = MedicalInstitutionTelephoneModel(
        medical_institution_id="1", telephone="4445556666"
    )

    telephone = MedicalInstitutionTelephonePostRequest(
        medical_institution_id="1",
        telephone="5556667777",
    )
    # for key, value in telephone.model_dump().items():
    #     setattr(obj, key, value)

    db.add(obj)
    db.commit()
    db.refresh(obj)

    response = client.put(
        f"{path}/{obj.id}",
        json=telephone.model_dump(),
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["telephone"] == "5556667777"
    db_obj = (
        db.query(MedicalInstitutionTelephoneModel)
        .filter_by(telephone="5556667777")
        .first()
    )
    assert db_obj is not None


def test_delete_telephone(client, db):
    telephone = MedicalInstitutionTelephoneModel(
        medical_institution_id="1", telephone="6667778888"
    )
    db.add(telephone)
    db.commit()
    response = client.delete(f"{path}/{telephone.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db_obj = (
        db.query(MedicalInstitutionTelephoneModel).filter_by(id=telephone.id).first()
    )
    assert db_obj is None
