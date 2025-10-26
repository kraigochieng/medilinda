from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from server.models.adverse_drug_reaction_report import ADRModel
from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from server.basemodels.adverse_drug_reaction_report import ADRPostRequest


class AdverseDrugReactionReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, query: str | None) -> Page[ADRModel]:
        stmt = select(ADRModel)

        if query:
            stmt.filter(
                ADRModel.patient_name.ilike(f"%{query}%")
                | ADRModel.patient_address.ilike(f"%{query}%")
                | ADRModel.inpatient_or_outpatient_number.ilike(f"%{query}%")
                | ADRModel.ward_or_clinic.ilike(f"%{query}%")
            )

        stmt.order_by(desc(ADRModel.created_at))

        return paginate(self.db, stmt, params=Params(page=1, size=50))

    def get_by_id(self, id: str) -> ADRModel | None:
        stmt = select(ADRModel).where(ADRModel.id == id)

        return self.db.scalar(stmt)

    def update(self, id: str, data: ADRPostRequest) -> ADRModel | None:
        model = self.get(id)

        if not model:
            return None

        for key, value in data.model_dump().items():
            setattr(model, key, value)

        self.db.commit()
        self.db.refresh(model)

        return model

    def delete(self, id: str) -> bool:
        model = self.get(id)

        if not model:
            return False

        self.db.delete(model)
        self.db.commit()

        return True
