from fastapi_pagination import Page, Params
from sqlalchemy.orm import Session

from server.basemodels.medical_institution import (
    MedicalInstitutionGetResponse,
    MedicalInstitutionPostRequest,
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
        self, data: MedicalInstitutionPostRequest
    ) -> MedicalInstitutionGetResponse:
        model = self.repository.create(data=data)

        return MedicalInstitutionGetResponse.model_validate(model)

    def get_medical_institution_by_id(self, id: str) -> MedicalInstitutionGetResponse:
        model = self.repository.get(id=id)

        return MedicalInstitutionGetResponse.model_validate(model)

    def update_medical_institution(
        self, data: MedicalInstitutionPostRequest, id: str
    ) -> MedicalInstitutionGetResponse:
        model = self.repository.update(data=data, id=id)

        return MedicalInstitutionGetResponse.model_validate(model)

    def delete_medical_institution(self, id: str) -> None:
        self.repository.delete(id=id)
