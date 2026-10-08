<template>
	<div class="space-y-4">
		<UAlert
			v-if="isError"
			color="error"
			variant="subtle"
			icon="i-lucide-triangle-alert"
			title="Could not load the history"
			:description="errorMessage"
			:actions="[{ label: 'Try again', color: 'neutral', onClick: () => refetch() }]"
		/>

		<div v-else-if="isPending" class="space-y-4" aria-busy="true">
			<USkeleton v-for="n in 4" :key="n" class="h-14 w-full" />
		</div>

		<div v-else-if="!views.length" class="flex flex-col items-center gap-2 py-10 text-center">
			<UIcon name="i-lucide-history" class="size-10 text-muted" />
			<p class="font-medium">No history recorded yet</p>
			<p class="max-w-sm text-sm text-muted">
				History starts the first time this ADR is edited. From then on every change is kept: who made
				it, when, and what it was before.
			</p>
		</div>

		<ol v-else class="relative ms-3 space-y-6 border-s border-default ps-6">
			<li v-for="event in views" :key="event.id" class="relative">
				<span
					class="absolute -start-[2.15rem] flex size-6 items-center justify-center rounded-full bg-default ring-4 ring-default"
				>
					<UIcon :name="event.icon" :class="['size-4', COLOR_CLASS[event.color]]" />
				</span>

				<div class="flex flex-wrap items-center gap-2">
					<p class="font-medium">{{ event.title }}</p>
					<UBadge v-if="event.version" color="neutral" variant="subtle" size="sm">
						v{{ event.version }}
					</UBadge>
				</div>
				<p class="text-sm text-muted">
					{{ event.actor }} ·
					<time :datetime="event.at">{{ formatDateTime(event.at) }}</time>
				</p>
				<p v-if="event.note" class="mt-1 text-sm">{{ event.note }}</p>

				<details v-if="event.changes.length" class="mt-2">
					<summary class="cursor-pointer text-sm text-primary">
						{{ event.changes.length === 1 ? "Show the change" : `Show ${event.changes.length} changes` }}
					</summary>
					<dl class="mt-2 divide-y divide-default rounded-md border border-default text-sm">
						<div
							v-for="change in event.changes"
							:key="change.label"
							class="grid gap-1 p-2 sm:grid-cols-[12rem_1fr_1fr]"
						>
							<dt class="font-medium">{{ change.label }}</dt>
							<dd class="text-muted line-through decoration-muted/50">{{ change.old }}</dd>
							<dd>{{ change.new }}</dd>
						</div>
					</dl>
				</details>
			</li>
		</ol>

		<div v-if="hasNextPage" class="flex justify-center">
			<UButton
				color="neutral"
				variant="outline"
				label="Load more"
				:loading="isFetchingNextPage"
				@click="fetchNextPage()"
			/>
		</div>
	</div>
</template>

<script setup lang="ts">
import { fetchAdrActivity } from "@/api/audit";
import { useInfiniteQuery } from "@tanstack/vue-query";
import { describeEvents, type EventColor } from "~/utils/audit-events";
import { formatDateTime } from "~/utils/adr-table";

const props = defineProps<{ adrId: string }>();

const PAGE_SIZE = 20;

const COLOR_CLASS: Record<EventColor, string> = {
	neutral: "text-muted",
	success: "text-success",
	warning: "text-warning",
	error: "text-error",
	info: "text-info",
};

const { data, isPending, isError, error, refetch, hasNextPage, fetchNextPage, isFetchingNextPage } =
	useInfiniteQuery({
		queryKey: ["adr-activity", props.adrId],
		queryFn: ({ pageParam }) => fetchAdrActivity(props.adrId, { page: pageParam, size: PAGE_SIZE }),
		initialPageParam: 1,
		getNextPageParam: (last) => (last.page < last.pages ? last.page + 1 : undefined),
	});

const views = computed(() =>
	describeEvents((data.value?.pages ?? []).flatMap((page) => page.items ?? []))
);
const errorMessage = computed(
	() => (error.value as Error | null)?.message ?? "Check your connection and try again."
);
</script>
