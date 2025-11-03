from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from server.basemodels.review import ReviewStatsResponse

# Import standard dependencies from your samples
from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db

# Import our new service and response model
from server.services.review import ReviewService
from server.utils.auth import get_current_active_user

# Per your request, the router is named "reviews-details"
router = APIRouter(prefix="/api/v1/reviews-details", tags=["reviews-details", "v1"])


def get_review_service(
    db: Session = Depends(get_db)
):
    """
    Dependency injector for the ReviewService.
    This is simpler than the sample as it doesn't need ML models.
    """
    return ReviewService(db=db)


@router.get(
    "/{causality_assessment_level_id}/stats",
    response_model=ReviewStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Approved/Unapproved Review Counts by Causality Level"
)
def get_review_statistics(
    # The ID is passed as a path parameter
    causality_assessment_level_id: str,
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    service: ReviewService = Depends(
        get_review_service
    ),
):
    """
    Retrieves the total count of approved and unapproved reviews
    for a single **Causality Assessment Level ID**.
    """
    return service.get_review_stats(
        causality_assessment_level_id=causality_assessment_level_id
    )