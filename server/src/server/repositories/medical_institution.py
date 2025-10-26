from fastapi import HTTPException, status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from server.basemodels.medical_institution import (
    MedicalInstitutionPostRequest,
)
from server.models.medical_institution import (
    MedicalInstitutionModel,
    MedicalInstitutionTelephoneModel,
)
from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session


class MedicalInstitutionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, query: str = "") -> Page[MedicalInstitutionModel]:
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

        return paginate(self.db, stmt, params=Params(page=1, size=50))

    def create(
        self, institution_data: MedicalInstitutionPostRequest
    ) -> MedicalInstitutionModel:
        new_institution = MedicalInstitutionModel(**institution_data.model_dump())
        self.db.add(new_institution)
        self.db.commit()
        self.db.refresh(new_institution)
        return new_institution

    def get(self, institution_id: str) -> MedicalInstitutionModel:
        stmt = select(MedicalInstitutionModel).where(
            MedicalInstitutionModel.id == institution_id
        )
        return self.db.scalar(stmt)

    def update(
        self, institution: MedicalInstitutionPostRequest, institution_id: str
    ) -> MedicalInstitutionModel:
        stmt = select(MedicalInstitutionModel).where(
            MedicalInstitutionModel.id == institution_id
        )
        db_institution = self.db.scalar(stmt)

        if not db_institution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical Institution not found",
            )

        for key, value in institution.model_dump().items():
            setattr(db_institution, key, value)

        self.db.commit()
        self.db.refresh(db_institution)

        return db_institution

    def delete(self, institution_id: str) -> None:
        stmt = select(MedicalInstitutionModel).where(
            MedicalInstitutionModel.id == institution_id
        )

        institution = self.db.scalar(stmt)

        if not institution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical Institution not found",
            )

        self.db.delete(institution)
        self.db.commit()
