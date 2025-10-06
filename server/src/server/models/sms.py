from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from ..basemodels.sms import SMSMessageTypeEnum
from ..db.base import Base
from ._mixins import IDMixin, TimestampMixin


class SMSMessageModel(Base, IDMixin, TimestampMixin):
    __tablename__ = "sms_message"

    message_id = Column(String, nullable=True)
    sms_type = Column(SQLAlchemyEnum(SMSMessageTypeEnum), nullable=False)
    number = Column(String, nullable=False)
    content = Column(String, nullable=False)
    cost = Column(String, nullable=False)
    message_parts = Column(Integer, nullable=True)
    status = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)

    adr_id = Column(String, ForeignKey("adr.id"), nullable=True)
    adr = relationship("ADRModel", back_populates="sms_messages")
