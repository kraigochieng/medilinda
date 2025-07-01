import * as z from "zod";

export const medicalInstitutionFormValidationSchema = z.object({
	name: z.string().default("The default hospital name"),
	mfl_code: z.string().default("999999"),
	dhis_code: z.string().optional(),
	county: z.string().default("Nairobi").optional(),
	sub_county: z.string().default("Langata").optional(),
	telephone_numbers: z
		.array(z.string())
		.min(1, "At least one phone number is required")
		.default([]),
});

export type medicalInstitutionFormTypeValidationSchema = z.infer<
	typeof medicalInstitutionFormValidationSchema
>;
