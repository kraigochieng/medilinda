from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from server.basemodels.causality_asssessment_level import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelGetResponse,
    CausalityAssessmentLevelPostRequest,
    UnclassifiablePostRequest,
)
from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.services.auth import get_current_active_user
from server.services.causality_assessment_level import CausalityAssessmentLevelService

router = APIRouter(
    prefix="/api/v1/causality-assessment-levels",
    tags=["causality-assessment-levels", "v1"],
)


def get_causality_assessment_level_service(db: Session = Depends(get_db)):
    return CausalityAssessmentLevelService(db)


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
)
async def get_causality_assessment_level_by_id(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    id: str = Path(..., description="ID of Causality Assessment to read"),
    service: CausalityAssessmentLevelService = Depends(
        get_causality_assessment_level_service
    ),
):
    causality_assessment_level = service.get_causality_assessment_level_by_id(id)
    if not causality_assessment_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Causality Assessment Level record not found",
        )
    approved_count = sum(1 for r in causality_assessment_level.reviews if r.approved)
    not_approved_count = sum(
        1 for r in causality_assessment_level.reviews if not r.approved
    )
    content = {
        **jsonable_encoder(causality_assessment_level),
        "approved_count": approved_count,
        "not_approved_count": not_approved_count,
    }
    return JSONResponse(
        content=content,
        status_code=status.HTTP_200_OK,
    )


@router.put(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def update_causality_assessment_level_by_id(
    data: CausalityAssessmentLevelPostRequest,
    id: str = Path(..., description="ID of CAL to update"),
    service: CausalityAssessmentLevelService = Depends(
        get_causality_assessment_level_service
    ),
):
    updated = service.update_causality_assessment_level_by_id(id, data)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="CAL not found"
        )

    return JSONResponse(
        content=jsonable_encoder(updated), status_code=status.HTTP_200_OK
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_causality_assessment_level_by_id(
    id: str = Path(..., description="ID of CAL to delete"),
    service: CausalityAssessmentLevelService = Depends(
        get_causality_assessment_level_service
    ),
):
    deleted = service.delete_causality_assessment_level_by_id(id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="CAL record not found"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
