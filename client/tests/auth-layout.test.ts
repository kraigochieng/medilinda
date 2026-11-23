import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { ABOUT_PATH } from "../app/utils/route-access";

const layout = readFileSync(join(__dirname, "../app/layouts/auth.vue"), "utf8");

describe("the auth layout", () => {
	it("points to the About page, which opens without a sign-in", () => {
		expect(ABOUT_PATH).toBe("/about");
	});

	it("links the logo to that page", () => {
		expect(layout).toMatch(/<NuxtLink :to="aboutPath"[^>]*><Logo \/><\/NuxtLink>/);
		expect(layout).toContain("ABOUT_PATH");
	});
});
