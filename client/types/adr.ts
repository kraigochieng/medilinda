export type GenderEnum = "male" | "female";

export type PregnancyStatusEnum =
	| "not applicable"
	| "not pregnant"
	| "1st trimester"
	| "2nd trimester"
	| "3rd trimester";

export type KnownAllergyEnum = "yes" | "no";

export type RechallengeEnum = "yes" | "no" | "unknown" | "na";

export type DechallengeEnum = "yes" | "no" | "unknown" | "na";

export type SeverityEnum = "mild" | "moderate" | "severe" | "fatal" | "unknown";

export type IsSeriousEnum = "yes" | "no";

export type RouteEnum = "oral" | "IV";

export type CriteriaForSeriousnessEnum =
	| "hospitalisation"
	| "disability"
	| "congenital anomaly"
	| "life-threatening"
	| "death";

export type ActionTakenEnum =
	| "drug withdrawn"
	| "dose reduced"
	| "dose increased"
	| "dose not changed"
	| "not applicable"
	| "unknown";

export type OutcomeEnum =
	| "recovered"
	| "recovered with sequelae"
	| "recovering"
	| "not recovered"
	| "death"
	| "unknown";

export type CausalityAssessmentLevelEnum =
	| "certain"
	| "likely"
	| "possible"
	| "unlikely"
	| "unclassified"
	| "unclassifiable";

export type ADRBaseModel = {
	id: string;
	patientId: string;
	gender: GenderEnum;
	pregnancyStatus: PregnancyStatusEnum;
	knownAllergy: KnownAllergyEnum;
	rechallenge: RechallengeEnum;
	dechallenge: DechallengeEnum;
	severity: SeverityEnum;
	isSerious: IsSeriousEnum;
	criteriaForSeriousness: CriteriaForSeriousnessEnum;
	actionTaken: ActionTakenEnum;
	outcome: OutcomeEnum;
	causalityAssessmentLevel?: CausalityAssessmentLevelEnum;
	predictionReason?: string;
};

export interface ADRGetResponseInterface {
	id: string;
	medical_institution_id: string;
	// Personal Details
	patient_name: string;
	inpatient_or_outpatient_number?: string;
	patient_date_of_birth?: string;
	patient_age?: number;
	patient_weight_kg?: number;
	patient_height_cm?: number;
	patient_address?: string;
	ward_or_clinic?: string;
	patient_gender: GenderEnum;
	pregnancy_status: PregnancyStatusEnum;
	known_allergy: KnownAllergyEnum;
	// Suspected Adverse Reaction
	date_of_onset_of_reaction?: string;
	description_of_reaction?: string;
	// Medicine fields - Rifampicin
	rifampicin_suspected?: boolean;
	rifampicin_start_date?: string;
	rifampicin_stop_date?: string;
	rifampicin_dose_amount?: number;
	rifampicin_frequency_number?: number;
	rifampicin_route?: RouteEnum;
	rifampicin_batch_no?: string;
	rifampicin_manufacturer?: string;

	// Isoniazid
	isoniazid_suspected?: boolean;
	isoniazid_start_date?: string;
	isoniazid_stop_date?: string;
	isoniazid_dose_amount?: number;
	isoniazid_frequency_number?: number;
	isoniazid_route?: RouteEnum;
	isoniazid_batch_no?: string;
	isoniazid_manufacturer?: string;

	// Pyrazinamide
	pyrazinamide_suspected?: boolean;
	pyrazinamide_start_date?: string;
	pyrazinamide_stop_date?: string;
	pyrazinamide_dose_amount?: number;
	pyrazinamide_frequency_number?: number;
	pyrazinamide_route?: RouteEnum;
	pyrazinamide_batch_no?: string;
	pyrazinamide_manufacturer?: string;

	// Ethambutol
	ethambutol_suspected?: boolean;
	ethambutol_start_date?: string;
	ethambutol_stop_date?: string;
	ethambutol_dose_amount?: number;
	ethambutol_frequency_number?: number;
	ethambutol_route?: RouteEnum;
	ethambutol_batch_no?: string;
	ethambutol_manufacturer?: string;

	// Rechallenge/Dechallenge
	rechallenge: RechallengeEnum;
	dechallenge: DechallengeEnum;
	// Grading of Reaction/Event
	severity: SeverityEnum;
	is_serious: IsSeriousEnum;
	criteria_for_seriousness: CriteriaForSeriousnessEnum;
	action_taken: ActionTakenEnum;
	outcome: OutcomeEnum;
	comments?: string;
}

export interface ADRCreateResponse {
	id: string;
	patient_id: string;
	user_id: string;
	gender: GenderEnum;
	pregnancy_status: PregnancyStatusEnum;
	known_allergy: KnownAllergyEnum;
	rechallenge: RechallengeEnum;
	dechallenge: DechallengeEnum;
	severity: SeverityEnum;
	is_serious: IsSeriousEnum;
	criteria_for_seriousness: CriteriaForSeriousnessEnum;
	action_taken: ActionTakenEnum;
	outcome: OutcomeEnum;
	causality_assessment_level?: CausalityAssessmentLevelEnum;
}

interface ADRReview {
	id: string;
	adr_id: string;
	user_id: string;
	approved: boolean;
	proposed_causality_level: CausalityAssessmentLevelEnum;
	reason: string;
	created_at: string; // ISO 8601 timestamp
	updated_at: string; // ISO 8601 timestamp
}

interface Review {
	id: string;
	user_id: string;
	causality_assessment_level?: CausalityAssessmentLevelEnum;
	approved: boolean;
	proposed_causality_level?: CausalityAssessmentLevelEnum;
	reason?: string;
	created_at: string;
	updated_at: string;
}

interface ADRReviewFull {
	id: string;
	patient_id: string;
	user_id: string;
	gender: GenderEnum;
	pregnancy_status: PregnancyStatusEnum;
	known_allergy: KnownAllergyEnum;
	rechallenge: RechallengeEnum;
	dechallenge: DechallengeEnum;
	severity: SeverityEnum;
	is_serious: IsSeriousEnum;
	criteria_for_seriousness: CriteriaForSeriousnessEnum;
	action_taken: ActionTakenEnum;
	outcome: OutcomeEnum;
	causality_assessment_level: CausalityAssessmentLevelEnum;
	created_at: string; // ISO 8601 timestamp
	updated_at: string; // ISO 8601 timestamp
	reviews: ADRReview[]; // Array of reviews
}

interface ADRFull {
	id: string;
	patient_id: string;
	user_id: string;
	gender: GenderEnum;
	pregnancy_status: PregnancyStatusEnum;
	known_allergy: KnownAllergyEnum;
	rechallenge: RechallengeEnum;
	dechallenge: DechallengeEnum;
	severity: SeverityEnum;
	is_serious: IsSeriousEnum;
	criteria_for_seriousness: CriteriaForSeriousnessEnum;
	action_taken: ActionTakenEnum;
	outcome: OutcomeEnum;
	created_at: string; // ISO 8601 timestamp
	updated_at: string; // ISO 8601 timestamp
	reviews: Review[]; // Array of reviews
}

export interface ADRWithCausalityLevelAndReviewCountInterface {
	adr_id: string;
	patient_name: string;
	created_by: string;
	created_at: string;
	causality_assessment_level_value: string;
	approved_reviews: number;
	unapproved_reviews: number;
}
