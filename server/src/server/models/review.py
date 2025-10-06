from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from ..basemodels.causality_asssessment_level import CausalityAssessmentLevelEnum
from ..db.base import Base
from ._mixins import IDMixin, TimestampMixin


class ReviewModel(Base, IDMixin, TimestampMixin):
    __tablename__ = "review"

    causality_assessment_level_id = Column(
        String, ForeignKey("causality_assessment_level.id"), nullable=False
    )
    causality_assessment_level = relationship(
        "CausalityAssessmentLevelModel",
        back_populates="reviews",
    )

    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    user = relationship("UserModel", back_populates="reviews")

    approved = Column(Boolean, nullable=False)

    proposed_causality_level = Column(
        SQLAlchemyEnum(CausalityAssessmentLevelEnum), nullable=True
    )

    reason = Column(String, nullable=True)  # Why it was approved