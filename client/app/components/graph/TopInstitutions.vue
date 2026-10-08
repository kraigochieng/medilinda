<template>
	<GraphCard
		title="Top institutions"
		description="The institutions that reported the most ADRs."
		color="#3b82f6"
		:query="query"
	/>
</template>

<script setup lang="ts">
import { useQuery } from "@tanstack/vue-query";
import { fetchDashboardTopInstitutions } from "~/api/dashboard";

const query = useQuery({
	queryKey: ["dashboard", "top-institutions"],
	queryFn: () => fetchDashboardTopInstitutions(),
});
</script>
