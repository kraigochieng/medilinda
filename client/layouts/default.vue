<template>
	<div
		class="flex items-center justify-between sticky top-0 z-50 bg-background page-responsive-width py-4"
	>
		<NuxtLink href="/"><Logo /></NuxtLink>

		<NavigationMenu class="noprint">
			<NavigationMenuList class="flex gap-x-4 flex-col md:flex-row">
				<!-- <NavigationMenuItem>
					<NavigationMenuLink href="/">Home</NavigationMenuLink>
				</NavigationMenuItem> -->
				<NavigationMenuItem>
					<NavigationMenuTrigger>ADR</NavigationMenuTrigger>
					<NavigationMenuContent>
						<ul
							class="grid w-[400px] gap-3 p-4 md:w-[500px] md:grid-cols-2 lg:w-[600px]"
						>
							<li>
								<NavigationMenuLink
									as-child
									class="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
								>
									<NuxtLink to="/adr/add">Add ADR</NuxtLink>
								</NavigationMenuLink>
							</li>
							<li>
								<NavigationMenuLink
									as-child
									class="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
								>
									<NuxtLink to="/adr">View ADRs</NuxtLink>
								</NavigationMenuLink>
							</li>
						</ul>
					</NavigationMenuContent>
				</NavigationMenuItem>
				<NavigationMenuItem>
					<NavigationMenuTrigger>Communication</NavigationMenuTrigger>
					<NavigationMenuContent>
						<ul
							class="grid w-[400px] gap-3 p-4 md:w-[500px] md:grid-cols-2 lg:w-[600px]"
						>
							<li>
								<NavigationMenuLink
									as-child
									class="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
								>
									<NuxtLink
										to="/communication/additional-information-requests"
									>
										Additional Information Requests
									</NuxtLink>
								</NavigationMenuLink>
							</li>
							<li>
								<NavigationMenuLink
									as-child
									class="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
								>
									<NuxtLink
										to="/communication/individual-alerts"
									>
										Individual Alerts
									</NuxtLink>
								</NavigationMenuLink>
							</li>
						</ul>
					</NavigationMenuContent>
				</NavigationMenuItem>
				<!-- <NavigationMenuItem>
					<NavigationMenuTrigger>Monitoring</NavigationMenuTrigger>
					<NavigationMenuContent>
						<ul
							class="grid w-[400px] gap-3 p-4 md:w-[500px] md:grid-cols-2 lg:w-[600px]"
						>
							<li>
								<NavigationMenuLink
									as-child
									class="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
								>
									<NuxtLink to="/monitoring/adr">
										ADR Monitoring
									</NuxtLink>
								</NavigationMenuLink>
							</li>
							<li>
								<NavigationMenuLink
									as-child
									class="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
								>
									<NuxtLink to="/monitoring/review">
										Review Monitoring
									</NuxtLink>
								</NavigationMenuLink>
							</li>
							<li>
								<NavigationMenuLink
									as-child
									class="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
								>
									<NuxtLink to="/monitoring/sms">
										SMS Monitoring
									</NuxtLink>
								</NavigationMenuLink>
							</li>
						</ul>
					</NavigationMenuContent>
				</NavigationMenuItem> -->
				<NavigationMenuItem>
					<NavigationMenuLink href="/dashboard"
						>Dashboard</NavigationMenuLink
					>
				</NavigationMenuItem>
				<!-- <NavigationMenuItem>
					<NavigationMenuLink href="/about">About</NavigationMenuLink>
				</NavigationMenuItem> -->
				<NavigationMenuItem>
					<Button @mouseup="useAuthStore().logout()">Logout</Button>
				</NavigationMenuItem>
			</NavigationMenuList>
		</NavigationMenu>

		<div
			class="flex gap-1 bg-accent rounded-full p-4"
			:title="`${data?.first_name} ${data?.last_name}`"
		>
			<p>{{ capitalize(data?.first_name.charAt(0)) }}</p>
			<p>{{ capitalize(data?.last_name.charAt(0)) }}</p>
		</div>
	</div>

	<slot></slot>
</template>
<script setup lang="ts">
import type { UserDetails } from "@/types/user";

import { capitalize } from "lodash";

const authStore = useAuthStore();

const data = ref<UserDetails | null>(null);
const status = ref<"pending" | "success" | "error">("pending");
const error = ref<string | null>(null);

onMounted(async () => {
	await fetchUserData();
});

const fetchUserData = async () => {
	try {
		status.value = "pending";
		// Using $fetch for API call
		data.value = await $fetch(
			`${useRuntimeConfig().public.serverApi}/users/me`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
			}
		);

		status.value = "success";
	} catch (err: any) {
		status.value = "error";
		error.value = err.message || "Something went wrong";
	}
};
</script>

<style scoped>
.glass-bg {
	@apply backdrop-filter backdrop-blur-md bg-opacity-50;
}

@media print {
	.noprint {
		visibility: hidden;
	}
}
</style>
