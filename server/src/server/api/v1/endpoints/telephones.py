from fastapi import APIRouter, Depends, HTTPException, Path, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from fastapi_pagination import Page, Params
from sqlalchemy.orm import Session

from server.basemodels.medical_institution import (
    MedicalInstitutionTelephoneGetResponse,
    MedicalInstitutionTelephonePostRequest,
    MultipleMedicalInstitutionTelephonePostRequest,
)
from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.utils.auth import get_current_active_user
from server.services.telephone import TelephoneService

router = APIRouter(prefix="/api/v1/telephones", tags=["telephones", "v1"])


def get_telephone_service(db: Session = Depends(get_db)):
    return TelephoneService(db)


@router.get(
    "/",
    response_model=Page[MedicalInstitutionTelephoneGetResponse],
    status_code=status.HTTP_200_OK,
)
async def get_telephones(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    pagination_params: Params = Depends(),
    medical_institution_id: str | None = Query(
        None, dsecriprion="medical institution id"
    ),
    service: TelephoneService = Depends(get_telephone_service),
):
    return service.get_telephones(
        medical_institution_id=medical_institution_id,
        pagination_params=pagination_params,
    )


@router.post(
    "/",
    response_model=list[MedicalInstitutionTelephoneGetResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_telephone(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    data: MultipleMedicalInstitutionTelephonePostRequest = None,
    service: TelephoneService = Depends(get_telephone_service),
):
    created = [
        service.create_telephone(data=t)
        for t in data.telephones
        # if service.create_telephone(data=t) is not None
    ]
    return JSONResponse(
        content=jsonable_encoder(created), status_code=status.HTTP_201_CREATED
    )


@router.get(
    "/{id}",
    response_model=MedicalInstitutionTelephoneGetResponse,
    status_code=status.HTTP_200_OK,
)
async def get_telephone_by_id(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    id: str = Path(..., description="ID of Telephone record to get"),
    service: TelephoneService = Depends(get_telephone_service),
):
    return service.get_telephone_by_id(id=id)


@router.put(
    "/{id}",
    response_model=MedicalInstitutionTelephoneGetResponse,
    status_code=status.HTTP_200_OK,
)
async def update_telephone(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    data: MedicalInstitutionTelephonePostRequest = None,
    id: str = Path(..., description="ID of Telephone record to update"),
    service: TelephoneService = Depends(get_telephone_service),
):
    return service.update_telephone(id=id, data=data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_telephone(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    id: str = Path(..., description="ID of Telephone record to delete"),
    service: TelephoneService = Depends(get_telephone_service),
):
    service.delete_telephone(id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
