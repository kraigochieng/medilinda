from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from server.basemodels.medical_institution import MedicalInstitutionTelephonePostRequest
from server.models.medical_institution import MedicalInstitutionTelephoneModel
from sqlalchemy import select, desc
from sqlalchemy.orm import Session


class TelephoneRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self, medical_institution_id: str | None
    ) -> Page[MedicalInstitutionTelephoneModel]:
        stmt = select(MedicalInstitutionTelephoneModel)

        if medical_institution_id:
            stmt = stmt.where(
                MedicalInstitutionTelephoneModel.medical_institution_id
                == medical_institution_id
            )

        stmt = stmt.order_by(desc(MedicalInstitutionTelephoneModel.created_at))

        return paginate(self.db, stmt, params=Params(page=1, size=50))

    def get_by_id(self, telephone_id: str) -> MedicalInstitutionTelephoneModel | None:
        stmt = select(MedicalInstitutionTelephoneModel).where(
            MedicalInstitutionTelephoneModel.id == telephone_id
        )
        return self.db.scalar(stmt)

    def create(
        self, telephone: MedicalInstitutionTelephonePostRequest
    ) -> MedicalInstitutionTelephoneModel:
        obj = MedicalInstitutionTelephoneModel(**telephone.model_dump())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(
        self, telephone_id: str, telephone: MedicalInstitutionTelephonePostRequest
    ) -> MedicalInstitutionTelephoneModel | None:
        obj = self.get_by_id(telephone_id)

        if not obj:
            return None

        for key, value in telephone.model_dump().items():
            setattr(obj, key, value)

        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, telephone_id: str) -> bool:
        obj = self.get_by_id(telephone_id)

        if not obj:
            return False

        self.db.delete(obj)
        self.db.commit()
        return True
