// What the ADR details view shows, worked out from a report. Kept apart from the
// components so the rules (dashes, dates, durations, the timeline) can be tested.
import type { ADRGetResponseInterface } from "~/types/adr";
import { adrFormCategoricalValues } from "~/values/adr";

export const NONE = "—";

type Blank = null | undefined;

export function show(value: string | number | boolean | Blank): string {
	if (value === null || value === undefined) return NONE;
	if (typeof value === "boolean") return value ? "Yes" : "No";
	const text = String(value).trim();
	return text === "" ? NONE : text;
}

// The label of the chosen option of a choice field: "moderate" -> "Moderate".
export function optionLabel(
	group: keyof typeof adrFormCategoricalValues,
	value: string | Blank,
): string {
	if (!value) return NONE;
	const option = adrFormCategoricalValues[group].find((o) => o.value === value);
	return option?.label ?? value;
}

const DAY = /^(\d{4})-(\d{2})-(\d{2})/;

// A calendar date as a number of days. No timezone is involved: a date the
// reporter wrote must not move to the day before for someone west of UTC.
function dayNumber(day: string | Blank): number | null {
	const match = day ? DAY.exec(day) : null;
	if (!match) return null;
	return Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3])) / 86_400_000;
}

export function formatDay(day: string | Blank): string {
	if (!day) return NONE;
	const number = dayNumber(day);
	if (number === null) return day;
	return new Intl.DateTimeFormat("en-GB", { dateStyle: "medium", timeZone: "UTC" }).format(
		new Date(number * 86_400_000),
	);
}

export function daysBetween(from: string | Blank, to: string | Blank): number | null {
	const start = dayNumber(from);
	const end = dayNumber(to);
	return start === null || end === null ? null : end - start;
}

export const MEDICINE_KEYS = ["rifampicin", "isoniazid", "pyrazinamide", "ethambutol"] as const;

export interface Medicine {
	key: (typeof MEDICINE_KEYS)[number];
	name: string;
	suspected: boolean;
	dose?: number | null;
	frequency?: number | null;
	route?: string | null;
	batch?: string | null;
	manufacturer?: string | null;
	start?: string | null;
	stop?: string | null;
	days: number | null; // days from the start to the stop
}

export function medicinesOf(adr: ADRGetResponseInterface): Medicine[] {
	const field = adr as unknown as Record<string, unknown>;

	return MEDICINE_KEYS.map((key) => {
		const start = field[`${key}_start_date`] as string | undefined;
		const stop = field[`${key}_stop_date`] as string | undefined;

		return {
			key,
			name: key[0]!.toUpperCase() + key.slice(1),
			suspected: field[`${key}_suspected`] === true,
			dose: field[`${key}_dose_amount`] as number | undefined,
			frequency: field[`${key}_frequency_number`] as number | undefined,
			route: field[`${key}_route`] as string | undefined,
			batch: field[`${key}_batch_no`] as string | undefined,
			manufacturer: field[`${key}_manufacturer`] as string | undefined,
			start,
			stop,
			days: daysBetween(start, stop),
		};
	});
}

export type TimelineKind = "start" | "onset" | "stop";

export interface TimelineEvent {
	kind: TimelineKind;
	date: string;
	title: string;
	label: string;
	note?: string;
}

const KIND_ORDER: Record<TimelineKind, number> = { start: 0, onset: 1, stop: 2 };

function plural(count: number, word: string) {
	return `${count} ${word}${count === 1 ? "" : "s"}`;
}

// Drug start, reaction onset and drug stop in the order they happened. The
// medicines judged are the suspected ones, or all with dates if none is marked.
export function timelineOf(adr: ADRGetResponseInterface): TimelineEvent[] {
	const medicines = medicinesOf(adr);
	const suspected = medicines.filter((m) => m.suspected);
	const judged = suspected.length ? suspected : medicines;

	const events: TimelineEvent[] = [];

	for (const medicine of judged) {
		if (dayNumber(medicine.start) !== null) {
			events.push({
				kind: "start",
				date: medicine.start!,
				title: "Medicine started",
				label: medicine.name,
			});
		}
		if (dayNumber(medicine.stop) !== null) {
			events.push({
				kind: "stop",
				date: medicine.stop!,
				title: "Medicine stopped",
				label: medicine.name,
			});
		}
	}

	if (dayNumber(adr.date_of_onset_of_reaction) !== null) {
		const starts = events.filter((e) => e.kind === "start").map((e) => e.date).sort();
		const gap = starts.length ? daysBetween(starts[0], adr.date_of_onset_of_reaction) : null;

		events.push({
			kind: "onset",
			date: adr.date_of_onset_of_reaction!,
			title: "Reaction began",
			label: "Onset of the reaction",
			note:
				gap === null
					? undefined
					: gap >= 0
						? `${plural(gap, "day")} after the first suspected medicine started`
						: `${plural(-gap, "day")} before the first suspected medicine started`,
		});
	}

	return events.sort(
		(a, b) =>
			(dayNumber(a.date)! - dayNumber(b.date)!) || KIND_ORDER[a.kind] - KIND_ORDER[b.kind],
	);
}

export interface SummaryItem {
	label: string;
	value: string;
}

// The facts to read first, shown above the sections.
export function summaryOf(adr: ADRGetResponseInterface): SummaryItem[] {
	const age = adr.patient_age != null ? `${adr.patient_age} yrs` : undefined;
	const gender = adr.patient_gender ? optionLabel("patientGender", adr.patient_gender) : undefined;
	const ageAndGender = [age, gender].filter(Boolean).join(", ");

	return [
		{ label: "Patient", value: show(adr.patient_name) },
		{ label: "Age and gender", value: ageAndGender || NONE },
		{ label: "Onset", value: formatDay(adr.date_of_onset_of_reaction) },
		{ label: "Severity", value: optionLabel("severity", adr.severity) },
		{ label: "Serious", value: optionLabel("isSerious", adr.is_serious) },
		{ label: "Outcome", value: optionLabel("outcome", adr.outcome) },
	];
}
