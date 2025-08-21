import math
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import JSONResponse, Response
from fastapi_pagination import Page, paginate
from shap import KernelExplainer
from sklearn.base import BaseEstimator
from sqlalchemy import desc, text
from sqlalchemy.orm import Session

from server.basemodels.adverse_drug_reaction_report import (
    ADRGetResponse,
    ADRPostRequest,
    DechallengeEnum,
    RechallengeEnum,
)
from server.basemodels.causality_asssessment_level import (
    CausalityAssessmentLevelGetResponse,
)
from server.basemodels.user import UserDetailsBaseModel
from server.dependencies import get_db
from server.ml.artifacts import (
    ENCODERS_PATH,
    METADATA_PATH,
    SCALERS_PATH,
)
from server.ml.utils import (
    format_feature_values,
    get_column_metadata,
    get_encoders,
    get_shap_values,
    input_to_prediction_format,
)
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.causality_assessment_level import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelModel,
)
from server.models.user import UserModel
from server.services.auth import get_current_user

router = APIRouter(prefix="/api/v1/adrs", tags=["adrs", "v1"])


@router.get("/", response_model=Page[ADRGetResponse], status_code=status.HTTP_200_OK)
def get_adrs(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    query: str = Query("", description="Search query(optional)"),
    db: Session = Depends(get_db),
):
    if query:
        content = db.query(ADRModel).filter(
            ADRModel.patient_name.ilike(f"%{query}%")
            | ADRModel.patient_address.ilike(f"%{query}%")
            | ADRModel.inpatient_or_outpatient_number.ilike(f"%{query}%")
            | ADRModel.ward_or_clinic.ilike(f"%{query}%")
        )

    else:
        content = db.query(ADRModel)

    content = content.order_by(desc(ADRModel.created_at))

    return paginate(content)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def post_adr(
    request: Request,
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    adr: ADRPostRequest,
    db: Session = Depends(get_db),
):
    # Get user id
    db_user = (
        db.query(UserModel).filter(UserModel.username == current_user.username).first()
    )

    adr_model = ADRModel(
        **adr.model_dump(),
        user_id=db_user.id,
    )

    db.add(adr_model)
    db.commit()
    db.refresh(adr_model)

    # Check if ADR has the appropriate fields present.
    # If not, set the causality level to unclassified and just return immediately
    if (
        adr.rifampicin_suspected is None
        and adr.isoniazid_suspected is None
        and adr.pyrazinamide_suspected is None
        and adr.ethambutol_suspected is None
    ) or (
        adr.rechallenge is RechallengeEnum.unknown
        and adr.dechallenge is DechallengeEnum.unknown
    ):
        casuality_assessment_level_model = CausalityAssessmentLevelModel(
            adr_id=adr_model.id,
            causality_assessment_level_value=CausalityAssessmentLevelEnum.unclassified,
            base_values=None,
            shap_values_matrix=None,
            shap_values_sum_per_class=None,
            shap_values_and_base_values_sum_per_class=None,
            feature_names=None,
            feature_values=None,
        )

        db.add(casuality_assessment_level_model)
        db.commit()
        db.refresh(casuality_assessment_level_model)

        # To load the causality assessment levels
        content = db.query(ADRModel).filter(ADRModel.id == adr_model.id).first()

        return JSONResponse(
            content=jsonable_encoder(content),
            status_code=status.HTTP_201_CREATED,
        )

    ml_model: BaseEstimator = request.app.state.ml_model
    explainer: KernelExplainer = request.app.state.explainer

    # Get encoders
    _, ordinal_encoder = get_encoders(ENCODERS_PATH)

    # Save data as temp df
    temp_df = pd.DataFrame([adr.model_dump()])

    column_metadata = get_column_metadata(METADATA_PATH)
    # Extract prediction input
    prediction_input = input_to_prediction_format(
        input_df=temp_df,
        column_metadata=column_metadata,
        scalers_path=SCALERS_PATH,
        encoders_path=ENCODERS_PATH,
    )

    # Predict using the ML model
    prediction = ml_model.predict(prediction_input)

    decoded_prediction = ordinal_encoder.inverse_transform(prediction.reshape(-1, 1))[
        0
    ][0]

    shap_values = explainer(prediction_input)

    broken_down_shap_values = get_shap_values(shap_values)

    base_values = broken_down_shap_values["base_values"]
    shap_values_matrix = broken_down_shap_values["shap_values_matrix"]
    shap_values_sum_per_class = broken_down_shap_values["shap_values_sum_per_class"]
    shap_values_and_base_values_sum_per_class = broken_down_shap_values[
        "shap_values_and_base_values_sum_per_class"
    ]

    feature_names = prediction_input.columns.tolist()
    feature_values = prediction_input.iloc[0].tolist()

    # Add causality assessment level
    casuality_assessment_level_model = CausalityAssessmentLevelModel(
        adr_id=adr_model.id,
        causality_assessment_level_value=CausalityAssessmentLevelEnum(
            decoded_prediction
        ),
        base_values=base_values,
        shap_values_matrix=shap_values_matrix,
        shap_values_sum_per_class=shap_values_sum_per_class,
        shap_values_and_base_values_sum_per_class=shap_values_and_base_values_sum_per_class,
        feature_names=feature_names,
        feature_values=format_feature_values(
            feature_values=feature_values, scalers_path=SCALERS_PATH
        ),
    )

    db.add(casuality_assessment_level_model)
    db.commit()
    db.refresh(casuality_assessment_level_model)

    # To load the causality assessment levels
    content = db.query(ADRModel).filter(ADRModel.id == adr_model.id).first()

    return JSONResponse(
        content=jsonable_encoder(content),
        status_code=status.HTTP_201_CREATED,
    )


@router.delete("/{adr_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_adr_by_id(
    adr_id: str = Path(..., description="ID of ADR to delete"),
    db: Session = Depends(get_db),
):
    adr = db.query(ADRModel).filter(ADRModel.id == adr_id).first()

    if not adr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="ADR record not found"
        )

    db.delete(adr)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{adr_id}", status_code=status.HTTP_200_OK)
async def update_adr(
    request: Request,
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    updated_adr: ADRPostRequest,
    adr_id: str = Path(..., description="ID of the ADR record to update"),
    db: Session = Depends(get_db),
):
    # Get existing ADR record
    adr_model = db.query(ADRModel).filter(ADRModel.id == adr_id).first()
    if not adr_model:
        raise HTTPException(status_code=404, detail="ADR record not found")

    # Update ADR fields
    for key, value in updated_adr.model_dump().items():
        setattr(adr_model, key, value)

    db.commit()
    db.refresh(adr_model)

    if (
        adr_model.rifampicin_suspected is None
        and adr_model.isoniazid_suspected is None
        and adr_model.pyrazinamide_suspected is None
        and adr_model.ethambutol_suspected is None
    ) or (
        adr_model.rechallenge is RechallengeEnum.unknown
        and adr_model.dechallenge is DechallengeEnum.unknown
    ):
        casuality_assessment_level_model = CausalityAssessmentLevelModel(
            adr_id=adr_model.id,
            causality_assessment_level_value=CausalityAssessmentLevelEnum.unclassified,
            base_values=None,
            shap_values_matrix=None,
            shap_values_sum_per_class=None,
            shap_values_and_base_values_sum_per_class=None,
            feature_names=None,
            feature_values=None,
        )

        db.add(casuality_assessment_level_model)
        db.commit()
        db.refresh(casuality_assessment_level_model)

        # To load the causality assessment levels
        content = db.query(ADRModel).filter(ADRModel.id == adr_model.id).first()

        return JSONResponse(
            content=jsonable_encoder(content),
            status_code=status.HTTP_201_CREATED,
        )

    # Step 3: Load ML model and encoders
    ml_model: BaseEstimator = request.app.state.ml_model
    explainer: KernelExplainer = request.app.state.explainer

    _, ordinal_encoder = get_encoders(ENCODERS_PATH)

    temp_df = pd.DataFrame([updated_adr.model_dump()])

    column_metadata = get_column_metadata(METADATA_PATH)

    prediction_input = input_to_prediction_format(
        input_df=temp_df,
        column_metadata=column_metadata,
        scalers_path=SCALERS_PATH,
        encoders_path=ENCODERS_PATH,
    )

    # Predict and decode
    prediction = ml_model.predict(prediction_input)
    decoded_prediction = ordinal_encoder.inverse_transform(prediction.reshape(-1, 1))[
        0
    ][0]

    shap_values = explainer(prediction_input)

    broken_down_shap_values = get_shap_values(shap_values)

    base_values = broken_down_shap_values["base_values"]
    shap_values_matrix = broken_down_shap_values["shap_values_matrix"]
    shap_values_sum_per_class = broken_down_shap_values["shap_values_sum_per_class"]
    shap_values_and_base_values_sum_per_class = broken_down_shap_values[
        "shap_values_and_base_values_sum_per_class"
    ]

    feature_names = prediction_input.columns.tolist()
    feature_values = prediction_input.iloc[0].tolist()

    # Update causality assessment model
    causality_record = (
        db.query(CausalityAssessmentLevelModel)
        .filter(CausalityAssessmentLevelModel.adr_id == adr_model.id)
        .first()
    )

    if causality_record:
        causality_record.causality_assessment_level_value = (
            CausalityAssessmentLevelEnum(decoded_prediction)
        )
        causality_record.base_values = base_values
        causality_record.shap_values_matrix = shap_values_matrix
        causality_record.shap_values_sum_per_class = shap_values_sum_per_class
        causality_record.shap_values_and_base_values_sum_per_class = (
            shap_values_and_base_values_sum_per_class
        )
        causality_record.feature_names = feature_names
        causality_record.feature_values = format_feature_values(feature_values)

        db.commit()
        db.refresh(causality_record)
    else:
        new_causality = CausalityAssessmentLevelModel(
            adr_id=adr_model.id,
            causality_assessment_level_value=CausalityAssessmentLevelEnum(
                decoded_prediction
            ),
            base_values=base_values,
            shap_values_matrix=shap_values_matrix,
            shap_values_sum_per_class=shap_values_sum_per_class,
            shap_values_and_base_values_sum_per_class=shap_values_and_base_values_sum_per_class,
            feature_names=feature_names,
            feature_values=format_feature_values(feature_values),
        )
        db.add(new_causality)
        db.commit()
        db.refresh(new_causality)

    # Step 8: Return updated record with causality details
    content = db.query(ADRModel).filter(ADRModel.id == adr_model.id).first()

    return JSONResponse(
        content=jsonable_encoder(content),
        status_code=status.HTTP_200_OK,
    )


@router.get("/{adr_id}", status_code=status.HTTP_200_OK)
def get_adr_by_id(
    adr_id: str = Path(..., description="ID of ADR to read"),
    db: Session = Depends(get_db),
):
    adr = db.query(ADRModel).filter(ADRModel.id == adr_id).first()

    if not adr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="ADR record not found"
        )
    return JSONResponse(content=jsonable_encoder(adr), status_code=status.HTTP_200_OK)


@router.get(
    "/{adr_id}/causality-assessment-levels",
    response_model=Page[CausalityAssessmentLevelGetResponse],
    status_code=status.HTTP_200_OK,
)
def get_causality_assessment_levels_for_adr(
    adr_id: str = Path(..., description="ID of ADR to read"),
    db: Session = Depends(get_db),
):
    adr = db.query(ADRModel).filter(ADRModel.id == adr_id).first()

    if not adr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="ADR record not found"
        )

    content = (
        db.query(CausalityAssessmentLevelModel)
        .filter(CausalityAssessmentLevelModel.adr_id == adr_id)
        .order_by(desc(CausalityAssessmentLevelModel.created_at))
    )

    return paginate(content)


@router.get(
    "/{adr_id}/causality-assessment-level",
    status_code=status.HTTP_200_OK,
)
async def get_latest_causality_assessment_level_by_adr_id(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
    adr_id: str = Path(..., description="ID of Causality Assessment to read"),
    db: Session = Depends(get_db),
):
    causality_assessment_level = (
        db.query(CausalityAssessmentLevelModel)
        .filter(CausalityAssessmentLevelModel.adr_id == adr_id)
        .first()
    )

    if not causality_assessment_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Causality Assessment Level record not found",
        )

    approved_count = sum(1 for r in causality_assessment_level.reviews if r.approved)
    not_approved_count = sum(
        1 for r in causality_assessment_level.reviews if not r.approved
    )

    content = {
        **jsonable_encoder(causality_assessment_level),
        "approved_count": approved_count,
        "not_approved_count": not_approved_count,
    }
    return JSONResponse(
        content=content,
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "/with-causality-and-review-count",
    response_model=Page[dict],
    status_code=status.HTTP_200_OK,
)
def get_adrs_with_causality_and_review_count(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
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
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
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
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
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
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
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
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_user)],
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
