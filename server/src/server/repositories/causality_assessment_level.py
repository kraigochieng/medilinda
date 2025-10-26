from fastapi import HTTPException
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from server.basemodels.causality_asssessment_level import (
    CausalityAssessmentLevelPostRequest,
)
from server.basemodels.review import ReviewPostRequest
from server.models.causality_assessment_level import CausalityAssessmentLevelModel
from sqlalchemy import select, desc
from sqlalchemy.orm import Session


class CausalityAssessmentLevelRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, cal_id: str) -> CausalityAssessmentLevelModel | None:
        stmt = select(CausalityAssessmentLevelModel).where(
            CausalityAssessmentLevelModel.id == cal_id
        )
        return self.db.scalar(stmt)

    def get_all(self, adr_id: str | None) -> Page[CausalityAssessmentLevelModel]:
        stmt = select(CausalityAssessmentLevelModel)

        if adr_id:
            stmt = stmt.where(CausalityAssessmentLevelModel.adr_id == adr_id)

        stmt = stmt.order_by(desc(CausalityAssessmentLevelModel.created_at))

        return paginate(self.db, stmt, params=Params(page=1, size=50))

    def update(
        self,
        causality_assessment_level_id: str,
        causality_assessment_level: CausalityAssessmentLevelPostRequest,
    ) -> CausalityAssessmentLevelModel | None:
        cal_model = self.get_by_id(causality_assessment_level_id)

        if not cal_model:
            return None

        for key, value in causality_assessment_level.model_dump().items():
            setattr(cal_model, key, value)

        self.db.commit()
        self.db.refresh(cal_model)

        return cal_model

    def delete(self, id: str) -> bool:
        model = self.get_by_id(id)

        if not model:
            return False

        self.db.delete(model)
        self.db.commit()

        return True
