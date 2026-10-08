// What the Prediction tab shows, worked out from the model's explanation (SHAP values).
// Kept apart from the components so the rules can be tested.
import { NONE, formatDay, optionLabel } from "~/utils/adr-view";
import type { adrFormCategoricalValues } from "~/values/adr";

// The model predicts these four levels, in this order. Its columns follow the same order.
export const EXPLAINED_LEVELS = ["certain", "likely", "possible", "unlikely"] as const;
export type ExplainedLevel = (typeof EXPLAINED_LEVELS)[number];

const round1 = (n: number) => Math.round(n * 10) / 10;
// Remove -0 and noise such as 6.9e-18.
const clean = (n: number) => (Math.abs(n) < 0.05 ? 0 : n);

export interface LevelScore {
	level: ExplainedLevel;
	chance: number; // percent, after the report
	start: number; // percent, before the report: what the model expects for any report
	change: number; // percentage points the report added or removed
}

export function levelScores(
	baseValues: number[] | undefined,
	finalValues: number[] | undefined,
): LevelScore[] {
	if (!baseValues?.length || !finalValues?.length) return [];

	return EXPLAINED_LEVELS.map((level, index) => {
		const chance = Math.max(0, clean(round1((finalValues[index] ?? 0) * 100)));
		const start = Math.max(0, clean(round1((baseValues[index] ?? 0) * 100)));
		return { level, chance, start, change: clean(round1(chance - start)) };
	}).sort((a, b) => b.chance - a.chance); // a stable sort: ties keep the level order
}

const capital = (text: string) => text.charAt(0).toUpperCase() + text.slice(1);
const percent = (n: number) => `${n}%`;

export function headline(scores: LevelScore[]): string {
	const [top, second] = scores;
	if (!top) return "";
	if (second && second.chance === top.chance) {
		return `The model could not choose between ${capital(top.level)} and ${capital(second.level)}: ${percent(top.chance)} each.`;
	}
	return `The model gives ${capital(top.level)} the highest chance: ${percent(top.chance)}.`;
}

// --- Factors -------------------------------------------------------------------------

type Group = keyof typeof adrFormCategoricalValues;

const CHOICE_FIELDS: Record<string, Group> = {
	patient_gender: "patientGender",
	known_allergy: "knownAllergy",
	pregnancy_status: "pregnancyStatus",
	rechallenge: "rechallenge",
	dechallenge: "dechallenge",
	severity: "severity",
	is_serious: "isSerious",
	criteria_for_seriousness: "criteriaForSeriousness",
	action_taken: "actionTaken",
	outcome: "outcome",
};

const MAX_TEXT = 40;

function labelOf(name: string): string {
	const medicine = /^(rifampicin|isoniazid|pyrazinamide|ethambutol)_(.+)$/.exec(name);
	if (medicine) {
		const drug = capital(medicine[1]!);
		const part = medicine[2]!;
		if (part === "dose_amount") return `${drug} dose`;
		if (part === "frequency_number") return `${drug} doses a day`;
		if (part === "batch_no") return `${drug} batch number`;
		return `${drug} ${part.replace(/_/g, " ")}`;
	}
	if (name === "patient_weight_kg") return "Patient weight";
	if (name === "patient_height_cm") return "Patient height";
	return capital(name.replace(/_/g, " "));
}

function valueOf(name: string, value: unknown): string {
	if (value === null || value === undefined || value === "") return "Not recorded";
	if (typeof value === "boolean") return value ? "Yes" : "No";

	if (typeof value === "number") {
		if (name === "patient_age") return `${value} yrs`;
		if (name === "patient_weight_kg") return `${value} kg`;
		if (name === "patient_height_cm") return `${value} cm`;
		if (name.endsWith("_dose_amount")) return `${value} mg`;
		return String(value);
	}

	const text = String(value);
	const group = CHOICE_FIELDS[name] ?? (name.endsWith("_route") ? "route" : undefined);
	if (group) return optionLabel(group, text);

	if (/(_date$|^date_of_|_date_of_|^created_at$)/.test(name)) {
		const day = formatDay(text);
		return day === NONE ? "Not recorded" : day;
	}

	return text.length > MAX_TEXT ? `${text.slice(0, MAX_TEXT)}…` : text;
}

export function describeFeature(name: string, value: unknown): { label: string; value: string } {
	return { label: labelOf(name), value: valueOf(name, value) };
}

export interface Factor {
	name: string;
	label: string;
	value: string;
	effect: number; // the share of the chance (0.1 is 10 percentage points)
	direction: "toward" | "away";
	share: number; // 0 to 1: the size of the effect next to the largest one
}

const MIN_EFFECT = 0.0005;

// The facts of the report that moved the chance of one level, the largest effect first.
// The matrix has one row for each feature and one column for each level.
export function factorsFor(
	levelIndex: number,
	names: string[] | undefined,
	values: unknown[] | undefined,
	matrix: number[][] | undefined,
): Factor[] {
	if (!names || !values || !matrix) return [];
	if (names.length !== values.length || names.length !== matrix.length) return [];
	if (!Number.isInteger(levelIndex) || levelIndex < 0) return [];
	if (matrix.some((row) => !Array.isArray(row) || row.length <= levelIndex)) return [];

	const raw = names
		.map((name, i) => ({ name, value: values[i], effect: matrix[i]![levelIndex]! }))
		.filter((f) => Number.isFinite(f.effect) && Math.abs(f.effect) >= MIN_EFFECT)
		.sort((a, b) => Math.abs(b.effect) - Math.abs(a.effect));

	const largest = raw[0] ? Math.abs(raw[0].effect) : 1;

	return raw.map((f) => ({
		name: f.name,
		...describeFeature(f.name, f.value),
		effect: f.effect,
		direction: f.effect > 0 ? "toward" : "away",
		share: Math.round((Math.abs(f.effect) / largest) * 100) / 100,
	}));
}

// "+12.3 points" or "−4 points": percentage points of chance.
export function effectText(effect: number): string {
	const points = round1(Math.abs(effect) * 100);
	const sign = effect < 0 ? "−" : "+";
	return `${sign}${points} point${points === 1 ? "" : "s"}`;
}
