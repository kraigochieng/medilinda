// Pure helpers for the ADR table, kept apart from the page so they can be tested.

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

export const CAUSALITY_BADGE_CLASS: Record<string, string> = {
	certain: "bg-red-500 text-white",
	likely: "bg-red-400 text-black",
	possible: "bg-yellow-500 text-black",
	unlikely: "bg-yellow-300 text-black",
	unclassified: "bg-slate-500 text-white",
	unclassifiable: "bg-slate-300 text-black",
};

export const ALL = "all";

export const CAUSALITY_OPTIONS = [
	{ label: "All levels", value: ALL },
	{ label: "Certain", value: "certain" },
	{ label: "Likely", value: "likely" },
	{ label: "Possible", value: "possible" },
	{ label: "Unlikely", value: "unlikely" },
	{ label: "Unclassified", value: "unclassified" },
	{ label: "Unclassifiable", value: "unclassifiable" },
];

export const REVIEW_STATUS_OPTIONS = [
	{ label: "All reviews", value: ALL },
	{ label: "Needs review", value: "needs_review" },
	{ label: "Approved", value: "approved" },
	{ label: "Not approved", value: "not_approved" },
];

export interface AdrListState {
	page: number;
	query: string;
	causality: string;
	review: string;
}

export const DEFAULT_LIST_STATE: AdrListState = {
	page: 1,
	query: "",
	causality: ALL,
	review: ALL,
};

const isOption = (options: { value: string }[], value: unknown): value is string =>
	typeof value === "string" && options.some((o) => o.value === value);

const first = (value: unknown) => (Array.isArray(value) ? value[0] : value);

// Reads the list state from the page URL. Anything unknown falls back to the default.
export function parseListQuery(query: Record<string, unknown>): AdrListState {
	const page = Number.parseInt(String(first(query.page) ?? ""), 10);
	const causality = first(query.causality);
	const review = first(query.review);
	const search = first(query.q);

	return {
		page: Number.isInteger(page) && page >= 1 ? page : 1,
		query: typeof search === "string" ? search : "",
		causality: isOption(CAUSALITY_OPTIONS, causality) ? causality : ALL,
		review: isOption(REVIEW_STATUS_OPTIONS, review) ? review : ALL,
	};
}

// Writes the list state to the page URL, leaving out defaults.
export function serializeListQuery(state: AdrListState): Record<string, string> {
	const out: Record<string, string> = {};
	if (state.page > 1) out.page = String(state.page);
	if (state.query.trim()) out.q = state.query.trim();
	if (state.causality !== ALL) out.causality = state.causality;
	if (state.review !== ALL) out.review = state.review;
	return out;
}

export function hasActiveFilters(state: AdrListState): boolean {
	return Boolean(state.query.trim()) || state.causality !== ALL || state.review !== ALL;
}

// The parameters the server's list endpoint understands.
export function buildListParams(state: AdrListState, size: number) {
	return {
		page: state.page,
		size,
		query: state.query.trim() || undefined,
		causality_level: state.causality !== ALL ? state.causality : undefined,
		review_status: state.review !== ALL ? state.review : undefined,
	};
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
