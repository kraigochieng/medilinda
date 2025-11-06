from fastapi import HTTPException
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from server.basemodels.causality_asssessment_level import (
    CausalityAssessmentLevelPostRequest,
)
from server.basemodels.review import ReviewPostRequest
from server.exceptions import ResourceNotFoundError
from server.models.causality_assessment_level import CausalityAssessmentLevelModel
from sqlalchemy import desc, select
from sqlalchemy.orm import Session


class CausalityAssessmentLevelRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: str) -> CausalityAssessmentLevelModel:
        stmt = select(CausalityAssessmentLevelModel).where(
            CausalityAssessmentLevelModel.id == id
        )

        model = self.db.scalar(stmt)

        if not model:
            raise ResourceNotFoundError(
                f"Causality assessment level with id {id} not found"
            )

        return model

    def get_all(
        self, adr_id: str | None, pagination_params: Params
    ) -> Page[CausalityAssessmentLevelModel]:
        stmt = select(CausalityAssessmentLevelModel)

        if adr_id:
            stmt = stmt.where(CausalityAssessmentLevelModel.adr_id == adr_id)

        stmt = stmt.order_by(desc(CausalityAssessmentLevelModel.created_at))

        return paginate(self.db, stmt, params=pagination_params)

    def create(
        self, data: CausalityAssessmentLevelPostRequest
    ) -> CausalityAssessmentLevelModel:
        model = CausalityAssessmentLevelModel(**data.model_dump())

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return model

    def update(
        self,
        id: str,
        data: CausalityAssessmentLevelPostRequest,
    ) -> CausalityAssessmentLevelModel:
        model = self.get_by_id(id=id)

        for key, value in data.model_dump().items():
            setattr(model, key, value)

        self.db.commit()
        self.db.refresh(model)

        return model

    def delete(self, id: str) -> None:
        model = self.get_by_id(id)

        self.db.delete(model)
        self.db.commit()
