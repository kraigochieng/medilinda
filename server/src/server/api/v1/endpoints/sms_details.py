from fastapi import APIRouter, Depends, Query
from fastapi_pagination import Page, Params
from sqlalchemy.orm import Session

from server.basemodels.sms import SMSCountResponse, SMSMessageTypeEnum
from server.clients.sms import AfricasTalkingClient, get_sms_client
from server.dependencies import get_db
from server.services.sms import SMSMessageService

router = APIRouter(prefix="/api/v1/sms-messages-details", tags=["sms-messages", "v1"])


def get_sms_service(
    db: Session = Depends(get_db),
    sms_client: AfricasTalkingClient = Depends(get_sms_client),
) -> SMSMessageService:
    """
    Dependency injector for the SMSMessageService.
    """
    return SMSMessageService(db=db, sms_client=sms_client)


@router.get("/count", response_model=Page[SMSCountResponse])
async def get_sms_message_with_adr_and_counts(
    pagination_params: Params = Depends(),
    sms_type: SMSMessageTypeEnum | None = Query(None, description="Filter by SMS type"),
    service: SMSMessageService = Depends(get_sms_service),
):
    return service.get_paginated_sms_counts(params=pagination_params, sms_type=sms_type)
