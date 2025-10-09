export type SMSMessageTypeEnum =
	| "individual alert"
	// | "bulk alert"
	| "additional info";

export interface SMSMessageGetResponse {
	id: string;
	adr_id: string;
	content: string;
	sms_type: SMSMessageTypeEnum;
	cost?: string;
	message_id?: string;
	message_parts?: number;
	number?: string;
	status: string;
	status_code: number;
}

export interface SMSMessageCountGetResponse {
	adr_id: string;
	medical_institution_mfl_code: string;
	medical_institution_name: string;
	patient_name: string;
	sms_count: number;
	created_at: string;
	telephones: []
}