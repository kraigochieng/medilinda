import { defineConfig } from "vitest/config";
import { fileURLToPath } from "node:url";

export default defineConfig({
	// The tests do not need Nuxt. Without this, esbuild reads the root
	// tsconfig, which extends .nuxt/tsconfig.json (only present after `nuxt prepare`).
	esbuild: { tsconfigRaw: "{}" },
	resolve: {
		alias: { "~": fileURLToPath(new URL("./app", import.meta.url)) },
	},
	test: {
		environment: "node",
		include: ["tests/**/*.test.ts"],
		testTimeout: 20_000,
	},
});
