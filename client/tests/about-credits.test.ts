import { describe, expect, it } from "vitest";
import { CREDITS, CREDITS_HEADING } from "../app/utils/about-credits";

const paragraph = (id: string) => CREDITS.find((item) => item.id === id)!;

describe("the credits", () => {
	it("has a heading and the three paragraphs in this order", () => {
		expect(CREDITS_HEADING).toBe("About this project");
		expect(CREDITS.map((item) => item.id)).toEqual(["project", "data", "thanks"]);
	});

	it("says this is a fourth-year project", () => {
		expect(paragraph("project").before).toContain("fourth-year project");
		expect(paragraph("project").before).toContain("Computer Science");
	});

	it("names the data source, links it, and says the Board did not work on it", () => {
		const data = paragraph("data");

		expect(data.links.map((link) => link.label)).toEqual(["Pharmacy and Poisons Board"]);
		expect(data.after).toContain("did not work on MediLinda");
	});

	it("thanks both parties, each with a link", () => {
		const labels = paragraph("thanks").links.map((link) => link.label);

		expect(labels).toEqual(["IntelliSOFT Consulting Ltd", "Department of Computer Science, University of Nairobi"]);
	});

	it("links only with https addresses", () => {
		for (const link of CREDITS.flatMap((item) => item.links)) expect(link.to, link.label).toMatch(/^https:\/\//);
	});

	it("uses short sentences, as the project style asks", () => {
		for (const item of CREDITS) {
			const text = [item.before, ...item.links.map((link) => link.label), item.after].join(" ");
			for (const sentence of text.split(/(?<=[.!?])\s+/)) {
				expect(sentence.split(/\s+/).length, item.id + ": " + sentence).toBeLessThanOrEqual(28);
			}
		}
	});
});
