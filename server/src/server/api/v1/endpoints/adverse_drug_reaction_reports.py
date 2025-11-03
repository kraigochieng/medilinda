import math
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import JSONResponse, Response
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from mlflow.pyfunc import PyFuncModel
from shap import KernelExplainer
from sklearn.base import BaseEstimator
from sklearn.preprocessing import OrdinalEncoder
from sqlalchemy import desc, text
from sqlalchemy.orm import Session

from server.basemodels.adverse_drug_reaction_report import (
    ADRGetResponse,
    ADRPostRequest,
    DechallengeEnum,
    RechallengeEnum,
)
from server.basemodels.causality_asssessment_level import (
    CausalityAssessmentLevelGetResponse,
)
from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db

# from server.ml.artifacts import (
#     ENCODERS_PATH,
#     METADATA_PATH,
#     SCALERS_PATH,
# )
# from server.ml.utils import (
#     format_feature_values,
#     get_column_metadata,
#     get_encoders,
#     get_shap_values,
#     input_to_prediction_format,
# )
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.causality_assessment_level import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelModel,
)
from server.models.user import UserModel
from server.services.adverse_drug_reaction_report import (
    AdverseDrugReactionReportService,
)
from server.utils.auth import get_current_active_user


def get_adverse_drug_reaction_report_service(
    request: Request, db: Session = Depends(get_db)
):
    ml_model: PyFuncModel = request.app.state.ml_model
    encoder: OrdinalEncoder = request.app.state.encoder
    explainer: KernelExplainer = request.app.state.explainer

    return AdverseDrugReactionReportService(
        db=db, ml_model=ml_model, encoder=encoder, explainer=explainer
    )


router = APIRouter(prefix="/api/v1/adrs", tags=["adrs", "v1"])


@router.get("/", response_model=Page[ADRGetResponse], status_code=status.HTTP_200_OK)
def get_adrs(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    query: str = Query("", description="Search query(optional)"),
    service: AdverseDrugReactionReportService = Depends(
        get_adverse_drug_reaction_report_service
    ),
):
    content = service.get(query=query)

    return JSONResponse(jsonable_encoder(content), status_code=status.HTTP_200_OK)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ADRGetResponse)
async def post_adr(
    request: Request,  # To be used by service
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    data: ADRPostRequest,
    service: AdverseDrugReactionReportService = Depends(
        get_adverse_drug_reaction_report_service
    ),
):
    content = service.create_and_predict(data=data)

    return content


@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=ADRGetResponse)
async def update_adr(
    request: Request,  # To be used by service
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    data: ADRPostRequest,
    id: str = Path(..., description="ID of ADR to read"),
    service: AdverseDrugReactionReportService = Depends(
        get_adverse_drug_reaction_report_service
    ),
):
    content = service.update_and_predict(id=id, data=data)

    if not content:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="adr not found"
        )

    return content


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=ADRGetResponse)
def get_adr_by_id(
    id: str = Path(..., description="ID of ADR to read"),
    service: AdverseDrugReactionReportService = Depends(
        get_adverse_drug_reaction_report_service
    ),
):
    content = service.get_by_id(id)

    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return content


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_adr_by_id(
    id: str = Path(..., description="ID of ADR to delete"),
    service: AdverseDrugReactionReportService = Depends(
        get_adverse_drug_reaction_report_service
    ),
):
    deleted = service.delete_by_id(id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
