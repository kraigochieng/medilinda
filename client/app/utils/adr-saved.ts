// What to tell the user right after an ADR is saved: the assessment the model
// gave it, whether it needs a review, and what to do next.

export type SavedKind = "created" | "updated";

export interface SavedBannerInput {
	kind: SavedKind;
	adrId: string;
	level?: string | null; // the newest causality assessment
	approved: number; // reviews of that assessment
	unapproved: number;
	loading?: boolean; // the assessment or its reviews are still being fetched
}

export interface BannerAction {
	label: string;
	to: string;
}

export interface SavedBanner {
	color: "success" | "info" | "warning";
	icon: string;
	title: string;
	description: string;
	actions: BannerAction[];
}

const capitalize = (text: string) => text.charAt(0).toUpperCase() + text.slice(1);

export function savedBanner(input: SavedBannerInput): SavedBanner {
	const { kind, adrId, level, approved, unapproved, loading } = input;
	const title = kind === "created" ? "Report saved" : "Changes saved";

	const edit: BannerAction = { label: "Edit the report", to: `/adr/${adrId}/edit` };
	const review: BannerAction = { label: "Review now", to: `/adr/${adrId}/review` };
	const addAnother: BannerAction = { label: "Add another", to: "/adr/add" };
	const back: BannerAction = { label: "Back to ADRs", to: "/adr" };
	const next = (...actions: BannerAction[]) =>
		kind === "created" ? [...actions, addAnother, back] : [...actions, back];

	if (loading) {
		return {
			color: "info",
			icon: "i-lucide-loader-circle",
			title,
			description: "Checking the causality assessment…",
			actions: [],
		};
	}

	if (!level) {
		return {
			color: "warning",
			icon: "i-lucide-triangle-alert",
			title,
			description: "The report is saved, but it has no causality assessment yet.",
			actions: next(edit),
		};
	}

	if (level === "unclassifiable") {
		return {
			color: "warning",
			icon: "i-lucide-circle-help",
			title,
			description: "This report is marked as unclassifiable, so it cannot be assessed.",
			actions: next(),
		};
	}

	if (level === "unclassified") {
		return {
			color: "warning",
			icon: "i-lucide-circle-help",
			title,
			description:
				"The model could not classify this report. Mark the suspected medicines and answer the rechallenge or dechallenge question, then save again.",
			actions: next(edit),
		};
	}

	const name = capitalize(level);
	const total = approved + unapproved;
	const lead = kind === "created" ? `The model assessed it as ${name}.` : `The current assessment is ${name}.`;

	if (total === 0) {
		return {
			color: "info",
			icon: "i-lucide-clipboard-check",
			title,
			description: `${lead} ${kind === "created" ? "It needs a review." : "It needs a new review."}`,
			actions: next(review),
		};
	}

	const approvedOverall = approved > unapproved;
	return {
		color: approvedOverall ? "success" : "warning",
		icon: approvedOverall ? "i-lucide-circle-check" : "i-lucide-circle-alert",
		title,
		description: `${lead} It has been reviewed and ${approvedOverall ? "approved" : "not approved"}.`,
		actions: next(),
	};
}
