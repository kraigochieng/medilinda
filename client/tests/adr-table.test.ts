import { describe, expect, it } from "vitest";
import {
	ALL,
	DEFAULT_LIST_STATE,
	buildListParams,
	formatDateTime,
	hasActiveFilters,
	parseListQuery,
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

describe("list state in the URL", () => {
	it("round-trips a state", () => {
		const state = { page: 3, query: "alice", causality: "likely", review: "needs_review" };
		expect(parseListQuery(serializeListQuery(state))).toEqual(state);
	});

	it("leaves defaults out of the URL", () => {
		expect(serializeListQuery(DEFAULT_LIST_STATE)).toEqual({});
	});

	it("falls back to defaults for missing or invalid values", () => {
		expect(parseListQuery({})).toEqual(DEFAULT_LIST_STATE);
		expect(
			parseListQuery({ page: "0", causality: "bogus", review: "nope", q: 5 }),
		).toEqual(DEFAULT_LIST_STATE);
		expect(parseListQuery({ page: "abc" }).page).toBe(1);
		expect(parseListQuery({ page: "-4" }).page).toBe(1);
	});

	it("uses the first value when a parameter is repeated", () => {
		expect(parseListQuery({ causality: ["certain", "likely"] }).causality).toBe("certain");
	});

	it("trims the search text before writing it", () => {
		expect(serializeListQuery({ ...DEFAULT_LIST_STATE, query: "  bob  " })).toEqual({ q: "bob" });
		expect(serializeListQuery({ ...DEFAULT_LIST_STATE, query: "   " })).toEqual({});
	});
});

describe("hasActiveFilters", () => {
	it("is false for the default state, even on a later page", () => {
		expect(hasActiveFilters(DEFAULT_LIST_STATE)).toBe(false);
		expect(hasActiveFilters({ ...DEFAULT_LIST_STATE, page: 4 })).toBe(false);
	});

	it("is true when searching or filtering", () => {
		expect(hasActiveFilters({ ...DEFAULT_LIST_STATE, query: "x" })).toBe(true);
		expect(hasActiveFilters({ ...DEFAULT_LIST_STATE, causality: "certain" })).toBe(true);
		expect(hasActiveFilters({ ...DEFAULT_LIST_STATE, review: "approved" })).toBe(true);
	});

	it("ignores a search of only spaces", () => {
		expect(hasActiveFilters({ ...DEFAULT_LIST_STATE, query: "   " })).toBe(false);
	});
});

describe("buildListParams", () => {
	it("sends only what the user chose", () => {
		expect(buildListParams(DEFAULT_LIST_STATE, 20)).toEqual({
			page: 1,
			size: 20,
			query: undefined,
			causality_level: undefined,
			review_status: undefined,
		});
	});

	it("maps the filters to the server's parameter names", () => {
		expect(
			buildListParams(
				{ page: 2, query: " alice ", causality: "likely", review: "needs_review" },
				50,
			),
		).toEqual({
			page: 2,
			size: 50,
			query: "alice",
			causality_level: "likely",
			review_status: "needs_review",
		});
	});

	it("treats 'all' as no filter", () => {
		const params = buildListParams({ ...DEFAULT_LIST_STATE, causality: ALL, review: ALL }, 10);
		expect(params.causality_level).toBeUndefined();
		expect(params.review_status).toBeUndefined();
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
