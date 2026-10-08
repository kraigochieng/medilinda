// What the Home page shows. Kept apart from the page so it can be tested.
import { DEFAULT_LIST_STATE, serializeListQuery } from "~/utils/adr-table";

export interface HomeCard {
	key: "all" | "needs_review" | "not_approved";
	label: string;
	hint: string;
	icon: string;
	value: number | undefined; // undefined: not loaded yet
	to: string;
}

// The list address for a review filter, built by the list's own rules.
function listAddress(review: string[]): string {
	const query = new URLSearchParams(serializeListQuery({ ...DEFAULT_LIST_STATE, review }));
	const text = query.toString().replace(/%2C/g, ",");
	return text ? `/adr?${text}` : "/adr";
}

export function homeCards(counts: { all?: number; needsReview?: number; notApproved?: number }): HomeCard[] {
	return [
		{
			key: "all",
			label: "All ADRs",
			hint: "Every report in the system",
			icon: "i-lucide-file-heart",
			value: counts.all,
			to: listAddress([]),
		},
		{
			key: "needs_review",
			label: "Need a review",
			hint: "A prediction with no review yet",
			icon: "i-lucide-clock",
			value: counts.needsReview,
			to: listAddress(["needs_review"]),
		},
		{
			key: "not_approved",
			label: "Not approved",
			hint: "Reviewers did not agree with the prediction",
			icon: "i-lucide-circle-x",
			value: counts.notApproved,
			to: listAddress(["not_approved"]),
		},
	];
}

export function greeting(user: { first_name?: string | null } | undefined, hour: number): string {
	const part = hour >= 5 && hour < 12 ? "morning" : hour >= 12 && hour < 17 ? "afternoon" : "evening";
	const name = user?.first_name?.trim();
	return name ? `Good ${part}, ${name}` : `Good ${part}`;
}
