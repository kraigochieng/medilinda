from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from fastapi_pagination import Page, paginate
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
from server.services.auth import get_current_user

router = APIRouter(
    prefix="/api/v1/medical-institutions", tags=["medical-institutions", "v1"]
)


@router.get(
    "/",
    response_model=Page[MedicalInstitutionGetResponse],
)
async def get_medical_institution(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    query: str = Query("", description="Search query(optional)"),
    db: Session = Depends(get_db),
):
    if query:
        content = (
            db.query(MedicalInstitutionModel)
            .filter(
                MedicalInstitutionModel.name.ilike(f"%{query}%")
                | MedicalInstitutionModel.county.ilike(f"%{query}%")
                | MedicalInstitutionModel.sub_county.ilike(f"%{query}%")
            )
            .order_by(desc(MedicalInstitutionModel.created_at))
        )
    else:
        content = db.query(MedicalInstitutionModel).order_by(
            desc(MedicalInstitutionModel.created_at)
        )

    return paginate(content)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def post_medical_institution(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    institution: MedicalInstitutionPostRequest,
    db: Session = Depends(get_db),
):
    new_institution = MedicalInstitutionModel(**institution.model_dump())

    db.add(new_institution)
    db.commit()
    db.refresh(new_institution)

    return JSONResponse(
        content=jsonable_encoder(new_institution),
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/{institution_id}", status_code=status.HTTP_200_OK)
async def get_medical_institution_by_id(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    institution_id: str = Path(..., description="ID of Medical Institution to delete"),
    query: str = Query("", description="Search query(optional)"),
    db: Session = Depends(get_db),
):
    db_institution = (
        db.query(MedicalInstitutionModel)
        .filter(MedicalInstitutionModel.id == institution_id)
        .first()
    )

    if not db_institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical Institution not found",
        )

    return JSONResponse(
        content=jsonable_encoder(db_institution), status_code=status.HTTP_200_OK
    )


@router.put("/{institution_id}", status_code=status.HTTP_200_OK)
async def update_medical_institution(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    institution: MedicalInstitutionGetResponse,
    institution_id: str = Path(..., description="ID of Medical Institution to update"),
    db: Session = Depends(get_db),
):
    db_institution = (
        db.query(MedicalInstitutionModel)
        .filter(MedicalInstitutionModel.id == institution_id)
        .first()
    )

    if not db_institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical Institution not found",
        )

    for key, value in institution.model_dump().items():
        setattr(db_institution, key, value)

    db.commit()
    db.refresh(db_institution)

    return JSONResponse(
        content=jsonable_encoder(db_institution),
        status_code=status.HTTP_200_OK,
    )


@router.delete(
    "/{institution_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_medical_institution(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    institution_id: str = Path(..., description="ID of Medical Institution to delete"),
    db: Session = Depends(get_db),
):
    db_institution = (
        db.query(MedicalInstitutionModel)
        .filter(MedicalInstitutionModel.id == institution_id)
        .first()
    )

    if not db_institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical Institution not found",
        )

    db.delete(db_institution)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{institution_id}/telephone",
    response_model=Page[MedicalInstitutionTelephoneGetResponse],
)
async def get_telephones_for_medical_institution(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    institution_id: str = Path(..., description="ID of the Medical Institution"),
    db: Session = Depends(get_db),
):
    # Check if the medical institution exists first (optional but good)
    institution = (
        db.query(MedicalInstitutionModel)
        .filter(MedicalInstitutionModel.id == institution_id)
        .first()
    )

    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical Institution not found",
        )

    # Query all telephone numbers for the given institution
    telephones = db.query(MedicalInstitutionTelephoneModel).filter(
        MedicalInstitutionTelephoneModel.medical_institution_id == institution_id
    )

    return paginate(telephones)


@router.get(
    "/telephone",
    response_model=Page[MedicalInstitutionTelephoneGetResponse],
)
async def get_medical_institution_telephones(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    content = db.query(MedicalInstitutionTelephoneModel).order_by(
        desc(MedicalInstitutionTelephoneModel.created_at)
    )
    return paginate(content)


@router.post(
    "/telephone", status_code=status.HTTP_201_CREATED
)
async def create_medical_institution_telephone(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
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
    "/telephone/{telephone_id}",
    status_code=status.HTTP_200_OK,
)
async def update_medical_institution_telephone(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
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
    "/telephone/{telephone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_medical_institution_telephone(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
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
