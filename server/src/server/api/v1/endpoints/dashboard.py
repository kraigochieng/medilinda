import calendar
import datetime
from collections import defaultdict
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import case, func, select, text
from sqlalchemy.orm import Session

from server.basemodels.dashboard import MetricValue, SeriesData
from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.causality_assessment_level import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelModel,
)
from server.models.medical_institution import MedicalInstitutionModel
from server.models.review import ReviewModel
from server.models.sms import SMSMessageModel
from server.services.dashboard import DashboardService, get_sms_monthly_by_type
from server.utils.auth import get_current_active_user

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard", "v1"])


def get_dashboard_service(db: Session = Depends(get_db)):
    return DashboardService(db)


@router.get("/adr_monitoring", status_code=status.HTTP_200_OK)
def get_adr_monitoring(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    start: str = Query(...),
    end: str = Query(...),
    service: DashboardService = Depends(get_dashboard_service),
):
    # Parse date strings
    start_date = datetime.datetime.strptime(start, "%Y-%m-%d").replace(
        tzinfo=datetime.timezone.utc
    )

    # Include the full day by setting end time to 23:59:59.999999
    end_date = (
        datetime.datetime.strptime(end, "%Y-%m-%d").replace(
            tzinfo=datetime.timezone.utc
        )
        + datetime.timedelta(days=1)
        - datetime.timedelta(microseconds=1)
    )

    # Gender Proportion
    gender_proportions_content = service.get_column_proportion(
        column=ADRModel.patient_gender, start_date=start_date, end_date=end_date
    )

    # Pregnancy Status Proportion

    pregnancy_status_proportions_content = service.get_column_proportion(
        column=ADRModel.pregnancy_status, start_date=start_date, end_date=end_date
    )

    # Known Allergy Proportion
    known_allergy_proportions_content = service.get_column_proportion(
        column=ADRModel.known_allergy, start_date=start_date, end_date=end_date
    )

    # Rechallenge Proportion
    rechallenge_proportions_content = service.get_column_proportion(
        column=ADRModel.rechallenge, start_date=start_date, end_date=end_date
    )

    # Dechallenge Proportion (fixed column name)
    dechallenge_proportions_content = service.get_column_proportion(
        column=ADRModel.dechallenge, start_date=start_date, end_date=end_date
    )

    # Severity Proportion
    severity_proportions_content = service.get_column_proportion(
        column=ADRModel.severity, start_date=start_date, end_date=end_date
    )

    # Criteria For Seriousness Proportion
    criteria_for_seriousness_proportions_content = service.get_column_proportion(
        column=ADRModel.criteria_for_seriousness,
        start_date=start_date,
        end_date=end_date,
    )

    # Is Serious Proportion
    is_serious_proportions_content = service.get_column_proportion(
        column=ADRModel.is_serious, start_date=start_date, end_date=end_date
    )

    # Outcome Proportion
    outcome_proportions_content = service.get_column_proportion(
        column=ADRModel.outcome, start_date=start_date, end_date=end_date
    )

    content = {
        "gender_proportions": gender_proportions_content,
        "pregnancy_status_proportions": pregnancy_status_proportions_content,
        "known_allergy_proportions": known_allergy_proportions_content,
        "dechallenge_proportions": dechallenge_proportions_content,
        "rechallenge_proportions": rechallenge_proportions_content,
        "severity_proportions": severity_proportions_content,
        "criteria_for_seriousness_proportions": criteria_for_seriousness_proportions_content,
        "is_serious_proportions": is_serious_proportions_content,
        "outcome_proportions": outcome_proportions_content,
    }

    print(content)

    return JSONResponse(
        content=jsonable_encoder(content),
        status_code=status.HTTP_200_OK,
    )


#  Summary Cards
@router.get("/summary")
def dashboard_summary(service: DashboardService = Depends(get_dashboard_service)):
    content = service.get_summary()

    return JSONResponse(
        content=jsonable_encoder(content), status_code=status.HTTP_200_OK
    )


#  Reviewed vs Unreviewed
@router.get("/reviewed-unreviewed", response_model=list[MetricValue])
def reviewed_vs_unreviewed(service: DashboardService = Depends(get_dashboard_service)):
    content = service.reviewed_vs_unreviewed()

    return JSONResponse(
        content=jsonable_encoder(content), status_code=status.HTTP_200_OK
    )


#  Causality Distribution
@router.get("/causality-distribution", response_model=list[MetricValue])
def causality_distribution(service: DashboardService = Depends(get_dashboard_service)):
    content = service.causality_distribution()

    return JSONResponse(
        content=jsonable_encoder(content), status_code=status.HTTP_200_OK
    )


#  Approval Status
@router.get("/approval-status", response_model=list[MetricValue])
def approval_status(service: DashboardService = Depends(get_dashboard_service)):
    content = service.approval_status()

    return JSONResponse(
        content=jsonable_encoder(content), status_code=status.HTTP_200_OK
    )


#  Categorical Field Distribution
@router.get("/categorical-field/{field_name}", response_model=list[MetricValue])
def categorical_distribution(
    field_name: str, service: DashboardService = Depends(get_dashboard_service)
):
    """Dynamically group ADRs by a given field name."""
    field = getattr(ADRModel, field_name, None)

    if field is None:
        return JSONResponse(
            content=f"Invalid field name: {field_name}",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    content = service.categorical_distribution(field=field)

    return JSONResponse(
        content=jsonable_encoder(content), status_code=status.HTTP_200_OK
    )


#  Top Institutions
@router.get("/top-institutions", response_model=list[MetricValue])
def top_reporting_institutions(
    service: DashboardService = Depends(get_dashboard_service),
):
    content = service.top_institutions()

    return JSONResponse(
        content=jsonable_encoder(content), status_code=status.HTTP_200_OK
    )


#  ADRs Weekly (Raw SQL with structured output)
@router.get("/adrs-weekly", response_model=list[MetricValue])
def adrs_weekly(service: DashboardService = Depends(get_dashboard_service)):
    content = service.get_adrs_weekly()

    return JSONResponse(
        content=jsonable_encoder(content), status_code=status.HTTP_200_OK
    )


#  ADRs Monthly (Raw SQL with structured output)
@router.get("/adrs-monthly", response_model=list[MetricValue])
def adrs_monthly(service: DashboardService = Depends(get_dashboard_service)):
    content = service.get_adrs_monthly()

    return JSONResponse(
        content=jsonable_encoder(content), status_code=status.HTTP_200_OK
    )


#  SMS Summary
@router.get("/sms-summary")
def sms_summary(service: DashboardService = Depends(get_dashboard_service)):
    content = service.sms_summary()

    return JSONResponse(
        content=jsonable_encoder(content), status_code=status.HTTP_200_OK
    )


#  SMS Status Distribution
@router.get("/sms-status", response_model=list[MetricValue])
def sms_status_distribution(service: DashboardService = Depends(get_dashboard_service)):
    content = service.sms_status_distribution()

    return JSONResponse(
        content=jsonable_encoder(content), status_code=status.HTTP_200_OK
    )


#  SMS Type Distribution
@router.get("/sms-type", response_model=list[MetricValue])
def sms_type_distribution(service: DashboardService = Depends(get_dashboard_service)):
    content = service.sms_type_distribution()

    return JSONResponse(
        content=jsonable_encoder(content), status_code=status.HTTP_200_OK
    )


#  SMS Count Over Time
@router.get("/sms-weekly", response_model=list[MetricValue])
def sms_weekly(service: DashboardService = Depends(get_dashboard_service)):
    content = service.get_sms_weekly()

    return JSONResponse(
        content=jsonable_encoder(content), status_code=status.HTTP_200_OK
    )


#  SMS Monthly (Raw SQL with structured output)
@router.get("/sms-monthly", response_model=list[MetricValue])
def sms_monthly(service: DashboardService = Depends(get_dashboard_service)):
    content = service.get_sms_monthly()

    return JSONResponse(
        content=jsonable_encoder(content), status_code=status.HTTP_200_OK
    )


@router.get("/sms-monthly/individual-alert", response_model=list[MetricValue])
def sms_monthly_individual_alert(
    service: DashboardService = Depends(get_dashboard_service),
):
    return service.get_sms_monthly_by_type(sms_type="individual alert")


# Uncomment and add more routes if you add more message types in the future
# @router.get("/sms-monthly/bulk-alert")
# def sms_monthly_bulk_alert(db: Session = Depends(get_db)):
#     return get_sms_monthly_by_type(db, "bulk alert")


@router.get("/sms-monthly/additional-info", response_model=list[MetricValue])
def sms_monthly_additional_info(
    service: DashboardService = Depends(get_dashboard_service),
):
    return service.get_sms_monthly_by_type(sms_type="additional info")
