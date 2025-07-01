<template>
	<div class="page-wrapper">
		<p v-if="adrStatus == 'pending'">Loading ADR...</p>
		<p v-else-if="adrStatus == 'error'">Error {{ adrError }}</p>
		<div v-else-if="adrStatus == 'success'">
			<CausalityAssessmentLevelComparison
				v-if="causalityAssessmentLevelData"
				:value="
					causalityAssessmentLevelData.causality_assessment_level_value
				"
			/>
			<Tabs default-value="adr">
				<TabsList>
					<TabsTrigger value="adr">ADR Details</TabsTrigger>
					<TabsTrigger
						value="causality-assessment"
						v-if="
							causalityAssessmentLevelData &&
							!['unclassified', 'unclassifiable'].includes(
								causalityAssessmentLevelData.causality_assessment_level_value ??
									''
							)
						"
					>
						Prediction Explanations
					</TabsTrigger>
					<TabsTrigger value="review"> Review Details </TabsTrigger>
				</TabsList>
				<TabsContent value="adr">
					<ADRDetails v-if="adrData" :data="adrData" />
				</TabsContent>
				<TabsContent
					value="causality-assessment"
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
				</TabsContent>
				<TabsContent value="review">
					<ReviewCount
						:approved-count="
							causalityAssessmentLevelData?.approved_count || 0
						"
						:not-approved-count="
							causalityAssessmentLevelData?.not_approved_count ||
							0
						"
					/>
					<ReviewDetails
						v-if="currentReviewData"
						:data="currentReviewData"
						:causality_assessment_level_id="
							currentReviewData.causality_assessment_level_id
						"
					/>
					<div v-if="!currentReviewData">
						<Button
							class="my-4 w-full mx-auto"
							@mouseup="
								router.push(
									`/adr/${id}/review`
								)
							"
						>
							Add Review
						</Button>
					</div>
					<DataTable
						title="Reviews from Other Users"
						:data="reviewData?.items"
						:columns="reviewColumns"
						:isLoading="reviewStatus === 'pending'"
						:currentPage="currentPage"
						:pageSize="pageSize"
						:totalCount="totalCount"
						@pageChange="handlePageChange"
						@pageSizeChange="handlePageSizeChange"
					/>
				</TabsContent>
			</Tabs>
		</div>
	</div>
</template>

<script setup lang="ts">
import TableActionsReview from "@/components/table/actions/Review.vue";
import Checkbox from "@/components/ui/checkbox/Checkbox.vue";
import type { ADRGetResponseInterface } from "@/types/adr";
import type { CausalityAssessmentLevelWithReviewCountGetResponseInterface } from "@/types/cal";
import type { PaginatedResponseInterface } from "@/types/pagination";
import type { ReviewGetResponse } from "@/types/review";
import { type ColumnDef } from "@tanstack/vue-table";
import { capitalize } from "lodash";

// Get ADR id
const route = useRoute();
const id = route.params.id as string;

// Routes
const router = useRouter();
// const activeTab = ref(
// 	route.query.tab === "already-sent" ? "already-sent" : "to-be-sent"
// );

// watch(activeTab, (val) => {
// 	const router = useRouter();
// 	router.replace({ query: { ...route.query, tab: val } });
// });

// Stores
const authStore = useAuthStore();

const adrData = ref<ADRGetResponseInterface | null>(null);
const adrStatus = ref<"pending" | "success" | "error">("pending");
const adrError = ref<string | null>(null);

const causalityAssessmentLevelData =
	ref<CausalityAssessmentLevelWithReviewCountGetResponseInterface | null>(
		null
	);
const causalityAssessmentLevelStatus = ref<"pending" | "success" | "error">(
	"pending"
);
const causalityAssessmentLevelError = ref<string | null>(null);

const currentReviewData = ref<ReviewGetResponse | null>(null);
const currentReviewStatus = ref<"pending" | "success" | "error">("pending");
const currentReviewError = ref<string | null>(null);

const reviewData =
	ref<PaginatedResponseInterface<ReviewWithUserGetResponse> | null>(null);
const reviewStatus = ref<"pending" | "success" | "error">("pending");
const reviewError = ref<string | null>(null);

async function fetchADRData() {
	try {
		adrStatus.value = "pending";
		// Using $fetch for API call
		adrData.value = await $fetch(
			`${useRuntimeConfig().public.serverApi}/adr/${id}`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
			}
		);

		adrStatus.value = "success";
	} catch (err: any) {
		adrStatus.value = "error";
		adrError.value = err.message || "Something went wrong";
	}
}

async function fetchCausalityAssessmentLevelData() {
	try {
		causalityAssessmentLevelStatus.value = "pending";
		// Using $fetch for API call
		causalityAssessmentLevelData.value = await $fetch(
			`${
				useRuntimeConfig().public.serverApi
			}/specific_adr/${id}/causality_assessment_level`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
			}
		);

		causalityAssessmentLevelStatus.value = "success";
	} catch (err: any) {
		causalityAssessmentLevelStatus.value = "error";
		causalityAssessmentLevelError.value =
			err.message || "Something went wrong";
	}
}

async function fetchCurrentReviewData() {
	try {
		currentReviewStatus.value = "pending";
		// Using $fetch for API call
		currentReviewData.value = await $fetch(
			`${
				useRuntimeConfig().public.serverApi
			}/review_for_specific_user_and_causality_assessment_level`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
				params: {
					causality_assessment_level_id:
						causalityAssessmentLevelData.value?.id,
				},
			}
		);

		currentReviewStatus.value = "success";
	} catch (err: any) {
		currentReviewStatus.value = "error";
		currentReviewError.value = err.message || "Something went wrong";
	}
}

async function fetchReviewData() {
	try {
		reviewStatus.value = "pending";
		// Using $fetch for API call
		reviewData.value = await $fetch(
			`${
				useRuntimeConfig().public.serverApi
			}/causality_assessment_level/${
				currentReviewData.value?.causality_assessment_level_id
			}/review`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
				params: {
					page: currentPage.value,
					size: pageSize.value,
				},
			}
		);

		reviewStatus.value = "success";
	} catch (err: any) {
		reviewStatus.value = "error";
		reviewError.value = err.message || "Something went wrong";
	}
}

const currentPage = ref(1);
const pageSize = ref(20);

const totalCount = computed(() => reviewData.value?.total || 0);

function formatTime(isoString: string): string {
	const date = new Date(isoString);
	return new Intl.DateTimeFormat("en-US", {
		hour: "numeric",
		minute: "numeric",
		hour12: true,
	}).format(date);
}

const reviewColumns: ColumnDef<ReviewWithUserGetResponse>[] = [
	// {
	// 	id: "select",
	// 	header: ({ table }) =>
	// 		h(Checkbox, {
	// 			modelValue:
	// 				table.getIsAllPageRowsSelected() ||
	// 				(table.getIsSomePageRowsSelected() && "indeterminate"),
	// 			"onUpdate:modelValue": (value) =>
	// 				table.toggleAllPageRowsSelected(!!value),
	// 			ariaLabel: "Select all",
	// 		}),
	// 	cell: ({ row }) =>
	// 		h(Checkbox, {
	// 			modelValue: row.getIsSelected(),
	// 			"onUpdate:modelValue": (value) => row.toggleSelected(!!value),
	// 			ariaLabel: "Select row",
	// 		}),
	// 	enableSorting: false,
	// 	enableHiding: false,
	// },
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
	// {
	// 	id: "actions",
	// 	enableHiding: false,
	// 	cell: ({ row }) => {
	// 		return h(TableActionsReview, {
	// 			row: row.original,
	// 			onExpand: row.toggleExpanded,
	// 		});
	// 	},
	// },
];

onMounted(async () => {
	await fetchADRData();
	await fetchCausalityAssessmentLevelData();
	await fetchCurrentReviewData();
	await fetchReviewData();
});

watch([currentPage, pageSize], () => {
	fetchCausalityAssessmentLevelData();
});

function handlePageChange(page: number) {
	currentPage.value = page;
}

const handlePageSizeChange = (size: number) => {
	pageSize.value = size;
	currentPage.value = 1;
};

useHead({ title: "View an ADR | MediLinda" });
</script>
