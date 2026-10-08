import { describe, expect, it } from "vitest";
import { phonesText, queueColumns } from "../app/utils/sms-table";

describe("phonesText", () => {
	it("joins the numbers with commas and spaces", () => {
		expect(phonesText(["0700000001", "0700000002"])).toBe("0700000001, 0700000002");
	});

	it("shows a dash when there is no number", () => {
		expect(phonesText([])).toBe("—");
		expect(phonesText(undefined)).toBe("—");
		expect(phonesText(["", "  "])).toBe("—");
	});

	it("leaves out blank entries", () => {
		expect(phonesText(["0700000001", ""])).toBe("0700000001");
	});
});

describe("queueColumns", () => {
	it("has the same columns for both queues, and a count of messages only for the sent one", () => {
		const waiting = queueColumns(false).map((c) => c.key);
		const sent = queueColumns(true).map((c) => c.key);

		expect(waiting).toEqual(["patient_name", "medical_institution_name", "medical_institution_mfl_code", "telephones", "created_at"]);
		expect(sent).toEqual([...waiting, "sms_count"]);
	});

	it("uses sentence case headers", () => {
		expect(queueColumns(true).map((c) => c.header)).toEqual([
			"Patient",
			"Institution",
			"MFL code",
			"Telephones",
			"Reported",
			"Messages sent",
		]);
	});
});
