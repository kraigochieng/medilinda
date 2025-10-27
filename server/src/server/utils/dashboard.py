import calendar
from collections import defaultdict

from sqlalchemy import text
from sqlalchemy.orm import Session
from server.basemodels.dashboard import MetricValue


def get_sms_monthly_by_type(db: Session, sms_type: str) -> list[MetricValue]:
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
    result = db.execute(sql, {"sms_type": sms_type}).fetchall()

    return [
        {
            "metric": f"{calendar.month_abbr[int(row.month)]} {row.year}",
            "value": row.count,
        }
        for row in result
    ]
