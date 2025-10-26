from fastapi_pagination import Page
from sqlalchemy.orm import Session

from server.basemodels.review import (
    ReviewGetResponse,
    ReviewPostRequest,
)
from server.repositories.review import ReviewRepository


class ReviewService:
    def __init__(self, db: Session):
        self.repository = ReviewRepository(db)

    def get_reviews(
        self, causality_assessment_level_id: str | None, user_id: str | None
    ) -> Page[ReviewGetResponse]:
        return self.repository.get_all(
            causality_assessment_level_id=causality_assessment_level_id, user_id=user_id
        )

    def get_review_by_id(self, review_id: str) -> ReviewGetResponse:
        return self.repository.get(review_id)

    def create_review(
        self,
        data: ReviewPostRequest,
    ) -> ReviewGetResponse:
        return self.repository.create(data=data)

    def update_review(self, id: str, data: ReviewPostRequest) -> ReviewGetResponse:
        return self.repository.update(id, data)

    def delete_review(self, id: str) -> bool:
        return self.repository.delete(id)
