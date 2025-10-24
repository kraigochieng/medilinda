from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import desc
from sqlalchemy.orm import Session

from server.basemodels.medical_institution import (
    MedicalInstitutionGetResponse,
    MedicalInstitutionPostRequest,
    MedicalInstitutionTelephoneGetResponse,
    MedicalInstitutionTelephonePostRequest,
    MultipleMedicalInstitutionTelephonePostRequest,
)
from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.models.medical_institution import (
    MedicalInstitutionModel,
    MedicalInstitutionTelephoneModel,
)
from server.services.auth import get_current_active_user

router = APIRouter(prefix="/api/v1/telephones", tags=["medical-institutions-telephones", "v1"])


@router.get(
    "/",
    response_model=Page[MedicalInstitutionTelephoneGetResponse],
)
async def get_medical_institution_telephones(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    content = db.query(MedicalInstitutionTelephoneModel).order_by(
        desc(MedicalInstitutionTelephoneModel.created_at)
    )
    return paginate(content)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_medical_institution_telephone(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    data: MultipleMedicalInstitutionTelephonePostRequest,
    db: Session = Depends(get_db),
):
    # Create a list of MedicalInstitutionTelephoneModel instances
    new_telephones = [
        MedicalInstitutionTelephoneModel(
            medical_institution_id=telephone.medical_institution_id,
            telephone=telephone.telephone,
        )
        for telephone in data.telephones
    ]

    db.add_all(new_telephones)  # Add all telephones to the session
    db.commit()  # Commit the changes

    for telephone in new_telephones:
        db.refresh(telephone)

    return JSONResponse(
        content=jsonable_encoder(new_telephones),
        status_code=status.HTTP_201_CREATED,
    )


@router.put(
    "/{telephone_id}",
    status_code=status.HTTP_200_OK,
)
async def update_medical_institution_telephone(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    telephone_update: MedicalInstitutionTelephonePostRequest,
    telephone_id: str = Path(..., description="ID of Telephone record to update"),
    db: Session = Depends(get_db),
):
    db_telephone = (
        db.query(MedicalInstitutionTelephoneModel)
        .filter(MedicalInstitutionTelephoneModel.id == telephone_id)
        .first()
    )

    if not db_telephone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telephone record not found",
        )

    for key, value in telephone_update.model_dump().items():
        setattr(db_telephone, key, value)

    db.commit()
    db.refresh(db_telephone)

    return JSONResponse(
        content=jsonable_encoder(db_telephone),
        status_code=status.HTTP_200_OK,
    )


@router.delete(
    "/{telephone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_medical_institution_telephone(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    telephone_id: str = Path(..., description="ID of Telephone record to delete"),
    db: Session = Depends(get_db),
):
    db_telephone = (
        db.query(MedicalInstitutionTelephoneModel)
        .filter(MedicalInstitutionTelephoneModel.id == telephone_id)
        .first()
    )

    if not db_telephone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telephone record not found",
        )

    db.delete(db_telephone)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
