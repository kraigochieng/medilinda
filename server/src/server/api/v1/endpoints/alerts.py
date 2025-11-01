from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi_pagination import Page, Params
from sqlalchemy.orm import Session

from server.basemodels.alerts import ADRAlertResponse
from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.models.causality_assessment_level import (
    CausalityAssessmentLevelEnum,
)
from server.services.alerts import AlertService
from server.utils.auth import get_current_active_user


def get_alert_service(db: Session = Depends(get_db)) -> AlertService:
    """Dependency injector for the AlertService."""
    return AlertService(db=db)


router = APIRouter(prefix="/api/v1/alerts", tags=["alerts", "v1"])


@router.get(
    "/",
    response_model=Page[ADRAlertResponse],
    status_code=status.HTTP_200_OK,
)
async def get_adr_alerts(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    pagination_params: Params = Depends(),
    query: str = Query("", description="Search query for patient name (optional)"),
    causality_level: CausalityAssessmentLevelEnum | None = Query(
        None,
        description="Filter by a single causality level. (e.g., certain, unclassified)",
    ),
    has_been_sent: bool | None = Query(
        None,
        description="Filter by SMS status. True = SMS sent (count > 0), False = SMS not sent (count = 0), Not provided = All",
    ),
    service: AlertService = Depends(get_alert_service),
):
    """
    Individual Alerts: certain, has_been_sent
    Additional Info Requests: unclassified, has_been_sent
    To Be Sent Individual Alerts: certain, not has_been_sent
    To Be Sent Additional Info Requests: unclassified, not has_been_sent
    Unclassifiable: unclassifiable, has_been_sent
    """
    return service.get_paginated_alerts(
        pagination_params=pagination_params,
        query=query,
        causality_level=causality_level,
        has_been_sent=has_been_sent,
    )
