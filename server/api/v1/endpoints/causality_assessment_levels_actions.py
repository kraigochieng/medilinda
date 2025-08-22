from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.basemodels.causality_asssessment_level import (
    CausalityAssessmentLevelEnum,
    UnclassifiablePostRequest,
)
from server.dependencies import get_db
from server.models.causality_assessment_level import CausalityAssessmentLevelModel

router = APIRouter(
    prefix="/api/v1/causality-assessment-levels-actions",
    tags=["causality-assessment-levels-details", "v1"],
)


@router.put("/update-causalities-to-unclassifiable")
def update_causalities_to_unclassifiable(
    data: UnclassifiablePostRequest,
    db: Session = Depends(get_db),
):
    for adr_id in data.adr_ids:
        cals = (
            db.query(CausalityAssessmentLevelModel)
            .filter(CausalityAssessmentLevelModel.adr_id == adr_id)
            .all()
        )

        for cal in cals:
            cal.causality_assessment_level_value = (
                CausalityAssessmentLevelEnum.unclassifiable
            )

    db.commit()
    db.refresh()

    return JSONResponse(
        content="ADR models with unclassifiable set", status_code=status.HTTP_200_OK
    )
