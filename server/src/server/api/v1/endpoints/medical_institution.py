from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from fastapi_pagination import Page, Params
from sqlalchemy.orm import Session

from server.basemodels.medical_institution import (
    MedicalInstitutionGetResponse,
    MedicalInstitutionPostRequest,
)
from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.services.medical_institution import MedicalInstitutionService
from server.utils.auth import get_current_active_user


def get_medical_institution_service(db: Session = Depends(get_db)):
    return MedicalInstitutionService(db)


router = APIRouter(
    prefix="/api/v1/medical-institutions", tags=["medical-institutions", "v1"]
)


@router.get(
    "/",
    response_model=Page[MedicalInstitutionGetResponse],
    status_code=status.HTTP_200_OK,
)
async def get_medical_institutions(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    pagination_params: Params = Depends(),
    query: str = Query("", description="Search query(optional)"),
    service: MedicalInstitutionService = Depends(get_medical_institution_service),
):
    return service.get_medical_institutions(
        query=query, pagination_params=pagination_params
    )


@router.post(
    "/",
    response_model=MedicalInstitutionGetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def post_medical_institution(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    data: MedicalInstitutionPostRequest = None,
    service: MedicalInstitutionService = Depends(get_medical_institution_service),
):
    return service.create_medical_institution(data=data)


@router.get(
    "/{id}",
    response_model=MedicalInstitutionGetResponse,
    status_code=status.HTTP_200_OK,
)
async def get_medical_institution_by_id(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    id: str = Path(..., description="ID of Medical Institution"),
    service: MedicalInstitutionService = Depends(get_medical_institution_service),
):
    return service.get_medical_institution_by_id(id=id)


@router.put(
    "/{id}",
    response_model=MedicalInstitutionGetResponse,
    status_code=status.HTTP_200_OK,
)
async def update_medical_institution(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    data: MedicalInstitutionPostRequest = None,
    id: str = Path(..., description="ID of Medical Institution to update"),
    service: MedicalInstitutionService = Depends(get_medical_institution_service),
):
    return service.update_medical_institution(data=data, id=id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medical_institution(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    id: str = Path(..., description="ID of Medical Institution to delete"),
    service: MedicalInstitutionService = Depends(get_medical_institution_service),
):
    service.delete_medical_institution(id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
