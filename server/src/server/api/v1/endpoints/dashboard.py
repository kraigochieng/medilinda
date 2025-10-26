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
from server.utils.auth import get_current_active_user
from server.services.dashboard import get_sms_monthly_by_type

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard", "v1"])


@router.get("/adr_monitoring", status_code=status.HTTP_200_OK)
def get_adr_monitoring(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    start: str = Query(...),
    end: str = Query(...),
    db: Session = Depends(get_db),
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

    def query_proportion_data(db: Session, column):
        return (
            db.query(column, func.count(ADRModel.id))
            .filter(ADRModel.created_at >= start_date)
            .filter(ADRModel.created_at <= end_date)
            .group_by(column)
            .all()
        )

    def format_proportion_data(raw_data):
        return {
            "series": [label.value for label, _ in raw_data],
            "data": [count for _, count in raw_data],
        }

    # Gender Proportion
    gender_proportions_data = query_proportion_data(db, ADRModel.patient_gender)
    gender_proportions_content = format_proportion_data(gender_proportions_data)

    # Pregnancy Status Proportion
    pregnancy_status_proportions_data = query_proportion_data(
        db, ADRModel.pregnancy_status
    )
    pregnancy_status_proportions_content = format_proportion_data(
        pregnancy_status_proportions_data
    )

    # Known Allergy Proportion
    known_allergy_proportions_data = query_proportion_data(db, ADRModel.known_allergy)
    known_allergy_proportions_content = format_proportion_data(
        known_allergy_proportions_data
    )

    # Rechallenge Proportion
    rechallenge_proportions_data = query_proportion_data(db, ADRModel.rechallenge)
    rechallenge_proportions_content = format_proportion_data(
        rechallenge_proportions_data
    )

    # Dechallenge Proportion (fixed column name)
    dechallenge_proportions_data = query_proportion_data(db, ADRModel.dechallenge)
    dechallenge_proportions_content = format_proportion_data(
        dechallenge_proportions_data
    )

    # Severity Proportion
    severity_proportions_data = query_proportion_data(db, ADRModel.severity)
    severity_proportions_content = format_proportion_data(severity_proportions_data)

    # Criteria For Seriousness Proportion
    criteria_for_seriousness_proportions_data = query_proportion_data(
        db, ADRModel.criteria_for_seriousness
    )
    criteria_for_seriousness_proportions_content = format_proportion_data(
        criteria_for_seriousness_proportions_data
    )

    # Is Serious Proportion
    is_serious_proportions_data = query_proportion_data(db, ADRModel.is_serious)
    is_serious_proportions_content = format_proportion_data(is_serious_proportions_data)

    # Outcome Proportion
    outcome_proportions_data = query_proportion_data(db, ADRModel.outcome)
    outcome_proportions_content = format_proportion_data(outcome_proportions_data)

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
def dashboard_summary(db: Session = Depends(get_db)):
    return {
        "total_adrs": db.query(func.count(ADRModel.id)).scalar(),
        "total_institutions": db.query(
            func.count(func.distinct(ADRModel.medical_institution_id))
        ).scalar(),
    }


#  Reviewed vs Unreviewed
@router.get("/reviewed-unreviewed", response_model=list[MetricValue])
def reviewed_vs_unreviewed(db: Session = Depends(get_db)):
    stmt = (
        select(
            func.count(func.distinct(ADRModel.id)).label("total_adrs"),
            func.count(
                func.distinct(case((ReviewModel.id.is_not(None), ADRModel.id)))
            ).label("reviewed_adrs"),
        )
        .select_from(ADRModel)
        .join(
            CausalityAssessmentLevelModel,
            CausalityAssessmentLevelModel.adr_id == ADRModel.id,
            isouter=True,  # LEFT JOIN
        )
        .join(
            ReviewModel,
            ReviewModel.causality_assessment_level_id
            == CausalityAssessmentLevelModel.id,
            isouter=True,  # LEFT JOIN
        )
    )

    result = db.execute(stmt).one()

    total_adrs = result.total_adrs
    reviewed_adrs = result.reviewed_adrs

    unreviewed_adrs = total_adrs - reviewed_adrs

    return [
        {
            "metric": "Reviewed",
            "value": reviewed_adrs,
        },
        {
            "metric": "Unreviewed",
            "value": unreviewed_adrs,
        },
    ]


#  Causality Distribution
@router.get("/causality-distribution", response_model=list[MetricValue])
def causality_distribution(db: Session = Depends(get_db)):
    stmt = select(
        CausalityAssessmentLevelModel.causality_assessment_level_value,
        func.count().label("count"),
    ).group_by(CausalityAssessmentLevelModel.causality_assessment_level_value)

    rows = db.execute(stmt).all()
    counts = {str(r[0]): r[1] for r in rows}

    all_values = [val for val in CausalityAssessmentLevelEnum]

    def clean_label(enum_val):
        return enum_val.name.replace("_", " ").capitalize()

    results = [
        {"metric": clean_label(val), "value": counts.get(str(val), 0)}
        for val in all_values
    ]

    return results


#  Approval Status
@router.get("/approval-status", response_model=list[MetricValue])
def approval_status(db: Session = Depends(get_db)):
    sql = text("""
        SELECT status, COUNT(*) as count FROM (
            SELECT
                cal.id AS cal_id,
                SUM(CASE WHEN r.approved = 1 THEN 1 ELSE 0 END) AS approved_count,
                SUM(CASE WHEN r.approved = 0 THEN 1 ELSE 0 END) AS unapproved_count,
                CASE
                    WHEN SUM(CASE WHEN r.approved = 1 THEN 1 ELSE 0 END) >
                         SUM(CASE WHEN r.approved = 0 THEN 1 ELSE 0 END)
                    THEN 'Approved'
                    ELSE 'Unapproved'
                END AS status
            FROM causality_assessment_level cal
            JOIN review r ON cal.id = r.causality_assessment_level_id
            GROUP BY cal.id
        ) AS sub
        GROUP BY status
    """)
    result = db.execute(sql).fetchall()

    return [{"metric": row.status, "value": row.count} for row in result]


#  Categorical Field Distribution
@router.get("/categorical-field/{field_name}", response_model=list[MetricValue])
def categorical_distribution(field_name: str, db: Session = Depends(get_db)):
    """Dynamically group ADRs by a given field name."""
    field = getattr(ADRModel, field_name, None)

    if field is None:
        return {"error": f"Invalid field name: {field_name}"}

    stmt = select(field, func.count().label("count")).group_by(field)
    rows = db.execute(stmt).all()

    return [{"metric": str(row[0]), "value": row[1]} for row in rows]


#  Top Institutions
@router.get("/top-institutions", response_model=list[MetricValue])
def top_reporting_institutions(db: Session = Depends(get_db)):
    stmt = (
        select(
            MedicalInstitutionModel.name.label("institution_name"),
            func.count(ADRModel.id).label("adr_count"),
        )
        .join(ADRModel, MedicalInstitutionModel.id == ADRModel.medical_institution_id)
        .group_by(MedicalInstitutionModel.name)
        .order_by(func.count(ADRModel.id).desc())
        .limit(5)
    )

    rows = db.execute(stmt).all()

    results = [{"metric": row.institution_name, "value": row.adr_count} for row in rows]

    return results


#  ADRs Weekly (Raw SQL with structured output)
@router.get("/adrs-weekly", response_model=list[MetricValue])
def adrs_weekly(db: Session = Depends(get_db)):
    sql = text("""
        SELECT strftime('%Y-W%W', created_at) AS week_label, COUNT(*) AS count
        FROM adr
        GROUP BY week_label
        ORDER BY week_label
    """)
    result = db.execute(sql).fetchall()

    return [{"metric": row.week_label, "value": row.count} for row in result]


#  ADRs Monthly (Raw SQL with structured output)
@router.get("/adrs-monthly", response_model=list[MetricValue])
def adrs_monthly(db: Session = Depends(get_db)):
    sql = text("""
        SELECT
            strftime('%Y', created_at) AS year,
            strftime('%m', created_at) AS month,
            COUNT(*) AS count
        FROM adr
        GROUP BY year, month
        ORDER BY year, month
    """)
    result = db.execute(sql).fetchall()

    return [
        {
            "metric": f"{calendar.month_abbr[int(row.month)]} {row.year}",
            "value": row.count,
        }
        for row in result
    ]


#  SMS Summary
@router.get("/sms-summary")
def sms_summary(db: Session = Depends(get_db)):
    total_sms = db.query(func.count(SMSMessageModel.id)).scalar()
    total_cost = db.query(func.sum(SMSMessageModel.cost)).scalar()
    success_rate = (
        db.query(func.count()).filter(SMSMessageModel.status == "Delivered").scalar()
    )
    return {
        "total_sms": total_sms,
        "total_cost": total_cost,
        "delivered": success_rate,
        "average_cost": round(float(total_cost or 0) / total_sms, 4)
        if total_sms
        else 0,
    }


#  SMS Status Distribution
@router.get("/sms-status", response_model=list[MetricValue])
def sms_status_distribution(db: Session = Depends(get_db)):
    stmt = select(SMSMessageModel.status, func.count().label("count")).group_by(
        SMSMessageModel.status
    )
    rows = db.execute(stmt).all()

    return [{"metric": row.status, "value": row.count} for row in rows]


#  SMS Type Distribution
@router.get("/sms-type", response_model=list[MetricValue])
def sms_type_distribution(db: Session = Depends(get_db)):
    stmt = select(SMSMessageModel.sms_type, func.count().label("count")).group_by(
        SMSMessageModel.sms_type
    )
    rows = db.execute(stmt).all()

    return [{"metric": row.sms_type, "value": row.count} for row in rows]


#  SMS Count Over Time
@router.get("/sms-weekly", response_model=list[MetricValue])
def sms_weekly(db: Session = Depends(get_db)):
    sql = text("""
        SELECT strftime('%Y-W%W', created_at) AS week_label, COUNT(*) AS count
        FROM sms_message
        GROUP BY week_label
        ORDER BY week_label
    """)
    result = db.execute(sql).fetchall()

    return [{"metric": row.week_label, "value": row.count} for row in result]


#  SMS Monthly (Raw SQL with structured output)
@router.get("/sms-monthly", response_model=list[MetricValue])
def sms_monthly(db: Session = Depends(get_db)):
    sql = text("""
        SELECT
            strftime('%Y', created_at) AS year,
            strftime('%m', created_at) AS month,
            COUNT(*) AS count
        FROM sms_message
        GROUP BY year, month
        ORDER BY year, month
    """)
    result = db.execute(sql).fetchall()

    return [
        {
            "metric": f"{calendar.month_abbr[int(row.month)]} {row.year}",
            "value": row.count,
        }
        for row in result
    ]


@router.get("/sms-monthly/individual-alert", response_model=list[MetricValue])
def sms_monthly_individual_alert(db: Session = Depends(get_db)):
    return get_sms_monthly_by_type(db, "individual alert")


# Uncomment and add more routes if you add more message types in the future
# @router.get("/sms-monthly/bulk-alert")
# def sms_monthly_bulk_alert(db: Session = Depends(get_db)):
#     return get_sms_monthly_by_type(db, "bulk alert")


@router.get("/sms-monthly/additional-info", response_model=list[MetricValue])
def sms_monthly_additional_info(db: Session = Depends(get_db)):
    return get_sms_monthly_by_type(db, "additional info")
