<template>
	<GraphCard
		title="Causality levels"
		description="The newest predicted level of each ADR."
		color="#22c55e"
		:query="query"
	/>
</template>

<script setup lang="ts">
import { useQuery } from "@tanstack/vue-query";
import { fetchDashboardCausalityDistribution } from "~/api/dashboard";

const query = useQuery({
	queryKey: ["dashboard", "causality-distribution"],
	queryFn: () => fetchDashboardCausalityDistribution(),
});
</script>
