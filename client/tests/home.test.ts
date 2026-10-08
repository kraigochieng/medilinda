import { describe, expect, it } from "vitest";
import { greeting, homeCards } from "../app/utils/home";

describe("homeCards", () => {
	const cards = homeCards({ all: 120, needsReview: 7, notApproved: 3 });

	it("has the three counts in order", () => {
		expect(cards.map((c) => [c.key, c.value])).toEqual([
			["all", 120],
			["needs_review", 7],
			["not_approved", 3],
		]);
	});

	it("links each count to the list with the matching filter", () => {
		expect(cards.map((c) => c.to)).toEqual(["/adr", "/adr?review=needs_review", "/adr?review=not_approved"]);
	});

	it("keeps a count that is not known yet as undefined, not zero", () => {
		const unknown = homeCards({});

		expect(unknown.map((c) => c.value)).toEqual([undefined, undefined, undefined]);
	});
});

describe("greeting", () => {
	it("uses the first name", () => {
		expect(greeting({ first_name: "Jane", last_name: "Doe" }, 9)).toBe("Good morning, Jane");
	});

	it("follows the hour", () => {
		expect(greeting({ first_name: "Jane" }, 13)).toBe("Good afternoon, Jane");
		expect(greeting({ first_name: "Jane" }, 19)).toBe("Good evening, Jane");
		expect(greeting({ first_name: "Jane" }, 3)).toBe("Good evening, Jane");
	});

	it("has no name when none is known", () => {
		expect(greeting(undefined, 9)).toBe("Good morning");
		expect(greeting({ first_name: "  " }, 9)).toBe("Good morning");
	});
});
