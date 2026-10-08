import { describe, expect, it } from "vitest";
import {
	EXPLAINED_LEVELS,
	describeFeature,
	effectText,
	factorsFor,
	headline,
	levelScores,
} from "../app/utils/explanation";

describe("levelScores", () => {
	// certain, likely, possible, unlikely
	const base = [0.04, 0.52, 0.24, 0.2];
	const final = [0.1, 0.6, 0.25, 0.05];

	it("gives each level a chance in percent, the highest first", () => {
		const scores = levelScores(base, final);

		expect(scores.map((s) => [s.level, s.chance])).toEqual([
			["likely", 60],
			["possible", 25],
			["certain", 10],
			["unlikely", 5],
		]);
	});

	it("keeps the starting chance and the change the report made", () => {
		const likely = levelScores(base, final).find((s) => s.level === "likely")!;

		expect(likely.start).toBe(52);
		expect(likely.change).toBe(8);
	});

	it("removes floating point noise", () => {
		const scores = levelScores([0, 0, 0, 0], [6.9e-18, 1, 0, -1e-17]);

		expect(scores.find((s) => s.level === "certain")!.chance).toBe(0);
		expect(scores.find((s) => s.level === "unlikely")!.chance).toBe(0);
	});

	it("is empty without data", () => {
		expect(levelScores(undefined, undefined)).toEqual([]);
		expect(levelScores([], [])).toEqual([]);
	});

	it("covers only the levels the model predicts", () => {
		expect(EXPLAINED_LEVELS).toEqual(["certain", "likely", "possible", "unlikely"]);
	});
});

describe("headline", () => {
	it("names the top level and its chance", () => {
		expect(headline(levelScores([0, 0, 0, 0], [0.1, 0.6, 0.25, 0.05]))).toBe(
			"The model gives Likely the highest chance: 60%.",
		);
	});

	it("says when two levels are level", () => {
		expect(headline(levelScores([0, 0, 0, 0], [0.4, 0.4, 0.1, 0.1]))).toBe(
			"The model could not choose between Certain and Likely: 40% each.",
		);
	});

	it("says nothing without data", () => {
		expect(headline([])).toBe("");
	});
});

describe("describeFeature", () => {
	it("shows a choice as its label", () => {
		expect(describeFeature("known_allergy", "no")).toEqual({ label: "Known allergy", value: "No" });
		expect(describeFeature("severity", "moderate")).toEqual({ label: "Severity", value: "Moderate" });
		expect(describeFeature("rifampicin_route", "IV")).toEqual({ label: "Rifampicin route", value: "IV" });
	});

	it("shows numbers with their units", () => {
		expect(describeFeature("patient_age", 29)).toEqual({ label: "Patient age", value: "29 yrs" });
		expect(describeFeature("patient_weight_kg", 67.2)).toEqual({ label: "Patient weight", value: "67.2 kg" });
		expect(describeFeature("patient_height_cm", 170.6)).toEqual({ label: "Patient height", value: "170.6 cm" });
		expect(describeFeature("rifampicin_dose_amount", 600)).toEqual({ label: "Rifampicin dose", value: "600 mg" });
		expect(describeFeature("isoniazid_frequency_number", 2)).toEqual({
			label: "Isoniazid doses a day",
			value: "2",
		});
	});

	it("shows a yes or no for a flag", () => {
		expect(describeFeature("rifampicin_suspected", true)).toEqual({ label: "Rifampicin suspected", value: "Yes" });
		expect(describeFeature("isoniazid_suspected", false)).toEqual({ label: "Isoniazid suspected", value: "No" });
	});

	it("shows a date as a day", () => {
		expect(describeFeature("date_of_onset_of_reaction", "2024-04-26")).toEqual({
			label: "Date of onset of reaction",
			value: "26 Apr 2024",
		});
	});

	it("shows a dash for a missing value", () => {
		expect(describeFeature("isoniazid_dose_amount", null)).toEqual({ label: "Isoniazid dose", value: "Not recorded" });
		expect(describeFeature("isoniazid_start_date", undefined).value).toBe("Not recorded");
	});

	it("cuts long text, and writes an unknown name in plain words", () => {
		const long = "x".repeat(80);

		expect(describeFeature("description_of_reaction", long).value.length).toBeLessThanOrEqual(41);
		expect(describeFeature("some_new_column", "a")).toEqual({ label: "Some new column", value: "a" });
	});
});

describe("effectText", () => {
	it("shows percentage points with a sign", () => {
		expect(effectText(0.123)).toBe("+12.3 points");
		expect(effectText(-0.04)).toBe("−4 points");
		expect(effectText(0.001)).toBe("+0.1 points");
	});
});

describe("factorsFor", () => {
	const names = ["known_allergy", "patient_age", "dechallenge", "severity"];
	const values = ["no", 29, "yes", "mild"];
	// rows are features, columns are the four levels
	const matrix = [
		[0.0, 0.08, -0.02, -0.06],
		[0.0, -0.1, 0.05, 0.05],
		[0.01, 0.2, -0.1, -0.11],
		[0.0, 0.0, 0.0, 0.0],
	];

	it("lists the factors of a level, the largest effect first", () => {
		const factors = factorsFor(1, names, values, matrix);

		expect(factors.map((f) => f.label)).toEqual(["Dechallenge", "Patient age", "Known allergy"]);
		expect(factors.map((f) => f.effect)).toEqual([0.2, -0.1, 0.08]);
	});

	it("says whether each factor pushed toward the level or away from it", () => {
		const factors = factorsFor(1, names, values, matrix);

		expect(factors.map((f) => f.direction)).toEqual(["toward", "away", "toward"]);
	});

	it("hides factors with no effect", () => {
		expect(factorsFor(1, names, values, matrix).some((f) => f.label === "Severity")).toBe(false);
	});

	it("gives each bar a length in proportion to the largest effect", () => {
		const factors = factorsFor(1, names, values, matrix);

		expect(factors.map((f) => f.share)).toEqual([1, 0.5, 0.4]);
	});

	it("reads the right column for each level", () => {
		const factors = factorsFor(2, names, values, matrix);

		expect(factors[0]).toMatchObject({ label: "Dechallenge", direction: "away" });
	});

	it("is empty when the data does not fit together", () => {
		expect(factorsFor(1, names, values.slice(1), matrix)).toEqual([]);
		expect(factorsFor(1, undefined, values, matrix)).toEqual([]);
		expect(factorsFor(9, names, values, matrix)).toEqual([]);
	});
});
