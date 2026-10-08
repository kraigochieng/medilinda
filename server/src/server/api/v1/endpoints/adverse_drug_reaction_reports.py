import math
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import JSONResponse, Response
from fastapi_pagination import Page, Params
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
from server.basemodels.audit_log import AuditLogGetResponse
from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.repositories.audit_log import AuditLogRepository

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
    pagination_params: Params = Depends(),
    query: str = Query("", description="Search query(optional)"),
    service: AdverseDrugReactionReportService = Depends(
        get_adverse_drug_reaction_report_service
    ),
):
    return service.get(query=query, pagination_params=pagination_params)


@router.post("/", response_model=ADRGetResponse, status_code=status.HTTP_201_CREATED)
async def post_adr(
    request: Request,  # To be used by service
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    data: ADRPostRequest,
    service: AdverseDrugReactionReportService = Depends(
        get_adverse_drug_reaction_report_service
    ),
):
    return service.create_and_predict(data=data)


@router.put("/{id}", response_model=ADRGetResponse, status_code=status.HTTP_200_OK)
async def update_adr(
    request: Request,  # To be used by service
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    data: ADRPostRequest,
    id: str = Path(..., description="ID of ADR to read"),
    service: AdverseDrugReactionReportService = Depends(
        get_adverse_drug_reaction_report_service
    ),
):
    return service.update_and_predict(id=id, data=data)


@router.get("/{id}", response_model=ADRGetResponse, status_code=status.HTTP_200_OK)
def get_adr_by_id(
    id: str = Path(..., description="ID of ADR to read"),
    service: AdverseDrugReactionReportService = Depends(
        get_adverse_drug_reaction_report_service
    ),
):
    return service.get_by_id(id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_adr_by_id(
    id: str = Path(..., description="ID of ADR to delete"),
    service: AdverseDrugReactionReportService = Depends(
        get_adverse_drug_reaction_report_service
    ),
):
    service.delete_by_id(id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{id}/restore", response_model=ADRGetResponse, status_code=status.HTTP_200_OK)
def restore_adr(
    id: str = Path(..., description="ID of the deleted ADR to restore"),
    service: AdverseDrugReactionReportService = Depends(
        get_adverse_drug_reaction_report_service
    ),
):
    return service.restore(id)


@router.get(
    "/{id}/versions",
    response_model=list[AuditLogGetResponse],
    response_model_exclude={"__all__": {"snapshot"}},
    status_code=status.HTTP_200_OK,
)
def get_adr_versions(
    id: str = Path(..., description="ID of the ADR (it may have been deleted)"),
    db: Session = Depends(get_db),
):
    """Every recorded change to this ADR, newest first."""
    return AuditLogRepository(db).versions_of("adr", id)


@router.get(
    "/{id}/versions/{version}",
    response_model=AuditLogGetResponse,
    status_code=status.HTTP_200_OK,
)
def get_adr_version(
    id: str = Path(..., description="ID of the ADR"),
    version: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    """One version, with the full record as it was then."""
    return AuditLogRepository(db).get_version("adr", id, version)


@router.get(
    "/{id}/activity",
    response_model=Page[AuditLogGetResponse],
    response_model_exclude={"items": {"__all__": {"snapshot"}}},
    status_code=status.HTTP_200_OK,
)
def get_adr_activity(
    id: str = Path(..., description="ID of the ADR"),
    pagination_params: Params = Depends(),
    db: Session = Depends(get_db),
):
    """Everything that happened to this ADR and the rows that belong to it
    (assessments, reviews, SMS messages), newest first."""
    return AuditLogRepository(db).get(pagination_params=pagination_params, root_id=id)
