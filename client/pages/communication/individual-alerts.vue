<template>
	<div class="page-wrapper">
		<Tabs v-model="activeTab">
			<div class="flex space-x-4">
				<h1 class="text-4xl font-bold">Individual Alerts</h1>
				<TabsList value="to-be-sent">
					<TabsTrigger value="to-be-sent"> To Be Sent </TabsTrigger>
					<TabsTrigger value="already-sent">
						Already Sent
					</TabsTrigger>
				</TabsList>
			</div>

			<TabsContent value="to-be-sent">
				<DataTable
					v-if="toBeSentTableStatus == 'success'"
					title=""
					:data="toBeSentTableData?.items"
					:columns="toBeSentColumns"
					:currentPage="toBeSentCurrentPage"
					:pageSize="toBeSentPageSize"
					:totalCount="toBeSentTotalCount"
					@pageChange="handleToBeSentPageChange"
					@pageSizeChange="handleToBeSentPageSizeChange"
				>
					<template
						#selectionActions="{
							allSelected,
							someSelected,
							selectedRows,
						}"
					>
						<Input
							type="text"
							placeholder="Filter..."
							class="w-max"
							ref="toBeSentFilterInputRef"
							v-model="toBeSentTableFilter"
						/>
						<Button
							v-if="allSelected || someSelected"
							@click="handleBulkSend(selectedRows)"
						>
							Bulk Send ({{ selectedRows.length }})
						</Button>
					</template>
				</DataTable>

				<div
					v-if="toBeSentTableError"
					class="mt-4 p-4 rounded bg-red-100 text-red-800"
				>
					<p>{{ toBeSentTableError }}</p>
				</div>
			</TabsContent>
			<TabsContent value="already-sent">
				<DataTable
					v-if="alreadySentTableStatus == 'success'"
					title=""
					:data="alreadySentTableData?.items"
					:columns="alreadySentColumns"
					:currentPage="alreadySentCurrentPage"
					:pageSize="alreadySentPageSize"
					:totalCount="alreadySentTotalCount"
					@pageChange="handleAlreadySentPageChange"
					@pageSizeChange="handleAlreadySentPageSizeChange"
				>
					<template
						#selectionActions="{
							allSelected,
							someSelected,
							selectedRows,
						}"
					>
						<Input
							type="text"
							placeholder="Filter..."
							class="w-max"
							ref="alreadySentFilterInputRef"
							v-model="alreadySentTableFilter"
						/>
						<Button
							v-if="allSelected || someSelected"
							@click="handleBulkSend(selectedRows)"
						>
							Bulk Send ({{ selectedRows.length }})
						</Button>
					</template>
				</DataTable>

				<div
					v-if="alreadySentTableError"
					class="mt-4 p-4 rounded bg-red-100 text-red-800"
				>
					<p>{{ alreadySentTableError }}</p>
				</div>
			</TabsContent>
		</Tabs>
	</div>
</template>

<script setup lang="ts">
import TableActionsIndividualAlerts from "@/components/table/actions/IndividualAlerts.vue";
import Checkbox from "@/components/ui/checkbox/Checkbox.vue";
import { useToast } from "@/components/ui/toast";
import ToastAction from "@/components/ui/toast/ToastAction.vue";
import type { PaginatedResponseInterface } from "@/types/pagination";
import type { SMSMessageCountGetResponse } from "@/types/sms_message";
import { type ColumnDef, type Row } from "@tanstack/vue-table";

const { toast } = useToast();
const alreadySentTableData =
	ref<PaginatedResponseInterface<SMSMessageCountGetResponse> | null>(null);
const alreadySentTableStatus = ref<"idle" | "error" | "success" | "pending">(
	"idle"
);
const alreadySentTableError = ref<unknown | null>(null);

const alreadySentCurrentPage = ref(1);
const alreadySentPageSize = ref(20);

const alreadySentTotalCount = computed(
	() => alreadySentTableData.value?.total || 0
);

const toBeSentTableData =
	ref<PaginatedResponseInterface<SMSMessageCountGetResponse> | null>(null);
const toBeSentTableStatus = ref<"idle" | "error" | "success" | "pending">(
	"idle"
);
const toBeSentTableError = ref<unknown | null>(null);

const toBeSentCurrentPage = ref(1);
const toBeSentPageSize = ref(20);

const toBeSentTotalCount = computed(
	() => alreadySentTableData.value?.total || 0
);

const alreadySentFilterInputRef = ref<HTMLInputElement | null>(null);
const toBeSentFilterInputRef = ref<HTMLInputElement | null>(null);

const alreadySentTableFilter = ref<string>("");

const toBeSentTableFilter = ref<string>("");

const authStore = useAuthStore();

const route = useRoute();
const activeTab = ref(
	route.query.tab === "already-sent" ? "already-sent" : "to-be-sent"
);

onMounted(async () => {
	await fetchAlreadySentTableData();
	await fetchToBeSentTableData();
});

async function handleBulkSend(rows: Row<SMSMessageCountGetResponse>[]) {
	rows.map(async (row) => {
		// const count = rows.length;
		// toast({
		// 	title: `Bulk send triggered`,
		// 	description: `${count} alerts sent.`,
		// });

		const response = await $fetch<SMSMessageGetResponse[]>(
			`${useRuntimeConfig().public.serverApi}/send_individual_alert`,
			{
				method: "POST",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
				body: {
					adr_id: row.original.adr_id,
				},
			}
		);
		response.map(async (message) => {
			if (message.status_code == 100) {
				console.log("Toast message:", message);
				toast({
					title: message.status,
					description: h("div", [
						h(
							"p",
							`Medical Institution Name: ${row.original.medical_institution_name}`
						),
						h("p", `Medical Institution Number: ${message.number}`),
						h("p", `Patient Name: ${row.original.patient_name}`),
					]),
				});
			} else {
				toast({
					title: message.status,
					description: message.content,
					variant: "destructive",
					action: h(
						ToastAction,
						{ altText: "Error" },
						{ default: () => "Try again" }
					),
				});
				await new Promise((resolve) => setTimeout(resolve, 500));
			}
		});
	});

	setTimeout(() => {
		window.location.reload();
	}, 2500);
}

const fetchAlreadySentTableData = async () => {
	alreadySentTableStatus.value = "pending";
	try {
		const data = await $fetch<
			PaginatedResponseInterface<SMSMessageCountGetResponse>
		>(
			`${
				useRuntimeConfig().public.serverApi
			}/adrs_with_individual_alerts`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
				params: {
					page: alreadySentCurrentPage.value,
					size: alreadySentPageSize.value,
					query: alreadySentTableFilter.value,
				},
			}
		);

		if (!data) throw new Error("No ADRs received");

		alreadySentTableData.value = data;

		alreadySentTableStatus.value = "success";
	} catch (error) {
		alreadySentTableError.value = error;
		alreadySentTableStatus.value = "error";
	}
};

const fetchToBeSentTableData = async () => {
	toBeSentTableStatus.value = "pending";
	try {
		const data = await $fetch<
			PaginatedResponseInterface<SMSMessageCountGetResponse>
		>(
			`${
				useRuntimeConfig().public.serverApi
			}/adrs_to_be_sent_individual_alerts`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
				params: {
					page: toBeSentCurrentPage.value,
					size: toBeSentPageSize.value,
					query: toBeSentTableFilter.value,
				},
			}
		);

		if (!data) throw new Error("No ADRs received");

		toBeSentTableData.value = data;

		toBeSentTableStatus.value = "success";
	} catch (error) {
		toBeSentTableError.value = error;
		toBeSentTableStatus.value = "error";
	}
};

watch([alreadySentCurrentPage, alreadySentPageSize], () => {
	fetchAlreadySentTableData();
});

watch([toBeSentCurrentPage, toBeSentPageSize], () => {
	fetchToBeSentTableData();
});

watch(alreadySentTableFilter, (newValue, oldValue) => {
	fetchAlreadySentTableData();
	alreadySentFilterInputRef.value?.focus();
});

watch(toBeSentTableFilter, (newValue, oldValue) => {
	fetchToBeSentTableData();
	toBeSentFilterInputRef.value?.focus();
});

function handleAlreadySentPageChange(page: number) {
	alreadySentCurrentPage.value = page;
}

function handleToBeSentPageChange(page: number) {
	toBeSentCurrentPage.value = page;
}

const handleAlreadySentPageSizeChange = (size: number) => {
	alreadySentPageSize.value = size;
	alreadySentCurrentPage.value = 1;
};

const handleToBeSentPageSizeChange = (size: number) => {
	toBeSentPageSize.value = size;
	toBeSentCurrentPage.value = 1;
};

function formatTime(isoString: string): string {
	const date = new Date(isoString);
	return new Intl.DateTimeFormat("en-US", {
		hour: "numeric",
		minute: "numeric",
		hour12: true,
	}).format(date);
}

const alreadySentColumns: ColumnDef<SMSMessageCountGetResponse>[] = [
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
		cell: ({ row }) => {
			const val = row.getValue("medical_institution_mfl_code");
			// Narrow unknown type safely
			if (val === "0") {
				return h("em", {}, "BLANK");
			}

			// Cast to string or number for safe rendering
			if (typeof val === "string" || typeof val === "number") {
				return h("div", {}, val);
			}

			// Fallback (optional)
			return h("div", {}, "");
		},
		enableSorting: true,
	},

	{
		id: "sms_count",
		accessorKey: "sms_count",
		header: "Messages Sent",
		cell: ({ row }) => h("div", {}, row.getValue("sms_count")),
		enableSorting: true,
	},
	{
		id: "telephones",
		accessorKey: "telephones",
		header: "Telephone(s)",
		cell: ({ row }) => h("div", {}, row.getValue("telephones")),
		enableSorting: true,
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
			h("div", {}, `${row.original.created_at.slice(0, 10)}`),
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
	{
		id: "actions",
		enableHiding: false,
		cell: ({ row }) => {
			return h(TableActionsIndividualAlerts, {
				row: row.original,
				onExpand: row.toggleExpanded,
			});
		},
	},
];

const toBeSentColumns: ColumnDef<SMSMessageCountGetResponse>[] = [
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
		cell: ({ row }) => {
			const val = row.getValue("medical_institution_mfl_code");
			// Narrow unknown type safely
			if (val === "0") {
				return h("em", {}, "BLANK");
			}

			// Cast to string or number for safe rendering
			if (typeof val === "string" || typeof val === "number") {
				return h("div", {}, val);
			}

			// Fallback (optional)
			return h("div", {}, "");
		},
		enableSorting: true,
	},
	{
		id: "telephones",
		accessorKey: "telephones",
		header: "Telephone(s)",
		cell: ({ row }) => h("div", {}, row.getValue("telephones")),
		enableSorting: true,
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
			h("div", {}, `${row.original.created_at.slice(0, 10)}`),
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
	{
		id: "actions",
		enableHiding: false,
		cell: ({ row }) => {
			return h(TableActionsIndividualAlerts, {
				row: row.original,
				onExpand: row.toggleExpanded,
			});
		},
	},
];

watch(activeTab, (val) => {
	const router = useRouter();
	router.replace({ query: { ...route.query, tab: val } });
});

useHead({ title: "Communication | Individual Alerts | MediLinda" });
</script>
