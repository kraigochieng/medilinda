import logging

import pandas as pd
from fastapi_pagination import Page, Params
from mlflow.pyfunc import PyFuncModel
from pydantic import ValidationError
from shap import Explanation, KernelExplainer
from sklearn.preprocessing import OrdinalEncoder
from sqlalchemy.orm import Session

from server.basemodels.adverse_drug_reaction_report import (
    ADRGetResponse,
    ADRPostRequest,
    ADRWithReviewsResponse,
    DechallengeEnum,
    MLModelInput,
    RechallengeEnum,
)
from server.basemodels.causality_asssessment_level import (
    CausalityAssessmentLevelPostRequest,
)
from server.models.adverse_drug_reaction_report import ADRModel
from server.models.causality_assessment_level import (
    CausalityAssessmentLevelEnum,
    CausalityAssessmentLevelModel,
)
from server.repositories.adverse_drug_reaction_report import (
    AdverseDrugReactionReportRepository,
)
from server.repositories.causality_assessment_level import (
    CausalityAssessmentLevelRepository,
)
from server.utils.ml import get_shap_values


class AdverseDrugReactionReportService:
    def __init__(
        self,
        db: Session,
        ml_model: PyFuncModel,
        encoder: OrdinalEncoder,
        explainer: KernelExplainer,
    ):
        self.repository = AdverseDrugReactionReportRepository(db)
        self.cal_repository = CausalityAssessmentLevelRepository(db)
        self.ml_model = ml_model
        self.encoder = encoder
        self.explainer = explainer

    def get(self, query: str | None, pagination_params: Params) -> Page[ADRGetResponse]:
        return self.repository.get(query=query, pagination_params=pagination_params)

    def get_by_id(self, id: str) -> ADRGetResponse | None:
        return self.repository.get_by_id(id)

    def get_adrs_with_causality_and_review_count(
        self, pagination_params: Params, query: str | None
    ) -> Page[ADRWithReviewsResponse]:
        """
        Pass-through method to get paginated ADRs with review counts.
        """
        return self.repository.get_paginated_adrs_with_reviews(
            pagination_params=pagination_params, query=query
        )

    def create(self, data: ADRPostRequest) -> ADRGetResponse:
        model = self.repository.create(data=data)
        return ADRGetResponse.model_validate(model)

    def create_and_predict(self, data: ADRPostRequest) -> ADRGetResponse:
        adr_model = self.repository.create(data=data)

        print("adr")
        print(adr_model)
        self.predict(data=data, adr_model=adr_model)

        return ADRGetResponse.model_validate(adr_model)

    def update(self, id: str, data: ADRPostRequest) -> ADRGetResponse | None:
        return self.repository.update(id=id, data=data)

    def update_and_predict(
        self, id: str, data: ADRPostRequest
    ) -> ADRGetResponse | None:
        adr_model = self.repository.update(id=id, data=data)

        if not adr_model:
            return None

        self.predict(data=data)

        return ADRGetResponse.model_validate(adr_model)

    def delete_by_id(self, id: str) -> bool:
        return self.repository.delete(id)

    def predict(self, data: ADRPostRequest, adr_model: ADRModel):
        if (
            data.rifampicin_suspected is None
            and data.isoniazid_suspected is None
            and data.pyrazinamide_suspected is None
            and data.ethambutol_suspected is None
        ) or (
            data.rechallenge is RechallengeEnum.unknown
            and data.dechallenge is DechallengeEnum.unknown
        ):
            cal_data = CausalityAssessmentLevelPostRequest(
                adr_id=adr_model.id,
                causality_assessment_level_value=CausalityAssessmentLevelEnum.unclassified,
                base_values=None,
                shap_values_matrix=None,
                shap_values_sum_per_class=None,
                shap_values_and_base_values_sum_per_class=None,
                feature_names=None,
                feature_values=None,
            )

            self.cal_repository.create(data=cal_data)

            return  # Exit the function since no prediction will be done here

        try:
            ml_model_input = MLModelInput.model_validate(adr_model)

        except ValidationError as e:
            logging.error(f"Pydantic validation failed for ADR {adr_model.id}: {e}")
            raise e

        ml_model_input_df = pd.DataFrame([ml_model_input.model_dump()])

        # The MLflow model's schema expects 'created_at' to be a string,
        # but the DataFrame has it as a datetime object (datetime64[ns]).
        # We must explicitly convert the column to a string to match the schema.
        if "created_at" in ml_model_input_df.columns:
            ml_model_input_df["created_at"] = ml_model_input_df["created_at"].astype(
                str
            )

        prediction = self.ml_model.predict(ml_model_input_df)

        decoded_prediction = self.encoder.inverse_transform(prediction.reshape(-1, 1))[
            0
        ][0]

        logging.info("Generation SHAP value...")
        shap_values: Explanation = self.explainer(ml_model_input_df)

        final_feature_names = shap_values.feature_names

        final_feature_values = shap_values.data[0].tolist()

        broken_down_shap_values = get_shap_values(shap_values)

        base_values = broken_down_shap_values["base_values"]
        shap_values_matrix = broken_down_shap_values["shap_values_matrix"]
        shap_values_sum_per_class = broken_down_shap_values["shap_values_sum_per_class"]
        shap_values_and_base_values_sum_per_class = broken_down_shap_values[
            "shap_values_and_base_values_sum_per_class"
        ]

        cal_data = CausalityAssessmentLevelPostRequest(
            adr_id=adr_model.id,
            causality_assessment_level_value=CausalityAssessmentLevelEnum(
                decoded_prediction
            ),
            base_values=base_values,
            shap_values_matrix=shap_values_matrix,
            shap_values_sum_per_class=shap_values_sum_per_class,
            shap_values_and_base_values_sum_per_class=shap_values_and_base_values_sum_per_class,
            feature_names=final_feature_names, # hardcoded but will be changed
            feature_values=final_feature_values,
        )

        logging.info("Creating causality after prediction...")

        cal_model = self.cal_repository.create(data=cal_data)

        logging.info(cal_model)
