<template>
	<GraphCard
		title="Approval status"
		description="How reviewers voted on the newest prediction of each ADR."
		color="#22c55e"
		:query="query"
	/>
</template>

<script setup lang="ts">
import { useQuery } from "@tanstack/vue-query";
import { fetchDashboardApprovalStatus } from "~/api/dashboard";

const query = useQuery({
	queryKey: ["dashboard", "approval-status"],
	queryFn: () => fetchDashboardApprovalStatus(),
});
</script>
