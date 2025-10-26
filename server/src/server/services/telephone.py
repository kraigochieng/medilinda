from fastapi_pagination import Page

from server.basemodels.medical_institution import (
    MedicalInstitutionGetResponse,
    MedicalInstitutionTelephonePostRequest,
)
from server.repositories.telephone import TelephoneRepository


class TelephoneService:
    def __init__(self, db):
        self.repository = TelephoneRepository(db)

    def get_telephones(
        self, medical_institution_id: str | None
    ) -> Page[MedicalInstitutionGetResponse]:
        return self.repository.get_all(medical_institution_id=medical_institution_id)

    def get_telephone_by_id(self, telephone_id: str) -> MedicalInstitutionGetResponse:
        return self.repository.get_by_id(telephone_id)

    def create_telephone(
        self, telephone: MedicalInstitutionTelephonePostRequest
    ) -> MedicalInstitutionGetResponse:
        return self.repository.create(telephone)

    def update_telephone(
        self, telephone_id: str, telephone: MedicalInstitutionTelephonePostRequest
    ) -> MedicalInstitutionGetResponse:
        return self.repository.update(telephone_id, telephone)

    def delete_telephone(self, telephone_id: str) -> bool:
        return self.repository.delete(telephone_id)
