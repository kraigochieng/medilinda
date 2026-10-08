// Turns audit entries into the items shown on an ADR's History tab.
import type { AuditEvent } from "~/types/audit";
import { formatDateTime } from "~/utils/adr-table";

export type EventColor = "neutral" | "success" | "warning" | "error" | "info";

export interface ChangeView {
	label: string;
	old: string;
	new: string;
}

export interface EventView {
	id: string;
	icon: string;
	color: EventColor;
	title: string;
	actor: string;
	at: string;
	version?: number;
	note?: string;
	changes: ChangeView[];
}

const FIELD_LABELS: Record<string, string> = {
	is_serious: "Serious",
	medical_institution_id: "Medical institution",
	ward_or_clinic: "Ward or clinic",
	patient_weight_kg: "Weight (kg)",
	patient_height_cm: "Height (cm)",
	patient_date_of_birth: "Date of birth",
	inpatient_or_outpatient_number: "Inpatient/outpatient number",
	criteria_for_seriousness: "Criteria for seriousness",
	date_of_onset_of_reaction: "Date of onset of reaction",
	description_of_reaction: "Description of reaction",
};

export function humanizeField(field: string): string {
	if (FIELD_LABELS[field]) return FIELD_LABELS[field];

	const words = field
		.replace(/_batch_no$/, "_batch_number")
		.replace(/_/g, " ")
		.trim();

	return words.charAt(0).toUpperCase() + words.slice(1);
}

const LONG_TEXT = 120;
const ISO_DATETIME = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/;

export function formatValue(value: unknown): string {
	if (value === null || value === undefined || value === "") return "(empty)";
	if (typeof value === "boolean") return value ? "Yes" : "No";
	if (typeof value === "number") return String(value);

	const text = String(value);
	if (ISO_DATETIME.test(text)) return formatDateTime(text);

	return text.length > LONG_TEXT ? `${text.slice(0, LONG_TEXT)}…` : text;
}

const capitalize = (text: string) => text.charAt(0).toUpperCase() + text.slice(1);

export function actorName(event: AuditEvent): string {
	const name = event.actor_username;
	if (!name || name.startsWith("system")) return "System";
	return name;
}

// "patient name, age and 2 more fields"
function listFields(labels: string[]): string {
	const names = labels.map((l) => l.toLowerCase());
	if (names.length <= 3) {
		return names.length > 1
			? `${names.slice(0, -1).join(", ")} and ${names.at(-1)}`
			: (names[0] ?? "the report");
	}
	const rest = names.length - 2;
	return `${names.slice(0, 2).join(", ")} and ${rest} more fields`;
}

// Rows written because an ADR was deleted or restored (its assessments,
// reviews...). The ADR's own entry already says it, so they are hidden.
function cascadeGroups(events: AuditEvent[]): Set<string> {
	return new Set(
		events
			.filter((e) => e.entity_type === "adr" && ["delete", "restore"].includes(e.action))
			.map((e) => e.group_id),
	);
}

function describe(event: AuditEvent, editedGroups: Set<string>): Omit<EventView, "id" | "actor" | "at"> {
	const summary = event.summary ?? {};
	const changes: ChangeView[] = (event.changes ?? []).map((c) => ({
		label: humanizeField(c.field),
		old: formatValue(c.old),
		new: formatValue(c.new),
	}));

	switch (`${event.entity_type}:${event.action}`) {
		case "adr:create":
			return event.actor_username?.startsWith("system")
				? {
						icon: "i-lucide-archive",
						color: "neutral",
						title: "This record existed before history started",
						version: event.version,
						changes,
					}
				: { icon: "i-lucide-file-plus", color: "success", title: "Report created", version: event.version, changes };
		case "adr:update":
			return {
				icon: "i-lucide-pencil",
				color: "info",
				title: `Edited ${listFields(changes.map((c) => c.label))}`,
				version: event.version,
				changes,
			};
		case "adr:delete":
			return { icon: "i-lucide-trash-2", color: "error", title: "Deleted", version: event.version, changes };
		case "adr:restore":
			return { icon: "i-lucide-rotate-ccw", color: "success", title: "Restored", version: event.version, changes };

		case "causality_assessment_level:create":
		case "causality_assessment_level:restore": {
			const level = capitalize(String(summary.causality_assessment_level_value ?? "unknown"));
			return editedGroups.has(event.group_id)
				? {
						icon: "i-lucide-scale",
						color: "warning",
						title: `Re-assessed as ${level} after an edit`,
						note: "Earlier reviews stay with the previous assessment. This one needs a new review.",
						changes,
					}
				: { icon: "i-lucide-scale", color: "info", title: `Causality assessed as ${level}`, changes };
		}

		case "review:create":
		case "review:restore": {
			const approved = summary.approved === true;
			const proposed = summary.proposed_causality_level
				? `Proposed level: ${capitalize(String(summary.proposed_causality_level))}. `
				: "";
			const reason = summary.reason ? `Reason: ${summary.reason}` : "";
			return {
				icon: approved ? "i-lucide-circle-check" : "i-lucide-circle-x",
				color: approved ? "success" : "warning",
				title: approved ? "Approved the assessment" : "Did not approve the assessment",
				note: `${proposed}${reason}`.trim() || undefined,
				changes,
			};
		}
		case "review:update":
			return { icon: "i-lucide-pencil", color: "info", title: "Changed a review", changes };
		case "review:delete":
			return { icon: "i-lucide-trash-2", color: "neutral", title: "Removed a review", changes };

		case "sms_message:create": {
			const type = summary.sms_type ? ` (${summary.sms_type})` : "";
			const status = summary.status ? `: ${String(summary.status).toLowerCase()}` : "";
			return { icon: "i-lucide-message-square", color: "neutral", title: `SMS sent${type}${status}`, changes };
		}
		case "sms_message:update":
			// Unlinked from the ADR when it was deleted, relinked when restored.
			return { icon: "i-lucide-link", color: "neutral", title: "SMS link updated", changes };
	}

	return {
		icon: "i-lucide-circle-dot",
		color: "neutral",
		title: `${capitalize(event.action)} ${event.entity_type.replace(/_/g, " ")}`,
		changes,
	};
}

// `events` come newest first, as the server returns them.
export function describeEvents(events: AuditEvent[]): EventView[] {
	const cascade = cascadeGroups(events);
	// A new assessment written in the same request as an edit is a re-assessment.
	const editedGroups = new Set(
		events.filter((e) => e.entity_type === "adr" && e.action === "update").map((e) => e.group_id),
	);

	return events
		.filter(
			(e) =>
				!(
					cascade.has(e.group_id) &&
					e.entity_type !== "adr" &&
					!(e.entity_type === "causality_assessment_level" && e.action === "create" && editedGroups.has(e.group_id))
				),
		)
		.map((event) => ({
			id: event.id,
			actor: actorName(event),
			at: event.at,
			...describe(event, editedGroups),
		}));
}
