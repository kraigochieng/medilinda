from typing import Dict

import africastalking
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.basemodels.sms import (
    AdditionalInfoPostRequest,
    IndividualAlertPostRequest,
    SMSMessageTypeEnum,
)
from server.config import settings
from server.dependencies import get_db
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.medical_institution import (
    MedicalInstitutionModel,
    MedicalInstitutionTelephoneModel,
)
from server.models.sms import SMSMessageModel

router = APIRouter(prefix="/api/v1/sms-messages-actions", tags=["sms-messages", "v1"])


@router.post("/send-individual-alert")
def send_individual_alert(
    data: IndividualAlertPostRequest, db: Session = Depends(get_db)
):
    try:
        africastalking.initialize(
            settings.africas_talking_username, settings.africas_talking_api_key
        )
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to initialize Africa's Talking: " + str(e),
        )

    sms = africastalking.SMS

    adr_model = db.query(ADRModel).filter(ADRModel.id == data.adr_id).first()

    medical_institution_model = (
        db.query(MedicalInstitutionModel)
        .filter(MedicalInstitutionModel.id == adr_model.medical_institution_id)
        .first()
    )

    telephone_number_model = (
        db.query(MedicalInstitutionTelephoneModel)
        .filter(
            MedicalInstitutionTelephoneModel.medical_institution_id
            == adr_model.medical_institution_id
        )
        .first()
    )

    message_content = (
        f"URGENT ADR ALERT: {adr_model.patient_name} at {medical_institution_model.name} "
        f"has a causality assessment of CERTAIN. We are further investigating this as the Pharmacy and Poisons Board (PPB) for further guidance. Call +254795743049 for further information."
    )

    message_type = SMSMessageTypeEnum.individual_alert

    recipients = [telephone_number_model.telephone]

    response: Dict = sms.send(message_content, recipients)

    sms_messages = []

    for message in response.get("SMSMessageData").get("Recipients"):
        sms_message = SMSMessageModel(
            adr_id=adr_model.id,
            content=message_content,
            sms_type=message_type,
            cost=message.get("cost", None),
            message_id=message.get("messageId", None),
            message_parts=message.get("messageParts", None),
            number=message.get("number", None),
            status=message.get("status"),
            status_code=message.get("statusCode"),
        )

        sms_messages.append(sms_message)

    db.add_all(sms_messages)
    db.commit()

    for sms_message in sms_messages:
        db.refresh(sms_message)

    content = jsonable_encoder(sms_messages)

    return JSONResponse(content=content, status_code=status.HTTP_200_OK)


@router.post("/send-additional-info-request")
def send_additional_info_request(
    data: AdditionalInfoPostRequest, db: Session = Depends(get_db)
):
    try:
        africastalking.initialize(
            settings.africas_talking_username, settings.africas_talking_api_key
        )
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to initialize Africa's Talking: " + str(e),
        )

    sms = africastalking.SMS

    adr_model = db.query(ADRModel).filter(ADRModel.id == data.adr_id).first()

    medical_institution_model = (
        db.query(MedicalInstitutionModel)
        .filter(MedicalInstitutionModel.id == adr_model.medical_institution_id)
        .first()
    )

    telephone_number_model = (
        db.query(MedicalInstitutionTelephoneModel)
        .filter(
            MedicalInstitutionTelephoneModel.medical_institution_id
            == adr_model.medical_institution_id
        )
        .first()
    )

    message_content = (
        f"ADR FOLLOW-UP: An ADR case involving {adr_model.patient_name} from {medical_institution_model.name} requires additional clinical details. "
        f"Kindly review and submit supporting information to the Pharmacy and Poisons Board (PPB)."
    )

    message_type = SMSMessageTypeEnum.additional_info

    recipients = [telephone_number_model.telephone]

    response: Dict = sms.send(message_content, recipients)

    sms_messages = []

    for message in response.get("SMSMessageData").get("Recipients"):
        sms_message = SMSMessageModel(
            adr_id=adr_model.id,
            content=message_content,
            sms_type=message_type,
            cost=message.get("cost", None),
            message_id=message.get("messageId", None),
            message_parts=message.get("messageParts", None),
            number=message.get("number", None),
            status=message.get("status"),
            status_code=message.get("statusCode"),
        )

        sms_messages.append(sms_message)

    db.add_all(sms_messages)
    db.commit()

    for sms_message in sms_messages:
        db.refresh(sms_message)

    content = jsonable_encoder(sms_messages)

    return JSONResponse(content=content, status_code=status.HTTP_200_OK)
