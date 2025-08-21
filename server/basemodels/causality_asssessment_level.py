import enum
from typing import Any, List, Optional

from pydantic import BaseModel


class CausalityAssessmentLevelEnum(str, enum.Enum):
    certain = "certain"
    likely = "likely"
    possible = "possible"
    unlikely = "unlikely"
    unclassified = "unclassified"
    unclassifiable = "unclassifiable"

class CausalityAssessmentLevelGetResponse(BaseModel):
    id: str
    adr_id: str
    ml_model_id: str = "final_ml_model@champion"
    causality_assessment_level_value: CausalityAssessmentLevelEnum

    base_values: Optional[List[float]] = None
    shap_values_matrix: Optional[List[List[float]]] = None
    shap_values_sum_per_class: Optional[List[float]] = None
    shap_values_and_base_values_sum_per_class: Optional[List[float]] = None
    feature_names: Optional[List[str]] = None
    feature_values: Optional[List[Any]] = None


class UnclassifiablePostRequest(BaseModel):
    adr_ids: List[str]
