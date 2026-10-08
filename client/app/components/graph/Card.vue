<template>
	<UCard class="graph-card" :ui="{ body: 'min-h-[18rem]' }">
		<template #header>
			<h2 class="font-semibold">{{ title }}</h2>
			<p class="mt-1 text-sm text-muted">{{ description }}</p>
		</template>

		<USkeleton v-if="query.isPending.value" class="h-72 w-full" aria-busy="true" />

		<UAlert
			v-else-if="query.isError.value"
			color="error"
			variant="subtle"
			icon="i-lucide-triangle-alert"
			title="Could not load this chart"
			:actions="[{ label: 'Try again', color: 'neutral', onClick: () => query.refetch() }]"
		/>

		<p v-else-if="!hasData(query.data.value)" class="flex h-72 items-center justify-center text-sm text-muted">
			Nothing to show yet.
		</p>

		<BarChart
			v-else
			:data="query.data.value"
			:x-formatter="(i: number) => shorten(labelAt(query.data.value, i))"
			:y-formatter="(tick: number) => (Number.isInteger(tick) ? String(tick) : '')"
			:categories="{ value: { name: title, color } }"
			:y-axis="['value']"
			:y-grid-line="true"
			:height="288"
			:radius="4"
			:hide-legend="true"
			bar-direction="horizontal"
		/>
	</UCard>
</template>

<script setup lang="ts">
import type { MetricValue } from "~/types/dashboard";
import { hasData, labelAt, shorten } from "~/utils/dashboard-chart";

// The chart of one metric. The card shows loading, error and empty states, so each
// chart only says which query it reads.
defineProps<{
	title: string;
	description: string;
	color: string;
	query: {
		data: Ref<MetricValue[] | undefined>;
		isPending: Ref<boolean>;
		isError: Ref<boolean>;
		refetch: () => unknown;
	};
}>();
</script>

<style scoped>
/* The chart library draws its axes in white. Use the colors of the app instead, so
   they show on a light page and on a dark one. */
.graph-card {
	--vis-axis-tick-label-color: var(--ui-text-muted);
	--vis-axis-label-color: var(--ui-text-muted);
	--vis-axis-grid-color: var(--ui-border);
	--vis-axis-tick-color: var(--ui-border);
	--vis-axis-domain-color: var(--ui-border);
}
</style>
