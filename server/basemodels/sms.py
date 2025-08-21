import enum
from datetime import datetime

from pydantic import BaseModel


class SMSMessageTypeEnum(str, enum.Enum):
    individual_alert = "individual alert"
    # bulk_alert = "bulk alert"
    additional_info = "additional info"


# SMS Message
class SMSMessageGetResponse(BaseModel):
    id: str
    adr_id: str
    content: str
    sms_type: SMSMessageTypeEnum
    cost: str | None = None
    message_id: str | None = None
    message_parts: int | None = None
    number: str | None = None
    status: str
    status_code: int
    created_at: datetime


class IndividualAlertPostRequest(BaseModel):
    adr_id: str


class AdditionalInfoPostRequest(BaseModel):
    adr_id: str
