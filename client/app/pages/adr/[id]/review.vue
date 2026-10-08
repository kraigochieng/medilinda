<template>
	<div class="page-wrapper space-y-4">
		<div class="flex items-center justify-between gap-4">
			<h1 class="text-2xl font-bold">Review the prediction</h1>
			<UButton :to="`/adr/${id}`" color="neutral" variant="outline" icon="i-lucide-arrow-left" label="Back to the ADR" />
		</div>

		<UAlert
			v-if="loadError"
			color="error"
			variant="subtle"
			icon="i-lucide-triangle-alert"
			title="Could not load this report"
			:description="apiErrorMessage(loadError)"
			:actions="[
				{ label: 'Try again', color: 'neutral', onClick: () => reload() },
				{ label: 'Back to ADRs', color: 'neutral', to: '/adr' },
			]"
		/>

		<div v-else-if="isLoading" class="space-y-4" aria-busy="true">
			<USkeleton class="h-40 w-full" />
			<USkeleton class="h-72 w-full" />
		</div>

		<UAlert
			v-else-if="!assessment"
			color="warning"
			variant="subtle"
			icon="i-lucide-circle-help"
			title="This report has no causality assessment yet"
			description="There is nothing to review. Edit the report so the model can assess it."
			:actions="[{ label: 'Edit the report', color: 'neutral', to: `/adr/${id}/edit` }]"
		/>

		<template v-else>
			<CausalityAssessmentLevelComparison :value="assessment.causality_assessment_level_value" />

			<UTabs v-model="tab" :items="tabs" color="neutral">
				<template #review>
					<div class="mt-4">
						<ADRReviewForm
							:key="myReview?.id ?? 'new'"
							:causality-assessment-level-id="assessment.id"
							:predicted-level="assessment.causality_assessment_level_value"
							:existing-review="myReview"
							@saved="navigateTo(tabAddress(id, 'review'))"
							@removed="navigateTo(tabAddress(id, 'review'))"
						/>
					</div>
				</template>

				<template #adr>
					<ADRDetails v-if="adr" :data="adr" />
				</template>

				<template #explanations>
					<PredictionExplanation :assessment="assessment" class="mt-4" />
				</template>
			</UTabs>
		</template>
	</div>
</template>

<script setup lang="ts">
import { fetchAdrById } from "@/api/adr";
import { fetchCausalityAssessmentLevels } from "@/api/cal";
import { fetchReviews } from "@/api/review";
import { fetchCurrentUser } from "@/api/user";
import type { TabsItem } from "@nuxt/ui";
import { useQuery } from "@tanstack/vue-query";
import { tabAddress } from "~/utils/adr-tabs";
import { apiErrorMessage } from "~/utils/review-form";

const route = useRoute();
const id = route.params.id as string;

const tab = ref("review");

// The same queries, and cache keys, as the ADR page.
const adrQuery = useQuery({ queryKey: ["adr", id], queryFn: () => fetchAdrById(id) });
const assessmentsQuery = useQuery({
	queryKey: ["causality-assessment", id],
	queryFn: () => fetchCausalityAssessmentLevels({ adr_id: id }),
});
const userQuery = useQuery({ queryKey: ["currentUser"], queryFn: fetchCurrentUser });

const adr = computed(() => adrQuery.data.value);
// The server lists the newest assessment first. Only the newest can be reviewed.
const assessment = computed(() => assessmentsQuery.data.value?.items?.[0]);

const myReviewQuery = useQuery({
	queryKey: computed(() => ["my-review", assessment.value?.id, userQuery.data.value?.id]),
	queryFn: () =>
		fetchReviews({
			causality_assessment_level_id: assessment.value!.id,
			user_id: userQuery.data.value!.id,
		}),
	enabled: computed(() => !!assessment.value?.id && !!userQuery.data.value?.id),
});
const myReview = computed(() => myReviewQuery.data.value?.items?.[0] ?? null);

const loadError = computed(() => adrQuery.error.value ?? assessmentsQuery.error.value ?? userQuery.error.value);
const isLoading = computed(
	() =>
		adrQuery.isPending.value ||
		assessmentsQuery.isPending.value ||
		userQuery.isPending.value ||
		(!!assessment.value && myReviewQuery.isPending.value)
);

function reload() {
	adrQuery.refetch();
	assessmentsQuery.refetch();
	userQuery.refetch();
}

const tabs = computed<TabsItem[]>(() => {
	const items: TabsItem[] = [
		{ label: myReview.value ? "Your review" : "Review", value: "review", slot: "review" as const },
		{ label: "Report details", value: "adr", slot: "adr" as const },
	];
	const level = assessment.value?.causality_assessment_level_value;
	if (level && !["unclassified", "unclassifiable"].includes(level)) {
		items.push({ label: "Prediction explanations", value: "explanations", slot: "explanations" as const });
	}
	return items;
});

useHead({ title: "Review the prediction | MediLinda" });
</script>
