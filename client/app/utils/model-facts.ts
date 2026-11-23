// The facts about the data that the model learned from. One place, so the About page and the
// Prediction tab say the same numbers. Keep it in step with docs/synthetic-data-report.md.

export const MODEL_FACTS = {
	rows: 30_000, // the generated reports (issue #164)
	medicines: 4, // rifampicin, isoniazid, pyrazinamide, ethambutol
	aboutAddress: "/about#scope",
} as const;

// A count with a comma between the thousands, for example 30,000.
export function formatCount(value: number): string {
	return value.toLocaleString("en-US");
}

// The line on the Prediction tab: what the model learned from, and where to read the limits.
export function predictionTabNote(): { text: string; linkLabel: string; to: string } {
	return {
		text: `This model learned from ${formatCount(MODEL_FACTS.rows)} synthetic reports about ${MODEL_FACTS.medicines} TB medicines. The reports are not real patients.`,
		linkLabel: "Read what this means",
		to: MODEL_FACTS.aboutAddress,
	};
}
