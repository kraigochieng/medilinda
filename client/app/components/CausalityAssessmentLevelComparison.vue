<template>
	<UCard class="my-4">
		<template #header>
			<div class="flex flex-col">
				<h2 class="text-lg font-semibold">Predicted Causality Level</h2>
				<p class="text-sm text-gray-500">
					Predicted level is the visible one. This is just a
					prediction, not the final result.
				</p>
			</div>
		</template>

		<template #default>
			<div class="flex w-max mx-auto flex-col md:flex-row">
				<div
					v-for="(level, i) in levels"
					:key="i"
					class="box-size"
					:class="[
						level.color,
						value === level.label.toLowerCase()
							? 'opacity-100 shadow-2xl scale-110 z-10 rounded-sm'
							: 'opacity-30',
						level.textColor ?? 'text-black',
					]"
				>
					{{ level.label }}
				</div>
			</div>
		</template>

		<template #footer>
			<div class="flex justify-end">
				<UModal>
					<UButton
						label="Causality Assessment Level Descriptions"
						icon="i-lucide-circle-question-mark"
						color="neutral"
						variant="ghost"
					/>
					<template #content>
						<div class="p-4">
							<h3 class="text-lg font-semibold">
								Causality Assessment Level Descriptions
							</h3>
							<p class="text-sm text-gray-500">
								Get a short description of each causality
								assessment level
							</p>

							<ul
								class="py-4 text-sm text-gray-700 dark:text-gray-400 space-y-2"
							>
								<li>
									<strong>Certain:</strong> Clear link to drug
									intake with no alternative explanation and
									strong evidence, including positive
									withdrawal and rechallenge if needed.
								</li>
								<li>
									<strong>Probable/Likely:</strong> Reasonable
									link to drug, unlikely due to other causes,
									with improvement on withdrawal—rechallenge
									not needed.
								</li>
								<li>
									<strong>Possible:</strong> Reasonable
									timing, but the event could also be due to
									other factors, and withdrawal data may be
									unclear.
								</li>
								<li>
									<strong>Unlikely:</strong> Timing and
									context make a drug link improbable, with
									other causes being more plausible.
								</li>
								<li>
									<strong>Conditional/Unclassified:</strong>
									Event noted, but more data or analysis is
									needed before making a conclusion.
								</li>
								<li>
									<strong
										>Unassessable/Unclassifiable:</strong
									>
									Insufficient or contradictory information
									prevents any judgment.
								</li>
							</ul>
						</div>
					</template>
				</UModal>
			</div>
		</template>
	</UCard>
</template>

<script setup lang="ts">
import type { CausalityAssessmentLevelEnum } from "@/types/adr";

const props = defineProps<{
	value?: CausalityAssessmentLevelEnum;
}>();

const levels = [
	{ label: "Unclassifiable", color: "bg-slate-300" },
	{ label: "Unclassified", color: "bg-slate-500", textColor: "text-white" },
	{ label: "Unlikely", color: "bg-yellow-300" },
	{ label: "Possible", color: "bg-yellow-500" },
	{ label: "Likely", color: "bg-red-400" },
	{ label: "Certain", color: "bg-red-500", textColor: "text-white" },
];
</script>

<style scoped>
@reference "assets/css/main.css";

.box-size {
	@apply py-1 px-4 text-center transition-transform duration-300 transform;
}
</style>
