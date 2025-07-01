import * as z from "zod";

export const signupValidationSchema = z.object({
	username: z.string(),
	firstName: z.string(),
	lastName: z.string(),
	password: z.string(),
});

export type signupTypeValidationSchema = z.infer<typeof signupValidationSchema>;
