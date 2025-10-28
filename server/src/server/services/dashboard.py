import calendar
from datetime import datetime

from sqlalchemy import Column

from server.basemodels.dashboard import MetricValue
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.causality_assessment_level import CausalityAssessmentLevelEnum
from server.models.sms import SMSMessageModel
from server.repositories.dashboard import DashboardRepository


class DashboardService:
    def __init__(self, repo: DashboardRepository):
        self.repo = repo

    def format_proportion(self, raw_data):
        return {
            "series": [label.value for label, _ in raw_data],
            "data": [count for _, count in raw_data],
        }

    def get_column_proportion(
        self, column: Column, start_date: datetime, end_date: datetime
    ):
        raw_data = self.repo.get_column_proportion(column, start_date, end_date)

        return self.format_proportion(raw_data)

    def get_summary(self):
        return {
            "total_adrs": self.repo.get_total_adrs(),
            "total_institutions": self.repo.get_total_institutions(),
        }

    def reviewed_vs_unreviewed(self) -> list[MetricValue]:
        result = self.repo.get_reviewed_counts()
        total = result.total_adrs
        reviewed = result.reviewed_adrs

        return [
            {"metric": "Reviewed", "value": reviewed},
            {"metric": "Unreviewed", "value": total - reviewed},
        ]

    def causality_distribution(self) -> list[MetricValue]:
        rows = self.repo.get_causality_distribution()

        counts = {str(r[0]): r[1] for r in rows}

        all_values = [val for val in CausalityAssessmentLevelEnum]

        def clean_label(enum_val):
            return enum_val.name.replace("_", " ").capitalize()

        return [
            {"metric": clean_label(val), "value": counts.get(str(val), 0)}
            for val in all_values
        ]

    def approval_status(self) -> list[MetricValue]:
        rows = self.repo.get_approval_status()

        return [{"metric": row.status, "value": row.count} for row in rows]

    def categorical_distribution(self, field: Column):
        rows = self.repo.get_categorical_distribution(field)

        return [{"metric": str(row[0]), "value": row[1]} for row in rows]

    def top_institutions(self) -> list[MetricValue]:
        rows = self.repo.get_top_institutions()

        return [
            {"metric": row.institution_name, "value": row.adr_count} for row in rows
        ]

    def get_adrs_weekly(self) -> list[MetricValue]:
        rows = self.repo.get_adrs_weekly()

        return [{"metric": row.week_label, "value": row.count} for row in rows]

    def get_adrs_monthly(self) -> list[MetricValue]:
        rows = self.repo.get_adrs_monthly()

        return [
            {
                "metric": f"{calendar.month_abbr[int(row.month)]} {row.year}",
                "value": row.count,
            }
            for row in rows
        ]

    def sms_summary(self):
        total_sms = self.repo.get_count(SMSMessageModel.id)
        total_cost = self.repo.get_sum(SMSMessageModel.cost)
        success_rate = self.repo.get_sms_success_rate()

        return {
            "total_sms": total_sms,
            "total_cost": total_cost,
            "delivered": success_rate,
            "average_cost": round(float(total_cost or 0) / total_sms, 4)
            if total_sms
            else 0,
        }

    def sms_status_distribution(self) -> list[MetricValue]:
        rows = self.repo.get_sms_status_distribution()

        return [{"metric": row.status, "value": row.count} for row in rows]

    def sms_type_distribution(self) -> list[MetricValue]:
        rows = self.repo.get_sms_type_distribution()

        return [{"metric": row.sms_type, "value": row.count} for row in rows]

    def get_sms_weekly(self) -> list[MetricValue]:
        rows = self.repo.get_sms_monthly()

        return [{"metric": row.week_label, "value": row.count} for row in rows]

    def get_sms_monthly(self) -> list[MetricValue]:
        rows = self.repo.get_sms_monthly()

        return [
            {
                "metric": f"{calendar.month_abbr[int(row.month)]} {row.year}",
                "value": row.count,
            }
            for row in rows
        ]

    def get_sms_monthly_by_type(self, sms_type: str) -> list[MetricValue]:
        rows = self.repo.get_sms_monthly_by_type(sms_type)

        return [
            {
                "metric": f"{calendar.month_abbr[int(r.month)]} {r.year}",
                "value": r.count,
            }
            for r in rows
        ]
