import { describe, expect, it } from "vitest";
import {
	DEFAULT_LIST_STATE,
	buildListParams,
	formatDateTime,
	hasActiveFilters,
	parseListQuery,
	nextSort,
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
