import { describe, expect, it } from "vitest";
import type { MedicalInstitutionGetResponseInterface as Institution } from "../app/types/medical_institution";
import {
	emptyInstitutionForm,
	institutionFormSchema,
	normalizeKenyanPhone,
	toInstitutionPayload,
} from "../app/utils/institution-form";
import { buildItems, locationLine, toItem } from "../app/utils/institution-picker";

describe("normalizeKenyanPhone", () => {
	it("turns the usual ways of writing a number into +254 form", () => {
		for (const input of [
			"0712345678",
			"0712 345 678",
			"+254712345678",
			"254712345678",
			"+254 712-345-678",
			"(0712) 345678",
			"  0712345678  ",
		]) {
			expect(normalizeKenyanPhone(input), input).toBe("+254712345678");
		}
	});

	it("accepts numbers that start with 1 as well as 7", () => {
		expect(normalizeKenyanPhone("0112345678")).toBe("+254112345678");
	});

	it("rejects things that are not Kenyan mobile numbers", () => {
		for (const input of [
			"",
			"abc",
			"071234567", // too short
			"07123456789", // too long
			"0212345678", // landline prefix
			"+255712345678", // Tanzania
			"+1 202 555 0100",
			"0712345678x",
		]) {
			expect(normalizeKenyanPhone(input), input).toBeNull();
		}
	});
});

describe("the institution form", () => {
	const valid = {
		name: "Kijabe Mission Hospital",
		mfl_code: "12345",
		telephone_numbers: ["0712345678"],
	};

	it("starts blank, with no preset phone numbers or names", () => {
		const form = emptyInstitutionForm();

		expect(form.name).toBeUndefined();
		expect(form.mfl_code).toBeUndefined();
		expect(form.telephone_numbers).toEqual([""]);
	});

	it("accepts a valid institution", () => {
		expect(institutionFormSchema.safeParse(valid).success).toBe(true);
	});

	it("does not invent a name when it is empty", () => {
		const result = institutionFormSchema.safeParse({ ...valid, name: "" });

		expect(result.success).toBe(false);
		expect(result.error!.issues[0]!.message).toBe("Enter the institution's name.");
	});

	it("rejects an empty or invalid phone number, and says which one", () => {
		const result = institutionFormSchema.safeParse({
			...valid,
			telephone_numbers: ["0712345678", "", "12345"],
		});

		expect(result.success).toBe(false);
		expect(result.error!.issues.map((i) => i.path.join("."))).toEqual([
			"telephone_numbers.1",
			"telephone_numbers.2",
		]);
	});

	it("needs at least one phone number", () => {
		expect(institutionFormSchema.safeParse({ ...valid, telephone_numbers: [] }).success).toBe(false);
	});

	it("only names and phone numbers are required", () => {
		const result = institutionFormSchema.safeParse({
			name: "Small Clinic",
			telephone_numbers: ["0712345678"],
		});

		expect(result.success).toBe(true);
	});
});

describe("toInstitutionPayload", () => {
	it("normalises the numbers, drops repeats and blanks out empty optional fields", () => {
		const payload = toInstitutionPayload({
			name: "  Kijabe Mission Hospital ",
			mfl_code: "  ",
			dhis_code: undefined,
			county: "Kiambu",
			sub_county: "",
			telephone_numbers: ["0712345678", "+254 712 345 678", "0722000111"],
		});

		expect(payload.phones).toEqual(["+254712345678", "+254722000111"]);
		expect(payload.institution).toEqual({
			name: "Kijabe Mission Hospital",
			mfl_code: undefined,
			dhis_code: undefined,
			county: "Kiambu",
			sub_county: undefined,
		});
	});
});

const institution = (overrides: Partial<Institution> = {}) =>
	({ id: "i1", name: "Kijabe Mission Hospital", ...overrides }) as Institution;

describe("picker items", () => {
	it("describes where an institution is", () => {
		expect(locationLine(institution({ sub_county: "Lari", county: "Kiambu", mfl_code: "12345" }))).toBe(
			"Lari, Kiambu · MFL 12345",
		);
		expect(locationLine(institution({ county: "Kiambu" }))).toBe("Kiambu");
		expect(locationLine(institution({ mfl_code: "12345" }))).toBe("MFL 12345");
		expect(locationLine(institution())).toBe("");
	});

	it("uses the id as the value and the name as the label", () => {
		expect(toItem(institution())).toMatchObject({ value: "i1", label: "Kijabe Mission Hospital" });
	});

	it("keeps the chosen institution in the list even if the search no longer finds it", () => {
		const items = buildItems([institution({ id: "a", name: "A" })], institution({ id: "chosen", name: "Chosen" }));

		expect(items.map((i) => i.value)).toEqual(["chosen", "a"]);
	});

	it("does not list the chosen institution twice", () => {
		const chosen = institution({ id: "a", name: "A" });

		expect(buildItems([chosen, institution({ id: "b", name: "B" })], chosen).map((i) => i.value)).toEqual(["a", "b"]);
	});

	it("works with no results and no choice", () => {
		expect(buildItems([], null)).toEqual([]);
		expect(buildItems([], undefined)).toEqual([]);
	});
});
