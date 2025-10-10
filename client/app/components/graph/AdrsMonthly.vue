<template>
	<AreaChart
		v-if="query.data.value"
		:data="query.data.value"
		:x-formatter="xFormatter"
		:y-formatter="yFormatter"
		:categories="categories"
		:y-axis="['value']"
		:height="300"
		:legend-position="LegendPosition.Top"
	/>
</template>

<script setup lang="ts">
import { useQuery } from "@tanstack/vue-query";
import { fetchDashboardAdrsMonthly } from "~/api/dashboard";

const query = useQuery({
	queryKey: ["dashboard", "adrs-monthly"],
	queryFn: () => fetchDashboardAdrsMonthly(),
});

const categories = computed(() => ({
	value: { name: "Monthly ADRs", color: "#10b981" },
}));

const xFormatter = (i: number): string => query.data.value?.[i]?.metric ?? "";

const yFormatter = (tick: number) => tick.toString();
</script>
