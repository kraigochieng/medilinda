<template>
	<PieChart
		v-if="query.data.value"
		:data="query.data.value"
		:value-key="'value'"
		:label-key="'metric'"
		:height="300"
	/>
</template>

<script setup lang="ts">
import { useQuery } from "@tanstack/vue-query";
import { fetchDashboardSmsType } from "~/api/dashboard";

const query = useQuery({
	queryKey: ["dashboard", "sms-type"],
	queryFn: () => fetchDashboardSmsType(),
});
</script>
