import { describe, expect, it } from "vitest";
import {
	SCOPE_DOES,
	SCOPE_DOES_NOT,
	SCOPE_HEADING,
	SCOPE_ID,
	SCOPE_MODEL,
	SCOPE_PURPOSE,
} from "../app/utils/about-scope";

const allSentences = (texts: string[]): string[] => texts.flatMap((text) => text.split(/(?<=[.!?])\s+/));

describe("the scope", () => {
	it("has an anchor and a heading", () => {
		expect(SCOPE_ID).toBe("scope");
		expect(SCOPE_HEADING).toBe("What MediLinda does, and what it does not do");
	});

	it("says what the project is for: causality assessment in pharmacovigilance", () => {
		expect(SCOPE_PURPOSE).toContain("fourth-year project");
		expect(SCOPE_PURPOSE).toContain("causality assessment");
		expect(SCOPE_PURPOSE).toContain("pharmacovigilance");
	});

	it("lists what the project does, in the words of the project", () => {
		const text = SCOPE_DOES.join(" ");

		for (const word of ["causality assessment", "review", "alert", "facility"]) expect(text, word).toContain(word);
	});

	it("says it does not manage what happens after the alert", () => {
		const text = SCOPE_DOES_NOT.join(" ");

		expect(text).toContain("after an alert reaches a facility");
		expect(text).toContain("does not track");
		expect(text).toContain("regulatory action");
		expect(text).toContain("clinical decisions");
	});

	it("names the four medicines and the four predicted levels", () => {
		const text = SCOPE_MODEL.join(" ");

		for (const word of ["rifampicin", "isoniazid", "pyrazinamide", "ethambutol", "certain", "likely", "possible", "unlikely"]) {
			expect(text, word).toContain(word);
		}
	});

	it("does not promise a feature the app does not have", () => {
		const text = [...SCOPE_DOES, ...SCOPE_DOES_NOT, ...SCOPE_MODEL, SCOPE_PURPOSE].join(" ").toLowerCase();

		expect(text).not.toContain("real-time");
		expect(text).not.toContain("replies are");
	});

	it("uses short sentences, as the project style asks", () => {
		const sentences = allSentences([SCOPE_PURPOSE, ...SCOPE_DOES, ...SCOPE_DOES_NOT, ...SCOPE_MODEL]);

		for (const sentence of sentences) expect(sentence.split(/\s+/).length, sentence).toBeLessThanOrEqual(28);
	});
});
