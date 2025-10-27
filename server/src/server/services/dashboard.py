# server/services/dashboard_service.py
import calendar

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate

from server.models.adverse_drug_reaction_report import ADRModel
from server.models.causality_assessment_level import CausalityAssessmentLevelEnum
from server.repositories.dashboard import DashboardRepository


class DashboardService:
    def __init__(self, repo: DashboardRepository):
        self.repo = repo

    def format_proportion(self, raw_data):
        return {
            "series": [label.value for label, _ in raw_data],
            "data": [count for _, count in raw_data],
        }

    def get_column_proportion(self, column, start_date, end_date):
        raw_data = self.repo.get_column_proportion(column, start_date, end_date)
        return self.format_proportion(raw_data)

    def get_summary(self):
        return {
            "total_adrs": self.repo.get_total_adrs(),
            "total_institutions": self.repo.get_total_institutions(),
        }

    def reviewed_vs_unreviewed(self):
        result = self.repo.get_reviewed_counts()
        total = result.total_adrs
        reviewed = result.reviewed_adrs
        return [
            {"metric": "Reviewed", "value": reviewed},
            {"metric": "Unreviewed", "value": total - reviewed},
        ]

    def causality_distribution(self):
        rows = self.repo.get_causality_distribution()
        counts = {str(r[0]): r[1] for r in rows}
        all_values = [val for val in CausalityAssessmentLevelEnum]

        def clean_label(enum_val):
            return enum_val.name.replace("_", " ").capitalize()

        return [
            {"metric": clean_label(val), "value": counts.get(str(val), 0)}
            for val in all_values
        ]

    def approval_status(self):
        rows = self.repo.get_approval_status()
        return [{"metric": row.status, "value": row.count} for row in rows]

    def categorical_distribution(self, field):
        rows = self.repo.get_categorical_distribution(field)
        return [{"metric": str(row[0]), "value": row[1]} for row in rows]

    def top_institutions(self):
        rows = self.repo.get_top_institutions()
        return [
            {"metric": row.institution_name, "value": row.adr_count} for row in rows
        ]

    def sms_summary(self):
        total_sms, total_cost, delivered = self.repo.get_sms_summary()
        return {
            "total_sms": total_sms,
            "total_cost": total_cost,
            "delivered": delivered,
            "average_cost": round(float(total_cost or 0) / total_sms, 4)
            if total_sms
            else 0,
        }

    def sms_status_distribution(self):
        rows = self.repo.get_sms_status_distribution()
        return [{"metric": row.status, "value": row.count} for row in rows]

    def sms_type_distribution(self):
        rows = self.repo.get_sms_type_distribution()
        return [{"metric": row.sms_type, "value": row.count} for row in rows]

    def get_sms_monthly_by_type(self, sms_type: str):
        rows = self.repo.get_sms_monthly_by_type(sms_type)
        return [
            {
                "metric": f"{calendar.month_abbr[int(r.month)]} {r.year}",
                "value": r.count,
            }
            for r in rows
        ]
