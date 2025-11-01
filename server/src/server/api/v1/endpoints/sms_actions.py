from typing import Dict

import africastalking
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.basemodels.sms import (
    AdditionalInfoPostRequest,
    IndividualAlertPostRequest,
    SMSMessageGetResponse,
    SMSMessageTypeEnum,
)
from server.clients.sms import AfricasTalkingClient, get_sms_client
from server.dependencies import get_db
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.medical_institution import (
    MedicalInstitutionModel,
    MedicalInstitutionTelephoneModel,
)
from server.models.sms import SMSMessageModel
from server.repositories.sms import SMSMessageRepository
from server.services.sms import SMSMessageService
from server.settings import settings

router = APIRouter(prefix="/api/v1/sms-messages-actions", tags=["sms-messages", "v1"])


def get_sms_service(
    db: Session = Depends(get_db),
    sms_client: AfricasTalkingClient = Depends(get_sms_client),
) -> SMSMessageService:
    """
    Dependency injector for the SMSMessageService.
    """
    return SMSMessageService(db=db, sms_client=sms_client)


@router.post("/send-individual-alert", response_model=list[SMSMessageGetResponse])
def send_individual_alert(
    data: IndividualAlertPostRequest,
    service: SMSMessageService = Depends(get_sms_service),
):
    sms_messages = service.send_individual_alert(adr_id=data.adr_id)

    return sms_messages


@router.post(
    "/send-additional-info-request", response_model=list[SMSMessageGetResponse]
)
def send_additional_info_request(
    data: AdditionalInfoPostRequest,
    service: SMSMessageService = Depends(get_sms_service),
):
    sms_messages = service.send_additional_info_request(adr_id=data.adr_id)

    return sms_messages
