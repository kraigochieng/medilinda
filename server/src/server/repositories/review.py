from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from server.basemodels.review import ReviewPostRequest
from server.models.review import ReviewModel
from sqlalchemy import Row, case, desc, false, func, select, true
from sqlalchemy.orm import Session, selectinload


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self, causality_assessment_level_id: str | None, user_id: str | None
    ) -> Page[ReviewModel]:
        stmt = select(ReviewModel).options(selectinload(ReviewModel.user))

        if causality_assessment_level_id:
            stmt = stmt.filter(
                ReviewModel.causality_assessment_level_id
                == causality_assessment_level_id
            )

        if user_id:
            stmt = stmt.filter(ReviewModel.user_id == user_id)

        return paginate(self.db, stmt, params=Params(page=1, size=50))

    def get(self, review_id: str) -> ReviewModel:
        stmt = select(ReviewModel).where(ReviewModel.id == review_id)
        return self.db.scalar(stmt)

    def get_by_causality_assessment_level_id(
        self, causality_assessment_level_id: str
    ) -> Page[ReviewModel]:
        stmt = (
            select(ReviewModel)
            .where(
                ReviewModel.causality_assessment_level_id
                == causality_assessment_level_id
            )
            .order_by(desc(ReviewModel.created_at))
        )

        return paginate(self.db, stmt)

    def get_review_counts_by_causality_level(
        self, causality_assessment_level_id: str
    ) -> Row:
        """
        Gets the count of approved and unapproved reviews for a specific
        causality_assessment_level_id.
        """
        stmt = (
            select(
                # Use func.count(case(...)) to conditionally count
                func.count(case((ReviewModel.approved == true(), 1))).label(
                    "approved_reviews"
                ),
                func.count(case((ReviewModel.approved == false(), 1))).label(
                    "unapproved_reviews"
                ),
            )
            .select_from(ReviewModel)
            .where(
                ReviewModel.causality_assessment_level_id
                == causality_assessment_level_id
            )
        )

        # .first() is correct here because a count query always returns one row
        result = self.db.execute(stmt).first()

        # This will return a single Row object, e.g., (approved_reviews=5, unapproved_reviews=2)
        # If no reviews match, it will correctly return (approved_reviews=0, unapproved_reviews=0)
        return result

    def create(
        self,
        data: ReviewPostRequest,
    ) -> ReviewModel:
        model = ReviewModel(**data.model_dump())

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return model

    def update(self, review_id: str, review_update: ReviewPostRequest) -> ReviewModel:
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
