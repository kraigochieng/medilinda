from server.basemodels.alerts import ADRAlertResponse


def transform_alert_rows(rows: list) -> list[ADRAlertResponse]:
    """
    Transforms SQLAlchemy Row objects into the desired dictionary
    structure, splitting the comma-separated telephones.
    """
    return [
        {
            "adr_id": row.adr_id,
            "patient_name": row.patient_name,
            "medical_institution_mfl_code": row.medical_institution_mfl_code,
            "medical_institution_name": row.medical_institution_name,
            "created_at": row.created_at,
            "telephones": row.telephones.split(",") if row.telephones else [],
            "sms_count": row.sms_count,
        }
        for row in rows
    ]
