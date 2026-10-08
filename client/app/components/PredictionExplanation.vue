<template>
	<div class="space-y-6">
		<UCard>
			<template #header>
				<h3 class="font-semibold">How sure is the model?</h3>
				<p class="mt-1 text-sm">{{ headline(scores) }}</p>
			</template>

			<ul class="space-y-3">
				<li v-for="score in scores" :key="score.level" class="grid grid-cols-[6.5rem_1fr_3rem] items-center gap-3">
					<CausalityBadge :value="score.level" />
					<div
						class="h-3 overflow-hidden rounded-full bg-elevated"
						role="img"
						:aria-label="`${score.level}: ${score.chance} percent`"
					>
						<div
							class="h-full rounded-full"
							:class="score.level === predicted ? 'bg-primary' : 'bg-neutral-400'"
							:style="{ width: `${score.chance}%` }"
						/>
					</div>
					<span class="text-end text-sm font-medium tabular-nums">{{ score.chance }}%</span>
				</li>
			</ul>

			<p class="mt-4 text-xs text-muted">
				The bars add up to 100%. The model also predicts the levels Unclassified and Unclassifiable by
				rule, and they are not shown here.
			</p>
		</UCard>

		<UCard>
			<template #header>
				<h3 class="font-semibold">Why {{ capital(level) }}?</h3>
				<p class="mt-1 text-sm text-muted">
					These facts from the report pushed the chance of
					<strong>{{ capital(level) }}</strong> up (green) or down (red). A longer bar is a bigger push.
				</p>
			</template>

			<UTabs v-model="level" :items="levelTabs" :content="false" color="neutral" class="mb-4" />

			<p v-if="!factors.length" class="py-6 text-center text-sm text-muted">
				No fact in the report moved the chance of this level.
			</p>

			<ul v-else class="space-y-3">
				<li v-for="factor in shown" :key="factor.name" class="grid grid-cols-[1fr_auto] items-center gap-x-4 gap-y-1">
					<div class="flex min-w-0 items-center gap-2">
						<UIcon
							:name="factor.direction === 'toward' ? 'i-lucide-trending-up' : 'i-lucide-trending-down'"
							class="size-4 shrink-0"
							:class="factor.direction === 'toward' ? 'text-success' : 'text-error'"
						/>
						<span class="truncate text-sm">
							<span class="font-medium">{{ factor.label }}:</span> {{ factor.value }}
						</span>
					</div>
					<span
						class="text-end text-sm font-medium tabular-nums"
						:class="factor.direction === 'toward' ? 'text-success' : 'text-error'"
					>
						{{ effectText(factor.effect) }}
					</span>
					<div class="col-span-2 h-1.5 overflow-hidden rounded-full bg-elevated" aria-hidden="true">
						<div
							class="h-full rounded-full"
							:class="factor.direction === 'toward' ? 'bg-success' : 'bg-error'"
							:style="{ width: `${Math.max(factor.share * 100, 2)}%` }"
						/>
					</div>
				</li>
			</ul>

			<div v-if="factors.length > FIRST" class="mt-4 flex justify-center">
				<UButton
					color="neutral"
					variant="outline"
					size="sm"
					:label="showAll ? 'Show fewer facts' : `Show all ${factors.length} facts`"
					:trailing-icon="showAll ? 'i-lucide-chevron-up' : 'i-lucide-chevron-down'"
					@click="showAll = !showAll"
				/>
			</div>
		</UCard>

		<UCollapsible>
			<UButton
				color="neutral"
				variant="ghost"
				size="sm"
				icon="i-lucide-table"
				trailing-icon="i-lucide-chevron-down"
				label="Show the numbers"
			/>
			<template #content>
				<div class="mt-2 overflow-x-auto rounded-lg border border-default">
					<table class="w-full text-sm">
						<thead>
							<tr class="border-b border-default text-start text-xs uppercase tracking-wide text-muted">
								<th class="p-2 text-start font-medium">Level</th>
								<th class="p-2 text-end font-medium">A typical report</th>
								<th class="p-2 text-end font-medium">What this report changed</th>
								<th class="p-2 text-end font-medium">This report</th>
							</tr>
						</thead>
						<tbody>
							<tr v-for="score in scores" :key="score.level" class="border-b border-default last:border-0">
								<td class="p-2">{{ capital(score.level) }}</td>
								<td class="p-2 text-end tabular-nums">{{ score.start }}%</td>
								<td class="p-2 text-end tabular-nums">{{ score.change > 0 ? "+" : "" }}{{ score.change }} points</td>
								<td class="p-2 text-end font-medium tabular-nums">{{ score.chance }}%</td>
							</tr>
						</tbody>
					</table>
				</div>
			</template>
		</UCollapsible>
	</div>
</template>

<script setup lang="ts">
import type { CausalityAssessmentLevelGetResponseInterface as Assessment } from "@/types/cal";
import type { TabsItem } from "@nuxt/ui";
import {
	EXPLAINED_LEVELS,
	effectText,
	factorsFor,
	headline,
	levelScores,
} from "~/utils/explanation";

const props = defineProps<{ assessment: Assessment }>();

const FIRST = 8; // the facts shown before the reader asks for all of them

const capital = (text: string) => text.charAt(0).toUpperCase() + text.slice(1);

const scores = computed(() =>
	levelScores(props.assessment.base_values, props.assessment.shap_values_and_base_values_sum_per_class),
);

// The level the model predicted. If the model gave none of its own four, the top score.
const predicted = computed(() => {
	const value = props.assessment.causality_assessment_level_value as string | undefined;
	return EXPLAINED_LEVELS.find((l) => l === value) ?? scores.value[0]?.level ?? "likely";
});

const level = ref<string>(predicted.value);
watch(predicted, (value) => (level.value = value));

const levelTabs = EXPLAINED_LEVELS.map<TabsItem>((value) => ({ label: capital(value), value }));

const factors = computed(() =>
	factorsFor(
		EXPLAINED_LEVELS.indexOf(level.value as (typeof EXPLAINED_LEVELS)[number]),
		props.assessment.feature_names,
		props.assessment.feature_values as unknown[] | undefined,
		props.assessment.shap_values_matrix,
	),
);

const showAll = ref(false);
watch(level, () => (showAll.value = false));
const shown = computed(() => (showAll.value ? factors.value : factors.value.slice(0, FIRST)));
</script>
