import { existsSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { STORY } from "../app/utils/about-story";
import { CAUSALITY_LEVELS } from "../app/utils/causality-levels";

const PAGES = join(__dirname, "../app/pages");

// A page exists when a file or an index file matches its address.
function pageExists(address: string): boolean {
	const path = address.split("?")[0]!.replace(/^\//, "");
	const files = path === "" ? ["index.vue"] : [`${path}.vue`, `${path}/index.vue`];
	return files.some((file) => existsSync(join(PAGES, file)));
}

describe("the story", () => {
	it("goes from the suspected case to the record, in this order", () => {
		expect(STORY.map((step) => step.id)).toEqual(["suspect", "report", "predict", "review", "communicate", "learn"]);
	});

	it("gives every stage a title, a story and a date label", () => {
		for (const step of STORY) {
			expect(step.title.length, step.id).toBeGreaterThan(3);
			expect(step.story.length, step.id).toBeGreaterThan(40);
			expect(step.stage, step.id).toMatch(/^Step \d$/);
		}
	});

	it("links only to pages that exist", () => {
		const links = STORY.flatMap((step) => step.where.map((place) => place.to));

		expect(links.length).toBeGreaterThan(5);
		for (const link of links) expect(pageExists(link), link).toBe(true);
	});

	it("names each page it links to", () => {
		for (const place of STORY.flatMap((step) => step.where)) {
			expect(place.label.length, place.to).toBeGreaterThan(2);
			expect(place.note.length, place.to).toBeGreaterThan(10);
		}
	});

	it("defines the terms of the project once each", () => {
		const terms = STORY.flatMap((step) => step.definitions.map((d) => d.term));

		expect(new Set(terms).size).toBe(terms.length);
		for (const term of ["ADR", "Pharmacovigilance", "Dechallenge", "Rechallenge", "Causality assessment", "SHAP", "Approved"]) {
			expect(terms, term).toContain(term);
		}
	});

	it("lists the six levels from the shared descriptions, so the story cannot drift", () => {
		const step = STORY.find((s) => s.id === "predict")!;

		expect(step.levels).toEqual(CAUSALITY_LEVELS.map((l) => l.value));
	});

	it("uses short sentences, as the project style asks", () => {
		for (const step of STORY) {
			for (const sentence of step.story.split(/(?<=[.!?])\s+/)) {
				expect(sentence.split(/\s+/).length, `${step.id}: ${sentence}`).toBeLessThanOrEqual(28);
			}
		}
	});
});
