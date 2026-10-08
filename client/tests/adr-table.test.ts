import { describe, expect, it } from "vitest";
import {
	DEFAULT_LIST_STATE,
	buildListParams,
	formatDateTime,
	hasActiveFilters,
	parseListQuery,
	MY_REVIEW_OPTIONS,
	myReviewTag,
	nextSort,
	rowMenu,
	reviewState,
	serializeListQuery,
} from "../app/utils/adr-table";

const row = (approved: number, unapproved: number, level: string | null = "likely") => ({
	causality_assessment_level_value: level,
	approved_reviews: approved,
	unapproved_reviews: unapproved,
});

describe("reviewState", () => {
	it("is 'no_assessment' when the ADR has no causality level", () => {
		expect(reviewState(row(0, 0, null))).toBe("no_assessment");
		expect(reviewState(row(3, 0, null))).toBe("no_assessment");
	});

	it("is 'needs_review' when the assessment has no reviews", () => {
		expect(reviewState(row(0, 0))).toBe("needs_review");
	});

	it("is 'approved' only when approvals outnumber rejections", () => {
		expect(reviewState(row(2, 1))).toBe("approved");
		expect(reviewState(row(1, 0))).toBe("approved");
	});

	it("is 'not_approved' for ties and for more rejections", () => {
		expect(reviewState(row(1, 1))).toBe("not_approved");
		expect(reviewState(row(0, 2))).toBe("not_approved");
	});
});

const state = (extra = {}) => ({ ...DEFAULT_LIST_STATE, ...extra });

describe("list state in the URL", () => {
	it("round-trips a state with several values and a sort", () => {
		const full = state({
			page: 3,
			query: "alice",
			causality: ["likely", "certain"],
			review: ["needs_review", "approved"],
			mine: ["not_reviewed"],
			sortBy: "patient_name",
			sortOrder: "asc",
		});

		expect(parseListQuery(serializeListQuery(full))).toEqual(full);
	});

	it("writes several values as one comma separated parameter", () => {
		expect(serializeListQuery(state({ causality: ["likely", "certain"] }))).toEqual({
			causality: "likely,certain",
		});
	});

	it("leaves defaults out of the URL", () => {
		expect(serializeListQuery(DEFAULT_LIST_STATE)).toEqual({});
	});

	it("sorts newest first by default", () => {
		expect(DEFAULT_LIST_STATE.sortBy).toBe("created_at");
		expect(DEFAULT_LIST_STATE.sortOrder).toBe("desc");
	});

	it("writes a sort only when it is not the default", () => {
		expect(serializeListQuery(state({ sortBy: "created_by" }))).toEqual({ sort: "created_by" });
		expect(serializeListQuery(state({ sortOrder: "asc" }))).toEqual({ order: "asc" });
	});

	it("falls back to defaults for missing or invalid values", () => {
		expect(parseListQuery({})).toEqual(DEFAULT_LIST_STATE);
		expect(
			parseListQuery({
				page: "0",
				causality: "bogus",
				review: "nope",
				q: 5,
				sort: "password",
				order: "sideways",
			}),
		).toEqual(DEFAULT_LIST_STATE);
		expect(parseListQuery({ page: "abc" }).page).toBe(1);
		expect(parseListQuery({ page: "-4" }).page).toBe(1);
	});

	it("keeps the valid values of a list and drops the others", () => {
		expect(parseListQuery({ causality: "likely,bogus,certain,likely" }).causality).toEqual([
			"likely",
			"certain",
		]);
	});

	it("reads a repeated parameter as well as a comma separated one", () => {
		expect(parseListQuery({ causality: ["certain", "likely,possible"] }).causality).toEqual([
			"certain",
			"likely",
			"possible",
		]);
	});

	it("trims the search text before writing it", () => {
		expect(serializeListQuery(state({ query: "  bob  " }))).toEqual({ q: "bob" });
		expect(serializeListQuery(state({ query: "   " }))).toEqual({});
	});
});

describe("hasActiveFilters", () => {
	it("is false for the default state, even on a later page or with a sort", () => {
		expect(hasActiveFilters(DEFAULT_LIST_STATE)).toBe(false);
		expect(hasActiveFilters(state({ page: 4 }))).toBe(false);
		expect(hasActiveFilters(state({ sortBy: "patient_name", sortOrder: "asc" }))).toBe(false);
	});

	it("is true when searching or filtering", () => {
		expect(hasActiveFilters(state({ query: "x" }))).toBe(true);
		expect(hasActiveFilters(state({ causality: ["certain"] }))).toBe(true);
		expect(hasActiveFilters(state({ review: ["approved"] }))).toBe(true);
		expect(hasActiveFilters(state({ mine: ["not_reviewed"] }))).toBe(true);
	});

	it("ignores a search of only spaces", () => {
		expect(hasActiveFilters(state({ query: "   " }))).toBe(false);
	});
});

describe("buildListParams", () => {
	it("sends only what the user chose, and the sort", () => {
		expect(buildListParams(DEFAULT_LIST_STATE, 20)).toEqual({
			page: 1,
			size: 20,
			query: undefined,
			causality_level: undefined,
			review_status: undefined,
			my_review: undefined,
			sort_by: "created_at",
			sort_order: "desc",
		});
	});

	it("maps the filters to the server's parameter names, as lists", () => {
		expect(
			buildListParams(
				state({
					page: 2,
					query: " alice ",
					causality: ["likely", "certain"],
					review: ["needs_review"],
					mine: ["not_reviewed", "reviewed"],
					sortBy: "causality_level",
					sortOrder: "asc",
				}),
				50,
			),
		).toEqual({
			page: 2,
			size: 50,
			query: "alice",
			causality_level: ["likely", "certain"],
			review_status: ["needs_review"],
			my_review: ["not_reviewed", "reviewed"],
			sort_by: "causality_level",
			sort_order: "asc",
		});
	});
});

describe("nextSort", () => {
	it("sorts a new column ascending, except the dates, which start newest first", () => {
		expect(nextSort(DEFAULT_LIST_STATE, "patient_name")).toEqual({
			sortBy: "patient_name",
			sortOrder: "asc",
		});
		expect(nextSort(state({ sortBy: "patient_name" }), "created_at")).toEqual({
			sortBy: "created_at",
			sortOrder: "desc",
		});
	});

	it("flips the order when the same column is chosen again", () => {
		expect(nextSort(state({ sortBy: "patient_name", sortOrder: "asc" }), "patient_name")).toEqual({
			sortBy: "patient_name",
			sortOrder: "desc",
		});
		expect(nextSort(DEFAULT_LIST_STATE, "created_at")).toEqual({
			sortBy: "created_at",
			sortOrder: "asc",
		});
	});
});

describe("formatDateTime", () => {
	it("treats a time without a zone as UTC, like the server writes it", () => {
		expect(formatDateTime("2025-03-04T09:05:00", "UTC")).toBe("4 Mar 2025, 09:05");
	});

	it("shows the time in the viewer's timezone", () => {
		expect(formatDateTime("2025-03-04T09:05:00", "Africa/Nairobi")).toBe("4 Mar 2025, 12:05");
	});

	it("respects a zone that is already there", () => {
		expect(formatDateTime("2025-03-04T09:05:00Z", "UTC")).toBe("4 Mar 2025, 09:05");
		expect(formatDateTime("2025-03-04T12:05:00+03:00", "UTC")).toBe("4 Mar 2025, 09:05");
	});

	it("handles fractional seconds", () => {
		expect(formatDateTime("2025-03-04T09:05:00.123456", "UTC")).toBe("4 Mar 2025, 09:05");
	});
});


describe("the reviews of the signed-in user", () => {
	it("offers needs your review first, then reviewed by you", () => {
		expect(MY_REVIEW_OPTIONS).toEqual([
			{ label: "Needs your review", value: "not_reviewed" },
			{ label: "Reviewed by you", value: "reviewed" },
		]);
	});

	it("keeps the filter in the address", () => {
		expect(serializeListQuery(state({ mine: ["not_reviewed"] }))).toEqual({ mine: "not_reviewed" });
		expect(parseListQuery({ mine: "reviewed,bogus,not_reviewed" }).mine).toEqual(["reviewed", "not_reviewed"]);
		expect(parseListQuery({ mine: "bogus" }).mine).toEqual([]);
	});
});

describe("myReviewTag", () => {
	const row = (extra = {}) => ({
		causality_assessment_level_value: "likely",
		reviewed_by_me: false,
		...extra,
	});

	it("says needs your review when the user has not reviewed the newest prediction", () => {
		expect(myReviewTag(row())).toMatchObject({ label: "Needs your review", color: "warning" });
	});

	it("says reviewed by you when the user has", () => {
		expect(myReviewTag(row({ reviewed_by_me: true }))).toMatchObject({
			label: "Reviewed by you",
			color: "success",
		});
	});

	it("has no tag when there is no prediction to review", () => {
		expect(myReviewTag(row({ causality_assessment_level_value: null }))).toBeNull();
		expect(myReviewTag(row({ causality_assessment_level_value: undefined }))).toBeNull();
	});
});

describe("rowMenu", () => {
	const row = (extra = {}) => ({
		adr_id: "a1",
		causality_assessment_level_value: "likely",
		reviewed_by_me: false,
		...extra,
	});
	const labels = (menu: ReturnType<typeof rowMenu>) => menu.map((group) => group.map((item) => item.label));

	it("links to each tab of the ADR", () => {
		const [views] = rowMenu(row());

		expect(views!.map((i) => [i.label, i.to])).toEqual([
			["View details", "/adr/a1"],
			["View prediction", "/adr/a1?tab=prediction"],
			["View review", "/adr/a1?tab=review"],
			["View history", "/adr/a1?tab=history"],
		]);
	});

	it("offers to add a review when the user has none", () => {
		const menu = rowMenu(row());

		expect(labels(menu)[1]).toEqual(["Add review"]);
		expect(menu[1]![0]!.to).toBe("/adr/a1/review");
	});

	it("offers to edit the review when the user has one", () => {
		expect(labels(rowMenu(row({ reviewed_by_me: true })))[1]).toEqual(["Edit review"]);
	});

	it("leaves out the prediction, the review and the review action when there is no prediction", () => {
		const menu = rowMenu(row({ causality_assessment_level_value: null }));

		expect(labels(menu)[0]).toEqual(["View details", "View history"]);
		expect(labels(menu).flat()).not.toContain("Add review");
		expect(labels(menu).flat()).not.toContain("Edit review");
	});

	it("ends with edit and delete", () => {
		const menu = rowMenu(row());

		expect(labels(menu).at(-1)).toEqual(["Edit ADR", "Delete"]);
		expect(menu.at(-1)![0]!.to).toBe("/adr/a1/edit");
		expect(menu.at(-1)![1]!.id).toBe("delete");
	});
});
