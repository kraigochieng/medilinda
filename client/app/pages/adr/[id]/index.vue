<template>
	<div class="mb-6 flex items-center justify-between gap-4">
		<h1 class="text-2xl font-bold">Adverse Drug Reaction Details</h1>
		<UButton
			:to="`/adr/${id}/edit`"
			icon="i-lucide-pencil"
			color="neutral"
			variant="outline"
			label="Edit"
		/>
	</div>

	<UAlert
		v-if="banner"
		:color="banner.color"
		variant="subtle"
		:icon="banner.icon"
		:title="banner.title"
		:description="banner.description"
		:actions="banner.actions.map((a) => ({ label: a.label, to: a.to, color: 'neutral', variant: 'outline' }))"
		close
		class="mb-4"
		@update:open="savedKind = null"
	/>

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
				v-if="firstCurrentReview"
				:data="firstCurrentReview"
				:adr-id="id"
			/>
			<UButton
				v-else-if="firstCausalityAssessmentLevel && !iscurrentReviewDetailsPending"
				class="my-4 w-full justify-center"
				icon="i-lucide-clipboard-check"
				:to="`/adr/${id}/review`"
				label="Add your review"
			/>
			<UTable :data="reviewRows" :columns="reviewColumns" />
		</template>
		<template #history>
			<ADRHistory :adr-id="id" />
		</template>
	</UTabs>
</template>

<script setup lang="ts">
import { fetchAdrById, deleteAdrById } from "@/api/adr";
import { fetchCausalityAssessmentLevels } from "@/api/cal";
import { fetchCurrentUser } from "@/api/user";
import { savedBanner, type SavedKind } from "~/utils/adr-saved";
import { fetchReviews, fetchReviewStats } from "@/api/review";
import type { ADRGetResponseInterface } from "@/types/adr";
import type { TableColumn, TabsItem } from "@nuxt/ui";
import { useQuery, useMutation, useQueryClient } from "@tanstack/vue-query";
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
	{
		label: "History",
		slot: "history",
		icon: "i-lucide-history",
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
	isFetching: isCausalityAssessmentFetching,
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

// ---- Just saved ----------------------------------------------------------------
// The form sends us here with ?created=1 or ?saved=1. Remember it, then take it
// out of the address, so a refresh or a shared link does not show the banner again.
const savedKind = ref<SavedKind | null>(
	route.query.created ? "created" : route.query.saved ? "updated" : null
);
onMounted(() => {
	if (savedKind.value) router.replace({ query: {} });
});

const banner = computed(() => {
	if (!savedKind.value) return null;

	const hasAssessment = !!firstCausalityAssessmentLevel.value;
	const loading =
		isCausalityAssessmentPending.value ||
		isCausalityAssessmentFetching.value ||
		(hasAssessment && (isStatsPending.value || isStatsFetching.value));

	return savedBanner({
		kind: savedKind.value,
		adrId: id,
		level: firstCausalityAssessmentLevel.value?.causality_assessment_level_value,
		approved: reviewStats.value?.approved_reviews ?? 0,
		unapproved: reviewStats.value?.unapproved_reviews ?? 0,
		loading,
	});
});

// The signed-in user's own review of the current assessment ("My vote").
const { data: currentUser } = useQuery({
	queryKey: ["currentUser"],
	queryFn: fetchCurrentUser,
});

const {
	data: currentReviewDetails,
	isPending: iscurrentReviewDetailsPending,
	isError: isReviewDetailsError,
	error: reviewDetailsError,
	status: reviewDetailsStatus,
} = useQuery({
	queryKey: computed(() => [
		"my-review",
		firstCausalityAssessmentLevel.value?.id,
		currentUser.value?.id,
	]),
	queryFn: () =>
		fetchReviews({
			causality_assessment_level_id: firstCausalityAssessmentLevel.value
				?.id as string,
			user_id: currentUser.value?.id as string,
		}),
	enabled: computed(
		() => !!firstCausalityAssessmentLevel.value?.id && !!currentUser.value?.id
	),
});

const firstCurrentReview = computed(
	() => currentReviewDetails.value?.items?.[0]
);

const {
	data: reviewData,
	isLoading,
	isError,
} = useQuery({
	queryKey: computed(() => [
		"reviews-by-causality-level",
		firstCausalityAssessmentLevel.value?.id,
	]),
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
	isFetching: isStatsFetching,
	isError: isStatsError,
	error: statsError,
	refetch: refetchStats,
} = useQuery({
	queryKey: computed(() => ["reviews-stats", firstCausalityAssessmentLevel.value?.id]),
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

			return h(resolveComponent("CausalityBadge"), {
				value: row.original.proposed_causality_level,
			});
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
