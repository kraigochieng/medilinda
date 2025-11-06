from fastapi_pagination import Page, Params
from sqlalchemy.orm import Session

from server.basemodels.review import (
    ReviewGetResponse,
    ReviewPostRequest,
    ReviewStatsResponse,
)
from server.repositories.review import ReviewRepository


class ReviewService:
    def __init__(self, db: Session):
        self.repository = ReviewRepository(db)

    def get_reviews(
        self,
        causality_assessment_level_id: str | None,
        user_id: str | None,
        pagination_params: Params,
    ) -> Page[ReviewGetResponse]:
        return self.repository.get_all(
            causality_assessment_level_id=causality_assessment_level_id,
            user_id=user_id,
            pagination_params=pagination_params,
        )

    def get_review_by_id(self, id: str) -> ReviewGetResponse:
        model = self.repository.get(id=id)
    
        return ReviewGetResponse.model_validate(model)

    def get_review_stats(
        self, causality_assessment_level_id: str
    ) -> ReviewStatsResponse:
        """
        Retrieves review counts and maps them to the response model.
        """
        # Call the repository to get the database row
        counts_row = self.repository.get_review_counts_by_causality_level(
            causality_assessment_level_id=causality_assessment_level_id
        )

        # Map the RowProxy (which acts like a dict) to the Pydantic model
        # Because we set orm_mode = True in the BaseModel,
        # we can use .from_orm() for clean mapping.
        if counts_row:
            return ReviewStatsResponse.model_validate(counts_row)

        # Fallback in case something goes wrong, though count() should always return a row
        return ReviewStatsResponse(approved_reviews=0, unapproved_reviews=0)

    def create_review(
        self,
        data: ReviewPostRequest,
    ) -> ReviewGetResponse:
        model = self.repository.create(data=data)

        return ReviewGetResponse.model_validate(model)

    def update_review(self, id: str, data: ReviewPostRequest) -> ReviewGetResponse:
        model = self.repository.update(id=id, data=data)

        return ReviewGetResponse.model_validate(model)

    def delete_review(self, id: str) -> None:
        self.repository.delete(id=id)
