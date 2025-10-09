// types/plugins.d.ts

import type { ServerApiFetch } from "@/plugins/serverApiFetch"; // Adjust the path as needed

declare module "#app" {
	interface NuxtApp {
		$serverApiFetch: ServerApiFetch;
	}
}

declare module "vue" {
	interface ComponentCustomProperties {
		$serverApiFetch: ServerApiFetch;
	}
}
