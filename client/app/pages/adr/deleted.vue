<template>
	<div class="space-y-4">
		<div class="flex items-center justify-between gap-4">
			<div>
				<h1 class="text-2xl font-bold">Recently deleted ADRs</h1>
				<p class="text-sm text-muted">
					Deleted ADRs are kept, with their assessments and reviews, so they can be restored.
				</p>
			</div>
			<UButton to="/adr" color="neutral" variant="outline" icon="i-lucide-arrow-left" label="Back to ADRs" />
		</div>

		<UAlert
			v-if="isError"
			color="error"
			variant="subtle"
			icon="i-lucide-triangle-alert"
			title="Could not load deleted ADRs"
			:description="errorMessage"
			:actions="[{ label: 'Try again', color: 'neutral', onClick: () => refetch() }]"
		/>

		<UTable :data="rows" :columns="columns" :loading="isFetching">
			<template #patient-cell="{ row }">
				{{ row.original.summary?.patient_name ?? "Unknown patient" }}
			</template>
			<template #deleted_by-cell="{ row }">
				{{ actorName(row.original) }}
			</template>
			<template #at-cell="{ row }">
				{{ formatDateTime(row.original.at) }}
			</template>
			<template #actions-cell="{ row }">
				<div class="text-right">
					<UButton
						icon="i-lucide-rotate-ccw"
						color="neutral"
						variant="outline"
						label="Restore"
						:loading="restoringId === row.original.entity_id"
						@click="restore(row.original)"
					/>
				</div>
			</template>
			<template #loading>
				<div class="space-y-3 py-2">
					<USkeleton v-for="n in 4" :key="n" class="h-8 w-full" />
				</div>
			</template>
			<template #empty>
				<div class="flex flex-col items-center gap-2 py-10 text-center">
					<UIcon name="i-lucide-trash-2" class="size-10 text-muted" />
					<p class="font-medium">Nothing has been deleted</p>
				</div>
			</template>
		</UTable>

		<div v-if="total > PAGE_SIZE" class="flex justify-center">
			<UPagination v-model:page="page" :total="total" :items-per-page="PAGE_SIZE" color="neutral" />
		</div>
	</div>
</template>

<script setup lang="ts">
import { restoreAdrById } from "@/api/adr";
import { fetchDeletedAdrs } from "@/api/audit";
import type { AuditEvent } from "@/types/audit";
import type { TableColumn } from "@nuxt/ui";
import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/vue-query";
import { formatDateTime } from "~/utils/adr-table";
import { actorName } from "~/utils/audit-events";

const PAGE_SIZE = 20;

const toast = useToast();
const queryClient = useQueryClient();
const page = ref(1);

const { data, isFetching, isError, error, refetch } = useQuery({
	queryKey: computed(() => ["adrs-deleted", page.value]),
	queryFn: () => fetchDeletedAdrs({ page: page.value, size: PAGE_SIZE }),
	placeholderData: keepPreviousData,
});

const rows = computed<AuditEvent[]>(() => data.value?.items ?? []);
const total = computed(() => data.value?.total ?? 0);
const errorMessage = computed(
	() => (error.value as Error | null)?.message ?? "Check your connection and try again."
);

const columns: TableColumn<AuditEvent>[] = [
	{ id: "patient", header: "Patient" },
	{ id: "deleted_by", header: "Deleted by" },
	{ id: "at", header: "Deleted" },
	{ id: "actions" },
];

const restoringId = ref<string | null>(null);

const restoreMutation = useMutation({
	mutationFn: (event: AuditEvent) => restoreAdrById(event.entity_id),
	onMutate: (event) => (restoringId.value = event.entity_id),
	onSettled: () => (restoringId.value = null),
	onSuccess: (_, event) => {
		queryClient.invalidateQueries({ queryKey: ["adrs-deleted"] });
		queryClient.invalidateQueries({ queryKey: ["adrs"] });
		toast.add({
			title: "ADR restored",
			description: event.summary?.patient_name,
			color: "success",
			actions: [{ label: "Open", color: "neutral", variant: "outline", to: `/adr/${event.entity_id}` }],
		});
	},
	onError: (err: Error) =>
		toast.add({ title: "Could not restore the ADR", description: err.message, color: "error" }),
});

function restore(event: AuditEvent) {
	restoreMutation.mutate(event);
}

useHead({ title: "Recently deleted ADRs | MediLinda" });
</script>
