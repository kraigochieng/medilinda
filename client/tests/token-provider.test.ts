import { describe, expect, it, vi } from "vitest";
import { createTokenProvider, readTokenExpiry } from "../app/utils/token-provider";

const jwtWithExp = (expSeconds: number) =>
	`h.${Buffer.from(JSON.stringify({ exp: expSeconds })).toString("base64url")}.s`;

describe("readTokenExpiry", () => {
	it("returns the exp claim in milliseconds", () => {
		expect(readTokenExpiry(jwtWithExp(1000))).toBe(1_000_000);
	});

	it("returns 0 for a malformed token", () => {
		expect(readTokenExpiry("not-a-jwt")).toBe(0);
		expect(readTokenExpiry("")).toBe(0);
	});
});

describe("token provider", () => {
	it("reuses a cached token until shortly before it expires", async () => {
		let now = 0;
		const fetchToken = vi.fn().mockResolvedValue(jwtWithExp(900)); // expires at 900_000 ms
		const tokens = createTokenProvider({ fetchToken, cache: true, now: () => now });

		await tokens.get();
		now = 800_000;
		await tokens.get();
		expect(fetchToken).toHaveBeenCalledTimes(1);

		now = 880_000; // inside the 30s safety margin
		await tokens.get();
		expect(fetchToken).toHaveBeenCalledTimes(2);
	});

	it("never caches on the server", async () => {
		const fetchToken = vi.fn().mockResolvedValue(jwtWithExp(9_999_999_999));
		const tokens = createTokenProvider({ fetchToken, cache: false });

		await tokens.get();
		await tokens.get();
		expect(fetchToken).toHaveBeenCalledTimes(2);
	});

	it("returns null and drops the cache when fetching fails", async () => {
		const fetchToken = vi
			.fn()
			.mockResolvedValueOnce(jwtWithExp(9_999_999_999))
			.mockRejectedValueOnce(new Error("401"))
			.mockResolvedValueOnce(jwtWithExp(9_999_999_999));
		const tokens = createTokenProvider({ fetchToken, cache: true });

		expect(await tokens.get()).not.toBeNull();
		tokens.clear();
		expect(await tokens.get()).toBeNull();
		expect(await tokens.get()).not.toBeNull();
		expect(fetchToken).toHaveBeenCalledTimes(3);
	});
});
