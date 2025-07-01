<template>
	<div class="page-wrapper">
		<p class="page-title">ADR Management</p>
		<Button class="w-full my-4">
			<NuxtLink to="/adr/add">Add Adr</NuxtLink>
		</Button>
		<LoadingMedilinda label="Loading ADRs" v-if="status == 'pending'" />
		<DataTable
			v-if="status == 'success'"
			title=""
			:data="data?.items"
			:columns="columns"
			:currentPage="currentPage"
			:pageSize="pageSize"
			:totalCount="totalCount"
			@pageChange="handlePageChange"
			@pageSizeChange="handlePageSizeChange"
		>
			<template
				#selectionActions="{ allSelected, someSelected, selectedRows }"
			>
				<Input
					type="text"
					placeholder="Filter..."
					class="w-max"
					ref="filterInputRef"
					v-model="debouncedTableFilter"
				/>
				<Button v-if="allSelected || someSelected">
					Delete ({{ selectedRows.length }})
				</Button>
			</template>
		</DataTable>

		<div v-if="error" class="mt-4 p-4 rounded bg-red-100 text-red-800">
			<p>{{ error }}</p>
		</div>
	</div>
</template>

<script setup lang="ts">
import TableActionsAdr from "@/components/table/actions/Adr.vue";
import { useAuthStore } from "@/stores/auth";
import { capitalize } from "lodash";

import Button from "@/components/ui/button/Button.vue";
import Checkbox from "@/components/ui/checkbox/Checkbox.vue";
import type { ADRWithCausalityLevelAndReviewCountInterface } from "@/types/adr";
import type { PaginatedResponseInterface } from "@/types/pagination";
import { type ColumnDef } from "@tanstack/vue-table";

// Fetch ADR Data
const authStore = useAuthStore();

// Create reactive variables for data, status, and error
const data =
	ref<PaginatedResponseInterface<ADRWithCausalityLevelAndReviewCountInterface> | null>(
		null
	);
const status = ref<"pending" | "success" | "error">("pending");
const error = ref<string | null>(null);

const filterInputRef = ref<HTMLInputElement | null>(null);

const currentPage = ref(1);
const pageSize = ref(20);
const tableFilter = ref<string>("");
const debouncedTableFilter = refDebounced(tableFilter, 1000);

const totalCount = computed(() => data.value?.total || 0);

// Fetch data when component is mounted
onMounted(async () => {
	await fetchADRData();
});

const fetchADRData = async () => {
	try {
		status.value = "pending";
		// Using $fetch for API call
		data.value = await $fetch(
			`${
				useRuntimeConfig().public.serverApi
			}/adrs_with_causality_and_review_count`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
				params: {
					page: currentPage.value,
					size: pageSize.value,
					query: debouncedTableFilter.value,
				},
			}
		);

		status.value = "success";
	} catch (err: any) {
		status.value = "error";
		error.value = err.message || "Something went wrong";
	}
};

function formatTime(isoString: string): string {
	const date = new Date(isoString);
	return new Intl.DateTimeFormat("en-US", {
		hour: "numeric",
		minute: "numeric",
		hour12: true,
	}).format(date);
}

watch([currentPage, pageSize], () => {
	fetchADRData();
});

watch(debouncedTableFilter, (newValue, oldValue) => {
	fetchADRData();
	filterInputRef.value?.focus();
});

function handlePageChange(page: number) {
	currentPage.value = page;
}

const handlePageSizeChange = (size: number) => {
	pageSize.value = size;
	currentPage.value = 1;
};

const columns: ColumnDef<ADRWithCausalityLevelAndReviewCountInterface>[] = [
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
		id: "patient_name",
		accessorKey: "patient_name",
		header: "Patient Name",
		cell: ({ row }) => h("div", {}, row.getValue("patient_name")),
	},

	// {
	// 	id: "causality_assessment_level_value",
	// 	accessorKey: "causality_assessment_level_value",
	// 	header: "Causality Asssessment Level",
	// 	cell: ({ row }) =>
	// 		h("div", {}, row.getValue("causality_assessment_level_value")),
	// 	enableSorting: false,
	// },
	{
		id: "causality_assessment_level_value",
		accessorKey: "causality_assessment_level_value",
		header: "Causality Asssessment Level",
		cell: ({ row }) => {
			let color = "";
			if (row.original.causality_assessment_level_value == "certain") {
				color = "bg-red-500 text-white";
			} else if (
				row.original.causality_assessment_level_value == "likely"
			) {
				color = "bg-red-400";
			} else if (
				row.original.causality_assessment_level_value == "possible"
			) {
				color = "bg-yellow-500";
			} else if (
				row.original.causality_assessment_level_value == "unlikely"
			) {
				color = "bg-yellow-300";
			} else if (
				row.original.causality_assessment_level_value == "unclassified"
			) {
				color = "bg-slate-500 text-white";
			} else if (
				row.original.causality_assessment_level_value ==
				"unclassifiable"
			) {
				color = "bg-slate-300";
			}

			return h(
				"div",
				{ class: `badge ${color}` },
				capitalize(row.getValue("causality_assessment_level_value"))
			);
		},

		enableSorting: false,
	},
	// {
	// 	id: "review_count",
	// 	accessorKey: "review_count",
	// 	header: "Reviews (Approved | Not Approved)",
	// 	cell: ({ row }) =>
	// 		h(
	// 			"div",
	// 			{},
	// 			`${row.original.approved_reviews} | ${row.original.unapproved_reviews}`
	// 		),
	// },
	{
		id: "review_count",
		accessorKey: "review_count",
		header: "Reviews (Approved | Not Approved)",
		cell: ({ row }) => {
			const approved = row.original.approved_reviews;
			const unapproved = row.original.unapproved_reviews;

			let iconName = "lucide:minus";
			let iconColor = "text-yellow-600";

			if (approved > unapproved) {
				iconName = "lucide:check";
				iconColor = "text-green-600";
			} else if (approved < unapproved) {
				iconName = "lucide:x";
				iconColor = "text-red-600";
			}

			const Icon = resolveComponent("Icon");

			return h("div", { class: "flex items-center gap-2" }, [
				h(Icon, { name: iconName, class: `w-6 h-6 ${iconColor}` }),
				h("span", {}, `${approved} | ${unapproved}`),
			]);
		},
	},
	{
		id: "created_by",
		accessorKey: "created_by",
		header: "Created By",
		cell: ({ row }) => h("div", {}, row.getValue("created_by")),
		enableSorting: false,
	},
	// {
	// 	id: "created_at",
	// 	accessorKey: "created_at",
	// 	header: "Created At",
	// 	cell: ({ row }) =>
	// 		h(
	// 			"div",
	// 			{},
	// 			`${row.original.created_at.slice(0, 10)} ${formatTime(
	// 				row.original.created_at
	// 			)}`
	// 		),
	// 	enableSorting: true,
	// },
	{
		id: "created_at",
		accessorKey: "created_at",
		header: "Created At",
		cell: ({ row }) =>
			h(
				"div",
				{},
				`${row.original.created_at.slice(0, 10)}`
			),
		enableSorting: true,
	},
	{
		id: "actions",
		enableHiding: false,
		cell: ({ row }) => {
			return h(TableActionsAdr, {
				row: row.original,
				onExpand: row.toggleExpanded,
			});
		},
	},
];

useHead({ title: "ADR | MediLinda" });
</script>
