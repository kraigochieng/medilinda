<template>
	<UDashboardGroup unit="rem">
		<UDashboardSidebar
			v-model:collapsed="collapsed"
			collapsible
			:default-size="16"
			:min-size="14"
			:max-size="20"
			:collapsed-size="4"
			class="noprint"
		>
			<template #header="{ collapsed: isCollapsed }">
				<NuxtLink to="/" class="flex items-center">
					<span
						v-if="isCollapsed"
						class="text-2xl font-bold italic text-primary"
						>M</span
					>
					<Logo v-else />
				</NuxtLink>
			</template>

			<template #default="{ collapsed: isCollapsed }">
				<UNavigationMenu
					:items="mainItems"
					:collapsed="isCollapsed"
					orientation="vertical"
					tooltip
					popover
				/>

				<UNavigationMenu
					:items="footerItems"
					:collapsed="isCollapsed"
					orientation="vertical"
					tooltip
					class="mt-auto"
				/>
			</template>

			<template #footer="{ collapsed: isCollapsed }">
				<UDropdownMenu
					:items="userMenuItems"
					:content="{ align: 'start' }"
					class="w-full"
				>
					<UButton
						color="neutral"
						variant="ghost"
						block
						:square="isCollapsed"
						class="w-full"
						:class="isCollapsed ? '' : 'justify-start'"
					>
						<UAvatar :alt="fullName" size="sm" />
						<span v-if="!isCollapsed" class="truncate">
							{{ fullName }}
						</span>
					</UButton>
				</UDropdownMenu>
			</template>
		</UDashboardSidebar>

		<UDashboardPanel>
			<template #header>
				<UDashboardNavbar class="noprint">
					<template #leading>
						<UDashboardSidebarCollapse />
					</template>
				</UDashboardNavbar>
			</template>

			<template #body>
				<slot></slot>
			</template>
		</UDashboardPanel>
	</UDashboardGroup>
</template>

<script setup lang="ts">
import type { DropdownMenuItem, NavigationMenuItem } from "@nuxt/ui";
import { useQuery } from "@tanstack/vue-query";

import { fetchCurrentUser } from "@/api/user";
import { capitalize } from "lodash-es";
import { authClient } from "~/lib/auth-client";

const collapsed = ref(false);

const mainItems: NavigationMenuItem[] = [
	{ label: "Home", icon: "i-lucide-house", to: "/", exact: true },
	{
		label: "ADRs",
		icon: "i-lucide-file-heart",
		defaultOpen: true,
		children: [
			{ label: "View ADRs", to: "/adr", exact: true },
			{ label: "Add ADR", to: "/adr/add" },
			{ label: "Recently deleted", to: "/adr/deleted" },
		],
	},
	{ label: "Reviews", icon: "i-lucide-clipboard-check", to: "/review" },
	{
		label: "Causality assessment",
		icon: "i-lucide-scale",
		to: "/causality-assessment-level",
	},
	{
		label: "Communication",
		icon: "i-lucide-messages-square",
		children: [
			{
				label: "Individual alerts",
				to: "/communication/individual-alerts",
			},
			{
				label: "Additional info requests",
				to: "/communication/additional-information-requests",
			},
		],
	},
	{
		label: "Monitoring",
		icon: "i-lucide-activity",
		children: [
			{ label: "Overview", to: "/monitoring", exact: true },
			{ label: "ADR", to: "/monitoring/adr" },
			{ label: "Review", to: "/monitoring/review" },
			{ label: "SMS", to: "/monitoring/sms" },
		],
	},
	{ label: "Dashboard", icon: "i-lucide-layout-dashboard", to: "/dashboard" },
];

const footerItems: NavigationMenuItem[] = [
	{ label: "About", icon: "i-lucide-info", to: "/about" },
];

const { data: userData } = useQuery({
	queryKey: ["users"],
	queryFn: () => fetchCurrentUser(),
});

const fullName = computed(() =>
	[userData.value?.first_name, userData.value?.last_name]
		.filter(Boolean)
		.map((name) => capitalize(name))
		.join(" ") || "Account",
);

const userMenuItems: DropdownMenuItem[][] = [
	[
		{
			label: "API keys",
			icon: "i-lucide-key-round",
			to: "/settings/api-keys",
		},
		{
			label: "Sign out",
			icon: "i-lucide-log-out",
			onSelect: async () => {
				await authClient.signOut();
				await navigateTo("/auth/login");
			},
		},
	],
];
</script>

<style scoped>
@media print {
	.noprint {
		display: none;
	}
}
</style>
