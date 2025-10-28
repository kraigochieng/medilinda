# server/repositories/dashboard_repository.py
from datetime import datetime
from typing import Any, List, Tuple

from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.causality_assessment_level import CausalityAssessmentLevelModel
from server.models.medical_institution import MedicalInstitutionModel
from server.models.review import ReviewModel
from server.models.sms import SMSMessageModel
from sqlalchemy import Column, Row, case, desc, func, select, text
from sqlalchemy.orm import Session


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------- ADR Proportions ----------
    def get_column_proportion(
        self, column: Column, start_date: datetime, end_date: datetime
    ) -> List[Row[Tuple[Any, int]]]:
        stmt = (
            self.db.query(column, func.count(ADRModel.id))
            .filter(ADRModel.created_at >= start_date)
            .filter(ADRModel.created_at <= end_date)
            .group_by(column)
        )

        return stmt.all()

    # ---------- Summary ----------
    def get_total_adrs(self) -> int:
        return self.db.query(func.count(ADRModel.id)).scalar()

    def get_total_institutions(self) -> int:
        return self.db.query(
            func.count(func.distinct(ADRModel.medical_institution_id))
        ).scalar()

    def get_count(self, column: Column) -> int:
        return self.db.query(func.count(func.distinct(column))).scalar()

    def get_sum(self, column: Column) -> int:
        return self.db.query(func.sum(column)).scalar()

    def get_sms_success_rate(self) -> int:
        return (
            self.db.query(func.count())
            .filter(SMSMessageModel.status == "Delivered")
            .scalar()
        )

    # ---------- Reviewed vs Unreviewed ----------
    def get_reviewed_counts(self) -> Row[Tuple[int, int]]:
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
                isouter=True,
            )
            .join(
                ReviewModel,
                ReviewModel.causality_assessment_level_id
                == CausalityAssessmentLevelModel.id,
                isouter=True,
            )
        )

        return self.db.execute(stmt).one()

    # ---------- Causality Distribution ----------
    def get_causality_distribution(self):
        stmt = select(
            CausalityAssessmentLevelModel.causality_assessment_level_value,
            func.count().label("count"),
        ).group_by(CausalityAssessmentLevelModel.causality_assessment_level_value)

        return self.db.execute(stmt).all()

    # ---------- Approval Status ----------
    def get_approval_status(self):
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

        return self.db.execute(sql).fetchall()

    # ---------- Categorical field ----------
    def get_categorical_distribution(self, field: Column):
        stmt = select(field, func.count().label("count")).group_by(field)

        return self.db.execute(stmt).all()

    # ---------- Top Institutions ----------
    def get_top_institutions(self, limit: int = 5):
        stmt = (
            select(
                MedicalInstitutionModel.name.label("institution_name"),
                func.count(ADRModel.id).label("adr_count"),
            )
            .join(
                ADRModel, MedicalInstitutionModel.id == ADRModel.medical_institution_id
            )
            .group_by(MedicalInstitutionModel.name)
            .order_by(func.count(ADRModel.id).desc())
            .limit(limit)
        )

        return self.db.execute(stmt).all()

    # ADR
    def get_adrs_weekly(self):
        sql = text("""
            SELECT strftime('%Y-W%W', created_at) AS week_label, COUNT(*) AS count
            FROM adr
            GROUP BY week_label
            ORDER BY week_label
        """)

        return self.db.execute(sql).fetchall()

    def get_adrs_monthly(self):
        sql = text("""
            SELECT
                strftime('%Y', created_at) AS year,
                strftime('%m', created_at) AS month,
                COUNT(*) AS count
            FROM adr
            GROUP BY year, month
            ORDER BY year, month
        """)

        return self.db.execute(sql).fetchall()

    # ---------- SMS Aggregations ----------
    def get_sms_summary(self):
        total_sms = self.db.query(func.count(SMSMessageModel.id)).scalar()
        total_cost = self.db.query(func.sum(SMSMessageModel.cost)).scalar()
        delivered = (
            self.db.query(func.count())
            .filter(SMSMessageModel.status == "Delivered")
            .scalar()
        )

        return total_sms, total_cost, delivered

    def get_sms_status_distribution(self):
        stmt = select(SMSMessageModel.status, func.count().label("count")).group_by(
            SMSMessageModel.status
        )

        return self.db.execute(stmt).all()

    def get_sms_type_distribution(self):
        stmt = select(SMSMessageModel.sms_type, func.count().label("count")).group_by(
            SMSMessageModel.sms_type
        )

        return self.db.execute(stmt).all()

    def get_sms_weekly(self):
        sql = text("""
        SELECT strftime('%Y-W%W', created_at) AS week_label, COUNT(*) AS count
        FROM sms_message
        GROUP BY week_label
        ORDER BY week_label
        """)

        return self.db.execute(sql).fetchall()

    def get_sms_monthly(self):
        sql = text("""
        SELECT
            strftime('%Y', created_at) AS year,
            strftime('%m', created_at) AS month,
            COUNT(*) AS count
        FROM sms_message
        GROUP BY year, month
        ORDER BY year, month
        """)

        return self.db.execute(sql).fetchall()

    def get_sms_monthly_by_type(self, sms_type: str):
        sql = text("""
            SELECT
                strftime('%Y', created_at) AS year,
                strftime('%m', created_at) AS month,
                COUNT(*) AS count
            FROM sms_message
            WHERE sms_type = :sms_type
            GROUP BY year, month
            ORDER BY year, month
        """)

        return self.db.execute(sql, {"sms_type": sms_type}).fetchall()
