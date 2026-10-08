import { describe, expect, it } from "vitest";
import { describeKey, expiryInSeconds } from "../app/utils/api-keys";

const NOW = new Date("2025-06-15T12:00:00Z");

describe("describeKey", () => {
	it("says there is no expiry when there is none", () => {
		expect(describeKey({ expiresAt: null }, NOW)).toEqual({ text: "No expiry", expired: false });
	});

	it("shows a future expiry as a date", () => {
		expect(describeKey({ expiresAt: "2025-08-13T12:00:00Z" }, NOW)).toEqual({
			text: "Expires 13 Aug 2025",
			expired: false,
		});
	});

	it("marks a key that has expired", () => {
		expect(describeKey({ expiresAt: "2025-06-01T00:00:00Z" }, NOW)).toEqual({
			text: "Expired 1 Jun 2025",
			expired: true,
		});
	});

	it("treats the moment of expiry as expired", () => {
		expect(describeKey({ expiresAt: NOW }, NOW).expired).toBe(true);
	});

	it("accepts a Date or text, and does not fail on text it cannot read", () => {
		expect(describeKey({ expiresAt: new Date("2025-07-01T00:00:00Z") }, NOW).text).toBe("Expires 1 Jul 2025");
		expect(describeKey({ expiresAt: "not a date" }, NOW)).toEqual({ text: "No expiry", expired: false });
	});
});

describe("expiryInSeconds", () => {
	it("turns days into seconds", () => {
		expect(expiryInSeconds(1)).toBe(86_400);
		expect(expiryInSeconds(90)).toBe(7_776_000);
	});

	it("means no expiry for an empty, zero or invalid value", () => {
		for (const value of [undefined, null, 0, -3, Number.NaN]) {
			expect(expiryInSeconds(value as number)).toBeUndefined();
		}
	});

	it("rounds a part of a day down to whole days", () => {
		expect(expiryInSeconds(1.9)).toBe(86_400);
	});
});
