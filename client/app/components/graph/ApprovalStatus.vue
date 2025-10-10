<template>
	<BarChart
		v-if="query.data.value"
		:data="query.data.value"
		:x-formatter="xFormatter"
		:y-formatter="yFormatter"
		:categories="categories"
		:y-grid-line="true"
		:y-axis="['value']"
		:height="300"
		:radius="4"
		:legend-position="LegendPosition.Top"
		:hide-legend="false"
		bar-direction="horizontal"
	/>
</template>

<script setup lang="ts">
import { useQuery } from "@tanstack/vue-query";
import { fetchDashboardApprovalStatus } from "~/api/dashboard";

const query = useQuery({
	queryKey: ["dashboard", "approval-status"],
	queryFn: () => fetchDashboardApprovalStatus(),
});

const categories = computed(() => ({
	value: {
		name: "Approval Status",
		color: "#22c55e",
	},
}));

const xFormatter = (i: number): string =>
	query.data.value && query.data.value[i]
		? `${query.data.value[i].metric}`
		: "";

const yFormatter = (tick: number) => tick.toString();
</script>

<style scoped>
@reference "assets/css/main.css";

* {
	background-color: grey;
}
</style>
