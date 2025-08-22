from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from ..db.base import Base
from ._mixins import IDMixin, TimestampMixin


# Add the relationship in ADRModel to allow back-reference to reviews
class UserModel(Base, IDMixin, TimestampMixin):
    __tablename__ = "user"

    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    disabled = Column(Boolean, nullable=False, default=False)

    reviews = relationship(
        "ReviewModel", back_populates="user", cascade="all, delete-orphan"
    )
    adrs = relationship("ADRModel", back_populates="user", cascade="all, delete-orphan")
