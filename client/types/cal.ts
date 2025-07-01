// export interface CausalityAssessmentLevelGetResponseInterface {
// 	id: string;
// 	adr_id: string;
// 	ml_model_id: string;
// 	causality_assessment_level_value: CausalityAssessmentLevelEnum;
// 	prediction_reason: string;
// 	created_at: string;
// 	updated_at: string;
// }

export interface CausalityAssessmentLevelGetResponseInterface {
	id: string;
	adr_id: string;
	ml_model_id: string;
	causality_assessment_level_value: CausalityAssessmentLevelEnum;
	base_values?: number[];
	shap_values_matrix?: number[][];
	shap_values_sum_per_class?: number[];
	shap_values_and_base_values_sum_per_class?: number[];
	feature_names?: string[];
	feature_values?: string[];
	created_at: string;
	updated_at: string;
}

export interface CausalityAssessmentLevelWithReviewCountGetResponseInterface {
	id: string;
	adr_id: string;
	ml_model_id: string;
	causality_assessment_level_value: CausalityAssessmentLevelEnum;
	base_values?: number[];
	shap_values_matrix?: number[][];
	shap_values_sum_per_class?: number[];
	shap_values_and_base_values_sum_per_class?: number[];
	feature_names?: string[];
	feature_values?: any[];
	approved_count: number;
	not_approved_count: number;
	created_at: string;
	updated_at: string;
}
