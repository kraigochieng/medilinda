import { describe, expect, it } from "vitest";
import { savedBanner, type SavedBannerInput } from "../app/utils/adr-saved";

const input = (overrides: Partial<SavedBannerInput> = {}): SavedBannerInput => ({
	kind: "created",
	adrId: "adr-1",
	level: "likely",
	approved: 0,
	unapproved: 0,
	...overrides,
});

const labels = (banner: ReturnType<typeof savedBanner>) => banner.actions.map((a) => a.label);
const targets = (banner: ReturnType<typeof savedBanner>) => banner.actions.map((a) => a.to);

describe("a new report", () => {
	it("says what the model assessed and that it needs a review", () => {
		const banner = savedBanner(input());

		expect(banner.title).toBe("Report saved");
		expect(banner.description).toBe("The model assessed it as Likely. It needs a review.");
		expect(banner.color).toBe("info");
		expect(labels(banner)).toEqual(["Review now", "Add another", "Back to ADRs"]);
		expect(targets(banner)).toEqual(["/adr/adr-1/review", "/adr/add", "/adr"]);
	});

	it("explains a report the model could not classify, and offers Edit", () => {
		const banner = savedBanner(input({ level: "unclassified" }));

		expect(banner.color).toBe("warning");
		expect(banner.description).toMatch(/could not classify/);
		expect(banner.description).toMatch(/suspected medicines/);
		expect(labels(banner)).toEqual(["Edit the report", "Add another", "Back to ADRs"]);
		expect(targets(banner)[0]).toBe("/adr/adr-1/edit");
	});

	it("says so for a report marked unclassifiable, without offering a review", () => {
		const banner = savedBanner(input({ level: "unclassifiable" }));

		expect(banner.description).toMatch(/unclassifiable/);
		expect(labels(banner)).not.toContain("Review now");
	});

	it("does not claim an assessment when there is none", () => {
		const banner = savedBanner(input({ level: null }));

		expect(banner.description).toMatch(/no causality assessment yet/);
		expect(labels(banner)).toContain("Edit the report");
	});

	it("shows a waiting message with no actions while the assessment is being fetched", () => {
		const banner = savedBanner(input({ loading: true, level: "likely" }));

		expect(banner.description).toBe("Checking the causality assessment…");
		expect(banner.actions).toEqual([]);
	});
});

describe("an edited report", () => {
	it("says the changes are saved and the current level, and asks for a new review", () => {
		const banner = savedBanner(input({ kind: "updated" }));

		expect(banner.title).toBe("Changes saved");
		expect(banner.description).toBe("The current assessment is Likely. It needs a new review.");
		expect(labels(banner)).toEqual(["Review now", "Back to ADRs"]); // no 'Add another'
	});

	it("does not ask for a review when the current assessment already has one", () => {
		const banner = savedBanner(input({ kind: "updated", approved: 2, unapproved: 1 }));

		expect(banner.description).toBe("The current assessment is Likely. It has been reviewed and approved.");
		expect(banner.color).toBe("success");
		expect(labels(banner)).toEqual(["Back to ADRs"]);
	});

	it("still points to Edit when an edit leaves the report unclassified", () => {
		const banner = savedBanner(input({ kind: "updated", level: "unclassified" }));

		expect(labels(banner)).toEqual(["Edit the report", "Back to ADRs"]);
	});
});

describe("review state", () => {
	it("a tie is not approved", () => {
		const banner = savedBanner(input({ approved: 1, unapproved: 1 }));

		expect(banner.description).toMatch(/reviewed and not approved/);
		expect(banner.color).toBe("warning");
	});

	it("capitalises any level", () => {
		expect(savedBanner(input({ level: "certain" })).description).toMatch(/Certain/);
		expect(savedBanner(input({ level: "possible" })).description).toMatch(/Possible/);
	});
});
