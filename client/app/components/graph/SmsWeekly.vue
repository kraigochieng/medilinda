<template>
	<LineChart
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
import { fetchDashboardSmsWeekly } from "~/api/dashboard";

const query = useQuery({
	queryKey: ["dashboard", "sms-weekly"],
	queryFn: () => fetchDashboardSmsWeekly(),
});

const categories = computed(() => ({
	value: { name: "Weekly SMS", color: "#6366f1" },
}));

const xFormatter = (i: number): string => query.data.value?.[i]?.metric ?? "";

const yFormatter = (tick: number) => tick.toString();
</script>
