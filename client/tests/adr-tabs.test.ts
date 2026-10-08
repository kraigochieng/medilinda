import { describe, expect, it } from "vitest";
import { ADR_TABS, DEFAULT_TAB, parseTab, tabAddress, tabQuery, withoutSaved } from "../app/utils/adr-tabs";

describe("parseTab", () => {
	it("reads a known tab", () => {
		for (const tab of ["details", "prediction", "review", "history"]) expect(parseTab(tab)).toBe(tab);
	});

	it("falls back to the details tab", () => {
		for (const bad of [undefined, null, "", "nope", "DETAILS", 5]) {
			expect(parseTab(bad)).toBe(DEFAULT_TAB);
		}
		expect(DEFAULT_TAB).toBe("details");
	});

	it("uses the first value when the parameter is repeated", () => {
		expect(parseTab(["review", "history"])).toBe("review");
		expect(parseTab(["nope", "history"])).toBe("details");
	});
});

describe("tabQuery", () => {
	it("leaves the default tab out of the address", () => {
		expect(tabQuery("details", {})).toEqual({});
	});

	it("writes another tab, and keeps the other parameters", () => {
		expect(tabQuery("review", {})).toEqual({ tab: "review" });
		expect(tabQuery("history", { foo: "1" })).toEqual({ foo: "1", tab: "history" });
	});

	it("removes an old tab when the default is chosen", () => {
		expect(tabQuery("details", { tab: "review", foo: "1" })).toEqual({ foo: "1" });
	});
});

describe("tabAddress", () => {
	it("links to a tab of an ADR, for the list", () => {
		expect(tabAddress("a1", "details")).toBe("/adr/a1");
		expect(tabAddress("a1", "prediction")).toBe("/adr/a1?tab=prediction");
		expect(tabAddress("a1", "review")).toBe("/adr/a1?tab=review");
		expect(tabAddress("a1", "history")).toBe("/adr/a1?tab=history");
	});
});

describe("withoutSaved", () => {
	it("removes the saved markers and keeps the tab", () => {
		expect(withoutSaved({ saved: "1", tab: "review" })).toEqual({ tab: "review" });
		expect(withoutSaved({ created: "1" })).toEqual({});
	});
});

describe("ADR_TABS", () => {
	it("has the four tabs in order, with labels", () => {
		expect(ADR_TABS.map((t) => [t.value, t.label])).toEqual([
			["details", "Details"],
			["prediction", "Prediction"],
			["review", "Review"],
			["history", "History"],
		]);
	});
});
