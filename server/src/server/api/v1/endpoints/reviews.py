from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from server.basemodels.review import ADRReviewCreateRequest, ADRReviewGetResponse, ReviewGetResponse
from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.services.auth import get_current_active_user
from server.services.review import ReviewService
from fastapi_pagination import Page

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews", "v1"])


def get_review_service(db: Session = Depends(get_db)):
    return ReviewService(db)


@router.get(
    "/", response_model=Page[ReviewGetResponse], status_code=status.HTTP_200_OK
)
async def get_reviews(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    service: ReviewService = Depends(get_review_service),
):
    return service.get_reviews()


@router.get("/{review_id}", status_code=status.HTTP_200_OK)
async def get_review_by_id(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    review_id: str = Path(..., description="Review ID"),
    service: ReviewService = Depends(get_review_service),
):
    review = service.get_review_by_id(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )
    return JSONResponse(
        content=jsonable_encoder(review), status_code=status.HTTP_200_OK
    )


@router.put("/{review_id}", status_code=status.HTTP_200_OK)
async def update_review_by_id(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    review_update: ADRReviewCreateRequest = None,
    review_id: str = Path(..., description="ID of review to update"),
    service: ReviewService = Depends(get_review_service),
):
    updated_review = service.update_review(review_id, review_update)
    if not updated_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )
    return JSONResponse(
        content=jsonable_encoder(updated_review), status_code=status.HTTP_200_OK
    )


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review_by_id(
    review_id: str = Path(..., description="ID of review to delete"),
    service: ReviewService = Depends(get_review_service),
):
    deleted = service.delete_review(review_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review record not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
