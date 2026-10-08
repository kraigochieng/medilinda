<template>
	<div class="flex flex-wrap items-center gap-1.5" role="group" :aria-label="label">
		<UBadge
			v-for="option in states"
			:key="option.value"
			:color="option.chosen ? 'success' : 'neutral'"
			:variant="option.chosen ? 'solid' : 'outline'"
			:icon="option.chosen ? 'i-lucide-check' : undefined"
			:class="option.chosen ? '' : 'opacity-60'"
		>
			{{ option.label }}
			<span v-if="option.chosen" class="sr-only">(chosen)</span>
		</UBadge>
		<span v-if="!states.some((option) => option.chosen)" class="text-sm text-muted">Not recorded</span>
	</div>
</template>

<script setup lang="ts">
import type { adrFormCategoricalValues } from "~/values/adr";
import { optionStates } from "~/utils/adr-view";

// All the options of a choice field. The chosen one is solid and green, the others are
// faint, so the reader sees what else was possible.
const props = defineProps<{
	group: keyof typeof adrFormCategoricalValues;
	value?: string | null;
	label?: string;
}>();

const states = computed(() => optionStates(props.group, props.value));
</script>
