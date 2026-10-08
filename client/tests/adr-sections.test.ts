import { describe, expect, it } from "vitest";
import {
	SECTIONS,
	firstSectionWithProblems,
	groupIssues,
	requiredProgress,
	sectionOf,
	sectionStatuses,
	progressText,
} from "../app/utils/adr-sections";
import { adrFormSchema, emptyFormState, sampleFormState } from "../app/utils/adr-form";

const INSTITUTION = "8ade772c-0808-4681-a22c-34f99cb742e5";

const issuesOf = (state: object) => adrFormSchema.safeParse(state).error?.issues ?? [];
const byId = (statuses: ReturnType<typeof sectionStatuses>) =>
	Object.fromEntries(statuses.map((s) => [s.section.id, s.state]));

const complete = () => ({
	...sampleFormState(),
	medical_institution_id: INSTITUTION,
});

describe("which section a field belongs to", () => {
	it("knows every field the schema can complain about", () => {
		const everyField = Object.keys(adrFormSchema.shape);
		const covered = SECTIONS.flatMap((s) => s.fields);

		expect(everyField.filter((field) => !covered.includes(field))).toEqual([]);
	});

	it("maps nested paths by their first part", () => {
		expect(sectionOf(["medicines", 2, "dose_amount"])?.id).toBe("medicines");
		expect(sectionOf(["patient_name"])?.id).toBe("patient-details");
		expect(sectionOf(["is_serious"])?.id).toBe("grading");
	});

	it("returns nothing for an unknown field", () => {
		expect(sectionOf(["nope"])).toBeUndefined();
		expect(sectionOf([])).toBeUndefined();
	});

	it("groups issues by section", () => {
		const grouped = groupIssues([
			{ path: ["patient_name"] },
			{ path: ["patient_gender"] },
			{ path: ["is_serious"] },
		]);

		expect(grouped.get("patient-details")).toHaveLength(2);
		expect(grouped.get("grading")).toHaveLength(1);
		expect(grouped.has("medicines")).toBe(false);
	});
});

describe("section status", () => {
	it("a blank form needs attention where something is required, and nowhere else", () => {
		const blank = emptyFormState();
		const statuses = sectionStatuses(blank, issuesOf(blank), false);

		expect(byId(statuses)).toEqual({
			"institution-details": "incomplete",
			"patient-details": "incomplete",
			"suspected-adverse-reaction": "optional",
			medicines: "optional",
			rechallenge: "optional",
			grading: "incomplete",
		});
	});

	it("a finished form has every section complete", () => {
		const form = complete();
		const statuses = sectionStatuses(form, issuesOf(form), false);

		expect(statuses.every((s) => s.state === "complete")).toBe(true);
	});

	it("does not scold about a problem in an optional field before the first save", () => {
		const form = { ...complete(), description_of_reaction: "too short" };

		const before = byId(sectionStatuses(form, issuesOf(form), false));
		const after = byId(sectionStatuses(form, issuesOf(form), true));

		expect(before["suspected-adverse-reaction"]).toBe("complete");
		expect(after["suspected-adverse-reaction"]).toBe("error");
	});

	it("after a failed save, marks the sections with problems as errors", () => {
		const blank = emptyFormState();
		const statuses = sectionStatuses(blank, issuesOf(blank), true);

		expect(byId(statuses)["patient-details"]).toBe("error");
		expect(byId(statuses)["grading"]).toBe("error");
		expect(byId(statuses)["medicines"]).toBe("optional"); // nothing wrong there
		expect(statuses.find((s) => s.section.id === "patient-details")!.problems).toBeGreaterThan(0);
	});

	it("clears the error as soon as the field is fixed", () => {
		const form = { ...complete(), is_serious: undefined };
		expect(byId(sectionStatuses(form, issuesOf(form), true))["grading"]).toBe("error");

		const fixed = { ...form, is_serious: "no" };
		expect(byId(sectionStatuses(fixed, issuesOf(fixed), true))["grading"]).toBe("complete");
	});

	it("marks an optional section complete once something is entered in it", () => {
		const form = emptyFormState();
		form.medicines![0]!.suspected = true;

		expect(byId(sectionStatuses(form, [], false))["medicines"]).toBe("complete");
	});

	it("counts problems found by a custom check, such as a missing date of birth", () => {
		const form = complete();
		const issues = [{ path: ["patient_date_of_birth"] }];

		const status = sectionStatuses(form, issues, true).find((s) => s.section.id === "patient-details")!;
		expect(status.state).toBe("error");
		expect(status.problems).toBe(1);
	});
});

describe("required progress", () => {
	it("counts the required fields that are in order", () => {
		const blank = emptyFormState();
		expect(requiredProgress(issuesOf(blank))).toEqual({ done: 0, total: 7 });

		const form = complete();
		expect(requiredProgress(issuesOf(form))).toEqual({ done: 7, total: 7 });
	});

	it("moves one field at a time", () => {
		const form = { ...complete(), known_allergy: undefined, is_serious: undefined };

		expect(requiredProgress(issuesOf(form))).toEqual({ done: 5, total: 7 });
	});

	it("counts a field with an invalid value as not done", () => {
		const form = { ...complete(), patient_name: "ab" };

		expect(requiredProgress(issuesOf(form)).done).toBe(6);
	});
});

describe("first section with problems", () => {
	it("is the first in form order", () => {
		const blank = emptyFormState();
		const statuses = sectionStatuses(blank, issuesOf(blank), true);

		expect(firstSectionWithProblems(statuses)?.id).toBe("institution-details");
	});

	it("is nothing when there are no errors", () => {
		const form = complete();
		expect(firstSectionWithProblems(sectionStatuses(form, [], true))).toBeUndefined();
	});
});

describe("progressText", () => {
	it("counts the required fields done", () => {
		expect(progressText({ done: 1, total: 4 })).toBe("1 of 4 required fields");
	});

	it("says when all are done, and when there is nothing to fill", () => {
		expect(progressText({ done: 4, total: 4 })).toBe("All required fields done");
		expect(progressText({ done: 0, total: 0 })).toBe("No required fields");
	});

	it("uses the singular for one field", () => {
		expect(progressText({ done: 0, total: 1 })).toBe("0 of 1 required field");
	});
});
