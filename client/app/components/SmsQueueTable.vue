<template>
	<div class="space-y-4">
		<UInput
			v-model="search"
			icon="i-lucide-search"
			placeholder="Search by patient name"
			aria-label="Search by patient name"
			class="w-full sm:w-80"
		/>

		<UAlert
			v-if="query.isError.value"
			color="error"
			variant="subtle"
			icon="i-lucide-triangle-alert"
			title="Could not load this list"
			description="Check your connection and try again."
			:actions="[{ label: 'Try again', color: 'neutral', onClick: () => query.refetch() }]"
		/>

		<template v-else>
			<UTable
				:data="rows"
				:columns="columns"
				:loading="query.isFetching.value"
				class="rounded-lg border border-default"
			>
				<template #empty>
					<p class="py-6 text-center text-sm text-muted">
						{{ search.trim() ? "No patient matches that name." : emptyText }}
					</p>
				</template>
			</UTable>

			<div v-if="total > pageSize" class="flex justify-center">
				<UPagination
					v-model:page="page"
					:total="total"
					:items-per-page="pageSize"
					show-edges
					color="neutral"
				/>
			</div>
		</template>
	</div>
</template>

<script setup lang="ts">
import type { PaginatedResponseInterface } from "@/types/pagination";
import type { SMSMessageCountGetResponse as Row } from "@/types/sms_message";
import type { CausalityAssessmentLevelEnum } from "@/types/adr";
import type { TableColumn } from "@nuxt/ui";
import { keepPreviousData, useQuery } from "@tanstack/vue-query";
import { formatDateTime } from "~/utils/adr-table";
import { phonesText, queueColumns } from "~/utils/sms-table";

const props = defineProps<{
	// One of the fetch functions of api/sms.ts.
	fetcher: (params: {
		page: number;
		size: number;
		query?: string;
		causality_level?: CausalityAssessmentLevelEnum;
		has_been_sent?: boolean;
	}) => Promise<PaginatedResponseInterface<Row>>;
	queryKey: string[];
	causalityLevel: CausalityAssessmentLevelEnum;
	sent: boolean;
	emptyText: string;
}>();

const pageSize = 20;
const page = ref(1);
const search = ref("");
const debouncedSearch = refDebounced(search, 400);

watch(debouncedSearch, () => (page.value = 1));

const query = useQuery({
	queryKey: computed(() => [...props.queryKey, page.value, debouncedSearch.value]),
	queryFn: () =>
		props.fetcher({
			page: page.value,
			size: pageSize,
			query: debouncedSearch.value.trim() || undefined,
			causality_level: props.causalityLevel,
			has_been_sent: props.sent,
		}),
	placeholderData: keepPreviousData,
});

const rows = computed<Row[]>(() => query.data.value?.items ?? []);
const total = computed(() => query.data.value?.total ?? 0);

const columns = computed<TableColumn<Row>[]>(() =>
	queueColumns(props.sent).map(({ key, header }) => ({
		accessorKey: key,
		header,
		cell: ({ row }) => {
			if (key === "telephones") return phonesText(row.original.telephones);
			if (key === "created_at") return formatDateTime(row.original.created_at);
			return String(row.original[key] ?? "—");
		},
	})),
);
</script>
