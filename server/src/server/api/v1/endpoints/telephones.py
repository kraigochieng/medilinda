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


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_telephone(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    data: MultipleMedicalInstitutionTelephonePostRequest = None,
    service: TelephoneService = Depends(get_telephone_service),
):
    created = [
        service.create_telephone(t)
        for t in data.telephones
        if service.create_telephone(t) is not None
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
    telephone = service.get_telephone_by_id(id)
    if not telephone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Telephone record not found"
        )
    return telephone


@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_telephone(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    telephone_update: MedicalInstitutionTelephonePostRequest = None,
    id: str = Path(..., description="ID of Telephone record to update"),
    service: TelephoneService = Depends(get_telephone_service),
):
    updated = service.update_telephone(id, telephone_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Telephone record not found"
        )
    return JSONResponse(
        content=jsonable_encoder(updated), status_code=status.HTTP_200_OK
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_telephone(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    id: str = Path(..., description="ID of Telephone record to delete"),
    service: TelephoneService = Depends(get_telephone_service),
):
    deleted = service.delete_telephone(id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Telephone record not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
