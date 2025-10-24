from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from server.basemodels.medical_institution import (
    MedicalInstitutionTelephoneGetResponse,
    MedicalInstitutionTelephonePostRequest,
    MultipleMedicalInstitutionTelephonePostRequest,
)
from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.services.auth import get_current_active_user
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
    service: TelephoneService = Depends(get_telephone_service),
):
    return service.get_telephones()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_telephone(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    data: MultipleMedicalInstitutionTelephonePostRequest = None,
    service: TelephoneService = Depends(get_telephone_service),
):
    created = [service.create_telephone(t) for t in data.telephones]
    return JSONResponse(
        content=jsonable_encoder(created), status_code=status.HTTP_201_CREATED
    )


@router.get(
    "/{telephone_id}",
    response_model=MedicalInstitutionTelephoneGetResponse,
    status_code=status.HTTP_200_OK,
)
async def get_telephone_by_id(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    telephone_id: str = Path(..., description="ID of Telephone record to get"),
    service: TelephoneService = Depends(get_telephone_service),
):
    telephone = service.get_telephone_by_id(telephone_id)
    if not telephone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Telephone record not found"
        )
    return telephone


@router.put("/{telephone_id}", status_code=status.HTTP_200_OK)
async def update_telephone(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    telephone_update: MedicalInstitutionTelephonePostRequest = None,
    telephone_id: str = Path(..., description="ID of Telephone record to update"),
    service: TelephoneService = Depends(get_telephone_service),
):
    updated = service.update_telephone(telephone_id, telephone_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Telephone record not found"
        )
    return JSONResponse(
        content=jsonable_encoder(updated), status_code=status.HTTP_200_OK
    )


@router.delete("/{telephone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_telephone(
    current_user: UserDetailsBaseModel = Depends(get_current_active_user),
    telephone_id: str = Path(..., description="ID of Telephone record to delete"),
    service: TelephoneService = Depends(get_telephone_service),
):
    deleted = service.delete_telephone(telephone_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Telephone record not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
