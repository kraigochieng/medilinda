<template>
	<GraphCard
		title="Reviewed and not reviewed"
		description="How many ADRs have at least one review, and how many have none."
		color="#22c55e"
		:query="query"
	/>
</template>

<script setup lang="ts">
import { useQuery } from "@tanstack/vue-query";
import { fetchDashboardReviewedUnreviewed } from "~/api/dashboard";

const query = useQuery({
	queryKey: ["dashboard", "reviewed-unreviewed"],
	queryFn: () => fetchDashboardReviewedUnreviewed(),
});
</script>
