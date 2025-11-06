import enum
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SMSMessageTypeEnum(str, enum.Enum):
    individual_alert = "individual alert"
    # bulk_alert = "bulk alert"
    additional_info = "additional info"


# SMS Message
class SMSMessageGetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)
    
    adr_id: str


class AdditionalInfoPostRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    adr_id: str


class SMSCountResponse(BaseModel):
    """
    Response model for aggregated SMS counts by ADR.
    """
    model_config = ConfigDict(from_attributes=True)

    adr_id: str
    sms_type: SMSMessageTypeEnum
    medical_institution_mfl_code: str
    medical_institution_name: str
    patient_name: str
    sms_count: int