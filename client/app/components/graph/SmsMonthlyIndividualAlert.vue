<template>
	<AreaChart
		v-if="query.data.value"
		:data="query.data.value"
		:x-formatter="xFormatter"
		:y-formatter="yFormatter"
		:categories="categories"
		:y-axis="['value']"
		:height="300"
	/>
</template>

<script setup lang="ts">
import { useQuery } from "@tanstack/vue-query";
import { fetchDashboardSmsMonthlyIndividualAlert } from "~/api/dashboard";

const query = useQuery({
	queryKey: ["dashboard", "sms-monthly-individual-alert"],
	queryFn: () => fetchDashboardSmsMonthlyIndividualAlert(),
});

const categories = computed(() => ({
	value: { name: "Individual Alerts", color: "#f59e0b" },
}));

const xFormatter = (i: number): string => query.data.value?.[i]?.metric ?? "";

const yFormatter = (tick: number) => tick.toString();
</script>
