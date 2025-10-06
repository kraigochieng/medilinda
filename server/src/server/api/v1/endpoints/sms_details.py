from fastapi import APIRouter, Depends, Query
from fastapi_pagination import Page
from sqlalchemy import func
from sqlalchemy.orm import Session

from server.basemodels.sms import (
    SMSMessageTypeEnum,
)
from server.dependencies import get_db
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.medical_institution import (
    MedicalInstitutionModel,
)
from server.models.sms import SMSMessageModel

router = APIRouter(prefix="/api/v1/sms-messages-details", tags=["sms-messages", "v1"])


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
