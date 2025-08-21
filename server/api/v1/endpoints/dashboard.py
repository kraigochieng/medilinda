import calendar
import datetime
from collections import defaultdict
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.causality_assessment_level import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelModel,
)
from server.models.medical_institution import MedicalInstitutionModel
from server.models.sms import SMSMessageModel
from server.services.auth import get_current_user
from server.services.dashboard import get_sms_monthly_by_type

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard", "v1"])


@router.get("/adr_monitoring", status_code=status.HTTP_200_OK)
def get_adr_monitoring(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
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
@router.get("/reviewed-unreviewed")
def reviewed_vs_unreviewed(db: Session = Depends(get_db)):
    total = db.query(ADRModel.id).count()
    reviewed = (
        db.query(func.count(func.distinct(CausalityAssessmentLevelModel.id)))
        .join(CausalityAssessmentLevelModel.reviews)
        .scalar()
    )
    return {"series": [reviewed, total - reviewed], "data": ["Reviewed", "Unreviewed"]}


#  Causality Distribution
@router.get("/causality-distribution")
def causality_distribution(db: Session = Depends(get_db)):
    rows = (
        db.query(
            CausalityAssessmentLevelModel.causality_assessment_level_value, func.count()
        )
        .group_by(CausalityAssessmentLevelModel.causality_assessment_level_value)
        .all()
    )
    # return {"series": [r[1] for r in rows], "data": [str(r[0]) for r in rows]}
    counts = {str(r[0]): r[1] for r in rows}

    # Ensure all enum values are included
    all_values = [str(val) for val in CausalityAssessmentLevelEnum]
    series = []
    data = []
    for val in all_values:
        data.append(val)
        series.append(counts.get(val, 0))

    return {"series": series, "data": data}


#  Approval Status
@router.get("/approval-status")
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
    return {"series": [r[1] for r in result], "data": [r[0] for r in result]}


#  Categorical Field Distribution
@router.get("/categorical-field/{field_name}")
def categorical_distribution(field_name: str, db: Session = Depends(get_db)):
    field = getattr(ADRModel, field_name, None)
    if not field:
        return {"error": "Invalid field name"}
    rows = db.query(field, func.count()).group_by(field).all()
    return {"series": [r[1] for r in rows], "data": [str(r[0]) for r in rows]}


#  Top Institutions
@router.get("/top-institutions")
def top_reporting_institutions(db: Session = Depends(get_db)):
    rows = (
        db.query(MedicalInstitutionModel.name, func.count(ADRModel.id))
        .join(ADRModel, MedicalInstitutionModel.id == ADRModel.medical_institution_id)
        .group_by(MedicalInstitutionModel.name)
        .order_by(func.count(ADRModel.id).desc())
        .limit(5)
        .all()
    )
    return {"series": [r[1] for r in rows], "data": [r[0] for r in rows]}


#  ADRs Weekly (Raw SQL with structured output)
@router.get("/adrs-weekly")
def adrs_weekly(db: Session = Depends(get_db)):
    sql = text("""
        SELECT strftime('%Y-W%W', created_at) AS week_label, COUNT(*) AS count
        FROM adr
        GROUP BY week_label
        ORDER BY week_label
    """)
    result = db.execute(sql).fetchall()
    return {"series": [r[1] for r in result], "data": [r[0] for r in result]}


#  ADRs Monthly (Raw SQL with structured output)
@router.get("/adrs-monthly")
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

    data_by_year = defaultdict(lambda: {"series": [], "data": []})

    for row in result:
        year, month, count = row
        # Convert month number to short month name
        month_int = int(month)
        month_label = f"{calendar.month_abbr[month_int]}"
        data_by_year[year]["data"].append(month_label)
        data_by_year[year]["series"].append(count)

    return data_by_year


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
@router.get("/sms-status")
def sms_status_distribution(db: Session = Depends(get_db)):
    rows = (
        db.query(SMSMessageModel.status, func.count())
        .group_by(SMSMessageModel.status)
        .all()
    )
    return [{"series": r[0], "data": r[1]} for r in rows]


#  SMS Type Distribution
@router.get("/sms-type")
def sms_type_distribution(db: Session = Depends(get_db)):
    rows = (
        db.query(SMSMessageModel.sms_type, func.count())
        .group_by(SMSMessageModel.sms_type)
        .all()
    )
    return [{"type": r[0], "count": r[1]} for r in rows]


#  SMS Count Over Time
@router.get("/sms-weekly")
def sms_weekly(db: Session = Depends(get_db)):
    sql = text("""
        SELECT strftime('%Y-W%W', created_at) AS week_label, COUNT(*) AS count
        FROM sms_message
        GROUP BY week_label
        ORDER BY week_label
    """)
    result = db.execute(sql).fetchall()
    return {"series": [r[1] for r in result], "data": [r[0] for r in result]}


#  SMS Monthly (Raw SQL with structured output)
@router.get("/sms-monthly")
def sms_monthly(db: Session = Depends(get_db)):
    sql = text("""
        SELECT strftime('%Y-%m', created_at) AS month_label, COUNT(*) AS count
        FROM sms_message
        GROUP BY month_label
        ORDER BY month_label
    """)
    result = db.execute(sql).fetchall()
    return {"series": [r[1] for r in result], "data": [r[0] for r in result]}


@router.get("/sms-monthly/individual-alert")
def sms_monthly_individual_alert(db: Session = Depends(get_db)):
    return get_sms_monthly_by_type(db, "individual alert")


# Uncomment and add more routes if you add more message types in the future
# @router.get("/sms-monthly/bulk-alert")
# def sms_monthly_bulk_alert(db: Session = Depends(get_db)):
#     return get_sms_monthly_by_type(db, "bulk alert")


@router.get("/sms-monthly/additional-info")
def sms_monthly_additional_info(db: Session = Depends(get_db)):
    return get_sms_monthly_by_type(db, "additional info")
