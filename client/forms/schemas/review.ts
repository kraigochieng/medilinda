import * as z from "zod";

export const reviewFormValidationSchema = z.object({
	approved: z.boolean(),
	proposedCausalityLevel: z
		.enum(
			reviewFormCategoricalValues["proposedCausalityLevel"].map(
				(x) => x.value
			) as [string, ...string[]]
		)
		.optional(),
	reason: z
		.string()
		.min(3, "Reason must be at least 3 characters long")
		.optional(),
});
