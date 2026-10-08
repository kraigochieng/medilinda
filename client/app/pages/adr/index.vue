<template>
	<div class="space-y-4">
		<div class="flex items-center justify-between gap-4">
			<div>
				<h1 class="text-2xl font-bold">ADRs</h1>
				<p class="text-sm text-muted" aria-live="polite">{{ summary }}</p>
			</div>
			<div class="flex items-center gap-2">
				<UButton
					to="/adr/deleted"
					color="neutral"
					variant="ghost"
					icon="i-lucide-trash-2"
					label="Recently deleted"
				/>
				<UButton to="/adr/add" icon="i-lucide-plus" label="Add ADR" />
			</div>
		</div>

		<div class="flex flex-wrap items-center gap-2">
			<UInput
				v-model="state.query"
				icon="i-lucide-search"
				placeholder="Search patient, address, ward or number"
				aria-label="Search ADRs"
				class="w-full sm:w-80"
			>
				<template v-if="state.query" #trailing>
					<UButton
						color="neutral"
						variant="link"
						size="sm"
						icon="i-lucide-circle-x"
						aria-label="Clear search"
						@click="state.query = ''"
					/>
				</template>
			</UInput>
			<USelect
				v-model="state.causality"
				:items="CAUSALITY_OPTIONS"
				aria-label="Filter by causality level"
				class="w-44"
			/>
			<USelect
				v-model="state.review"
				:items="REVIEW_STATUS_OPTIONS"
				aria-label="Filter by review status"
				class="w-44"
			/>
			<UButton
				v-if="filtersActive"
				color="neutral"
				variant="ghost"
				icon="i-lucide-x"
				label="Clear filters"
				@click="clearFilters"
			/>
		</div>

		<UAlert
			v-if="isError"
			color="error"
			variant="subtle"
			icon="i-lucide-triangle-alert"
			title="Could not load ADRs"
			:description="errorMessage"
			:actions="[{ label: 'Try again', color: 'neutral', onClick: () => refetch() }]"
		/>

		<UTable
			:data="rows"
			:columns="columns"
			:loading="isFetching"
			:ui="{ tr: 'cursor-pointer hover:bg-elevated/50' }"
			@select="onSelect"
		>
			<template #causality_assessment_level_value-cell="{ row }">
				<UBadge
					v-if="row.original.causality_assessment_level_value"
					:class="CAUSALITY_BADGE_CLASS[row.original.causality_assessment_level_value]"
				>
					{{ capitalize(row.original.causality_assessment_level_value) }}
				</UBadge>
				<span v-else class="text-muted">—</span>
			</template>

			<template #review-cell="{ row }">
				<div class="flex items-center gap-2">
					<UBadge
						:color="REVIEW_STATE_BADGE[reviewState(row.original)].color"
						variant="subtle"
						:icon="REVIEW_STATE_BADGE[reviewState(row.original)].icon"
					>
						{{ REVIEW_STATE_BADGE[reviewState(row.original)].label }}
					</UBadge>
					<span
						v-if="row.original.approved_reviews + row.original.unapproved_reviews > 0"
						class="text-xs text-muted"
					>
						{{ row.original.approved_reviews }} approved ·
						{{ row.original.unapproved_reviews }} not
					</span>
				</div>
			</template>

			<template #created_at-cell="{ row }">
				{{ formatDateTime(row.original.created_at) }}
			</template>

			<template #actions-cell="{ row }">
				<div class="text-right" @click.stop>
					<UDropdownMenu :items="rowItems(row.original)" :content="{ align: 'end' }">
						<UButton
							icon="i-lucide-ellipsis-vertical"
							color="neutral"
							variant="ghost"
							:aria-label="`Actions for ${row.original.patient_name}`"
						/>
					</UDropdownMenu>
				</div>
			</template>

			<template #loading>
				<div class="space-y-3 py-2">
					<USkeleton v-for="n in 5" :key="n" class="h-8 w-full" />
				</div>
			</template>

			<template #empty>
				<div class="flex flex-col items-center gap-3 py-10 text-center">
					<UIcon
						:name="filtersActive ? 'i-lucide-search-x' : 'i-lucide-file-heart'"
						class="size-10 text-muted"
					/>
					<p class="font-medium">
						{{ filtersActive ? "No ADRs match your search" : "No ADRs yet" }}
					</p>
					<UButton
						v-if="filtersActive"
						color="neutral"
						variant="outline"
						label="Clear filters"
						@click="clearFilters"
					/>
					<UButton v-else to="/adr/add" icon="i-lucide-plus" label="Add the first ADR" />
				</div>
			</template>
		</UTable>

		<div v-if="totalCount > PAGE_SIZE" class="flex justify-center">
			<UPagination
				v-model:page="state.page"
				:total="totalCount"
				:items-per-page="PAGE_SIZE"
				show-edges
				color="neutral"
			/>
		</div>
	</div>

	<UModal v-model:open="deleteOpen" title="Delete this ADR?" :dismissible="!deleting">
		<template #body>
			<p>
				This removes the report for
				<strong>{{ toDelete?.patient_name }}</strong>
				together with its causality assessments and reviews.
			</p>
			<p class="mt-2 text-sm text-muted">
				It is kept in the history, and you can undo it right after.
			</p>
		</template>
		<template #footer>
			<div class="flex w-full justify-end gap-2">
				<UButton
					color="neutral"
					variant="outline"
					label="Cancel"
					:disabled="deleting"
					@click="toDelete = null"
				/>
				<UButton color="error" label="Delete" :loading="deleting" @click="confirmDelete" />
			</div>
		</template>
	</UModal>
</template>

<script setup lang="ts">
import { deleteAdrById, fetchAdrsWithCausalityAndReviewCount, restoreAdrById } from "@/api/adr";
import type { ADRWithCausalityLevelAndReviewCountInterface as Row } from "@/types/adr";
import type { TableColumn, TableRow } from "@nuxt/ui";
import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/vue-query";
import { capitalize } from "lodash-es";
import {
	CAUSALITY_BADGE_CLASS,
	CAUSALITY_OPTIONS,
	DEFAULT_LIST_STATE,
	REVIEW_STATE_BADGE,
	REVIEW_STATUS_OPTIONS,
	buildListParams,
	formatDateTime,
	hasActiveFilters,
	parseListQuery,
	reviewState,
	serializeListQuery,
} from "~/utils/adr-table";

const PAGE_SIZE = 20;

const route = useRoute();
const router = useRouter();
const toast = useToast();
const queryClient = useQueryClient();

// Search, filters and page live in the URL, so Back from an ADR returns here.
const state = reactive({ ...parseListQuery(route.query) });
const debouncedQuery = refDebounced(toRef(state, "query"), 400);
const applied = computed(() => ({ ...state, query: debouncedQuery.value }));

watch([debouncedQuery, () => state.causality, () => state.review], () => {
	state.page = 1;
});
watch(applied, (value) => router.replace({ query: serializeListQuery(value) }));

const filtersActive = computed(() => hasActiveFilters(applied.value));

function clearFilters() {
	Object.assign(state, { ...DEFAULT_LIST_STATE });
}

const { data, isFetching, isError, error, refetch } = useQuery({
	queryKey: computed(() => ["adrs", buildListParams(applied.value, PAGE_SIZE)]),
	queryFn: () => fetchAdrsWithCausalityAndReviewCount(buildListParams(applied.value, PAGE_SIZE)),
	placeholderData: keepPreviousData,
});

const rows = computed<Row[]>(() => data.value?.items ?? []);
const totalCount = computed(() => data.value?.total ?? 0);
const errorMessage = computed(
	() => (error.value as Error | null)?.message ?? "Check your connection and try again.",
);
const summary = computed(() => {
	if (!data.value) return "Loading…";
	const noun = totalCount.value === 1 ? "ADR" : "ADRs";
	return filtersActive.value
		? `${totalCount.value} matching ${noun}`
		: `${totalCount.value} ${noun}`;
});

const columns: TableColumn<Row>[] = [
	{ accessorKey: "patient_name", header: "Patient" },
	{ accessorKey: "causality_assessment_level_value", header: "Causality level" },
	{ id: "review", header: "Review" },
	{ accessorKey: "created_by", header: "Created by" },
	{ accessorKey: "created_at", header: "Created" },
	{ id: "actions" },
];

function onSelect(row: TableRow<Row>) {
	navigateTo(`/adr/${row.original.adr_id}`);
}

function rowItems(adr: Row) {
	return [
		[
			{ label: "View", icon: "i-lucide-eye", to: `/adr/${adr.adr_id}` },
			{ label: "Edit", icon: "i-lucide-pencil", to: `/adr/${adr.adr_id}/edit` },
		],
		[
			{
				label: "Delete",
				icon: "i-lucide-trash-2",
				color: "error" as const,
				onSelect: () => (toDelete.value = adr),
			},
		],
	];
}

// ---- Delete, with undo -------------------------------------------------

const toDelete = ref<Row | null>(null);
const deleteOpen = computed({
	get: () => toDelete.value !== null,
	set: (open: boolean) => {
		if (!open && !deleting.value) toDelete.value = null;
	},
});

const restoreMutation = useMutation({
	mutationFn: (adr: Row) => restoreAdrById(adr.adr_id),
	onSuccess: (_, adr) => {
		queryClient.invalidateQueries({ queryKey: ["adrs"] });
		toast.add({ title: "ADR restored", description: adr.patient_name, color: "success" });
	},
	onError: (err: Error) =>
		toast.add({ title: "Could not restore the ADR", description: err.message, color: "error" }),
});

const deleteMutation = useMutation({
	mutationFn: (adr: Row) => deleteAdrById(adr.adr_id),
	onSuccess: (_, adr) => {
		toDelete.value = null;
		queryClient.invalidateQueries({ queryKey: ["adrs"] });
		toast.add({
			title: "ADR deleted",
			description: adr.patient_name,
			color: "neutral",
			duration: 10000,
			actions: [
				{
					label: "Undo",
					color: "neutral",
					variant: "outline",
					onClick: () => restoreMutation.mutate(adr),
				},
			],
		});
	},
	onError: (err: Error) =>
		toast.add({ title: "Could not delete the ADR", description: err.message, color: "error" }),
});

const deleting = computed(() => deleteMutation.isPending.value);

function confirmDelete() {
	if (toDelete.value) deleteMutation.mutate(toDelete.value);
}

useHead({ title: "ADRs | MediLinda" });
</script>
