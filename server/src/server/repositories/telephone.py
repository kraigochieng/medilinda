from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from server.basemodels.medical_institution import MedicalInstitutionTelephonePostRequest
from server.models.medical_institution import MedicalInstitutionTelephoneModel
from sqlalchemy import select
from sqlalchemy.orm import Session


class TelephoneRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> Page[MedicalInstitutionTelephoneModel]:
        stmt = select(MedicalInstitutionTelephoneModel)
        return paginate(self.db, stmt)

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
