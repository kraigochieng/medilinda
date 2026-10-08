import { describe, expect, it } from "vitest";
import { MAX_LABEL, hasData, labelAt, shorten } from "../app/utils/dashboard-chart";

describe("shorten", () => {
	it("keeps a short label as it is", () => {
		expect(shorten("Likely")).toBe("Likely");
	});

	it("cuts a long label and marks the cut", () => {
		const long = "Kenyatta National Teaching and Referral Hospital";
		const short = shorten(long);

		expect(short.length).toBeLessThanOrEqual(MAX_LABEL);
		expect(short.endsWith("…")).toBe(true);
		expect(long.startsWith(short.slice(0, -1).trimEnd())).toBe(true);
	});

	it("does not cut a label of exactly the maximum length", () => {
		expect(shorten("x".repeat(MAX_LABEL))).toBe("x".repeat(MAX_LABEL));
	});
});

describe("labelAt", () => {
	const data = [
		{ metric: "certain", value: 3 },
		{ metric: "likely", value: 5 },
	];

	it("gives the label of the bar at that position", () => {
		expect(labelAt(data, 1)).toBe("likely");
	});

	it("gives an empty label for a position with no bar, such as a tick between bars", () => {
		expect(labelAt(data, 5)).toBe("");
		expect(labelAt(data, 0.5)).toBe("");
		expect(labelAt(undefined, 0)).toBe("");
	});
});

describe("hasData", () => {
	it("is false for nothing, an empty list, or only zeros", () => {
		expect(hasData(undefined)).toBe(false);
		expect(hasData([])).toBe(false);
		expect(hasData([{ metric: "a", value: 0 }])).toBe(false);
	});

	it("is true when any bar has a value", () => {
		expect(hasData([{ metric: "a", value: 0 }, { metric: "b", value: 2 }])).toBe(true);
	});
});
