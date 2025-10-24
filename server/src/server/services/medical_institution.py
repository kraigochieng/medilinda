from fastapi_pagination import Page
from sqlalchemy.orm import Session

from server.basemodels.medical_institution import (
    MedicalInstitutionGetResponse,
    MedicalInstitutionPostRequest,
    MedicalInstitutionTelephoneGetResponse,
)
from server.repositories.medical_institution import MedicalInstitutionRepository


class MedicalInstitutionService:
    def __init__(self, db: Session):
        self.repository = MedicalInstitutionRepository(db)

    def get_medical_institutions(
        self, query: str = ""
    ) -> Page[MedicalInstitutionGetResponse]:
        return self.repository.get_all(query)

    def create_medical_institution(
        self, institution: MedicalInstitutionPostRequest
    ) -> MedicalInstitutionGetResponse:
        return self.repository.create(institution)

    def get_medical_institution_by_id(
        self, institution_id: str
    ) -> MedicalInstitutionGetResponse:
        return self.repository.get(institution_id)

    def update_medical_institution(
        self, institution: MedicalInstitutionPostRequest, institution_id: str
    ) -> MedicalInstitutionGetResponse:
        return self.repository.update(institution, institution_id)

    def delete_medical_institution(self, institution_id: str) -> None:
        self.repository.delete(institution_id)

    def get_telephones_for_medical_institution(
        self, institution_id: str
    ) -> Page[MedicalInstitutionTelephoneGetResponse]:
        return self.repository.get_telephones(institution_id)
