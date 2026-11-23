import { describe, expect, it } from "vitest";
import { MODEL_FACTS, formatCount, predictionTabNote } from "../app/utils/model-facts";
import { SCOPE_ID } from "../app/utils/about-scope";

describe("model facts", () => {
	it("formats a count with a comma", () => {
		expect(formatCount(30000)).toBe("30,000");
		expect(formatCount(999)).toBe("999");
	});

	it("writes the line of the Prediction tab from the facts", () => {
		const note = predictionTabNote();

		expect(note.text).toContain("30,000 synthetic reports");
		expect(note.text).toContain("4 TB medicines");
		expect(note.text).toContain("not real patients");
	});

	it("links to the scope section of the About page", () => {
		expect(MODEL_FACTS.aboutAddress).toBe(`/about#${SCOPE_ID}`);
		expect(predictionTabNote().to).toBe(MODEL_FACTS.aboutAddress);
	});

	it("uses short sentences", () => {
		for (const sentence of predictionTabNote().text.split(/(?<=[.!?])\s+/)) {
			expect(sentence.split(/\s+/).length, sentence).toBeLessThanOrEqual(28);
		}
	});
});
