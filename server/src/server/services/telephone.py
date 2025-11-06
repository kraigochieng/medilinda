from fastapi_pagination import Page, Params

from server.basemodels.medical_institution import (
    MedicalInstitutionGetResponse,
    MedicalInstitutionTelephoneGetResponse,
    MedicalInstitutionTelephonePostRequest,
)
from server.repositories.telephone import TelephoneRepository


class TelephoneService:
    def __init__(self, db):
        self.repository = TelephoneRepository(db)

    def get_telephones(
        self, medical_institution_id: str | None, pagination_params: Params
    ) -> Page[MedicalInstitutionGetResponse]:
        return self.repository.get_all(
            medical_institution_id=medical_institution_id,
            pagination_params=pagination_params,
        )

    def get_telephone_by_id(self, id: str) -> MedicalInstitutionGetResponse:
        model = self.repository.get_by_id(id=id)

        return MedicalInstitutionGetResponse.model_validate(model)

    def create_telephone(
        self, data: MedicalInstitutionTelephonePostRequest
    ) -> MedicalInstitutionGetResponse:
        model = self.repository.create(data=data)

        return MedicalInstitutionTelephoneGetResponse.model_validate(model)

    def update_telephone(
        self, id: str, data: MedicalInstitutionTelephonePostRequest
    ) -> MedicalInstitutionGetResponse:
        model = self.repository.update(id=id, data=data)

        return MedicalInstitutionTelephoneGetResponse.model_validate(model)

    def delete_telephone(self, id: str) -> None:
        self.repository.delete(id=id)
