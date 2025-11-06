from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from fastapi_pagination import Page, Params
from sqlalchemy.orm import Session

from server.basemodels.review import (
    ReviewGetResponse,
    ReviewPostRequest,
)
from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.services.review import ReviewService
from server.utils.auth import get_current_active_user

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews", "v1"])


def get_review_service(db: Session = Depends(get_db)):
    return ReviewService(db)


@router.get("/", response_model=Page[ReviewGetResponse], status_code=status.HTTP_200_OK)
async def get_reviews(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    pagination_params: Params = Depends(),
    causality_assessment_level_id: str | None = Query(
        None, description="Causality Assessment Level Id"
    ),
    user_id: str | None = Query(None, description="User Id"),
    service: ReviewService = Depends(get_review_service),
):
    return service.get_reviews(
        causality_assessment_level_id=causality_assessment_level_id,
        user_id=user_id,
        pagination_params=pagination_params,
    )


@router.post("/", response_model=ReviewGetResponse, status_code=status.HTTP_201_CREATED)
async def post_review(
    data: ReviewPostRequest,
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    service: ReviewService = Depends(get_review_service),
):
    return service.create_review(data=data)


@router.get("/{id}", response_model=ReviewGetResponse, status_code=status.HTTP_200_OK)
async def get_review_by_id(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    id: str = Path(..., description="Review ID"),
    service: ReviewService = Depends(get_review_service),
):
    return service.get_review_by_id(id=id)


@router.put("/{id}", response_model=ReviewGetResponse, status_code=status.HTTP_200_OK)
async def update_review_by_id(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    data: ReviewPostRequest = None,
    id: str = Path(..., description="ID of review to update"),
    service: ReviewService = Depends(get_review_service),
):
    return service.update_review(id=id, data=data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review_by_id(
    id: str = Path(..., description="ID of review to delete"),
    service: ReviewService = Depends(get_review_service),
):
    service.delete_review(id=id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
