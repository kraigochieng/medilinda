<template>
	<CausalityTooltip v-if="info" :level="value">
		<UBadge :class="['cursor-help', info.badgeClass]" tabindex="0">{{ info.label }}</UBadge>
	</CausalityTooltip>
	<span v-else class="text-muted">—</span>
</template>

<script setup lang="ts">
import { causalityLevel } from "~/utils/causality-levels";

// A coloured badge for a causality level, with its meaning in a tooltip.
const props = defineProps<{ value?: string | null }>();

const info = computed(() => causalityLevel(props.value));
</script>
