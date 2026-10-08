from fastapi import status
from fastapi_pagination import Page, Params
from sqlalchemy import select
from sqlalchemy.orm import Session

from server.basemodels.review import (
    ReviewGetResponse,
    ReviewPostRequest,
    ReviewStatsResponse,
    ReviewUpdateRequest,
)
from server.basemodels.user import UserDetailsBaseModel
from server.exceptions import ResourceConflictError, ServiceError
from server.models.causality_assessment_level import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelModel,
)
from server.models.review import ReviewModel
from server.repositories.causality_assessment_level import (
    CausalityAssessmentLevelRepository,
)
from server.repositories.review import ReviewRepository

MIN_REASON_LENGTH = 3


class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ReviewRepository(db)
        self.cal_repository = CausalityAssessmentLevelRepository(db)

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
        counts_row = self.repository.get_review_counts_by_causality_level(
            causality_assessment_level_id=causality_assessment_level_id
        )

        if counts_row:
            return ReviewStatsResponse.model_validate(counts_row)

        # Fallback in case something goes wrong, though count() should always return a row
        return ReviewStatsResponse(approved_reviews=0, unapproved_reviews=0)

    # ---- rules -------------------------------------------------------------

    def _require_newest(self, assessment: CausalityAssessmentLevelModel) -> None:
        """An edit that changes a model input adds a new assessment. Reviews belong
        to the prediction they judged, so only the newest one can be reviewed."""
        newest_id = self.db.scalar(
            select(CausalityAssessmentLevelModel.id)
            .where(CausalityAssessmentLevelModel.adr_id == assessment.adr_id)
            .order_by(
                CausalityAssessmentLevelModel.created_at.desc(),
                CausalityAssessmentLevelModel.id.desc(),
            )
            .limit(1)
        )
        if newest_id != assessment.id:
            raise ResourceConflictError(
                "This assessment was replaced by a newer one when the report was "
                "edited. Review the latest assessment instead."
            )

    @staticmethod
    def _check_vote(
        assessment: CausalityAssessmentLevelModel,
        approved: bool,
        proposed: CausalityAssessmentLevelEnum | None,
        reason: str | None,
    ) -> tuple[CausalityAssessmentLevelEnum | None, str | None]:
        """Returns the proposed level and reason to store."""
        if approved:
            return None, reason

        if proposed is None:
            raise ServiceError(
                "Choose the causality level you propose instead.",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if proposed == assessment.causality_assessment_level_value:
            raise ServiceError(
                "The proposed level must differ from the predicted level.",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if not reason or len(reason.strip()) < MIN_REASON_LENGTH:
            raise ServiceError(
                f"Give a reason for not approving (at least {MIN_REASON_LENGTH} characters).",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return proposed, reason

    @staticmethod
    def _require_author(review: ReviewModel, user: UserDetailsBaseModel) -> None:
        if review.user_id != user.id:
            raise ServiceError(
                "You can only change your own review.", status.HTTP_403_FORBIDDEN
            )

    # ---- changes -----------------------------------------------------------

    def create_review(
        self, data: ReviewPostRequest, user: UserDetailsBaseModel
    ) -> ReviewGetResponse:
        assessment = self.cal_repository.get_by_id(data.causality_assessment_level_id)
        self._require_newest(assessment)

        already = self.db.scalar(
            select(ReviewModel.id).where(
                ReviewModel.causality_assessment_level_id == assessment.id,
                ReviewModel.user_id == user.id,
            )
        )
        if already:
            raise ResourceConflictError(
                "You have already reviewed this assessment. Change your review instead."
            )

        proposed, reason = self._check_vote(
            assessment, data.approved, data.proposed_causality_level, data.reason
        )

        model = self.repository.create(
            data=ReviewPostRequest(
                causality_assessment_level_id=assessment.id,
                user_id=user.id,
                approved=data.approved,
                proposed_causality_level=proposed,
                reason=reason,
            )
        )

        return ReviewGetResponse.model_validate(model)

    def update_review(
        self, id: str, data: ReviewUpdateRequest, user: UserDetailsBaseModel
    ) -> ReviewGetResponse:
        review = self.repository.get(id=id)
        self._require_author(review, user)

        assessment = self.cal_repository.get_by_id(review.causality_assessment_level_id)
        self._require_newest(assessment)

        proposed, reason = self._check_vote(
            assessment, data.approved, data.proposed_causality_level, data.reason
        )

        model = self.repository.update(
            id=id,
            data=ReviewPostRequest(
                causality_assessment_level_id=review.causality_assessment_level_id,
                user_id=review.user_id,
                approved=data.approved,
                proposed_causality_level=proposed,
                reason=reason,
            ),
        )

        return ReviewGetResponse.model_validate(model)

    def delete_review(self, id: str, user: UserDetailsBaseModel) -> None:
        review = self.repository.get(id=id)
        self._require_author(review, user)

        assessment = self.cal_repository.get_by_id(review.causality_assessment_level_id)
        self._require_newest(assessment)

        self.repository.delete(id=id)
