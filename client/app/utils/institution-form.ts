// Rules for adding a medical institution. SMS alerts go to its telephone
// numbers, so a number must be a real one and stored in international format.
import { z } from "zod";

// Kenyan mobile numbers: 0712345678, 0112345678, 254712345678, +254712345678,
// with spaces, dashes or brackets allowed. Returns +254712345678, or null.
export function normalizeKenyanPhone(input: string): string | null {
	const compact = input.replace(/[\s\-().]/g, "");
	const match = compact.match(/^(?:\+?254|0)([17]\d{8})$/);

	return match ? `+254${match[1]}` : null;
}

export const PHONE_MESSAGE = "Use a Kenyan mobile number, like 0712 345 678 or +254 712 345 678.";

export const institutionFormSchema = z.object({
	name: z.string().trim().min(3, "Enter the institution's name."),
	mfl_code: z.string().trim().optional(),
	dhis_code: z.string().trim().optional(),
	county: z.string().trim().optional(),
	sub_county: z.string().trim().optional(),
	telephone_numbers: z
		.array(z.string().refine((value) => normalizeKenyanPhone(value) !== null, PHONE_MESSAGE))
		.min(1, "Add at least one phone number."),
});

export type InstitutionForm = z.infer<typeof institutionFormSchema>;

export function emptyInstitutionForm(): Partial<InstitutionForm> {
	return { telephone_numbers: [""] };
}

const blankToUndefined = (value?: string) => value?.trim() || undefined;

// What to send to the server: blanks left out, numbers normalised, repeats removed.
export function toInstitutionPayload(form: InstitutionForm) {
	const phones = [
		...new Set(
			form.telephone_numbers
				.map(normalizeKenyanPhone)
				.filter((phone): phone is string => phone !== null),
		),
	];

	return {
		institution: {
			name: form.name.trim(),
			mfl_code: blankToUndefined(form.mfl_code),
			dhis_code: blankToUndefined(form.dhis_code),
			county: blankToUndefined(form.county),
			sub_county: blankToUndefined(form.sub_county),
		},
		phones,
	};
}
