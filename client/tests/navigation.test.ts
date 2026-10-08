import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const ROOT = join(__dirname, "..");
const read = (file: string) => readFileSync(join(ROOT, file), "utf8");

// Pages that were folded into the ADR page, and where their old addresses go.
const REMOVED = ["/review", "/causality-assessment-level", "/monitoring"];

describe("navigation", () => {
	const layout = read("app/layouts/default.vue");

	it("has one ADRs link, with no add or recently deleted links beside it", () => {
		expect(layout).toMatch(/label: "ADRs"[^}]*to: "\/adr"/);
		expect(layout).not.toMatch(/to: "\/adr\/(add|deleted)"/);
		expect(layout).not.toMatch(/label: "(View ADRs|Add ADR|Recently deleted)"/);
	});

	it("does not link to the removed pages", () => {
		for (const path of REMOVED) {
			expect(layout, path).not.toContain(`to: "${path}"`);
		}
	});

	it("leaves no page files at the removed addresses", () => {
		for (const path of REMOVED) {
			expect(existsSync(join(ROOT, "app/pages", path)), path).toBe(false);
		}
	});

	it("sends the old addresses, and everything under them, to the list or the dashboard", () => {
		const config = read("nuxt.config.ts");

		for (const path of REMOVED) {
			expect(config, path).toContain(`"${path}": { redirect`);
			expect(config, `${path}/**`).toContain(`"${path}/**": { redirect`);
		}
	});
});
