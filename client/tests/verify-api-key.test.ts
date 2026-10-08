import { describe, expect, it, vi } from "vitest";
import { handleVerifyApiKey } from "../server/utils/verify-api-key";

const verify = () => vi.fn().mockResolvedValue({ valid: true, key: { referenceId: "u1" } });

describe("internal api key verification", () => {
	it("rejects when no secret is configured", async () => {
		const v = verify();
		const result = await handleVerifyApiKey({
			expectedSecret: undefined,
			providedSecret: "",
			key: "k",
			verify: v,
		});
		expect(result.status).toBe(401);
		expect(v).not.toHaveBeenCalled();
	});

	it("rejects a missing or wrong shared secret", async () => {
		const v = verify();
		for (const providedSecret of [undefined, "", "wrong", "secret-but-longer"]) {
			const result = await handleVerifyApiKey({
				expectedSecret: "secret",
				providedSecret,
				key: "k",
				verify: v,
			});
			expect(result.status).toBe(401);
		}
		expect(v).not.toHaveBeenCalled();
	});

	it("rejects a request without a key", async () => {
		const result = await handleVerifyApiKey({
			expectedSecret: "secret",
			providedSecret: "secret",
			key: undefined,
			verify: verify(),
		});
		expect(result.status).toBe(400);
	});

	it("verifies the key when the secret matches", async () => {
		const v = verify();
		const result = await handleVerifyApiKey({
			expectedSecret: "secret",
			providedSecret: "secret",
			key: "my-key",
			verify: v,
		});
		expect(result).toEqual({ status: 200, body: { valid: true, key: { referenceId: "u1" } } });
		expect(v).toHaveBeenCalledWith("my-key");
	});
});
