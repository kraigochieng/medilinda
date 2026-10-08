<template>
	<UCard class="my-4">
		<template #header>
			<div class="flex flex-col">
				<h2 class="text-lg font-semibold">Predicted Causality Level</h2>
				<p class="text-sm text-gray-500">
					Predicted level is the visible one. This is just a prediction, not the final result.
					Hover a level to see what it means.
				</p>
			</div>
		</template>

		<template #default>
			<div class="flex w-max mx-auto flex-col md:flex-row" role="list">
				<CausalityTooltip v-for="level in CAUSALITY_LEVELS" :key="level.value" :level="level.value">
					<button
						type="button"
						role="listitem"
						class="box-size cursor-help"
						:aria-current="isPredicted(level.value) ? 'true' : undefined"
						:class="[
							level.badgeClass,
							isPredicted(level.value)
								? 'opacity-100 shadow-2xl scale-110 z-10 rounded-sm'
								: 'opacity-30',
						]"
					>
						{{ level.label }}
					</button>
				</CausalityTooltip>
			</div>
		</template>
	</UCard>
</template>

<script setup lang="ts">
import { CAUSALITY_LEVELS } from "~/utils/causality-levels";

const props = defineProps<{
	value?: string | null;
}>();

const isPredicted = (level: string) => props.value?.toLowerCase() === level;
</script>

<style scoped>
@reference "assets/css/main.css";

.box-size {
	@apply py-1 px-4 text-center transition-transform duration-300 transform;
}
</style>
