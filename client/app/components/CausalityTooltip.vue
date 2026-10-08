<template>
	<UTooltip
		v-if="info"
		:delay-duration="100"
		:content="{ side: 'top', sideOffset: 8 }"
		:ui="{ content: 'h-auto max-w-xs items-start px-3 py-2', text: 'whitespace-normal' }"
	>
		<slot />
		<template #content>
			<div class="space-y-1">
				<p class="text-sm font-semibold">{{ info.label }}</p>
				<p class="text-xs font-normal leading-snug whitespace-normal">{{ info.description }}</p>
			</div>
		</template>
	</UTooltip>
	<slot v-else />
</template>

<script setup lang="ts">
import { causalityLevel } from "~/utils/causality-levels";

// Shows what a causality level means when the wrapped element is hovered or focused.
const props = defineProps<{ level?: string | null }>();

const info = computed(() => causalityLevel(props.level));
</script>
