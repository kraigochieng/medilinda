from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from server.basemodels.review import ReviewPostRequest
from server.exceptions import ResourceNotFoundError
from server.models.review import ReviewModel
from sqlalchemy import Row, case, desc, false, func, select, true
from sqlalchemy.orm import Session, selectinload


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        causality_assessment_level_id: str | None,
        user_id: str | None,
        pagination_params: Params,
    ) -> Page[ReviewModel]:
        stmt = select(ReviewModel).options(selectinload(ReviewModel.user))

        if causality_assessment_level_id:
            stmt = stmt.filter(
                ReviewModel.causality_assessment_level_id
                == causality_assessment_level_id
            )

        if user_id:
            stmt = stmt.filter(ReviewModel.user_id == user_id)

        return paginate(self.db, stmt, params=pagination_params)

    def get(self, id: str) -> ReviewModel:
        stmt = select(ReviewModel).where(ReviewModel.id == id)

        model = self.db.scalar(stmt)

        if not model:
            raise ResourceNotFoundError(f"Review with id {id} not dound")

        return model

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

        result = self.db.execute(stmt).first()

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

    def update(self, id: str, data: ReviewPostRequest) -> ReviewModel:
        review = self.get(id=id)

        for key, value in data.model_dump().items():
            setattr(review, key, value)

        self.db.commit()
        self.db.refresh(review)

        return review

    def delete(self, id: str) -> None:
        review = self.get(id=id)

        self.db.delete(review)
        self.db.commit()
