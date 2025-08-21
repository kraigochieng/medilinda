from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from ..db.base import Base
from ._mixins import IDMixin, TimestampMixin


class MedicalInstitutionModel(Base, IDMixin, TimestampMixin):
    __tablename__ = "medical_institution"

    name = Column(String, nullable=False)
    mfl_code = Column(String, nullable=True)
    dhis_code = Column(String, nullable=True)
    county = Column(String, nullable=True)
    sub_county = Column(String, nullable=True)

    telephones = relationship(
        "MedicalInstitutionTelephoneModel",
        back_populates="medical_institution",
        cascade="all, delete-orphan",
    )

    adrs = relationship("ADRModel", back_populates="medical_institution")


class MedicalInstitutionTelephoneModel(Base, IDMixin, TimestampMixin):
    __tablename__ = "medical_institution_telephone"

    medical_institution_id = Column(
        String, ForeignKey("medical_institution.id", ondelete="CASCADE"), nullable=False
    )
    medical_institution = relationship(
        "MedicalInstitutionModel", back_populates="telephones"
    )

    telephone = Column(String, nullable=False)