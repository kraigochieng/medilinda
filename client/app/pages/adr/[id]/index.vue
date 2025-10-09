<template>
	<h1>Adverse Drug Reaction Details</h1>

	<CausalityAssessmentLevelComparison
		v-if="causalityAssessmentLevelData"
		:value="causalityAssessmentLevelData.causality_assessment_level_value"
	/>

	<UTabs :items="tabs">
		<template #adr>
			<ADRDetails v-if="adrData" :data="adrData" />
		</template>
		<template
			#causality-assessment
			v-if="
				causalityAssessmentLevelData &&
				!['unclassified', 'unclassifiable'].includes(
					causalityAssessmentLevelData.causality_assessment_level_value ??
						''
				)
			"
		>
			<ClassRankings
				v-if="
					causalityAssessmentLevelData &&
					!['unclassified', 'unclassifiable'].includes(
						causalityAssessmentLevelData.causality_assessment_level_value ??
							''
					)
				"
				:base-values="causalityAssessmentLevelData.base_values"
				:shap-values="
					causalityAssessmentLevelData.shap_values_sum_per_class
				"
				:base-shap-values="
					causalityAssessmentLevelData.shap_values_and_base_values_sum_per_class
				"
			/>
		</template>
		<template #review>
			<ReviewCount
				:approved-count="
					causalityAssessmentLevelData?.approved_count || 0
				"
				:not-approved-count="
					causalityAssessmentLevelData?.not_approved_count || 0
				"
			/>
			<ReviewDetails
				v-if="currentReviewDetails"
				:data="currentReviewDetails"
				:causality_assessment_level_id="
					currentReviewDetails.causality_assessment_level_id
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
	<!-- 
					<FeatureRankings
						v-if="
							causalityAssessmentLevelData &&
							!['unclassified', 'unclassifiable'].includes(
								causalityAssessmentLevelData.causality_assessment_level_value ??
									''
							)
						"
						:base-values="causalityAssessmentLevelData.base_values"
						:shap-values="
							causalityAssessmentLevelData.shap_values_sum_per_class
						"
						:base-shap-values="
							causalityAssessmentLevelData.shap_values_and_base_values_sum_per_class
						"
						:shap-matrix="
							causalityAssessmentLevelData.shap_values_matrix
						"
						:feature-names="
							causalityAssessmentLevelData.feature_names
						"
						:feature-values="
							causalityAssessmentLevelData.feature_values
						"
					/>
 -->
</template>

<script setup lang="ts">
import { fetchAdrById, fetchCausalityAssessmentByAdrId } from "@/api/adr";
import { fetchReviewsByCausalityAssessmentLevelId } from "@/api/cal";
import { fetchReviewByUserAndCausalityLevel } from "@/api/review";
import type { ADRGetResponseInterface } from "@/types/adr";
import type { TableColumn, TabsItem } from "@nuxt/ui";
import { useQuery } from "@tanstack/vue-query";
import { capitalize } from "lodash";
import type { ReviewWithUserGetResponse } from "~/types/review";

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
	queryFn: () => fetchCausalityAssessmentByAdrId(id),
	enabled: computed(() => !!id), // only runs when adrId exists
});

const {
	data: currentReviewDetails,
	isPending: iscurrentReviewDetailsPending,
	isError: isReviewDetailsError,
	error: reviewDetailsError,
	status: reviewDetailsStatus,
} = useQuery({
	queryKey: ["review-details", causalityAssessmentLevelData.value?.id],
	queryFn: () =>
		fetchReviewByUserAndCausalityLevel(
			causalityAssessmentLevelData.value?.id as string
		),
	enabled: computed(() => !!causalityAssessmentLevelData.value?.id),
});

const {
	data: reviewData,
	isLoading,
	isError,
} = useQuery({
	queryKey: [
		"reviews-by-causality-level",
		causalityAssessmentLevelData.value?.id,
	],
	queryFn: () =>
		fetchReviewsByCausalityAssessmentLevelId(
			causalityAssessmentLevelData.value?.id as string
		),
	enabled: computed(() => !!causalityAssessmentLevelData.value?.id),
});

const reviewRows = computed(
	() => (reviewData.value?.items as ReviewWithUserGetResponse[]) ?? []
);

function formatTime(isoString: string): string {
	const date = new Date(isoString);
	return new Intl.DateTimeFormat("en-US", {
		hour: "numeric",
		minute: "numeric",
		hour12: true,
	}).format(date);
}

const reviewColumns: TableColumn<ReviewWithUserGetResponse>[] = [
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
