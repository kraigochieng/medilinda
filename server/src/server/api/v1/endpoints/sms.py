from typing import Annotated, Dict

import africastalking
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, paginate
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from server.basemodels.sms import (
    AdditionalInfoPostRequest,
    IndividualAlertPostRequest,
    SMSMessageGetResponse,
    SMSMessageTypeEnum,
)
from server.basemodels.user import UserDetailsBaseModel
from server.settings import settings
from server.dependencies import get_db
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.medical_institution import (
    MedicalInstitutionModel,
    MedicalInstitutionTelephoneModel,
)
from server.models.sms import SMSMessageModel
from server.services.auth import get_current_active_user

router = APIRouter(prefix="/api/v1/sms-messages", tags=["sms-messages", "v1"])


@router.get(
    "/",
    response_model=Page[SMSMessageGetResponse],
)
async def get_sms_messages(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    sms_type: SMSMessageTypeEnum | None = Query(None, description="Filter by SMS type"),
    adr_id: str | None = Query(None, description="Filter by ADR ID"),
    db: Session = Depends(get_db),
):
    if sms_type:
        content = db.query(SMSMessageModel).filter(SMSMessageModel.sms_type == sms_type)
    elif adr_id:
        content = db.query(SMSMessageModel).filter(SMSMessageModel.adr_id == adr_id)
    else:
        content = db.query(SMSMessageModel)

    content = content.order_by(desc(SMSMessageModel.created_at))

    return paginate(content)


@router.get("/{sms_message_id}", status_code=status.HTTP_200_OK)
async def get_sms_message_by_id(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    sms_message_id: str = Path(..., description="ID of Medical Institution to delete"),
    db: Session = Depends(get_db),
):
    db_sms_message = (
        db.query(SMSMessageModel).filter(SMSMessageModel.id == sms_message_id).first()
    )

    if not db_sms_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMS Message not found",
        )

    return JSONResponse(
        content=jsonable_encoder(db_sms_message), status_code=status.HTTP_200_OK
    )
