<template>
	<div class="py-10">
		<UAlert
			v-if="error"
			color="error"
			variant="subtle"
			icon="i-lucide-triangle-alert"
			title="Could not open the review"
			:description="apiErrorMessage(error)"
			:actions="[{ label: 'Back to ADRs', color: 'neutral', to: '/adr' }]"
		/>
		<LoadingMedilinda v-else label="Opening the review" />
	</div>
</template>

<script setup lang="ts">
import { fetchCausalityAssessmentLevelById } from "@/api/cal";
import { useQuery } from "@tanstack/vue-query";
import { apiErrorMessage } from "~/utils/review-form";

// Reviews are done on the ADR's page. This address only finds the ADR of an assessment.
const route = useRoute();
const id = route.params.id as string;

const { data: assessment, error } = useQuery({
	queryKey: ["causality-assessment-by-id", id],
	queryFn: () => fetchCausalityAssessmentLevelById(id),
});

watch(
	assessment,
	(found) => {
		if (found) navigateTo(`/adr/${found.adr_id}/review`, { replace: true });
	},
	{ immediate: true }
);

useHead({ title: "Review | MediLinda" });
</script>
