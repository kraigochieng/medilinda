from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi_pagination import Page, Params
from mlflow.pyfunc import PyFuncModel
from shap import KernelExplainer
from sklearn.preprocessing import OrdinalEncoder
from sqlalchemy.orm import Session

from server.basemodels.adverse_drug_reaction_report import ADRWithReviewsResponse
from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.services.adverse_drug_reaction_report import (
    AdverseDrugReactionReportService,
)
from server.utils.auth import get_current_active_user

router = APIRouter(prefix="/api/v1/adrs-details", tags=["adr-details", "v1"])


def get_adverse_drug_reaction_report_service(
    request: Request, db: Session = Depends(get_db)
):
    ml_model: PyFuncModel = request.app.state.ml_model
    encoder: OrdinalEncoder = request.app.state.encoder
    explainer: KernelExplainer = request.app.state.explainer

    return AdverseDrugReactionReportService(
        db=db, ml_model=ml_model, encoder=encoder, explainer=explainer
    )


@router.get(
    "/with-causality-and-review-count",
    response_model=Page[ADRWithReviewsResponse],
    status_code=status.HTTP_200_OK,
)
def get_adrs_with_causality_and_review_count(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    pagination_params: Params = Depends(),
    query: str = Query("", description="Search query (optional)"),
    service: AdverseDrugReactionReportService = Depends(
        get_adverse_drug_reaction_report_service
    ),
):
    return service.get_adrs_with_causality_and_review_count(
        params=pagination_params, query=query
    )
