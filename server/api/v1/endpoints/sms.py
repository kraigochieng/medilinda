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
from server.config import settings
from server.dependencies import get_db
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.medical_institution import (
    MedicalInstitutionModel,
    MedicalInstitutionTelephoneModel,
)
from server.models.sms import SMSMessageModel
from server.services.auth import get_current_user

router = APIRouter(prefix="/api/v1/sms-messages", tags=["sms-messages", "v1"])


@router.get(
    "/",
    response_model=Page[SMSMessageGetResponse],
)
async def get_sms_messages(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
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
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
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


@router.get("/count", response_model=Page[dict])
async def get_sms_message_with_adr_and_counts(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    sms_type: SMSMessageTypeEnum | None = Query(None, description="Filter by SMS type"),
    db: Session = Depends(get_db),
):
    # Calculate offset and limit based on page and size
    offset = (page - 1) * size
    limit = size

    # Query to count rows grouped by adr_id, sms_type, and include medical institution name
    if sms_type:
        query = (
            db.query(
                SMSMessageModel.adr_id,
                SMSMessageModel.sms_type,
                MedicalInstitutionModel.mfl_code.label("medical_institution_mfl_code"),
                MedicalInstitutionModel.name.label("medical_institution_name"),
                ADRModel.patient_name.label("patient_name"),
                func.count().label("sms_count"),
            )
            .filter(SMSMessageModel.sms_type == sms_type)
            .join(
                ADRModel,
                ADRModel.id == SMSMessageModel.adr_id,
            )
            .join(
                MedicalInstitutionModel,
                MedicalInstitutionModel.id == ADRModel.medical_institution_id,
            )
            .group_by(
                SMSMessageModel.adr_id,
                SMSMessageModel.sms_type,
                MedicalInstitutionModel.name,
                MedicalInstitutionModel.mfl_code,
                ADRModel.patient_name,
            )
            .offset(offset)
            .limit(limit)
        )
    else:
        query = (
            db.query(
                SMSMessageModel.adr_id,
                SMSMessageModel.sms_type,
                MedicalInstitutionModel.mfl_code.label("medical_institution_mfl_code"),
                MedicalInstitutionModel.name.label("medical_institution_name"),
                ADRModel.patient_name.label("patient_name"),
                func.count().label("sms_count"),
            )
            .join(
                ADRModel,
                ADRModel.id == SMSMessageModel.adr_id,
            )
            .join(
                MedicalInstitutionModel,
                MedicalInstitutionModel.id == ADRModel.medical_institution_id,
            )
            .group_by(
                SMSMessageModel.adr_id,
                SMSMessageModel.sms_type,
                MedicalInstitutionModel.name,
                MedicalInstitutionModel.mfl_code,
                ADRModel.patient_name,
            )
            .offset(offset)
            .limit(limit)
        )

    # Query to get the total count of records
    if sms_type:
        total_query = (
            db.query(func.count().label("total"))
            .select_from(SMSMessageModel)
            .filter(SMSMessageModel.sms_type == sms_type)
            .join(
                ADRModel,
                ADRModel.id == SMSMessageModel.adr_id,
            )
            .join(
                MedicalInstitutionModel,
                MedicalInstitutionModel.id == ADRModel.medical_institution_id,
            )
        )
    else:
        total_query = (
            db.query(func.count().label("total"))
            .select_from(SMSMessageModel)
            .join(
                ADRModel,
                ADRModel.id == SMSMessageModel.adr_id,
            )
            .join(
                MedicalInstitutionModel,
                MedicalInstitutionModel.id == ADRModel.medical_institution_id,
            )
        )
    # Get total count
    total_result = (
        total_query.scalar()
    )  # Executes the query and gets the scalar value (total count)

    # Calculate the total number of pages
    pages = (total_result + size - 1) // size  # Equivalent to math.ceil(total / size)

    # Execute the query and get the results
    result = query.all()

    items = [
        {
            "adr_id": row.adr_id,
            "sms_type": row.sms_type,
            "medical_institution_mfl_code": row.medical_institution_mfl_code,
            "medical_institution_name": row.medical_institution_name,
            "patient_name": row.patient_name,
            "sms_count": row.sms_count,
        }
        for row in result
    ]

    return {
        "items": items,
        "total": total_result,
        "page": page,
        "size": size,
        "pages": pages,
    }


@router.post("/api/v1/send_individual_alert")
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


@router.post("/api/v1/send_additional_info_request")
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