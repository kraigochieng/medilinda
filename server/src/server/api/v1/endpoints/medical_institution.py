from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from server.basemodels.medical_institution import (
    MedicalInstitutionGetResponse,
    MedicalInstitutionPostRequest,
    MedicalInstitutionTelephoneGetResponse,
)
from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.services.auth import get_current_active_user
from server.services.medical_institution import MedicalInstitutionService


def get_medical_institution_service(db: Session = Depends(get_db)):
    return MedicalInstitutionService(db)


router = APIRouter(
    prefix="/api/v1/medical-institutions", tags=["medical-institutions", "v1"]
)


@router.get("/", response_model=Page[MedicalInstitutionGetResponse])
async def get_medical_institutions(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    query: str = Query("", description="Search query(optional)"),
    service: MedicalInstitutionService = Depends(get_medical_institution_service),
):
    return service.get_medical_institutions(query)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def post_medical_institution(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    institution: MedicalInstitutionPostRequest = None,
    service: MedicalInstitutionService = Depends(get_medical_institution_service),
):
    new_institution = service.create_medical_institution(institution)
    return JSONResponse(
        content=jsonable_encoder(new_institution), status_code=status.HTTP_201_CREATED
    )


@router.get("/{institution_id}", status_code=status.HTTP_200_OK)
async def get_medical_institution_by_id(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    institution_id: str = Path(..., description="ID of Medical Institution"),
    service: MedicalInstitutionService = Depends(get_medical_institution_service),
):
    institution = service.get_medical_institution_by_id(institution_id)
    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical Institution not found",
        )
    return JSONResponse(
        content=jsonable_encoder(institution), status_code=status.HTTP_200_OK
    )


@router.put("/{institution_id}", status_code=status.HTTP_200_OK)
async def update_medical_institution(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    institution: MedicalInstitutionPostRequest = None,
    institution_id: str = Path(..., description="ID of Medical Institution to update"),
    service: MedicalInstitutionService = Depends(get_medical_institution_service),
):
    updated_institution = service.update_medical_institution(
        institution, institution_id
    )
    return JSONResponse(
        content=jsonable_encoder(updated_institution), status_code=status.HTTP_200_OK
    )


@router.delete("/{institution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medical_institution(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    institution_id: str = Path(..., description="ID of Medical Institution to delete"),
    service: MedicalInstitutionService = Depends(get_medical_institution_service),
):
    service.delete_medical_institution(institution_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{institution_id}/telephone",
    response_model=Page[MedicalInstitutionTelephoneGetResponse],
)
async def get_telephones_for_medical_institution(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    institution_id: str = Path(..., description="ID of the Medical Institution"),
    service: MedicalInstitutionService = Depends(get_medical_institution_service),
):
    return service.get_telephones_for_medical_institution(institution_id)
