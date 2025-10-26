import math
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import JSONResponse, Response
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
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

# from server.ml.artifacts import (
#     ENCODERS_PATH,
#     METADATA_PATH,
#     SCALERS_PATH,
# )
# from server.ml.utils import (
#     format_feature_values,
#     get_column_metadata,
#     get_encoders,
#     get_shap_values,
#     input_to_prediction_format,
# )
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.causality_assessment_level import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelModel,
)
from server.models.user import UserModel
from server.utils.auth import get_current_active_user

router = APIRouter(prefix="/api/v1/adrs", tags=["adrs", "v1"])


@router.get("/", response_model=Page[ADRGetResponse], status_code=status.HTTP_200_OK)
def get_adrs(
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
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


# @router.post("/", status_code=status.HTTP_201_CREATED)
# async def post_adr(
#     request: Request,
#     current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
#     adr: ADRPostRequest,
#     db: Session = Depends(get_db),
# ):
#     # Get user id
#     db_user = (
#         db.query(UserModel).filter(UserModel.username == current_user.username).first()
#     )

#     adr_model = ADRModel(
#         **adr.model_dump(),
#         user_id=db_user.id,
#     )

#     db.add(adr_model)
#     db.commit()
#     db.refresh(adr_model)

#     # Check if ADR has the appropriate fields present.
#     # If not, set the causality level to unclassified and just return immediately
#     if (
#         adr.rifampicin_suspected is None
#         and adr.isoniazid_suspected is None
#         and adr.pyrazinamide_suspected is None
#         and adr.ethambutol_suspected is None
#     ) or (
#         adr.rechallenge is RechallengeEnum.unknown
#         and adr.dechallenge is DechallengeEnum.unknown
#     ):
#         casuality_assessment_level_model = CausalityAssessmentLevelModel(
#             adr_id=adr_model.id,
#             causality_assessment_level_value=CausalityAssessmentLevelEnum.unclassified,
#             base_values=None,
#             shap_values_matrix=None,
#             shap_values_sum_per_class=None,
#             shap_values_and_base_values_sum_per_class=None,
#             feature_names=None,
#             feature_values=None,
#         )

#         db.add(casuality_assessment_level_model)
#         db.commit()
#         db.refresh(casuality_assessment_level_model)

#         # To load the causality assessment levels
#         content = db.query(ADRModel).filter(ADRModel.id == adr_model.id).first()

#         return JSONResponse(
#             content=jsonable_encoder(content),
#             status_code=status.HTTP_201_CREATED,
#         )

#     ml_model: BaseEstimator = request.app.state.ml_model
#     explainer: KernelExplainer = request.app.state.explainer

#     # Get encoders
#     _, ordinal_encoder = get_encoders(ENCODERS_PATH)

#     # Save data as temp df
#     temp_df = pd.DataFrame([adr.model_dump()])

#     column_metadata = get_column_metadata(METADATA_PATH)
#     # Extract prediction input
#     prediction_input = input_to_prediction_format(
#         input_df=temp_df,
#         column_metadata=column_metadata,
#         scalers_path=SCALERS_PATH,
#         encoders_path=ENCODERS_PATH,
#     )

#     # Predict using the ML model
#     prediction = ml_model.predict(prediction_input)

#     decoded_prediction = ordinal_encoder.inverse_transform(prediction.reshape(-1, 1))[
#         0
#     ][0]

#     shap_values = explainer(prediction_input)

#     broken_down_shap_values = get_shap_values(shap_values)

#     base_values = broken_down_shap_values["base_values"]
#     shap_values_matrix = broken_down_shap_values["shap_values_matrix"]
#     shap_values_sum_per_class = broken_down_shap_values["shap_values_sum_per_class"]
#     shap_values_and_base_values_sum_per_class = broken_down_shap_values[
#         "shap_values_and_base_values_sum_per_class"
#     ]

#     feature_names = prediction_input.columns.tolist()
#     feature_values = prediction_input.iloc[0].tolist()

#     # Add causality assessment level
#     casuality_assessment_level_model = CausalityAssessmentLevelModel(
#         adr_id=adr_model.id,
#         causality_assessment_level_value=CausalityAssessmentLevelEnum(
#             decoded_prediction
#         ),
#         base_values=base_values,
#         shap_values_matrix=shap_values_matrix,
#         shap_values_sum_per_class=shap_values_sum_per_class,
#         shap_values_and_base_values_sum_per_class=shap_values_and_base_values_sum_per_class,
#         feature_names=feature_names,
#         feature_values=format_feature_values(
#             feature_values=feature_values, scalers_path=SCALERS_PATH
#         ),
#     )

#     db.add(casuality_assessment_level_model)
#     db.commit()
#     db.refresh(casuality_assessment_level_model)

#     # To load the causality assessment levels
#     content = db.query(ADRModel).filter(ADRModel.id == adr_model.id).first()

#     return JSONResponse(
#         content=jsonable_encoder(content),
#         status_code=status.HTTP_201_CREATED,
#     )


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


# @router.put("/{adr_id}", status_code=status.HTTP_200_OK)
# async def update_adr(
#     request: Request,
#     current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
#     updated_adr: ADRPostRequest,
#     adr_id: str = Path(..., description="ID of the ADR record to update"),
#     db: Session = Depends(get_db),
# ):
#     # Get existing ADR record
#     adr_model = db.query(ADRModel).filter(ADRModel.id == adr_id).first()
#     if not adr_model:
#         raise HTTPException(status_code=404, detail="ADR record not found")

#     # Update ADR fields
#     for key, value in updated_adr.model_dump().items():
#         setattr(adr_model, key, value)

#     db.commit()
#     db.refresh(adr_model)

#     if (
#         adr_model.rifampicin_suspected is None
#         and adr_model.isoniazid_suspected is None
#         and adr_model.pyrazinamide_suspected is None
#         and adr_model.ethambutol_suspected is None
#     ) or (
#         adr_model.rechallenge is RechallengeEnum.unknown
#         and adr_model.dechallenge is DechallengeEnum.unknown
#     ):
#         casuality_assessment_level_model = CausalityAssessmentLevelModel(
#             adr_id=adr_model.id,
#             causality_assessment_level_value=CausalityAssessmentLevelEnum.unclassified,
#             base_values=None,
#             shap_values_matrix=None,
#             shap_values_sum_per_class=None,
#             shap_values_and_base_values_sum_per_class=None,
#             feature_names=None,
#             feature_values=None,
#         )

#         db.add(casuality_assessment_level_model)
#         db.commit()
#         db.refresh(casuality_assessment_level_model)

#         # To load the causality assessment levels
#         content = db.query(ADRModel).filter(ADRModel.id == adr_model.id).first()

#         return JSONResponse(
#             content=jsonable_encoder(content),
#             status_code=status.HTTP_201_CREATED,
#         )

#     # Step 3: Load ML model and encoders
#     ml_model: BaseEstimator = request.app.state.ml_model
#     explainer: KernelExplainer = request.app.state.explainer

#     _, ordinal_encoder = get_encoders(ENCODERS_PATH)

#     temp_df = pd.DataFrame([updated_adr.model_dump()])

#     column_metadata = get_column_metadata(METADATA_PATH)

#     prediction_input = input_to_prediction_format(
#         input_df=temp_df,
#         column_metadata=column_metadata,
#         scalers_path=SCALERS_PATH,
#         encoders_path=ENCODERS_PATH,
#     )

#     # Predict and decode
#     prediction = ml_model.predict(prediction_input)
#     decoded_prediction = ordinal_encoder.inverse_transform(prediction.reshape(-1, 1))[
#         0
#     ][0]

#     shap_values = explainer(prediction_input)

#     broken_down_shap_values = get_shap_values(shap_values)

#     base_values = broken_down_shap_values["base_values"]
#     shap_values_matrix = broken_down_shap_values["shap_values_matrix"]
#     shap_values_sum_per_class = broken_down_shap_values["shap_values_sum_per_class"]
#     shap_values_and_base_values_sum_per_class = broken_down_shap_values[
#         "shap_values_and_base_values_sum_per_class"
#     ]

#     feature_names = prediction_input.columns.tolist()
#     feature_values = prediction_input.iloc[0].tolist()

#     # Update causality assessment model
#     causality_record = (
#         db.query(CausalityAssessmentLevelModel)
#         .filter(CausalityAssessmentLevelModel.adr_id == adr_model.id)
#         .first()
#     )

#     if causality_record:
#         causality_record.causality_assessment_level_value = (
#             CausalityAssessmentLevelEnum(decoded_prediction)
#         )
#         causality_record.base_values = base_values
#         causality_record.shap_values_matrix = shap_values_matrix
#         causality_record.shap_values_sum_per_class = shap_values_sum_per_class
#         causality_record.shap_values_and_base_values_sum_per_class = (
#             shap_values_and_base_values_sum_per_class
#         )
#         causality_record.feature_names = feature_names
#         causality_record.feature_values = format_feature_values(feature_values)

#         db.commit()
#         db.refresh(causality_record)
#     else:
#         new_causality = CausalityAssessmentLevelModel(
#             adr_id=adr_model.id,
#             causality_assessment_level_value=CausalityAssessmentLevelEnum(
#                 decoded_prediction
#             ),
#             base_values=base_values,
#             shap_values_matrix=shap_values_matrix,
#             shap_values_sum_per_class=shap_values_sum_per_class,
#             shap_values_and_base_values_sum_per_class=shap_values_and_base_values_sum_per_class,
#             feature_names=feature_names,
#             feature_values=format_feature_values(feature_values),
#         )
#         db.add(new_causality)
#         db.commit()
#         db.refresh(new_causality)

#     # Step 8: Return updated record with causality details
#     content = db.query(ADRModel).filter(ADRModel.id == adr_model.id).first()

#     return JSONResponse(
#         content=jsonable_encoder(content),
#         status_code=status.HTTP_200_OK,
#     )


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
    current_user: Annotated[UserDetailsBaseModel, Depends(get_current_active_user)],
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
