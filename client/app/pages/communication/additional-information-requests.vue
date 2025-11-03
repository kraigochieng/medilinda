<template>
	<div class="page-wrapper">
		<div class="flex items-center justify-between">
			<h1 class="text-2xl font-bold">Additional Information Requests</h1>
		</div>

		<UTabs :items="tabItems">
			<template #to-be-sent>
				<UTable
					:data="toBeSentRows"
					:columns="toBeSentColumns"
					:loading="toBeSentQuery.isPending.value"
					class="flex-1"
				/>
				<UPagination
					:total="toBeSentTotalCount"
					:items-per-page="toBeSentPageSize"
					:default-page="toBeSentCurrentPage"
					show-edges
					color="neutral"
					@update:page="(p) => (toBeSentCurrentPage = p)"
				/>
			</template>
			<template #already-sent>
				<UTable
					:data="alreadySentRows"
					:columns="alreadySentColumns"
					:loading="alreadySentQuery.isPending.value"
					class="flex-1"
				/>
				<UPagination
					:total="alreadySentTotalCount"
					:items-per-page="alreadySentPageSize"
					:default-page="alreadySentCurrentPage"
					show-edges
					color="neutral"
					@update:page="(p) => (alreadySentCurrentPage = p)"
				/>
			</template>
		</UTabs>

		<div
			class="flex justify-end px-3 py-3.5 border-t border-gray-200 dark:border-gray-700"
		></div>
	</div>
</template>

<script setup lang="ts">
import {
	fetchAlreadySentAdditionalInfoAlerts,
	fetchToBeSentAdditionalInfoAlerts,
} from "@/api/sms";
import type { CausalityAssessmentLevelEnum } from "~/types/adr";
import type { SMSMessageCountGetResponse } from "@/types/sms_message";
import type { TableColumn, TabsItem } from "@nuxt/ui";
import { useQuery, useQueryClient } from "@tanstack/vue-query";

const toast = useToast();
const route = useRoute();
const router = useRouter();
const queryClient = useQueryClient();

// --- State Management ---
const tabItems = ref<TabsItem[]>([
	{ slot: "to-be-sent", label: "To Be Sent" },
	{ slot: "already-sent", label: "Already Sent" },
]);

const alreadySentCurrentPage = ref(1);
const alreadySentPageSize = ref(20);

const toBeSentCurrentPage = ref(1);
const toBeSentPageSize = ref(20);

const filter = ref("");
const debouncedFilter = refDebounced(filter, 500);
const selectedRows = ref<SMSMessageCountGetResponse[]>([]);

// --- Data Fetching with vue-query ---
const toBeSentQuery = useQuery({
	queryKey: ["alerts", "toBeSent", toBeSentCurrentPage, toBeSentPageSize],
	queryFn: () =>
		fetchToBeSentAdditionalInfoAlerts({
			page: toBeSentCurrentPage.value,
			size: toBeSentPageSize.value,
			query: debouncedFilter.value,
			causality_level: "unclassified",
			has_been_sent: false,
		}),
});

const alreadySentQuery = useQuery({
	queryKey: [
		"alerts",
		"alreadySent",
		alreadySentCurrentPage,
		alreadySentPageSize,
		debouncedFilter,
	],
	queryFn: () =>
		fetchAlreadySentAdditionalInfoAlerts({
			page: alreadySentCurrentPage.value,
			size: alreadySentPageSize.value,
			query: debouncedFilter.value,
			causality_level: "unclassified",
			has_been_sent: true,
		}),
});

const alreadySentTotalCount = computed(
	() => alreadySentQuery.data.value?.total ?? 0
);
const toBeSentTotalCount = computed(() => toBeSentQuery.data.value?.total ?? 0);

const alreadySentRows = computed<SMSMessageCountGetResponse[]>(
	() => alreadySentQuery.data.value?.items ?? []
);
const toBeSentRows = computed<SMSMessageCountGetResponse[]>(
	() => toBeSentQuery.data.value?.items ?? []
);

// --- Actions with useMutation ---
// const sendAlertsMutation = useMutation({
// 	mutationFn: (adrId: string) => sendIndividualAlert(adrId),
// 	onSuccess: (data: SMSMessageGetResponse[], adrId) => {
// 		const rowData = selectedRows.value.find((r) => r.adr_id === adrId);
// 		data.forEach((message) => {
// 			toast.add({
// 				title: message.status,
// 				description: `Alert for ${rowData?.patient_name} to ${message.number}`,
// 				color: message.status_code === 100 ? "green" : "red",
// 			});
// 		});
// 	},
// 	onError: (error) => {
// 		toast.add({
// 			title: "An error occurred",
// 			description: error.message,
// 			color: "red",
// 		});
// 	},
// 	onSettled: () => {
// 		selectedRows.value = [];
// 		queryClient.invalidateQueries({ queryKey: ["alerts"] });
// 	},
// });

// function handleBulkSend() {
// 	selectedRows.value.forEach((row) => {
// 		sendAlertsMutation.mutate(row.adr_id);
// 	});
// }

const alreadySentColumns: TableColumn<SMSMessageCountGetResponse>[] = [
	{ accessorKey: "patient_name", header: "Patient Name" },
	{ accessorKey: "medical_institution_name", header: "Institution" },
	{ accessorKey: "medical_institution_mfl_code", header: "MFL Code" },
	{ accessorKey: "telephones", header: "Telephone(s)" },
	{
		accessorKey: "created_at",
		header: "Created At",
		cell: ({ row }) =>
			new Date(row.original.created_at).toLocaleDateString(),
	},
	{ accessorKey: "sms_count", header: "Messages Sent" },
];

const toBeSentColumns: TableColumn<SMSMessageCountGetResponse>[] = [
	{ accessorKey: "patient_name", header: "Patient Name" },
	{ accessorKey: "medical_institution_name", header: "Institution" },
	{ accessorKey: "medical_institution_mfl_code", header: "MFL Code" },
	{ accessorKey: "telephones", header: "Telephone(s)" },
	{
		accessorKey: "created_at",
		header: "Created At",
		cell: ({ row }) =>
			new Date(row.original.created_at).toLocaleDateString(),
	},
];

useHead({
	title: "Communication | Additional Information Requests | Medilinda",
});
</script>
