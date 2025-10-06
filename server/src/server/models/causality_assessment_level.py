from sqlalchemy import JSON, Column, ForeignKey, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from ..basemodels.causality_asssessment_level import CausalityAssessmentLevelEnum
from ..db.base import Base
from ._mixins import IDMixin, TimestampMixin


class CausalityAssessmentLevelModel(Base, IDMixin, TimestampMixin):
    __tablename__ = "causality_assessment_level"

    adr_id = Column(String, ForeignKey("adr.id"), nullable=False)
    adr = relationship(
        "ADRModel",
        back_populates="causality_assessment_levels",
    )

    ml_model_id = Column(
        String,
        nullable=False,
        default="final_ml_model@champion",
    )

    causality_assessment_level_value = Column(
        SQLAlchemyEnum(CausalityAssessmentLevelEnum), nullable=False
    )

    base_values = Column(JSON, nullable=True)
    shap_values_matrix = Column(JSON, nullable=True)
    shap_values_sum_per_class = Column(JSON, nullable=True)
    shap_values_and_base_values_sum_per_class = Column(JSON, nullable=True)
    feature_names = Column(JSON, nullable=True)
    feature_values = Column(JSON, nullable=True)

    reviews = relationship(
        "ReviewModel",
        back_populates="causality_assessment_level",
        cascade="all, delete-orphan",
    )
