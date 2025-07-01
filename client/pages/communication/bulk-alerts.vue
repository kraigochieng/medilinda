<template>
	<div class="page-wrapper">
		<DataTable
			v-if="tableStatus == 'success'"
			title="Bulk Alerts Communication"
			:data="tableData?.items"
			:columns="columns"
			:currentPage="currentPage"
			:pageSize="pageSize"
			:totalCount="totalCount"
			@pageChange="handlePageChange"
			@pageSizeChange="handlePageSizeChange"
		/>

		<div v-if="tableError" class="mt-4 p-4 rounded bg-red-100 text-red-800">
			<p>{{ tableError }}</p>
		</div>
	</div>
</template>

<script setup lang="ts">
import Checkbox from "@/components/ui/checkbox/Checkbox.vue";
import type { PaginatedResponseInterface } from "@/types/pagination";
import type { SMSMessageCountGetResponse } from "@/types/sms_message";
import { type ColumnDef } from "@tanstack/vue-table";

const tableData =
	ref<PaginatedResponseInterface<SMSMessageCountGetResponse> | null>(null);
const tableStatus = ref<"idle" | "error" | "success" | "pending">("idle");
const tableError = ref<unknown | null>(null);

const currentPage = ref(1);
const pageSize = ref(20);

const totalCount = computed(() => tableData.value?.total || 0);

const authStore = useAuthStore();

onMounted(async () => {
	await fetchTableData();
});

const fetchTableData = async () => {
	tableStatus.value = "pending";
	try {
		const data = await $fetch<
			PaginatedResponseInterface<SMSMessageCountGetResponse>
		>(`${useRuntimeConfig().public.serverApi}/sms_message_count`, {
			method: "GET",
			headers: {
				Authorization: `Bearer ${authStore.accessToken}`,
			},
			params: {
				sms_type: "bulk alert",
				page: currentPage.value,
                size: pageSize.value
			},
		});

		if (!data) throw new Error("No causality data received");

		tableData.value = data;

		tableStatus.value = "success";
	} catch (error) {
		tableError.value = error;
		tableStatus.value = "error";
	}
};

watch([currentPage, pageSize], () => {
	fetchTableData();
});

function handlePageChange(page: number) {
	currentPage.value = page;
}

const handlePageSizeChange = (size: number) => {
	pageSize.value = size;
	currentPage.value = 1;
};

const columns: ColumnDef<SMSMessageCountGetResponse>[] = [
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
		enableSorting: true,
	},
	{
		id: "medical_institution_name",
		accessorKey: "medical_institution_name",
		header: "Medical Institution Name",
		cell: ({ row }) =>
			h("div", {}, row.getValue("medical_institution_name")),
		enableSorting: true,
	},
	{
		id: "medical_institution_mfl_code",
		accessorKey: "medical_institution_mfl_code",
		header: "Medical Institution MFL Code",
		cell: ({ row }) =>
			h("div", {}, row.getValue("medical_institution_mfl_code")),
		enableSorting: true,
	},
	
	{
		id: "sms_type",
		accessorKey: "sms_type",
		header: "SMS Type",
		cell: ({ row }) => h("div", {}, row.getValue("sms_type")),
		enableSorting: true,
	},
	{
		id: "sms_count",
		accessorKey: "sms_count",
		header: "SMS Count",
		cell: ({ row }) => h("div", {}, row.getValue("sms_count")),
		enableSorting: true,
	},

	// {
	// 	accessorKey:
	// 		"causality_assessment_levels.causality_assessment_level_value",
	// 	header: "Causality Assessment Level",
	// 	cell: ({ row }) =>
	// 		h(
	// 			"div",
	// 			{},
	// 			row.getValue(
	// 				"causality_assessment_levels"
	// 			)
	// 		),
	// },
	// {
	// 	id: "actions",
	// 	enableHiding: false,
	// 	cell: ({ row }) => {
	// 		return h(TableActionsAdr, {
	// 			row: row.original,
	// 			onExpand: row.toggleExpanded,
	// 		});
	// 	},
	// },
];

useHead({ title: "Communication | Bulk Alerts | MediLinda" });
</script>
