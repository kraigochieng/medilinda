from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from server.basemodels.alerts import ADRAlertResponse
from server.models.causality_assessment_level import CausalityAssessmentLevelEnum
from server.repositories.alerts import AlertRepository


class AlertService:
    def __init__(self, db: Session):
        self.repository = AlertRepository(db=db)

    def get_paginated_alerts(
        self,
        pagination_params: Params,
        query: str,
        causality_level: CausalityAssessmentLevelEnum | None = None,
        has_been_sent: bool | None = None,
    ) -> Page[ADRAlertResponse]:
        search_term = f"%{query}%" if query else None

        return self.repository.get_alerts_query(
            search_term=search_term,
            causality_level=causality_level,
            has_been_sent=has_been_sent,
        )
