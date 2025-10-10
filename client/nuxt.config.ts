import tailwindcss from "@tailwindcss/vite";

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
	compatibilityDate: "2024-11-01",
	devtools: { enabled: false },
	css: ["~/assets/css/main.css"],
	runtimeConfig: {
		public: {
			serverApi: process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8000",
		},
	},
	app: {
		head: {
			link: [
				{ rel: "icon", type: "image/svg+xml", href: "/favicon.svg" },
			],
		},
	},
	// plugins: ["~/plugins/apexcharts.client.ts"],
	modules: [
		"@nuxtjs/google-fonts",
		"@nuxtjs/color-mode",
		"@nuxt/icon",
		"nuxt-security",
		"@pinia/nuxt",
		"@vueuse/nuxt",
		"@nuxt/ui",
		"nuxt-charts"
	],
	/**
	 * Module Configs
	 */
	googleFonts: {
		families: {
			Lexend: [100, 200, 300, 400, 500, 600, 700, 800, 900],
			Inter: [100, 200, 300, 400, 500, 600, 700, 800, 900],
		},
	},
	security: {
		headers: {
			crossOriginResourcePolicy: "cross-origin",
		},
	},
	vite: {
		plugins: [tailwindcss()],
	},
});
