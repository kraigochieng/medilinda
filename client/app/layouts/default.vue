<template>
	<div
		class="flex items-center justify-between sticky top-0 z-50 bg-background page-responsive-width py-4 glass-bg"
	>
		<NuxtLink href="/"><Logo /></NuxtLink>

		<UNavigationMenu :items="items" />

		<UAvatar
			:alt="`${capitalize(userData?.first_name.charAt(0))} ${capitalize(
				userData?.last_name.charAt(0)
			)}`"
			size="lg"
		/>
	</div>

	<div class="page-wrapper">
		<slot></slot>
	</div>
</template>
<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";
import { useQuery } from "@tanstack/vue-query";

import { fetchCurrentUser } from "@/api/user";
import { capitalize } from "lodash-es";

const items = ref<NavigationMenuItem[]>([
	{
		label: "Home",
		to: "/",
	},
	{
		label: "ADR",
		children: [
			{ label: "View ADRs", to: "/adr" },
			{ label: "Add ADRs", to: "/adr/add" },
		],
	},
	{
		label: "Communication",
		children: [
			{
				label: "Individual Alerts",
				to: "/communication/individual-alerts",
			},
			{
				label: "Additional Info Requests",
				to: "/communication/additional-information-requests",
			},
		],
	},
	{
		label: "Dashboard",
		to: "/dashboard",
	},
]);

const { data: userData } = useQuery({
	queryKey: ["users"],
	queryFn: () => fetchCurrentUser(),
});
</script>

<style scoped>
@reference "assets/css/main.css";

.glass-bg {
	@apply backdrop-filter backdrop-blur-xs;
}

@media print {
	.noprint {
		visibility: hidden;
	}
}
</style>
