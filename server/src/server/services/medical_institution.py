from fastapi_pagination import Page, Params
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
        self, pagination_params: Params, query: str = ""
    ) -> Page[MedicalInstitutionGetResponse]:
        return self.repository.get_all(query=query, pagination_params=pagination_params)

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
