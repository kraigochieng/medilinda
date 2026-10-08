// The tables of the Communication pages: what a row shows. Kept apart from the
// components so it can be tested.
export function phonesText(phones: readonly string[] | null | undefined): string {
	const numbers = (phones ?? []).map((n) => n.trim()).filter(Boolean);
	return numbers.length ? numbers.join(", ") : "—";
}

export type QueueColumnKey =
	| "patient_name"
	| "medical_institution_name"
	| "medical_institution_mfl_code"
	| "telephones"
	| "created_at"
	| "sms_count";

// The queue of messages waiting to be sent has no count: nothing was sent yet.
export function queueColumns(sent: boolean): { key: QueueColumnKey; header: string }[] {
	const columns: { key: QueueColumnKey; header: string }[] = [
		{ key: "patient_name", header: "Patient" },
		{ key: "medical_institution_name", header: "Institution" },
		{ key: "medical_institution_mfl_code", header: "MFL code" },
		{ key: "telephones", header: "Telephones" },
		{ key: "created_at", header: "Reported" },
	];
	return sent ? [...columns, { key: "sms_count", header: "Messages sent" }] : columns;
}
