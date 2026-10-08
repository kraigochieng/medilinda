<template>
	<div class="min-w-0" :class="wide ? 'sm:col-span-2 lg:col-span-3' : ''">
		<dt class="text-xs font-medium uppercase tracking-wide text-muted">{{ label }}</dt>
		<dd class="mt-0.5 break-words" :class="isBlank ? 'text-muted' : ''">
			<slot>{{ value === undefined || value === null || value === "" ? NONE : value }}</slot>
		</dd>
	</div>
</template>

<script setup lang="ts">
import { NONE } from "~/utils/adr-view";

// One fact of a report: the label above, the value below. A missing value is a dash.
const props = defineProps<{ label: string; value?: string | number | null; wide?: boolean }>();

const slots = useSlots();

const isBlank = computed(
	() => !slots.default && (props.value === undefined || props.value === null || props.value === "" || props.value === NONE),
);
</script>
