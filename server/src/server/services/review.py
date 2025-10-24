from sqlalchemy.orm import Session
from server.repositories.review import ReviewRepository
from server.basemodels.review import (
    ADRReviewCreateRequest,
    ADRReviewGetResponse,
    ReviewGetResponse,
)
from fastapi_pagination import Page


class ReviewService:
    def __init__(self, db: Session):
        self.repository = ReviewRepository(db)

    def get_reviews(self) -> Page[ReviewGetResponse]:
        return self.repository.get_all()

    def get_review_by_id(self, review_id: str) -> ReviewGetResponse:
        return self.repository.get(review_id)

    def create_review(
        self,
        review_data: ADRReviewCreateRequest,
        causality_assessment_level_id: str,
        user_id: str,
    ) -> ReviewGetResponse:
        return self.repository.create(
            review_data, causality_assessment_level_id, user_id
        )

    def update_review(
        self, review_id: str, review_update: ADRReviewCreateRequest
    ) -> ReviewGetResponse:
        return self.repository.update(review_id, review_update)

    def delete_review(self, review_id: str) -> bool:
        return self.repository.delete(review_id)
