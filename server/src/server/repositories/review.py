from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from server.basemodels.review import ADRReviewCreateRequest
from server.models.review import ReviewModel
from sqlalchemy import desc, select
from sqlalchemy.orm import Session


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> Page[ReviewModel]:
        stmt = select(ReviewModel).order_by(desc(ReviewModel.created_at))
        return paginate(self.db, stmt)

    def get(self, review_id: str) -> ReviewModel:
        stmt = select(ReviewModel).where(ReviewModel.id == review_id)
        return self.db.scalar(stmt)

    def create(
        self,
        review_data: ADRReviewCreateRequest,
        causality_assessment_level_id: str,
        user_id: str,
    ) -> ReviewModel:
        review = ReviewModel(
            causality_assessment_level_id=causality_assessment_level_id,
            user_id=user_id,
            approved=review_data.approved,
            proposed_causality_level=review_data.proposed_causality_level,
            reason=review_data.reason,
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def update(
        self, review_id: str, review_update: ADRReviewCreateRequest
    ) -> ReviewModel:
        review = self.get(review_id)
        if not review:
            return None
        for key, value in review_update.model_dump().items():
            setattr(review, key, value)
        self.db.commit()
        self.db.refresh(review)
        return review

    def delete(self, review_id: str) -> bool:
        review = self.get(review_id)
        if not review:
            return False
        self.db.delete(review)
        self.db.commit()
        return True
