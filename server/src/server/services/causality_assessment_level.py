from fastapi_pagination import Page, Params

from server.basemodels.causality_asssessment_level import (
    CausalityAssessmentLevelGetResponse,
    CausalityAssessmentLevelPostRequest,
)
from server.basemodels.review import ReviewGetResponse, ReviewPostRequest
from server.repositories.causality_assessment_level import (
    CausalityAssessmentLevelRepository,
)
from server.repositories.review import ReviewRepository
from server.repositories.user import UserRepository


class CausalityAssessmentLevelService:
    def __init__(self, db):
        self.repo = CausalityAssessmentLevelRepository(db)
        self.review_repo = ReviewRepository(db)
        self.user_repo = UserRepository(db)

    def get_causality_assessment_level_by_id(
        self, id: str
    ) -> CausalityAssessmentLevelGetResponse:
        model = self.repo.get_by_id(id=id)

        return CausalityAssessmentLevelGetResponse.model_validate(model)

    def get_causality_assessment_levels(
        self, adr_id: str | None, pagination_params: Params
    ) -> Page[CausalityAssessmentLevelGetResponse]:
        return self.repo.get_all(adr_id=adr_id, pagination_params=pagination_params)

    def create_causality_assessment_level(
        self, data: CausalityAssessmentLevelPostRequest
    ) -> CausalityAssessmentLevelGetResponse:
        model = self.repo.create(data=data)

        return CausalityAssessmentLevelGetResponse.model_validate(model)

    def update_causality_assessment_level_by_id(
        self, id: str, data: CausalityAssessmentLevelPostRequest
    ) -> CausalityAssessmentLevelGetResponse:
        model = self.repo.update(id=id, data=data)

        return CausalityAssessmentLevelGetResponse.model_validate(model)

    def delete_causality_assessment_level_by_id(self, id: str) -> None:
        self.repo.delete(id=id)

    # def create_review(
    #     self, id: str, username: str, data: ReviewPostRequest
    # ) -> ReviewGetResponse | None:
    #     cal_model = self.repo.get_by_id(id)

    #     if not cal_model:
    #         return None

    #     user = self.user_repo.get_by_username(username=username)

    #     if not user:
    #         return None

    #     review_model = self.review_repo.create(
    #         data=data, causality_assessment_level_id=id, user_id=user.id
    #     )

    #     return review_model
