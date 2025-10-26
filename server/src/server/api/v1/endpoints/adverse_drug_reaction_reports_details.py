import math
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi_pagination import Page
from sqlalchemy import text
from sqlalchemy.orm import Session

from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.utils.auth import get_current_active_user

router = APIRouter(prefix="/api/v1/adrs-details", tags=["adr-details", "v1"])


@router.get(
    "/with-causality-and-review-count",
    response_model=Page[dict],
    status_code=status.HTTP_200_OK,
)
def get_adrs_with_causality_and_review_count(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    query: str = Query("", description="Search query (optional)"),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * size
    search_term = f"%{query}%" if query else None

    # Total count query
    total_sql = text("""
        SELECT COUNT(*) FROM adr
        WHERE (:query IS NULL OR LOWER(patient_name) LIKE LOWER(:query));
    """)
    total_result = db.execute(total_sql, {"query": search_term})
    total = total_result.scalar_one()
    pages = math.ceil(total / size) if total > 0 else 1

    # Main query using ROW_NUMBER and CTE for SQLite compatibility
    main_sql = text("""
        WITH ranked_causality AS (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY adr_id ORDER BY created_at ASC) AS rn
            FROM causality_assessment_level
        )
        SELECT
            a.id AS adr_id,
            a.patient_name,
            u.first_name || ' ' || u.last_name AS created_by,
            a.created_at,
            cal.causality_assessment_level_value,
            COUNT(CASE WHEN r.approved = 1 THEN 1 END) AS approved_reviews,
            COUNT(CASE WHEN r.approved = 0 THEN 1 END) AS unapproved_reviews
        FROM adr a
        JOIN "user" u ON a.user_id = u.id
        LEFT JOIN ranked_causality cal ON cal.adr_id = a.id AND cal.rn = 1
        LEFT JOIN review r ON r.causality_assessment_level_id = cal.id
        WHERE (:query IS NULL OR LOWER(a.patient_name) LIKE LOWER(:query))
        GROUP BY a.id, a.patient_name, u.first_name, u.last_name, cal.causality_assessment_level_value
        ORDER BY a.created_at DESC
        LIMIT :limit OFFSET :offset;
    """)

    result = db.execute(
        main_sql,
        {
            "query": search_term,
            "limit": size,
            "offset": offset,
        },
    )

    items = [dict(row._mapping) for row in result.fetchall()]

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
    }


@router.get("/individual-alerts", response_model=Page[dict])
async def get_adrs_with_individual_alerts(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    query: str = Query("", description="Search query (optional)"),
    db: Session = Depends(get_db),
):
    # Calculate offset and limit based on page and size
    offset = (page - 1) * size
    limit = size

    search_term = f"%{query}%" if query else None

    result_sql = text("""
    SELECT
        adr.id AS adr_id,
        adr.patient_name AS patient_name,
        mi.name AS medical_institution_name,
        mi.mfl_code AS medical_institution_mfl_code,
        adr.created_at AS created_at,
        GROUP_CONCAT(DISTINCT mit.telephone) AS telephones,
        COUNT(DISTINCT sms.id) AS sms_count,
        COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) AS approved_reviews,
        COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END) AS unapproved_reviews
        
    FROM adr
    JOIN causality_assessment_level cal ON adr.id = cal.adr_id
    JOIN medical_institution mi ON adr.medical_institution_id = mi.id
    LEFT JOIN medical_institution_telephone mit ON mi.id = mit.medical_institution_id
    LEFT JOIN review ON cal.id = review.causality_assessment_level_id
    LEFT JOIN sms_message sms ON adr.id = sms.adr_id
    WHERE cal.causality_assessment_level_value = :level_value
        AND (:query IS NULL OR LOWER(adr.patient_name) LIKE LOWER(:query))
    GROUP BY adr.id, adr.patient_name, mi.name, mi.mfl_code, adr.created_at
    HAVING COUNT(DISTINCT sms.id) != 0
        AND COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) >
        COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END)
    ORDER BY adr.created_at DESC
    LIMIT :limit OFFSET :offset
    """)

    result_params = {
        "level_value": "certain",
        "limit": limit,
        "offset": offset,
        "query": search_term,
    }

    result = db.execute(result_sql, result_params)

    rows = result.fetchall()

    items = [
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

    total_sql = text("""
    SELECT COUNT(*) FROM (
        SELECT
            adr.id,
            COUNT(DISTINCT sms.id) AS sms_count
        FROM adr
        JOIN causality_assessment_level cal ON adr.id = cal.adr_id
        LEFT JOIN review ON cal.id = review.causality_assessment_level_id
        LEFT JOIN sms_message sms ON adr.id = sms.adr_id
        WHERE cal.causality_assessment_level_value = :level_value
            AND (:query IS NULL OR LOWER(adr.patient_name) LIKE LOWER(:query))
        GROUP BY adr.id
        HAVING COUNT(DISTINCT sms.id) != 0
            AND COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) >
            COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END)
    ) AS sub
    """)

    total_result_params = {"level_value": "certain", "query": search_term}
    total_result = db.execute(total_sql, total_result_params).scalar()
    # Calculate the total number of pages
    pages = (total_result + size - 1) // size  # Equivalent to math.ceil(total / size)

    return {
        "items": items,
        "total": total_result,
        "page": page,
        "size": size,
        "pages": pages,
    }


@router.get("/additional-info-requests", response_model=Page[dict])
async def get_adrs_with_additional_info_requests(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    query: str = Query("", description="Search query (optional)"),
    db: Session = Depends(get_db),
):
    # Calculate offset and limit based on page and size
    offset = (page - 1) * size
    limit = size

    search_term = f"%{query}%" if query else None

    result_sql = text("""
    SELECT
        adr.id AS adr_id,
        adr.patient_name AS patient_name,
        mi.name AS medical_institution_name,
        mi.mfl_code AS medical_institution_mfl_code,
        adr.created_at AS created_at,
        GROUP_CONCAT(DISTINCT mit.telephone) AS telephones,
        COUNT(DISTINCT sms.id) AS sms_count,
        COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) AS approved_reviews,
        COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END) AS unapproved_reviews
        
    FROM adr
    JOIN causality_assessment_level cal ON adr.id = cal.adr_id
    JOIN medical_institution mi ON adr.medical_institution_id = mi.id
    LEFT JOIN medical_institution_telephone mit ON mi.id = mit.medical_institution_id
    LEFT JOIN review ON cal.id = review.causality_assessment_level_id
    LEFT JOIN sms_message sms ON adr.id = sms.adr_id
    WHERE cal.causality_assessment_level_value = :level_value
        AND (:query IS NULL OR LOWER(adr.patient_name) LIKE LOWER(:query))
    GROUP BY adr.id, adr.patient_name, mi.name, mi.mfl_code, adr.created_at
    HAVING COUNT(DISTINCT sms.id) != 0
        AND COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) >
        COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END)
    ORDER BY adr.created_at DESC
    LIMIT :limit OFFSET :offset
    """)

    result_params = {
        "level_value": "unclassified",
        "limit": limit,
        "offset": offset,
        "query": search_term,
    }

    result = db.execute(result_sql, result_params)

    rows = result.fetchall()

    items = [
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

    total_sql = text("""
    SELECT COUNT(*) FROM (
        SELECT
            adr.id,
            COUNT(DISTINCT sms.id) AS sms_count
        FROM adr
        JOIN causality_assessment_level cal ON adr.id = cal.adr_id
        LEFT JOIN review ON cal.id = review.causality_assessment_level_id
        LEFT JOIN sms_message sms ON adr.id = sms.adr_id
        WHERE cal.causality_assessment_level_value = :level_value
            AND (:query IS NULL OR LOWER(adr.patient_name) LIKE LOWER(:query))
        GROUP BY adr.id
        HAVING COUNT(DISTINCT sms.id) != 0
            AND COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) >
            COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END)
    ) AS sub
    """)

    total_result_params = {"level_value": "unclassifiable", "query": search_term}

    total_result = db.execute(total_sql, total_result_params).scalar()
    # Calculate the total number of pages
    pages = (total_result + size - 1) // size  # Equivalent to math.ceil(total / size)

    return {
        "items": items,
        "total": total_result,
        "page": page,
        "size": size,
        "pages": pages,
    }


@router.get("/to-be-sent-additional-info-requests", response_model=Page[dict])
async def get_adrs_to_be_sent_for_additional_info_requests(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    query: str = Query("", description="Search query (optional)"),
    db: Session = Depends(get_db),
):
    # Calculate offset and limit based on page and size
    offset = (page - 1) * size
    limit = size

    search_term = f"%{query}%" if query else None

    result_sql = text("""
    SELECT
        adr.id AS adr_id,
        adr.patient_name AS patient_name,
        mi.name AS medical_institution_name,
        mi.mfl_code AS medical_institution_mfl_code,
        adr.created_at AS created_at,
        GROUP_CONCAT(DISTINCT mit.telephone) AS telephones,
        COUNT(DISTINCT sms.id) AS sms_count,
        COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) AS approved_reviews,
        COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END) AS unapproved_reviews
    FROM adr
    JOIN causality_assessment_level cal ON adr.id = cal.adr_id
    JOIN medical_institution mi ON adr.medical_institution_id = mi.id
    LEFT JOIN medical_institution_telephone mit ON mi.id = mit.medical_institution_id
    LEFT JOIN review ON cal.id = review.causality_assessment_level_id
    LEFT JOIN sms_message sms ON adr.id = sms.adr_id
    WHERE cal.causality_assessment_level_value = :level_value
        AND (:query IS NULL OR LOWER(adr.patient_name) LIKE LOWER(:query))
    GROUP BY adr.id, adr.patient_name, mi.name, mi.mfl_code, adr.created_at
    HAVING COUNT(DISTINCT sms.id) = 0
        AND COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) >
        COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END)
    ORDER BY adr.created_at DESC
    LIMIT :limit OFFSET :offset
    """)

    result_params = {
        "level_value": "unclassified",
        "limit": limit,
        "offset": offset,
        "query": search_term,
    }

    result = db.execute(result_sql, result_params)

    rows = result.fetchall()

    items = [
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

    total_sql = text("""
    SELECT COUNT(*) FROM (
        SELECT
            adr.id,
            COUNT(DISTINCT sms.id) AS sms_count
        FROM adr
        JOIN causality_assessment_level cal ON adr.id = cal.adr_id
        LEFT JOIN review ON cal.id = review.causality_assessment_level_id
        LEFT JOIN sms_message sms ON adr.id = sms.adr_id
        WHERE cal.causality_assessment_level_value = :level_value
            AND (:query IS NULL OR LOWER(adr.patient_name) LIKE LOWER(:query))
        GROUP BY adr.id
        HAVING COUNT(DISTINCT sms.id) = 0
            AND COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) >
            COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END)
    ) AS sub
    """)

    total_result_params = {"level_value": "unclassified", "query": search_term}

    total_result = db.execute(total_sql, total_result_params).scalar()
    # Calculate the total number of pages
    pages = (total_result + size - 1) // size  # Equivalent to math.ceil(total / size)

    return {
        "items": items,
        "total": total_result,
        "page": page,
        "size": size,
        "pages": pages,
    }


@router.get("/to-be-sent-individual-alerts", response_model=Page[dict])
async def get_adrs_to_be_sent_for_individual_alerts(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    query: str = Query("", description="Search query (optional)"),
    db: Session = Depends(get_db),
):
    # Calculate offset and limit based on page and size
    offset = (page - 1) * size
    limit = size

    search_term = f"%{query}%" if query else None

    result_sql = text("""
    SELECT
        adr.id AS adr_id,
        adr.patient_name AS patient_name,
        mi.name AS medical_institution_name,
        mi.mfl_code AS medical_institution_mfl_code,
        adr.created_at AS created_at,
        GROUP_CONCAT(DISTINCT mit.telephone) AS telephones,
        COUNT(DISTINCT sms.id) AS sms_count,
        COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) AS approved_reviews,
        COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END) AS unapproved_reviews
    FROM adr
    JOIN causality_assessment_level cal ON adr.id = cal.adr_id
    JOIN medical_institution mi ON adr.medical_institution_id = mi.id
    LEFT JOIN medical_institution_telephone mit ON mi.id = mit.medical_institution_id
    LEFT JOIN review ON cal.id = review.causality_assessment_level_id
    LEFT JOIN sms_message sms ON adr.id = sms.adr_id
    WHERE cal.causality_assessment_level_value = :level_value
        AND (:query IS NULL OR LOWER(adr.patient_name) LIKE LOWER(:query))
    GROUP BY adr.id, adr.patient_name, mi.name, mi.mfl_code, adr.created_at
    HAVING COUNT(DISTINCT sms.id) = 0
        AND COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) >
        COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END)
    ORDER BY adr.created_at DESC
    LIMIT :limit OFFSET :offset
    """)

    result_params = {
        "level_value": "certain",
        "limit": limit,
        "offset": offset,
        "query": search_term,
    }

    result = db.execute(result_sql, result_params)

    rows = result.fetchall()

    items = [
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

    total_sql = text("""
    SELECT COUNT(*) FROM (
        SELECT
            adr.id,
            COUNT(DISTINCT sms.id) AS sms_count
        FROM adr
        JOIN causality_assessment_level cal ON adr.id = cal.adr_id
        LEFT JOIN review ON cal.id = review.causality_assessment_level_id
        LEFT JOIN sms_message sms ON adr.id = sms.adr_id
        WHERE cal.causality_assessment_level_value = :level_value
            AND (:query IS NULL OR LOWER(adr.patient_name) LIKE LOWER(:query))
        GROUP BY adr.id
        HAVING COUNT(DISTINCT sms.id) = 0
            AND COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) >
            COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END)
    ) AS sub
    """)

    total_result_params = {"level_value": "certain", "query": search_term}

    total_result = db.execute(total_sql, total_result_params).scalar()
    # Calculate the total number of pages
    pages = (total_result + size - 1) // size  # Equivalent to math.ceil(total / size)

    return {
        "items": items,
        "total": total_result,
        "page": page,
        "size": size,
        "pages": pages,
    }


@router.get("/unclassifiable-causality", response_model=Page[dict])
async def get_adrs_with_unclassifiable_causality(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    # Calculate offset and limit based on page and size
    offset = (page - 1) * size
    limit = size

    result_sql = text("""
    SELECT
        adr.id AS adr_id,
        adr.patient_name AS patient_name,
        mi.name AS medical_institution_name,
        mi.mfl_code AS medical_institution_mfl_code,
        adr.created_at AS created_at,
        GROUP_CONCAT(DISTINCT mit.telephone) AS telephones,
        COUNT(DISTINCT sms.id) AS sms_count,
        COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) AS approved_reviews,
        COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END) AS unapproved_reviews
        
    FROM adr
    JOIN causality_assessment_level cal ON adr.id = cal.adr_id
    JOIN medical_institution mi ON adr.medical_institution_id = mi.id
    LEFT JOIN medical_institution_telephone mit ON mi.id = mit.medical_institution_id
    LEFT JOIN review ON cal.id = review.causality_assessment_level_id
    LEFT JOIN sms_message sms ON adr.id = sms.adr_id
    WHERE cal.causality_assessment_level_value = :level_value
    GROUP BY adr.id, adr.patient_name, mi.name, mi.mfl_code, adr.created_at
    HAVING COUNT(DISTINCT sms.id) != 0
        AND COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) >
        COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END)
    ORDER BY adr.created_at DESC
    LIMIT :limit OFFSET :offset
    """)

    result_params = {"level_value": "unclassifiable", "limit": limit, "offset": offset}

    result = db.execute(result_sql, result_params)

    rows = result.fetchall()

    items = [
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

    total_sql = text("""
    SELECT COUNT(*) FROM (
        SELECT
            adr.id,
            COUNT(DISTINCT sms.id) AS sms_count
        FROM adr
        JOIN causality_assessment_level cal ON adr.id = cal.adr_id
        LEFT JOIN review ON cal.id = review.causality_assessment_level_id
        LEFT JOIN sms_message sms ON adr.id = sms.adr_id
        WHERE cal.causality_assessment_level_value = :level_value
        GROUP BY adr.id
        HAVING COUNT(DISTINCT sms.id) != 0
            AND COUNT(DISTINCT CASE WHEN review.approved = 1 THEN review.id END) >
            COUNT(DISTINCT CASE WHEN review.approved = 0 THEN review.id END)
    ) AS sub
    """)

    total_result_params = {
        "level_value": "unclassifiable",
    }

    total_result = db.execute(total_sql, total_result_params).scalar()
    # Calculate the total number of pages
    pages = (total_result + size - 1) // size  # Equivalent to math.ceil(total / size)

    return {
        "items": items,
        "total": total_result,
        "page": page,
        "size": size,
        "pages": pages,
    }
