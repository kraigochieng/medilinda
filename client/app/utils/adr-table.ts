// Pure helpers for the ADR table, kept apart from the page so they can be tested.
import { CAUSALITY_LEVELS } from "~/utils/causality-levels";

export type ReviewState =
	| "no_assessment"
	| "needs_review"
	| "approved"
	| "not_approved";

export interface ReviewCounts {
	causality_assessment_level_value?: string | null;
	approved_reviews: number;
	unapproved_reviews: number;
}

// Mirrors the server's review_status filter, which looks at the newest
// assessment of the ADR.
export function reviewState(row: ReviewCounts): ReviewState {
	if (!row.causality_assessment_level_value) return "no_assessment";

	const total = row.approved_reviews + row.unapproved_reviews;
	if (total === 0) return "needs_review";

	return row.approved_reviews > row.unapproved_reviews
		? "approved"
		: "not_approved";
}

export const REVIEW_STATE_BADGE: Record<
	ReviewState,
	{ label: string; color: "warning" | "success" | "error" | "neutral"; icon: string }
> = {
	no_assessment: { label: "No assessment", color: "neutral", icon: "i-lucide-minus" },
	needs_review: { label: "Needs review", color: "warning", icon: "i-lucide-clock" },
	approved: { label: "Approved", color: "success", icon: "i-lucide-check" },
	not_approved: { label: "Not approved", color: "error", icon: "i-lucide-x" },
};

// Most certain first, the way people scan a list.
export const CAUSALITY_OPTIONS = [...CAUSALITY_LEVELS]
	.reverse()
	.map(({ label, value }) => ({ label, value }));

export const REVIEW_STATUS_OPTIONS = [
	{ label: "Needs review", value: "needs_review" },
	{ label: "Approved", value: "approved" },
	{ label: "Not approved", value: "not_approved" },
];

export type SortKey = "patient_name" | "causality_level" | "created_by" | "created_at";
export type SortOrder = "asc" | "desc";

const SORT_KEYS: SortKey[] = ["patient_name", "causality_level", "created_by", "created_at"];

export interface AdrListState {
	page: number;
	query: string;
	causality: string[]; // empty: any level
	review: string[]; // empty: any status
	sortBy: SortKey;
	sortOrder: SortOrder;
}

export const DEFAULT_LIST_STATE: AdrListState = {
	page: 1,
	query: "",
	causality: [],
	review: [],
	sortBy: "created_at",
	sortOrder: "desc",
};

// A URL parameter can be missing, text, or repeated. "a,b" and ["a", "b"] mean the same.
function toList(value: unknown): string[] {
	const parts = (Array.isArray(value) ? value : [value]).flatMap((v) =>
		typeof v === "string" ? v.split(",") : [],
	);
	return parts.map((part) => part.trim()).filter(Boolean);
}

// The known options of a list, in the order given, once each.
function validOptions(options: { value: string }[], value: unknown): string[] {
	const known = new Set(options.map((o) => o.value));
	return [...new Set(toList(value))].filter((v) => known.has(v));
}

const first = (value: unknown) => (Array.isArray(value) ? value[0] : value);

// Reads the list state from the page URL. Anything unknown falls back to the default.
export function parseListQuery(query: Record<string, unknown>): AdrListState {
	const page = Number.parseInt(String(first(query.page) ?? ""), 10);
	const search = first(query.q);
	const sort = first(query.sort);
	const order = first(query.order);

	return {
		page: Number.isInteger(page) && page >= 1 ? page : 1,
		query: typeof search === "string" ? search : "",
		causality: validOptions(CAUSALITY_OPTIONS, query.causality),
		review: validOptions(REVIEW_STATUS_OPTIONS, query.review),
		sortBy: SORT_KEYS.includes(sort as SortKey) ? (sort as SortKey) : DEFAULT_LIST_STATE.sortBy,
		sortOrder: order === "asc" || order === "desc" ? order : DEFAULT_LIST_STATE.sortOrder,
	};
}

// Writes the list state to the page URL, leaving out defaults.
export function serializeListQuery(state: AdrListState): Record<string, string> {
	const out: Record<string, string> = {};
	if (state.page > 1) out.page = String(state.page);
	if (state.query.trim()) out.q = state.query.trim();
	if (state.causality.length) out.causality = state.causality.join(",");
	if (state.review.length) out.review = state.review.join(",");
	if (state.sortBy !== DEFAULT_LIST_STATE.sortBy) out.sort = state.sortBy;
	if (state.sortOrder !== DEFAULT_LIST_STATE.sortOrder) out.order = state.sortOrder;
	return out;
}

// A sort alone is not a filter: it hides nothing.
export function hasActiveFilters(state: AdrListState): boolean {
	return Boolean(state.query.trim()) || state.causality.length > 0 || state.review.length > 0;
}

// The parameters the server's list endpoint understands.
export function buildListParams(state: AdrListState, size: number) {
	return {
		page: state.page,
		size,
		query: state.query.trim() || undefined,
		causality_level: state.causality.length ? state.causality : undefined,
		review_status: state.review.length ? state.review : undefined,
		sort_by: state.sortBy,
		sort_order: state.sortOrder,
	};
}

// What a click on a column header does: a new column sorts ascending (dates start
// with the newest), and the same column again flips the order.
export function nextSort(
	state: Pick<AdrListState, "sortBy" | "sortOrder">,
	column: SortKey,
): Pick<AdrListState, "sortBy" | "sortOrder"> {
	if (state.sortBy === column) {
		return { sortBy: column, sortOrder: state.sortOrder === "asc" ? "desc" : "asc" };
	}
	return { sortBy: column, sortOrder: column === "created_at" ? "desc" : "asc" };
}

// The server stores UTC but writes times without a "Z" (2025-03-04T09:05:00),
// and a browser reads such a string as local time. Treat it as UTC.
export function parseServerDate(iso: string): Date {
	const hasZone = /(Z|[+-]\d{2}:?\d{2})$/i.test(iso);
	return new Date(hasZone ? iso : `${iso}Z`);
}

// Shows a server time in the viewer's own timezone (or the one given).
export function formatDateTime(iso: string, timeZone?: string): string {
	return new Intl.DateTimeFormat("en-GB", {
		dateStyle: "medium",
		timeStyle: "short",
		timeZone,
	}).format(parseServerDate(iso));
}
