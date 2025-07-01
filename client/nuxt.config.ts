// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
	compatibilityDate: "2024-11-01",
	devtools: { enabled: false },
	imports: {
		dirs: [
			"./api/**",
			"./composables/**",
			"./forms/**",
			"./stores/**",
			"./types/**",
		],
	},
	runtimeConfig: {
		public: {
			serverApi: "http://localhost:8000/api/v1",
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
		"@vee-validate/nuxt",
		"@nuxtjs/google-fonts",
		"@nuxtjs/tailwindcss",
		"@nuxtjs/color-mode",
		"@nuxt/icon",
		"shadcn-nuxt",
		"nuxt-security",
		"@hebilicious/vue-query-nuxt",
		"@pinia/nuxt",
		"@vueuse/nuxt",
	],
	/**
	 * Module Configs
	 */
	veeValidate: {
		autoImports: true,
	},
	googleFonts: {
		families: {
			Lexend: [100, 200, 300, 400, 500, 600, 700, 800, 900],
			Inter: [100, 200, 300, 400, 500, 600, 700, 800, 900],
		},
	},
	shadcn: {
		prefix: "",
		/**
		 * Directory that the component lives in.
		 * @default "./components/ui"
		 */

		componentDir: "./components/ui",
	},
	security: {
		headers: {
			crossOriginResourcePolicy: "cross-origin",
		},
	},
	tailwindcss: {
		exposeConfig: true,
		// viewer: true
	},
});
