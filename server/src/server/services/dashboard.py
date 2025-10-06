import calendar
from collections import defaultdict

from sqlalchemy import text
from sqlalchemy.orm import Session


def get_sms_monthly_by_type(db: Session, sms_type: str):
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

    data_by_year = defaultdict(lambda: {"series": [], "data": []})

    for row in result:
        year, month, count = row
        month_int = int(month)
        month_label = calendar.month_abbr[month_int]
        data_by_year[year]["data"].append(month_label)
        data_by_year[year]["series"].append(count)

    return data_by_year
