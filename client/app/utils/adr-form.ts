// Conversion between an ADR record and the add/edit form. Kept apart from the
// component so it can be tested: loading a record and saving it unchanged
// must send the same data back.
import { z } from "zod";
import type { ADRGetResponseInterface, ADRPostRequestInterface } from "~/types/adr";

export const MEDICINE_NAMES = ["Rifampicin", "Isoniazid", "Pyrazinamide", "Ethambutol"] as const;
export type MedicineName = (typeof MEDICINE_NAMES)[number];

const prefix = (name: MedicineName) => name.toLowerCase();

const isoDate = z
	.string()
	.regex(/^\d{4}-\d{2}-\d{2}$/, "Enter a valid date.")
	.or(z.literal(""));

export const adrFormSchema = z.object({
	medical_institution_id: z.string().uuid("Please select a medical institution."),
	patient_name: z.string().min(3, "Name must be at least 3 characters."),
	// A plain YYYY-MM-DD string. A Date would shift by a day across timezones.
	patient_date_of_birth: isoDate.optional(),
	patient_age: z.number().positive().min(0).max(120).optional(),
	patient_height_cm: z.number().positive().optional(),
	patient_weight_kg: z.number().positive().optional(),
	inpatient_or_outpatient_number: z.string().optional(),
	ward_or_clinic: z.string().optional(),
	patient_address: z.string().optional(),
	patient_gender: z.string().optional(),
	date_of_onset_of_reaction: z.string().optional(),
	pregnancy_status: z.string().optional(),
	description_of_reaction: z.string().min(10, "Description is too short.").optional(),
	medicines: z.array(
		z.object({
			name: z.string(),
			suspected: z.boolean().default(false),
			batch_no: z.string().optional(),
			manufacturer: z.string().optional(),
			dose_amount: z.number().positive().optional(),
			frequency_number: z.number().positive().optional(),
			route: z.string().optional(),
			start_date: z.string().optional(),
			stop_date: z.string().optional(),
		}),
	),
	severity: z.string().optional(),
	outcome: z.string().optional(),
	known_allergy: z.string().optional(),
	rechallenge: z.string().optional(),
	dechallenge: z.string().optional(),
	is_serious: z.string().optional(),
	criteria_for_seriousness: z.string().optional(),
	action_taken: z.string().optional(),
	comments: z.string().optional(),
});

export type AdrForm = z.infer<typeof adrFormSchema>;
export type MedicineFormRow = AdrForm["medicines"][number];

export function emptyMedicines(): MedicineFormRow[] {
	return MEDICINE_NAMES.map((name) => ({
		name,
		suspected: false,
		batch_no: "",
		manufacturer: "",
		dose_amount: undefined,
		route: undefined,
		frequency_number: undefined,
		start_date: "",
		stop_date: "",
	}));
}

export function emptyFormState(): Partial<AdrForm> {
	return { patient_name: "", medicines: emptyMedicines() };
}

// The values the Add form starts with today.
export function sampleFormState(): Partial<AdrForm> {
	const medicines = emptyMedicines();
	for (const row of medicines) {
		row.route = row.name === "Pyrazinamide" ? undefined : "oral";
	}

	return {
		medical_institution_id: undefined,
		patient_name: "Kraig Ochieng",
		patient_date_of_birth: "2022-01-01",
		inpatient_or_outpatient_number: "IP-123456",
		patient_weight_kg: 60,
		patient_gender: "male",
		patient_height_cm: 178,
		patient_address: "Kileleshwa, Nairobi",
		ward_or_clinic: "Main Clininc",
		date_of_onset_of_reaction: undefined,
		description_of_reaction: "Very disturbing. Vomiting",
		medicines,
		pregnancy_status: "not applicable",
		known_allergy: "no",
		rechallenge: "yes",
		dechallenge: "yes",
		is_serious: "no",
		criteria_for_seriousness: "hospitalisation",
		action_taken: "unknown",
		outcome: "recovered",
		comments: "Will be looked into",
	};
}

// The server may send a date with a time. The form works with the date only.
const dateOnly = (value?: string | null) => (value ? value.slice(0, 10) : undefined);
const orUndefined = <T>(value: T | null | undefined) => value ?? undefined;

export function adrToFormState(adr: ADRGetResponseInterface): Partial<AdrForm> {
	const record = adr as unknown as Record<string, any>;

	const medicines = MEDICINE_NAMES.map((name) => {
		const p = prefix(name);
		return {
			name,
			suspected: Boolean(record[`${p}_suspected`]),
			batch_no: record[`${p}_batch_no`] ?? "",
			manufacturer: record[`${p}_manufacturer`] ?? "",
			dose_amount: orUndefined<number>(record[`${p}_dose_amount`]),
			route: orUndefined<string>(record[`${p}_route`]),
			frequency_number: orUndefined<number>(record[`${p}_frequency_number`]),
			start_date: dateOnly(record[`${p}_start_date`]) ?? "",
			stop_date: dateOnly(record[`${p}_stop_date`]) ?? "",
		};
	});

	return {
		medical_institution_id: orUndefined(adr.medical_institution_id),
		patient_name: adr.patient_name,
		patient_date_of_birth: dateOnly(adr.patient_date_of_birth),
		patient_age: orUndefined(adr.patient_age),
		patient_height_cm: orUndefined(adr.patient_height_cm),
		patient_weight_kg: orUndefined(adr.patient_weight_kg),
		inpatient_or_outpatient_number: orUndefined(adr.inpatient_or_outpatient_number),
		ward_or_clinic: orUndefined(adr.ward_or_clinic),
		patient_address: orUndefined(adr.patient_address),
		patient_gender: orUndefined(adr.patient_gender),
		pregnancy_status: orUndefined(adr.pregnancy_status),
		known_allergy: orUndefined(adr.known_allergy),
		date_of_onset_of_reaction: dateOnly(adr.date_of_onset_of_reaction),
		description_of_reaction: orUndefined(adr.description_of_reaction),
		medicines,
		rechallenge: orUndefined(adr.rechallenge),
		dechallenge: orUndefined(adr.dechallenge),
		severity: orUndefined(adr.severity),
		is_serious: orUndefined(adr.is_serious),
		criteria_for_seriousness: orUndefined(adr.criteria_for_seriousness),
		action_taken: orUndefined(adr.action_taken),
		outcome: orUndefined(adr.outcome),
		comments: orUndefined(adr.comments),
	};
}

export interface PayloadOptions {
	// False when the user chose "I do not know the date of birth".
	knowsDob: boolean;
}

export function formStateToPayload(
	form: AdrForm,
	userId: string,
	{ knowsDob }: PayloadOptions = { knowsDob: true },
): ADRPostRequestInterface {
	const { medicines, ...base } = form;
	const flat: Record<string, unknown> = {};

	for (const med of medicines ?? []) {
		const name = MEDICINE_NAMES.find((n) => n === med.name);
		if (!name) continue;
		const p = prefix(name);

		flat[`${p}_suspected`] = med.suspected;
		flat[`${p}_start_date`] = med.start_date || null;
		flat[`${p}_stop_date`] = med.stop_date || null;
		flat[`${p}_dose_amount`] = med.dose_amount;
		flat[`${p}_frequency_number`] = med.frequency_number;
		flat[`${p}_route`] = med.route;
		flat[`${p}_batch_no`] = med.batch_no;
		flat[`${p}_manufacturer`] = med.manufacturer;
	}

	return {
		...base,
		user_id: userId,
		medical_institution_id: base.medical_institution_id,
		patient_date_of_birth: knowsDob ? base.patient_date_of_birth || undefined : undefined,
		...flat,
	} as ADRPostRequestInterface;
}
