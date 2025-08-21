from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from fastapi_pagination import Page, paginate
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload, load_only

from server.basemodels.causality_asssessment_level import (
    CausalityAssessmentLevelEnum,
    UnclassifiablePostRequest,
)
from server.basemodels.review import ADRReviewCreateRequest, ReviewGetResponse
from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.causality_assessment_level import CausalityAssessmentLevelModel
from server.models.review import ReviewModel
from server.models.user import UserModel
from server.services.auth import get_current_user

router = APIRouter(
    prefix="/api/v1/causality_assessment_levels",
    tags=["causality_assessment_levels", "v1"],
)


@router.get(
    "/{causality_assessment_level_id}",
    status_code=status.HTTP_200_OK,
)
async def get_causality_assessment_level_by_id(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    causality_assessment_level_id: str = Path(
        ..., description="ID of Causality Assessment to read"
    ),
    db: Session = Depends(get_db),
):
    causality_assessment_level = (
        db.query(CausalityAssessmentLevelModel)
        .filter(CausalityAssessmentLevelModel.id == causality_assessment_level_id)
        .first()
    )

    if not causality_assessment_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Causality Assessment Level record not found",
        )

    approved_count = sum(1 for r in causality_assessment_level.reviews if r.approved)
    not_approved_count = sum(
        1 for r in causality_assessment_level.reviews if not r.approved
    )

    content = {
        **jsonable_encoder(causality_assessment_level),
        "approved_count": approved_count,
        "not_approved_count": not_approved_count,
    }
    return JSONResponse(
        content=content,
        status_code=status.HTTP_200_OK,
    )


@router.put(
    "/{causality_assessment_level_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def update_causality_assessment_level_by_id(
    causality_assessment_level_id: str = Path(..., description="ID of CAL to update"),
    db: Session = Depends(get_db),
):
    cal_model = (
        db.query(ADRModel)
        .filter(CausalityAssessmentLevelModel.id == causality_assessment_level_id)
        .first()
    )

    if not cal_model:
        raise HTTPException(status_code=404, detail="CAL record not found")

    # Update ADR fields
    for key, value in cal_model.model_dump().items():
        setattr(cal_model, key, value)

    db.commit()
    db.refresh()

    content = jsonable_encoder(cal_model)

    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


@router.delete(
    "/{causality_assessment_level_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_causality_assessment_level_by_id(
    causality_assessment_level_id: str = Path(..., description="ID of CAL to delete"),
    db: Session = Depends(get_db),
):
    cal = (
        db.query(CausalityAssessmentLevelModel)
        .filter(CausalityAssessmentLevelModel.id == causality_assessment_level_id)
        .first()
    )

    if not cal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="CAL record not found"
        )

    db.delete(cal)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get(
    "/{causality_assessment_level_id}/review",
    response_model=Page[ReviewGetResponse],
    status_code=status.HTTP_200_OK,
)
async def get_reviews_for_causality_assessment_level(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    causality_assessment_level_id: str = Path(
        ..., description="ID of Causality Assessment to read"
    ),
    db: Session = Depends(get_db),
):
    causality_assessment_level = (
        db.query(CausalityAssessmentLevelModel)
        .filter(CausalityAssessmentLevelModel.id == causality_assessment_level_id)
        .first()
    )

    if not causality_assessment_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Causality Assessment Level record not found",
        )

    content = (
        db.query(ReviewModel)
        .options(
            joinedload(ReviewModel.user).load_only(
                UserModel.id,
                UserModel.username,
                UserModel.first_name,
                UserModel.last_name,
            )
        )
        .filter(
            ReviewModel.causality_assessment_level_id == causality_assessment_level_id
        )
        .order_by(desc(ReviewModel.created_at))
    )

    return paginate(content)

@router.get(
    "/api/v1/review_for_specific_user_and_causality_assessment_level",
    status_code=status.HTTP_200_OK,
)
async def get_review_for_specific_user_and_causality_assessment_level(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
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


@router.post(
    "/{causality_assessment_level_id}/review",
    status_code=status.HTTP_201_CREATED,
)
async def post_review(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    review: ADRReviewCreateRequest,
    causality_assessment_level_id: str = Path(
        ..., description="ID of Causality Assessment to read"
    ),
    db: Session = Depends(get_db),
):
    causality_assessment_level = (
        db.query(CausalityAssessmentLevelModel)
        .filter(CausalityAssessmentLevelModel.id == causality_assessment_level_id)
        .first()
    )

    if not causality_assessment_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Causality Level not found"
        )

    db_user = (
        db.query(UserModel).filter(UserModel.username == current_user.username).first()
    )

    review_model = ReviewModel(
        **review.model_dump(),
        user_id=db_user.id,
        causality_assessment_level_id=causality_assessment_level_id,
    )

    db.add(review_model)
    db.commit()
    db.refresh(review_model)
    # content = ADRCreateResponse.model_validate(adr_model)
    return JSONResponse(
        content=jsonable_encoder(review_model),
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/update-causalities-to-unclassifiable")
def update_causalities_to_unclassifiable(
    data: UnclassifiablePostRequest,
    db: Session = Depends(get_db),
):
    for adr_id in data.adr_ids:
        cals = (
            db.query(CausalityAssessmentLevelModel)
            .filter(CausalityAssessmentLevelModel.adr_id == adr_id)
            .all()
        )

        for cal in cals:
            cal.causality_assessment_level_value = (
                CausalityAssessmentLevelEnum.unclassifiable
            )

    db.commit()
    db.refresh()

    return JSONResponse(
        content="ADR models with unclassifiable set", status_code=status.HTTP_200_OK
    )