from fastapi import HTTPException, status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from server.basemodels.medical_institution import (
    MedicalInstitutionPostRequest,
)
from server.exceptions import ResourceNotFoundError
from server.models.medical_institution import (
    MedicalInstitutionModel,
    MedicalInstitutionTelephoneModel,
)
from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session


class MedicalInstitutionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self, pagination_params: Params, query: str = ""
    ) -> Page[MedicalInstitutionModel]:
        stmt = select(MedicalInstitutionModel).order_by(
            desc(MedicalInstitutionModel.created_at)
        )

        if query:
            stmt = stmt.where(
                or_(
                    MedicalInstitutionModel.name.ilike(f"%{query}%"),
                    MedicalInstitutionModel.county.ilike(f"%{query}%"),
                    MedicalInstitutionModel.sub_county.ilike(f"%{query}%"),
                )
            )

        stmt = stmt.order_by(desc(MedicalInstitutionModel.created_at))

        return paginate(self.db, stmt, params=pagination_params)

    def create(self, data: MedicalInstitutionPostRequest) -> MedicalInstitutionModel:
        model = MedicalInstitutionModel(**data.model_dump())

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return model

    def get(self, id: str) -> MedicalInstitutionModel:
        stmt = select(MedicalInstitutionModel).where(MedicalInstitutionModel.id == id)
        model = self.db.scalar(stmt)

        if not model:
            raise ResourceNotFoundError(f"Medical Institution with id {id} not found")

        return model

    def update(
        self, data: MedicalInstitutionPostRequest, id: str
    ) -> MedicalInstitutionModel:
        model = self.get(id=id)

        for key, value in data.model_dump().items():
            setattr(model, key, value)

        self.db.commit()
        self.db.refresh(model)

        return model

    def delete(self, id: str) -> None:
        institution = self.get(id=id)

        self.db.delete(institution)
        self.db.commit()
