from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.models.review import ReviewModel
from server.models.user import UserModel
from server.utils.auth import get_current_active_user

router = APIRouter(prefix="/api/v1/reviews-details", tags=["reviews-details", "v1"])


@router.get(
    "/specific-user-and-causality-assessment-level",
    status_code=status.HTTP_200_OK,
)
async def get_review_for_specific_user_and_causality_assessment_level(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    causality_assessment_level_id: str = Query(
        ..., description="ID of Causality Assessment to read"
    ),
    db: Session = Depends(get_db),
):
    db_user = (
        db.query(UserModel).filter(UserModel.username == current_user.username).first()
    )

    review = (
        db.query(ReviewModel)
        .filter(
            ReviewModel.causality_assessment_level_id == causality_assessment_level_id,
            ReviewModel.user_id == db_user.id,
        )
        .first()
    )

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    return review
