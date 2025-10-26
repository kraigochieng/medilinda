from typing import Annotated, Dict

import africastalking
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from server.basemodels.sms import (
    SMSMessageGetResponse,
    SMSMessageTypeEnum,
)
from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.services.sms import SMSMessageService
from server.utils.auth import get_current_active_user

router = APIRouter(prefix="/api/v1/sms-messages", tags=["sms-messages", "v1"])


def get_sms_service(db: Session = Depends(get_db)):
    return SMSMessageService(db)


@router.get(
    "/",
    response_model=Page[SMSMessageGetResponse],
)
async def get_sms_messages(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    sms_type: SMSMessageTypeEnum | None = Query(None, description="Filter by SMS type"),
    adr_id: str | None = Query(None, description="Filter by ADR ID"),
    service: SMSMessageService = Depends(get_sms_service),
):
    return service.list_messages(adr_id=adr_id, sms_type=sms_type)


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_sms_message_by_id(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    id: str = Path(..., description="ID of Medical Institution to delete"),
    service: SMSMessageService = Depends(get_sms_service),
):
    content = service.get_message_by_id(id)

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMS Message not found",
        )

    return JSONResponse(
        content=jsonable_encoder(content), status_code=status.HTTP_200_OK
    )
