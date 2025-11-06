from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from server.basemodels.medical_institution import MedicalInstitutionTelephonePostRequest
from server.models.medical_institution import MedicalInstitutionTelephoneModel
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from server.exceptions import ResourceNotFoundError


class TelephoneRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self, medical_institution_id: str | None, pagination_params: Params
    ) -> Page[MedicalInstitutionTelephoneModel]:
        stmt = select(MedicalInstitutionTelephoneModel)

        if medical_institution_id:
            stmt = stmt.where(
                MedicalInstitutionTelephoneModel.medical_institution_id
                == medical_institution_id
            )

        stmt = stmt.order_by(desc(MedicalInstitutionTelephoneModel.created_at))

        return paginate(self.db, stmt, params=pagination_params)

    def get_by_id(self, id: str) -> MedicalInstitutionTelephoneModel:
        stmt = select(MedicalInstitutionTelephoneModel).where(
            MedicalInstitutionTelephoneModel.id == id
        )

        model = self.db.scalar(stmt)

        if not model:
            raise ResourceNotFoundError(f"Telephone with id {id} not found")

        return model

    def create(
        self, data: MedicalInstitutionTelephonePostRequest
    ) -> MedicalInstitutionTelephoneModel:
        model = MedicalInstitutionTelephoneModel(**data.model_dump())

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return model

    def update(
        self, id: str, data: MedicalInstitutionTelephonePostRequest
    ) -> MedicalInstitutionTelephoneModel:
        model = self.get_by_id(id=id)

        for key, value in data.model_dump().items():
            setattr(model, key, value)

        self.db.commit()
        self.db.refresh(model)

        return model

    def delete(self, id: str) -> None:
        model = self.get_by_id(id=id)

        self.db.delete(model)
        self.db.commit()
