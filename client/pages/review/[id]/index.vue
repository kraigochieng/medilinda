<template>
	<div class="page-wrapper">
		<ReviewCount
			:approved-count="causalityAssessmentLevelData?.approved_count || 0"
			:not-approved-count="
				causalityAssessmentLevelData?.not_approved_count || 0
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
					router.push(`/causality-assessment-level/${id}/review`)
				"
			>
				Add Review
			</Button>
		</div>
		<DataTable
			title="Reviews from Other Users"
			:data="reviewData?.items"
			:columns="columns"
			:isLoading="reviewStatus === 'pending'"
			:currentPage="currentPage"
			:pageSize="pageSize"
			:totalCount="totalCount"
			@pageChange="handlePageChange"
			@pageSizeChange="handlePageSizeChange"
		/>
	</div>
</template>

<script setup lang="ts">
import TableActionsReview from "@/components/table/actions/Review.vue";
import Checkbox from "@/components/ui/checkbox/Checkbox.vue";
import type { ColumnDef } from "@tanstack/vue-table";

onMounted(async () => {
	await fetchReviewData();
	await fetchCurrentReviewData();
	await fetchCausalityAssessmentLevelData();
});

const route = useRoute();
const id = route.params.id as string;

const router = useRouter();

// Store
const authStore = useAuthStore();

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

async function fetchCausalityAssessmentLevelData() {
	try {
		causalityAssessmentLevelStatus.value = "pending";
		// Using $fetch for API call
		causalityAssessmentLevelData.value = await $fetch(
			`${
				useRuntimeConfig().public.serverApi
			}/causality_assessment_level/${
				currentReviewData.value?.causality_assessment_level_id
			}`,
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
			`${useRuntimeConfig().public.serverApi}/review/${id}`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
			}
		);

		currentReviewStatus.value = "success";
	} catch (err: any) {
		currentReviewStatus.value = "error";
		currentReviewError.value = err.message || "Something went wrong";
	}
}

const currentPage = ref(1);
const pageSize = ref(20);

const totalCount = computed(() => reviewData.value?.total || 0);

// Table
watch([currentPage, pageSize], () => {
	fetchReviewData();
});

function handlePageChange(page: number) {
	currentPage.value = page;
}

const handlePageSizeChange = (size: number) => {
	pageSize.value = size;
	currentPage.value = 1;
};

const columns: ColumnDef<ReviewWithUserGetResponse>[] = [
	{
		id: "select",
		header: ({ table }) =>
			h(Checkbox, {
				modelValue:
					table.getIsAllPageRowsSelected() ||
					(table.getIsSomePageRowsSelected() && "indeterminate"),
				"onUpdate:modelValue": (value) =>
					table.toggleAllPageRowsSelected(!!value),
				ariaLabel: "Select all",
			}),
		cell: ({ row }) =>
			h(Checkbox, {
				modelValue: row.getIsSelected(),
				"onUpdate:modelValue": (value) => row.toggleSelected(!!value),
				ariaLabel: "Select row",
			}),
		enableSorting: false,
		enableHiding: false,
	},
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
		cell: ({ row }) => h("div", {}, row.getValue("approved")),
		enableSorting: false,
	},
	{
		id: "reason",
		accessorKey: "reason",
		header: "Reason",
		cell: ({ row }) => h("div", {}, row.getValue("reason")),
		enableSorting: false,
	},
	{
		id: "proposed_causality_level",
		accessorKey: "proposed_causality_level",
		header: "Proposed Causality Level",
		cell: ({ row }) =>
			h("div", {}, row.getValue("proposed_causality_level")),
		enableSorting: false,
	},

	{
		id: "actions",
		enableHiding: false,
		cell: ({ row }) => {
			return h(TableActionsReview, {
				row: row.original,
				onExpand: row.toggleExpanded,
			});
		},
	},
];
</script>
