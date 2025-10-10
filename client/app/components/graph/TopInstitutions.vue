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
import { fetchDashboardTopInstitutions } from "~/api/dashboard";

const query = useQuery({
	queryKey: ["dashboard", "top-institutions"],
	queryFn: () => fetchDashboardTopInstitutions(),
});

const categories = computed(() => ({
	value: { name: "Reported ADRs", color: "#3b82f6" },
}));

const xFormatter = (i: number): string => query.data.value?.[i]?.metric ?? "";

const yFormatter = (tick: number) => tick.toString();
</script>

<style scoped>
* {
	background-color: grey;
}
</style>