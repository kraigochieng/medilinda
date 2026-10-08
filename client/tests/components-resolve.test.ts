// A template that uses a component that does not exist does not fail: Vue only
// warns in the console and renders an empty unknown element, so the page just
// looks blank. This test finds those, starting from every page and layout and
// following the components they really use.
import { readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join, relative, sep } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const CLIENT = join(dirname(fileURLToPath(import.meta.url)), "..");
const APP = join(CLIENT, "app");

const walk = (dir: string): string[] =>
	readdirSync(dir).flatMap((name) => {
		const path = join(dir, name);
		return statSync(path).isDirectory() ? walk(path) : [path];
	});

const pascal = (text: string) => text.replace(/(^|[-_ ])(\w)/g, (_, __, c) => c.toUpperCase());

// How Nuxt names the components in app/components: the folders are a prefix,
// unless the file name already starts with it (components/form/ADR.vue is FormADR).
function localComponents(): Map<string, string> {
	const components = new Map<string, string>();
	const base = join(APP, "components");

	for (const file of walk(base).filter((f) => f.endsWith(".vue"))) {
		const parts = relative(base, file).replace(/\.vue$/, "").split(sep).map(pascal);
		const name = parts.pop()!;
		const prefix = parts.join("");
		components.set(name.toLowerCase().startsWith(prefix.toLowerCase()) ? name : prefix + name, file);
	}
	return components;
}

const nuxtUi = new Set(
	readdirSync(join(CLIENT, "node_modules/@nuxt/ui/dist/runtime/components"))
		.filter((name) => /^[A-Z].*\.vue$/.test(name))
		.map((name) => `U${name.replace(".vue", "")}`),
);

// Provided by Nuxt, Vue and the modules in nuxt.config.ts.
const provided = new Set([
	"NuxtPage", "NuxtLayout", "NuxtLink", "NuxtLoadingIndicator", "NuxtRouteAnnouncer", "ClientOnly",
	"Icon", "NuxtIcon", "Teleport", "Transition", "TransitionGroup", "KeepAlive", "Suspense",
	// nuxt-charts
	"AreaChart", "AreaStackedChart", "LineChart", "BarChart", "DonutChart", "BubbleChart",
	// vue3-apexcharts (plugins/apexcharts.client.ts)
	"ApexChart",
]);

function templateOf(source: string): string {
	source = source.replace(/<!--[\s\S]*?-->/g, ""); // commented-out code is not used
	const match = source.match(/<template>([\s\S]*)<\/template>\s*(?:<script|<style|$)/);
	return (match?.[1] ?? source.split("<script")[0] ?? "").replace(/<!--[\s\S]*?-->/g, "");
}

function usedComponents(source: string): string[] {
	const tags = [...templateOf(source).matchAll(/<([A-Z][A-Za-z0-9]*)[\s/>]/g)].map((m) => m[1]!);
	const resolved = [...source.matchAll(/resolveComponent\(["']([A-Za-z0-9]+)["']\)/g)].map((m) => m[1]!);
	return [...new Set([...tags, ...resolved])];
}

// Walks from the pages, layouts and app.vue through the components they use.
export function unresolvedComponents(): Record<string, string[]> {
	const local = localComponents();
	const entries = [
		join(APP, "app.vue"),
		...walk(join(APP, "pages")),
		...walk(join(APP, "layouts")),
	].filter((f) => f.endsWith(".vue"));

	const unresolved: Record<string, string[]> = {};
	const seen = new Set<string>();
	const queue = [...entries];

	while (queue.length) {
		const file = queue.pop()!;
		if (seen.has(file)) continue;
		seen.add(file);

		for (const tag of usedComponents(readFileSync(file, "utf8"))) {
			const target = local.get(tag);
			if (target) queue.push(target);
			else if (!nuxtUi.has(tag) && !provided.has(tag)) {
				const key = relative(CLIENT, file).split(sep).join("/");
				(unresolved[key] ??= []).push(tag);
			}
		}
	}

	return Object.fromEntries(Object.entries(unresolved).sort().map(([f, tags]) => [f, [...tags].sort()]));
}

// Leftovers from the move from shadcn to Nuxt UI. Fix a page, then remove it
// here. The test also fails when an entry is no longer needed.
const KNOWN_BROKEN: Record<string, string[]> = {};

describe("components used by the pages", () => {
	it("every component a page uses exists, apart from the known leftovers", () => {
		expect(unresolvedComponents()).toEqual(KNOWN_BROKEN);
	});

	it("the dashboard uses the names Nuxt gives the chart components", () => {
		const page = templateOf(readFileSync(join(APP, "pages/dashboard/index.vue"), "utf8"));
		const local = localComponents();

		for (const tag of page.matchAll(/<(Graph[A-Za-z]*)[\s/>]/g)) {
			expect(local.has(tag[1]!), `${tag[1]} is not a component`).toBe(true);
		}
		expect(page).toMatch(/<GraphReviewedVSUnreviewed/);
	});

	it("finds the components in components/graph under their folder name", () => {
		const local = localComponents();

		expect(local.has("GraphCausalityDistribution")).toBe(true);
		expect(local.has("GraphsCausalityDistribution")).toBe(false);
		expect(local.has("FormADR")).toBe(true); // a file named like its folder is not repeated
	});
});
