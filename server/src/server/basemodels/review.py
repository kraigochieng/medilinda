from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict

from server.basemodels.causality_asssessment_level import CausalityAssessmentLevelEnum
from server.basemodels.user import UserGetResponse


class ADRReviewSchema(BaseModel):
    review_id: str
    user_id: str
    approved: bool
    proposed_causality_level: CausalityAssessmentLevelEnum | None = None
    reason: str | None = None
    created_at: datetime


class ADRReviewGetResponse(BaseModel):
    adr_id: str
    patient_id: str
    user_id: str
    patient_gender: str
    pregnancy_status: str
    known_allergy: str
    rechallenge: str
    dechallenge: str
    severity: str
    is_serious: str
    criteria_for_seriousness: str
    action_taken: str
    outcome: str
    causality_assessment_level: str | None = None
    reviews: List[ADRReviewSchema] = []


# Review
class ReviewGetResponse(BaseModel):
    id: str
    causality_assessment_level_id: str
    user_id: str
    user: UserGetResponse | None = None
    approved: bool
    proposed_causality_level: CausalityAssessmentLevelEnum | None = None
    reason: str | None
    created_at: datetime


class ReviewPostRequest(BaseModel):
    causality_assessment_level_id: str
    user_id: str
    approved: bool
    proposed_causality_level: CausalityAssessmentLevelEnum | None = None
    reason: str | None = None


class ReviewStatsResponse(BaseModel):
    """
    Response model for review statistics, showing approved
    and unapproved counts.
    """

    model_config = ConfigDict(from_attributes=True)

    approved_reviews: int
    unapproved_reviews: int
