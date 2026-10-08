import { describe, expect, it } from "vitest";
import type { AuditEvent } from "../app/types/audit";
import {
	actorName,
	describeEvents,
	formatValue,
	humanizeField,
} from "../app/utils/audit-events";

let n = 0;
const event = (overrides: Partial<AuditEvent>): AuditEvent => ({
	id: `e${++n}`,
	group_id: "g1",
	entity_type: "adr",
	entity_id: "adr-1",
	root_type: "adr",
	root_id: "adr-1",
	action: "update",
	version: 2,
	actor_id: "u1",
	actor_username: "alice",
	at: "2025-03-04T09:05:00",
	changes: null,
	summary: null,
	...overrides,
});

describe("humanizeField", () => {
	it("turns column names into labels", () => {
		expect(humanizeField("patient_name")).toBe("Patient name");
		expect(humanizeField("rifampicin_dose_amount")).toBe("Rifampicin dose amount");
		expect(humanizeField("comments")).toBe("Comments");
	});

	it("uses clearer labels where the column name is unclear", () => {
		expect(humanizeField("is_serious")).toBe("Serious");
		expect(humanizeField("patient_weight_kg")).toBe("Weight (kg)");
		expect(humanizeField("inpatient_or_outpatient_number")).toBe("Inpatient/outpatient number");
		expect(humanizeField("isoniazid_batch_no")).toBe("Isoniazid batch number");
	});
});

describe("formatValue", () => {
	it("says so when a value is empty", () => {
		for (const empty of [null, undefined, ""]) {
			expect(formatValue(empty)).toBe("(empty)");
		}
	});

	it("shows booleans and numbers plainly, keeping zero and false", () => {
		expect(formatValue(true)).toBe("Yes");
		expect(formatValue(false)).toBe("No");
		expect(formatValue(0)).toBe("0");
		expect(formatValue(45)).toBe("45");
	});

	it("shortens long text", () => {
		const long = "x".repeat(300);
		expect(formatValue(long)).toHaveLength(121);
		expect(formatValue(long).endsWith("…")).toBe(true);
		expect(formatValue("short")).toBe("short");
	});

	it("formats times but leaves plain dates alone", () => {
		expect(formatValue("2025-10-15")).toBe("2025-10-15");
		expect(formatValue("2025-03-04T09:05:00")).toMatch(/2025/);
	});
});

describe("actorName", () => {
	it("shows the username, or System when there is none", () => {
		expect(actorName(event({ actor_username: "alice" }))).toBe("alice");
		expect(actorName(event({ actor_username: null }))).toBe("System");
		expect(actorName(event({ actor_username: "system (baseline)" }))).toBe("System");
	});
});

describe("describeEvents", () => {
	it("describes a new report and a baseline differently", () => {
		const [created, baseline] = describeEvents([
			event({ action: "create", version: 1 }),
			event({ action: "create", version: 1, actor_username: "system (baseline)", group_id: "g0" }),
		]);

		expect(created!.title).toBe("Report created");
		expect(baseline!.title).toBe("This record existed before history started");
		expect(baseline!.actor).toBe("System");
	});

	it("names what an edit changed and lists each old and new value", () => {
		const [view] = describeEvents([
			event({
				changes: [
					{ field: "patient_name", old: "Jane", new: "Janet" },
					{ field: "patient_age", old: 45, new: null },
				],
			}),
		]);

		expect(view!.title).toBe("Edited patient name and patient age");
		expect(view!.version).toBe(2);
		expect(view!.changes).toEqual([
			{ label: "Patient name", old: "Jane", new: "Janet" },
			{ label: "Patient age", old: "45", new: "(empty)" },
		]);
	});

	it("shortens the title of an edit that changed many fields", () => {
		const [view] = describeEvents([
			event({
				changes: ["a", "b", "c", "d", "e"].map((f) => ({ field: f, old: 1, new: 2 })),
			}),
		]);

		expect(view!.title).toBe("Edited a, b and 3 more fields");
		expect(view!.changes).toHaveLength(5);
	});

	it("labels the first assessment and a re-assessment after an edit differently", () => {
		const events = describeEvents([
			// Newest first: an edit and the new assessment from the same request, then the original.
			event({ id: "reassess", group_id: "edit", entity_type: "causality_assessment_level", action: "create", summary: { causality_assessment_level_value: "certain" } }),
			event({ id: "edit", group_id: "edit", action: "update", changes: [{ field: "patient_name", old: "a", new: "b" }] }),
			event({ id: "first", group_id: "create", entity_type: "causality_assessment_level", action: "create", summary: { causality_assessment_level_value: "likely" } }),
			event({ id: "created", group_id: "create", action: "create", version: 1 }),
		]);

		const byId = Object.fromEntries(events.map((e) => [e.id, e]));
		expect(byId.first!.title).toBe("Causality assessed as Likely");
		expect(byId.reassess!.title).toBe("Re-assessed as Certain after an edit");
		expect(byId.reassess!.note).toMatch(/needs a new review/);
	});

	it("describes reviews, with the proposed level and the reason", () => {
		const [approved, rejected] = describeEvents([
			event({ entity_type: "review", action: "create", summary: { approved: true } }),
			event({
				entity_type: "review",
				action: "create",
				group_id: "g2",
				summary: { approved: false, proposed_causality_level: "possible", reason: "Dechallenge unclear" },
			}),
		]);

		expect(approved!.title).toBe("Approved the assessment");
		expect(approved!.color).toBe("success");
		expect(rejected!.title).toBe("Did not approve the assessment");
		expect(rejected!.note).toBe("Proposed level: Possible. Reason: Dechallenge unclear");
	});

	it("shows an SMS", () => {
		const [view] = describeEvents([
			event({ entity_type: "sms_message", action: "create", summary: { sms_type: "individual alert", status: "Success" } }),
		]);

		expect(view!.title).toBe("SMS sent (individual alert): success");
	});

	it("shows a delete and a restore, and hides the rows they cascade to", () => {
		const events = describeEvents([
			event({ id: "restore", group_id: "r", action: "restore", version: 4 }),
			event({ id: "r-cal", group_id: "r", entity_type: "causality_assessment_level", action: "restore" }),
			event({ id: "r-review", group_id: "r", entity_type: "review", action: "restore", summary: { approved: true } }),
			event({ id: "delete", group_id: "d", action: "delete", version: 3 }),
			event({ id: "d-review", group_id: "d", entity_type: "review", action: "delete" }),
			event({ id: "d-sms", group_id: "d", entity_type: "sms_message", action: "update" }),
		]);

		expect(events.map((e) => e.id)).toEqual(["restore", "delete"]);
		expect(events[0]!.title).toBe("Restored");
		expect(events[1]!.title).toBe("Deleted");
	});

	it("keeps the new assessment of an edit even when it is in a group with a delete", () => {
		const events = describeEvents([
			event({ id: "cal", group_id: "x", entity_type: "causality_assessment_level", action: "create", summary: { causality_assessment_level_value: "likely" } }),
			event({ id: "edit", group_id: "x", action: "update", changes: [{ field: "comments", old: "a", new: "b" }] }),
			event({ id: "del", group_id: "x", action: "delete" }),
		]);

		expect(events.map((e) => e.id)).toContain("cal");
	});

	it("falls back to a plain description for entries it does not know", () => {
		const [view] = describeEvents([event({ entity_type: "medical_institution", action: "update" })]);

		expect(view!.title).toBe("Update medical institution");
	});

	it("returns nothing for no events", () => {
		expect(describeEvents([])).toEqual([]);
	});
});
