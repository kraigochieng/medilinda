import { describe, expect, it } from "vitest";
import { loginSchema, signupSchema } from "../app/utils/auth-forms";

const messages = (result: { success: boolean; error?: { issues: { message: string; path: PropertyKey[] }[] } }) =>
	result.error?.issues.map((i) => `${String(i.path[0])}: ${i.message}`) ?? [];

describe("login rules", () => {
	it("accepts a username and a password", () => {
		expect(loginSchema.safeParse({ username: "jane", password: "x" }).success).toBe(true);
	});

	it("asks for both when nothing was typed", () => {
		expect(messages(loginSchema.safeParse({}))).toEqual([
			"username: Username is required",
			"password: Password is required",
		]);
	});

	it("refuses empty text", () => {
		expect(loginSchema.safeParse({ username: "", password: "" }).success).toBe(false);
	});
});

describe("signup rules", () => {
	const valid = { username: "jane", firstName: "Jane", lastName: "Doe", password: "long-enough-1" };

	it("accepts a complete form", () => {
		expect(signupSchema.safeParse(valid).success).toBe(true);
	});

	it("asks for a password when none was typed, with a message the user can read", () => {
		const { password, ...withoutPassword } = valid;
		void password;

		expect(messages(signupSchema.safeParse(withoutPassword))).toEqual(["password: Password is required"]);
	});

	it("refuses a short password", () => {
		expect(messages(signupSchema.safeParse({ ...valid, password: "short" }))).toEqual([
			"password: Password must be at least 8 characters",
		]);
	});

	it("asks for every field when nothing was typed", () => {
		expect(messages(signupSchema.safeParse({})).map((m) => m.split(":")[0]).sort()).toEqual([
			"firstName",
			"lastName",
			"password",
			"username",
		]);
	});

	it("refuses a username that is too short, and blank names", () => {
		expect(messages(signupSchema.safeParse({ ...valid, username: "ab" }))).toEqual([
			"username: Username must be at least 3 characters",
		]);
		expect(signupSchema.safeParse({ ...valid, firstName: "   " }).success).toBe(false);
	});
});
