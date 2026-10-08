import { describe, expect, it } from "vitest";
import { CAUSALITY_OPTIONS, ALL } from "../app/utils/adr-table";
import { CAUSALITY_LEVELS, causalityLevel } from "../app/utils/causality-levels";

describe("causality levels", () => {
	it("has the six levels the server can send, from least to most certain", () => {
		expect(CAUSALITY_LEVELS.map((l) => l.value)).toEqual([
			"unclassifiable",
			"unclassified",
			"unlikely",
			"possible",
			"likely",
			"certain",
		]);
	});

	it("describes and colours every level", () => {
		for (const level of CAUSALITY_LEVELS) {
			expect(level.label, level.value).toMatch(/^[A-Z]/);
			expect(level.description.length, level.value).toBeGreaterThan(30);
			expect(level.badgeClass, level.value).toMatch(/bg-/);
		}
	});

	it("uses a different colour for every level", () => {
		const classes = CAUSALITY_LEVELS.map((l) => l.badgeClass);
		expect(new Set(classes).size).toBe(classes.length);
	});

	it("tells the user what to do about an unclassified report", () => {
		expect(causalityLevel("unclassified")!.description).toMatch(/suspected medicines/);
	});

	it("finds a level whatever the case, and returns nothing for the unknown", () => {
		expect(causalityLevel("likely")!.label).toBe("Likely");
		expect(causalityLevel("LIKELY")!.label).toBe("Likely");
		expect(causalityLevel("nonsense")).toBeUndefined();
		expect(causalityLevel(undefined)).toBeUndefined();
		expect(causalityLevel(null)).toBeUndefined();
		expect(causalityLevel("")).toBeUndefined();
	});
});

describe("the list filter", () => {
	it("offers every level, most certain first, after 'All levels'", () => {
		expect(CAUSALITY_OPTIONS.map((o) => o.value)).toEqual([
			ALL,
			"certain",
			"likely",
			"possible",
			"unlikely",
			"unclassified",
			"unclassifiable",
		]);
	});

	it("uses the same labels as the scale", () => {
		for (const level of CAUSALITY_LEVELS) {
			expect(CAUSALITY_OPTIONS.find((o) => o.value === level.value)?.label).toBe(level.label);
		}
	});
});
