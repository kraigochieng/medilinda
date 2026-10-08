import bcrypt from "bcryptjs";
import { describe, expect, it } from "vitest";
import {
	hashUserPassword,
	isBcryptHash,
	verifyUserPassword,
} from "../server/utils/password";

describe("password hashing", () => {
	it("recognises bcrypt hashes", () => {
		expect(isBcryptHash(bcrypt.hashSync("x", 4))).toBe(true);
		expect(isBcryptHash("$2b$12$abcdefghijklmnopqrstuv")).toBe(true);
		expect(isBcryptHash("0f8fb3ad:f136a3a5")).toBe(false);
	});

	it("verifies a legacy bcrypt hash", async () => {
		const hash = bcrypt.hashSync("oldpassword1", 4);
		expect(await verifyUserPassword({ hash, password: "oldpassword1" })).toBe(true);
		expect(await verifyUserPassword({ hash, password: "wrong" })).toBe(false);
	});

	it("hashes new passwords with scrypt, not bcrypt", async () => {
		const hash = await hashUserPassword("newpassword1");
		expect(isBcryptHash(hash)).toBe(false);
		expect(await verifyUserPassword({ hash, password: "newpassword1" })).toBe(true);
		expect(await verifyUserPassword({ hash, password: "nope" })).toBe(false);
	});
});
