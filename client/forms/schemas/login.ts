import * as z from "zod"

export const loginValidationSchema = z.object({
	username: z.string(),
	password: z.string(),
});

export type loginTypeValidationSchema = z.infer<typeof loginValidationSchema>
