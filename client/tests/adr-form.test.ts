import { describe, expect, it } from "vitest";
import type { ADRGetResponseInterface } from "../app/types/adr";
import {
	MEDICINE_NAMES,
	adrFormSchema,
	adrToFormState,
	emptyFormState,
	formStateToPayload,
	sampleFormState,
} from "../app/utils/adr-form";

const INSTITUTION_ID = "8ade772c-0808-4681-a22c-34f99cb742e5";

// A record as the server returns it.
const record = {
	id: "adr-1",
	medical_institution_id: INSTITUTION_ID,
	user_id: "creator-1",
	patient_name: "Jane Smith",
	inpatient_or_outpatient_number: "OP-123456",
	patient_date_of_birth: "1980-05-10",
	patient_age: 45,
	patient_weight_kg: 68.5,
	patient_height_cm: 165,
	patient_address: "123 Kijabe Street, Nairobi",
	ward_or_clinic: "TB Clinic A",
	patient_gender: "female",
	pregnancy_status: "not pregnant",
	known_allergy: "yes",
	date_of_onset_of_reaction: "2025-10-15",
	description_of_reaction: "Severe rash and jaundice.",
	rifampicin_suspected: true,
	rifampicin_start_date: "2025-10-01",
	rifampicin_stop_date: "2025-10-16",
	rifampicin_dose_amount: 600,
	rifampicin_frequency_number: 1,
	rifampicin_route: "oral",
	rifampicin_batch_no: "RF-1",
	rifampicin_manufacturer: "Kenya Medical Supplies",
	isoniazid_suspected: true,
	isoniazid_start_date: "2025-10-01",
	isoniazid_stop_date: "2025-10-16",
	isoniazid_dose_amount: 300,
	isoniazid_frequency_number: 1,
	isoniazid_route: "oral",
	isoniazid_batch_no: "IZ-2",
	isoniazid_manufacturer: "Kenya Medical Supplies",
	pyrazinamide_suspected: false,
	pyrazinamide_start_date: "2025-10-01",
	pyrazinamide_stop_date: null,
	pyrazinamide_dose_amount: 1500,
	pyrazinamide_frequency_number: 1,
	pyrazinamide_route: "oral",
	pyrazinamide_batch_no: "PZ-3",
	pyrazinamide_manufacturer: "Acme",
	ethambutol_suspected: false,
	ethambutol_start_date: "2025-10-01",
	ethambutol_stop_date: null,
	ethambutol_dose_amount: 800,
	ethambutol_frequency_number: 1,
	ethambutol_route: "oral",
	ethambutol_batch_no: "EB-4",
	ethambutol_manufacturer: "Acme",
	rechallenge: "no",
	dechallenge: "yes",
	severity: "severe",
	is_serious: "yes",
	criteria_for_seriousness: "hospitalisation",
	action_taken: "drug withdrawn",
	outcome: "recovering",
	comments: "Admitted for monitoring.",
} as unknown as ADRGetResponseInterface;

// What the server expects back for that record: the same fields, minus its id.
const { id: _id, ...expectedPayload } = record as unknown as Record<string, unknown>;

describe("loading a record into the form and saving it back", () => {
	it("sends exactly the same data back", () => {
		const form = adrToFormState(record) as any;

		const payload = formStateToPayload(form, record.user_id);

		expect(payload).toEqual(expectedPayload);
	});

	it("keeps the date of birth exactly as it was, in any timezone", () => {
		for (const dob of ["2022-01-01", "1999-12-31", "2024-02-29"]) {
			const form = adrToFormState({ ...record, patient_date_of_birth: dob }) as any;

			expect(formStateToPayload(form, "u").patient_date_of_birth).toBe(dob);
		}
	});

	it("cuts a date that came with a time down to the date", () => {
		const form = adrToFormState({
			...record,
			patient_date_of_birth: "1980-05-10T00:00:00",
			rifampicin_start_date: "2025-10-01T08:30:00",
		}) as any;

		const payload = formStateToPayload(form, "u");
		expect(payload.patient_date_of_birth).toBe("1980-05-10");
		expect(payload.rifampicin_start_date).toBe("2025-10-01");
	});

	it("turns missing values from the server into blanks, not the text 'null'", () => {
		const sparse = {
			...record,
			patient_age: null,
			patient_address: null,
			comments: null,
			patient_date_of_birth: null,
			isoniazid_dose_amount: null,
			isoniazid_batch_no: null,
			isoniazid_start_date: null,
		} as unknown as ADRGetResponseInterface;

		const form = adrToFormState(sparse) as any;

		expect(form.patient_age).toBeUndefined();
		expect(form.patient_address).toBeUndefined();
		expect(form.comments).toBeUndefined();
		expect(form.patient_date_of_birth).toBeUndefined();
		const isoniazid = form.medicines.find((m: any) => m.name === "Isoniazid");
		expect(isoniazid.dose_amount).toBeUndefined();
		expect(isoniazid.batch_no).toBe("");
		expect(isoniazid.start_date).toBe("");

		const payload = formStateToPayload(form, "u");
		expect(payload.isoniazid_start_date).toBeNull(); // a blank date is cleared
		expect(payload.isoniazid_dose_amount).toBeUndefined();
	});

	it("always lists the four medicines in the same order", () => {
		const form = adrToFormState(record) as any;

		expect(form.medicines.map((m: any) => m.name)).toEqual([...MEDICINE_NAMES]);
		expect(form.medicines[0]).toMatchObject({
			suspected: true,
			dose_amount: 600,
			route: "oral",
			batch_no: "RF-1",
		});
	});
});

describe("date of birth", () => {
	it("is left out when the user does not know it", () => {
		const form = adrToFormState(record) as any;

		const payload = formStateToPayload(form, "u", { knowsDob: false });

		expect(payload.patient_date_of_birth).toBeUndefined();
		expect(payload.patient_age).toBe(45); // the age is kept
	});

	it("treats an emptied date field as no date", () => {
		const form = { ...(adrToFormState(record) as any), patient_date_of_birth: "" };

		expect(formStateToPayload(form, "u").patient_date_of_birth).toBeUndefined();
	});
});

describe("the form's validation", () => {
	const valid = () => ({ ...sampleFormState(), medical_institution_id: INSTITUTION_ID });

	it("accepts the sample data once an institution is chosen", () => {
		expect(adrFormSchema.safeParse(valid()).success).toBe(true);
	});

	it("accepts a record loaded for editing", () => {
		const result = adrFormSchema.safeParse(adrToFormState(record));

		expect(result.success, JSON.stringify(result.error?.issues)).toBe(true);
	});

	it("requires an institution", () => {
		const result = adrFormSchema.safeParse({ ...valid(), medical_institution_id: undefined });

		expect(result.success).toBe(false);
	});

	it("rejects a date of birth that is not a date", () => {
		for (const bad of ["01/02/2022", "2022-1-1", "yesterday"]) {
			expect(adrFormSchema.safeParse({ ...valid(), patient_date_of_birth: bad }).success).toBe(false);
		}
	});

	it("accepts a blank or missing date of birth", () => {
		expect(adrFormSchema.safeParse({ ...valid(), patient_date_of_birth: "" }).success).toBe(true);
		expect(adrFormSchema.safeParse({ ...valid(), patient_date_of_birth: undefined }).success).toBe(true);
	});
});

describe("starting states", () => {
	it("an empty form has the four medicines and nothing else filled in", () => {
		const form = emptyFormState();

		expect(form.patient_name).toBe("");
		expect(form.medicines).toHaveLength(4);
		expect(form.medicines?.every((m) => !m.suspected)).toBe(true);
	});

	it("the sample is a separate copy each time, so editing it cannot leak", () => {
		const a = sampleFormState();
		const b = sampleFormState();
		a.medicines![0]!.suspected = true;

		expect(b.medicines![0]!.suspected).toBe(false);
	});
});
