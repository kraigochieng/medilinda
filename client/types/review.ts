import type { UserDetails } from "./user";

export interface ReviewGetResponse {
	id: string;
	user_id: string;
	causality_assessment_level_id: string;
	approved: boolean;
	proposed_causality_level?: CausalityAssessmentLevelEnum;
	reason?: string;
	created_at: string;
	updated_at: string;
}

export interface ReviewPostResponse {
	id: string;
	user_id: string;
	causality_assessment_level_id: string;
	approved: boolean;
	proposed_causality_level?: CausalityAssessmentLevelEnum;
	reason?: string;
	created_at: string;
	updated_at: string;
}

export interface ReviewWithUserGetResponse {
	id: string;
	user_id: string;
	causality_assessment_level_id: string;
	user: UserDetails;
	approved: boolean;
	proposed_causality_level?: CausalityAssessmentLevelEnum;
	reason?: string;
	created_at: string;
	updated_at: string;
}
