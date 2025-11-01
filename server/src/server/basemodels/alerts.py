from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ADRAlertResponse(BaseModel):
    """
    Response model for an ADR alert, including institution
    details and SMS count.
    """

    model_config = ConfigDict(from_attributes=True)

    adr_id: str
    patient_name: str
    medical_institution_name: str
    medical_institution_mfl_code: str
    created_at: datetime
    telephones: list[str]
    sms_count: int
