import enum
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict


class CausalityAssessmentLevelEnum(str, enum.Enum):
    certain = "certain"
    likely = "likely"
    possible = "possible"
    unlikely = "unlikely"
    unclassified = "unclassified"
    unclassifiable = "unclassifiable"


class CausalityAssessmentLevelGetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class CausalityAssessmentLevelPostRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    adr_id: str | None
    ml_model_id: str = "final_ml_model@champion"
    causality_assessment_level_value: CausalityAssessmentLevelEnum | None

    base_values: Optional[List[float]] = None
    shap_values_matrix: Optional[List[List[float]]] = None
    shap_values_sum_per_class: Optional[List[float]] = None
    shap_values_and_base_values_sum_per_class: Optional[List[float]] = None
    feature_names: Optional[List[str]] = None
    feature_values: Optional[List[Any]] = None


class UnclassifiablePostRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    adr_ids: List[str]
