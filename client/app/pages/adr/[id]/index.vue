<template>
	<h1 class="page-title">Adverse Drug Reaction Details</h1>

	<CausalityAssessmentLevelComparison
		:value="firstCausalityAssessmentLevel?.causality_assessment_level_value"
	/>

	<UTabs :items="tabs" color="neutral">
		<template #adr>
			<ADRDetails v-if="adrData" :data="adrData" />
		</template>
		<template
			#causality-assessment
			v-if="
				!['unclassified', 'unclassifiable'].includes(
					firstCausalityAssessmentLevel?.causality_assessment_level_value ??
						''
				)
			"
		>
			<ClassRankings
				v-if="
					!['unclassified', 'unclassifiable'].includes(
						firstCausalityAssessmentLevel?.causality_assessment_level_value ??
							''
					)
				"
				:base-values="firstCausalityAssessmentLevel?.base_values"
				:shap-values="
					firstCausalityAssessmentLevel?.shap_values_sum_per_class
				"
				:base-shap-values="
					firstCausalityAssessmentLevel?.shap_values_and_base_values_sum_per_class
				"
			/>
			<FeatureRankings
				v-if="
					firstCausalityAssessmentLevel &&
					!['unclassified', 'unclassifiable'].includes(
						firstCausalityAssessmentLevel.causality_assessment_level_value ??
							''
					)
				"
				:default-class="firstCausalityAssessmentLevel.causality_assessment_level_value"
				:base-values="firstCausalityAssessmentLevel.base_values"
				:shap-values="
					firstCausalityAssessmentLevel.shap_values_sum_per_class
				"
				:base-shap-values="
					firstCausalityAssessmentLevel.shap_values_and_base_values_sum_per_class
				"
				:shap-matrix="firstCausalityAssessmentLevel.shap_values_matrix"
				:feature-names="firstCausalityAssessmentLevel.feature_names"
				:feature-values="firstCausalityAssessmentLevel.feature_values"
			/>
		</template>
		<template #review>
			<ReviewCount
				:approved-count="reviewStats?.approved_reviews || 0"
				:not-approved-count="reviewStats?.unapproved_reviews || 0"
			/>
			<ReviewDetails
				:v-if="firstCurrentReview"
				:data="firstCurrentReview"
				:causality_assessment_level_id="
					firstCurrentReview?.causality_assessment_level_id
				"
			/>
			<div v-if="!currentReviewDetails">
				<UButton
					class="my-4 w-full mx-auto"
					@mouseup="router.push(`/adr/${id}/review`)"
				>
					Add Review
				</UButton>
			</div>
			<UTable :data="reviewRows" :columns="reviewColumns" />
		</template>
	</UTabs>
</template>

<script setup lang="ts">
import { fetchAdrById, deleteAdrById } from "@/api/adr";
import { fetchCausalityAssessmentLevels } from "@/api/cal";
import { fetchReviews, fetchReviewStats } from "@/api/review";
import type { ADRGetResponseInterface } from "@/types/adr";
import type { TableColumn, TabsItem } from "@nuxt/ui";
import { useQuery, useMutation, useQueryClient } from "@tanstack/vue-query";
import { capitalize } from "lodash-es";
import type { ReviewGetResponse } from "~/types/review";

// Get ADR id
const route = useRoute();
const router = useRouter();
const id = route.params.id as string;

const tabs: TabsItem[] = [
	{
		label: "ADR Details",
		slot: "adr",
	},
	{
		label: "Prediction Explanations",
		slot: "causality-assessment",
	},
	{
		label: "Review Details",
		slot: "review",
	},
];
const {
	data: adrData,
	isPending: isAdrPending,
	isError: isAdrError,
	error: adrError,
	refetch: refetchAdr,
} = useQuery<ADRGetResponseInterface>({
	queryKey: ["adr", id],
	queryFn: () => fetchAdrById(id),
	enabled: computed(() => !!id),
});

const {
	data: causalityAssessmentLevelData,
	isPending: isCausalityAssessmentPending,
	isError: isCausalityAssessmentError,
	error: causalityAssessmentError,
	status: causalityAssessmentStatus,
} = useQuery({
	queryKey: ["causality-assessment", id],
	queryFn: () => fetchCausalityAssessmentLevels({ adr_id: id }),
	enabled: computed(() => !!id), // only runs when adrId exists
});

const firstCausalityAssessmentLevel = computed(
	() => causalityAssessmentLevelData.value?.items?.[0]
);

const {
	data: currentReviewDetails,
	isPending: iscurrentReviewDetailsPending,
	isError: isReviewDetailsError,
	error: reviewDetailsError,
	status: reviewDetailsStatus,
} = useQuery({
	queryKey: ["review-details", firstCausalityAssessmentLevel.value?.id],
	queryFn: () =>
		fetchReviews({
			causality_assessment_level_id: firstCausalityAssessmentLevel.value
				?.id as string,
		}),
	enabled: computed(() => !!firstCausalityAssessmentLevel.value?.id),
});

const firstCurrentReview = computed(
	() => currentReviewDetails.value?.items?.[0]
);

const {
	data: reviewData,
	isLoading,
	isError,
} = useQuery({
	queryKey: [
		"reviews-by-causality-level",
		firstCausalityAssessmentLevel.value?.id,
	],
	queryFn: () =>
		fetchReviews({
			causality_assessment_level_id:
				firstCausalityAssessmentLevel.value?.id,
		}),
	enabled: computed(() => !!firstCausalityAssessmentLevel.value?.id),
});

const {
	data: reviewStats,
	isPending: isStatsPending,
	isError: isStatsError,
	error: statsError,
	refetch: refetchStats,
} = useQuery({
	queryKey: ["reviews-stats", firstCausalityAssessmentLevel.value?.id],
	queryFn: () =>
		fetchReviewStats(firstCausalityAssessmentLevel.value?.id as string),
	enabled: computed(() => !!firstCausalityAssessmentLevel.value?.id),
});

const reviewRows = computed(
	() => (reviewData.value?.items as ReviewGetResponse[]) ?? []
);

function formatTime(isoString: string): string {
	const date = new Date(isoString);
	return new Intl.DateTimeFormat("en-US", {
		hour: "numeric",
		minute: "numeric",
		hour12: true,
	}).format(date);
}

const reviewColumns: TableColumn<ReviewGetResponse>[] = [
	{
		id: "user.first_name",
		accessorKey: "user.first_name",
		header: "First Name",
		cell: ({ row }) => h("div", {}, row.getValue("user.first_name")),
		enableSorting: false,
	},
	{
		id: "user.last_name",
		accessorKey: "user.last_name",
		header: "Last Name",
		cell: ({ row }) => h("div", {}, row.getValue("user.last_name")),
		enableSorting: false,
	},
	{
		id: "approved",
		accessorKey: "approved",
		header: "Approved",
		cell: ({ row }) => {
			let iconName = "";
			let iconColor = "";

			if (row.original.approved) {
				iconName = "lucide:check";
				iconColor = "text-green-600";
			} else {
				iconName = "lucide:x";
				iconColor = "text-red-600";
			}

			const Icon = resolveComponent("Icon");

			return h("div", { class: "flex items-center gap-2" }, [
				h(Icon, { name: iconName, class: `w-6 h-6 ${iconColor}` }),
			]);
		},
	},
	{
		id: "reason",
		accessorKey: "reason",
		header: "Reason",
		cell: ({ row }) => {
			if (row.original.reason) {
				return h("div", {}, row.getValue("reason"));
			} else {
				return h("div", { class: "badge blank-badge italic" }, "BLANK");
			}
		},
		enableSorting: false,
	},

	{
		id: "proposed_causality_level",
		accessorKey: "proposed_causality_level",
		header: "Proposed Causality Asssessment Level",
		cell: ({ row }) => {
			if (!row.original.proposed_causality_level) {
				return h("div", { class: "badge blank-badge italic" }, "BLANK");
			}

			let color = "";
			if (row.original.proposed_causality_level == "certain") {
				color = "bg-red-500 text-white";
			} else if (row.original.proposed_causality_level == "likely") {
				color = "bg-red-400";
			} else if (row.original.proposed_causality_level == "possible") {
				color = "bg-yellow-500";
			} else if (row.original.proposed_causality_level == "unlikely") {
				color = "bg-yellow-300";
			} else if (
				row.original.proposed_causality_level == "unclassified"
			) {
				color = "bg-slate-500 text-white";
			} else if (
				row.original.proposed_causality_level == "unclassifiable"
			) {
				color = "bg-slate-300";
			}

			return h(
				"div",
				{ class: `badge ${color}` },
				capitalize(row.getValue("proposed_causality_level"))
			);
		},

		enableSorting: false,
	},
	{
		id: "created_at",
		accessorKey: "created_at",
		header: "Created At",
		cell: ({ row }) => {
			return h(
				"div",
				{},
				`${row.original.created_at.slice(0, 10) || ""} ${formatTime(
					row.original.created_at
				)}`
			);
		},
		enableSorting: true,
	},
];

useHead({ title: "View an ADR | MediLinda" });
</script>
