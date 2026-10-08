// Sections of the ADR form, and the status shown for each one. Kept apart from
// the component so the rules can be tested.
import { stableString } from "~/utils/adr-draft";
import { emptyFormState, type AdrForm } from "~/utils/adr-form";

export interface FormSection {
	id: string; // the id of the heading in the form
	label: string;
	fields: string[];
	required: string[];
}

export const SECTIONS: FormSection[] = [
	{
		id: "institution-details",
		label: "Institution",
		fields: ["medical_institution_id"],
		required: ["medical_institution_id"],
	},
	{
		id: "patient-details",
		label: "Patient",
		fields: [
			"patient_name",
			"patient_date_of_birth",
			"patient_age",
			"patient_height_cm",
			"patient_weight_kg",
			"inpatient_or_outpatient_number",
			"patient_address",
			"ward_or_clinic",
			"patient_gender",
			"pregnancy_status",
			"known_allergy",
		],
		required: ["patient_name", "patient_gender", "pregnancy_status", "known_allergy"],
	},
	{
		id: "suspected-adverse-reaction",
		label: "Reaction",
		fields: ["date_of_onset_of_reaction", "description_of_reaction"],
		required: [],
	},
	{ id: "medicines", label: "Medicines", fields: ["medicines"], required: [] },
	{
		id: "rechallenge",
		label: "Rechallenge and dechallenge",
		fields: ["rechallenge", "dechallenge"],
		required: [],
	},
	{
		id: "grading",
		label: "Grading",
		fields: [
			"severity",
			"is_serious",
			"criteria_for_seriousness",
			"action_taken",
			"outcome",
			"comments",
		],
		required: ["is_serious", "criteria_for_seriousness"],
	},
];

export type SectionState = "complete" | "incomplete" | "error" | "optional";

export interface SectionStatus {
	section: FormSection;
	state: SectionState;
	problems: number;
}

// A validation problem, as the schema or a custom check reports it.
export interface FormIssue {
	path: PropertyKey[];
}

export function sectionOf(path: PropertyKey[]): FormSection | undefined {
	const field = String(path[0] ?? "");
	return SECTIONS.find((section) => section.fields.includes(field));
}

export function groupIssues(issues: FormIssue[]): Map<string, FormIssue[]> {
	const grouped = new Map<string, FormIssue[]>();
	for (const issue of issues) {
		const section = sectionOf(issue.path);
		if (!section) continue;
		grouped.set(section.id, [...(grouped.get(section.id) ?? []), issue]);
	}
	return grouped;
}

// Has the user entered anything in this section, beyond the blank form?
function touched(section: FormSection, state: Partial<AdrForm>): boolean {
	const blank = emptyFormState() as Record<string, unknown>;
	const current = state as Record<string, unknown>;

	return section.fields.some(
		(field) => stableString(current[field]) !== stableString(blank[field]),
	);
}

// Before the user tries to save, only a missing required field counts, so the
// form does not scold anyone who has just started. After a failed save, every
// problem counts.
export function sectionStatuses(
	state: Partial<AdrForm>,
	issues: FormIssue[],
	attempted: boolean,
): SectionStatus[] {
	const grouped = groupIssues(issues);

	return SECTIONS.map((section) => {
		const sectionIssues = grouped.get(section.id) ?? [];
		const missingRequired = sectionIssues.filter((issue) =>
			section.required.includes(String(issue.path[0])),
		);

		if (attempted && sectionIssues.length) {
			return { section, state: "error", problems: sectionIssues.length };
		}
		if (missingRequired.length) {
			return { section, state: "incomplete", problems: missingRequired.length };
		}
		if (section.required.length) return { section, state: "complete", problems: 0 };

		return { section, state: touched(section, state) ? "complete" : "optional", problems: 0 };
	});
}

// How many required fields are in order.
export function requiredProgress(issues: FormIssue[]): { done: number; total: number } {
	const required = SECTIONS.flatMap((section) => section.required);
	const failing = new Set(issues.map((issue) => String(issue.path[0])));

	return {
		total: required.length,
		done: required.filter((field) => !failing.has(field)).length,
	};
}

export function firstSectionWithProblems(statuses: SectionStatus[]): FormSection | undefined {
	return statuses.find((status) => status.state === "error")?.section;
}

// The line that sums up how much of the form is done.
export function progressText(progress: { done: number; total: number }): string {
	if (progress.total === 0) return "No required fields";
	if (progress.done === progress.total) return "All required fields done";
	return `${progress.done} of ${progress.total} required field${progress.total === 1 ? "" : "s"}`;
}
