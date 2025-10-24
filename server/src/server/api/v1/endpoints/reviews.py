from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import desc
from sqlalchemy.orm import Session

from server.basemodels.review import ADRReviewCreateRequest, ReviewGetResponse
from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.models.review import ReviewModel
from server.models.user import UserModel
from server.services.auth import get_current_active_user

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews", "v1"])


@router.get(
    "/",
    response_model=Page[ReviewGetResponse],
    status_code=status.HTTP_200_OK,
)
async def get_reviews(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    query: str = Query("", description="Search query(optional)"),
    db: Session = Depends(get_db),
):
    if query:
        content = db.query(ReviewModel).order_by(desc(ReviewModel.created_at))
    else:
        content = db.query(ReviewModel).order_by(desc(ReviewModel.created_at))

    return paginate(content)


@router.get(
    "/{review_id}",
    response_model=Page[ReviewGetResponse],
    status_code=status.HTTP_200_OK,
)
async def get_reviews_by_id(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    review_id: str = Path(..., description="Review ID"),
    db: Session = Depends(get_db),
):
    review = db.query(ReviewModel).filter(ReviewModel.id == review_id).first()

    if not review:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )
    content = jsonable_encoder(review)

    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


@router.put("/{review_id}", status_code=status.HTTP_200_OK)
async def update_review_by_id(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    review_update: ADRReviewCreateRequest,
    review_id: str = Path(..., description="ID of review to update"),
    db: Session = Depends(get_db),
):
    # Step 1: Get the existing review
    review = db.query(ReviewModel).filter(ReviewModel.id == review_id).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    # Step 2: Update the fields
    for key, value in review_update.model_dump().items():
        setattr(review, key, value)

    db.commit()
    db.refresh(review)

    return JSONResponse(
        content=jsonable_encoder(review),
        status_code=status.HTTP_200_OK,
    )


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_review_by_id(
    review_id: str = Path(..., description="ID of review to delete"),
    db: Session = Depends(get_db),
):
    review = db.query(ReviewModel).filter(ReviewModel.id == review_id).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review record not found"
        )

    db.delete(review)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
