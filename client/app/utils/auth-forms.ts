// Rules of the login and signup forms. An untouched field is undefined, so each
// rule has its own message for that case.
import { z } from "zod";

export const loginSchema = z.object({
	username: z.string({ error: "Username is required" }).min(1, "Username is required"),
	password: z.string({ error: "Password is required" }).min(1, "Password is required"),
});

export const signupSchema = z.object({
	username: z
		.string({ error: "Username is required" })
		.min(3, "Username must be at least 3 characters"),
	firstName: z.string({ error: "First name is required" }).trim().min(1, "First name is required"),
	lastName: z.string({ error: "Last name is required" }).trim().min(1, "Last name is required"),
	password: z
		.string({ error: "Password is required" })
		.min(8, "Password must be at least 8 characters"),
});

export type LoginForm = z.output<typeof loginSchema>;
export type SignupForm = z.output<typeof signupSchema>;
