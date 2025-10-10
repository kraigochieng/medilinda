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
import { fetchDashboardSmsMonthly } from "~/api/dashboard";

const query = useQuery({
	queryKey: ["dashboard", "sms-monthly"],
	queryFn: () => fetchDashboardSmsMonthly(),
});

const categories = computed(() => ({
	value: { name: "Monthly SMS", color: "#8b5cf6" },
}));

const xFormatter = (i: number): string => query.data.value?.[i]?.metric ?? "";

const yFormatter = (tick: number) => tick.toString();
</script>
