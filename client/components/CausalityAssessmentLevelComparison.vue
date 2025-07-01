<template>
	<Card class="my-4">
		<CardHeader>
			<CardTitle>Predicted Causality Level</CardTitle>
			<CardDescription
				>Predicted level is the visible one. This is just a prediction,
				not the final result</CardDescription
			>
		</CardHeader>
		<CardContent>
			<div class="flex w-max mx-auto flex-col md:flex-row">
				<div
					v-for="(level, i) in levels"
					:key="i"
					class="box-size"
					:class="[
						level.color,
						props.value === level.label.toLocaleLowerCase()
							? 'opacity-100 shadow-2xl scale-110 z-10 rounded-sm'
							: 'opacity-30',
						level.textColor ?? 'text-black',
					]"
				>
					{{ level.label }}
				</div>
			</div>
		</CardContent>
		<CardFooter class="flex justify-end">
			<Dialog>
				<DialogTrigger as-child>
					<Button variant="ghost" class="flex items-center">
						<Icon name="lucide:circle-help" />
						<p>Causality Assessment Level Descriptions</p>
					</Button>
				</DialogTrigger>
				<DialogContent>
					<DialogHeader>
						<DialogTitle>
							Causality Assessment Level Descriptions
						</DialogTitle>
						<DialogDescription>
							Get a short description of each causality assessment
							level
						</DialogDescription>
					</DialogHeader>
					<ul
						class="py-4 text-sm text-neutral-700 dark:text-neutral-400"
					>
						<li>
							<strong>Certain:</strong> Clear link to drug intake
							with no alternative explanation and strong evidence,
							including positive withdrawal and rechallenge if
							needed.
						</li>
						<li>
							<strong>Probable/Likely:</strong> Reasonable link to
							drug, unlikely due to other causes, with improvement
							on withdrawal—rechallenge not needed.
						</li>
						<li>
							<strong>Possible:</strong> Reasonable timing, but
							the event could also be due to other factors, and
							withdrawal data may be unclear.
						</li>
						<li>
							<strong>Unlikely:</strong> Timing and context make a
							drug link improbable, with other causes being more
							plausible.
						</li>
						<li>
							<strong>Conditional/Unclassified:</strong> Event
							noted, but more data or analysis is needed before
							making a conclusion.
						</li>
						<li>
							<strong>Unassessable/Unclassifiable:</strong>
							Insufficient or contradictory information prevents
							any judgment.
						</li>
					</ul>
				</DialogContent>
			</Dialog>
		</CardFooter>
	</Card>
</template>

<script setup lang="ts">
import type { CausalityAssessmentLevelEnum } from "@/types/adr";

import { capitalize } from "lodash";
const props = defineProps<{
	value?: CausalityAssessmentLevelEnum;
}>();

const levels = [
	{ label: "Unclassifiable", color: "bg-slate-300" },
	{ label: "Unclassified", color: "bg-slate-500", textColor: "text-white" },
	{ label: "Unlikely", color: "bg-yellow-300" },
	{ label: "Possible", color: "bg-yellow-500" },
	{ label: "Likely", color: "bg-red-400" },
	{
		label: "Certain",
		color: "bg-red-500",
		textColor: "text-white",
	},
];
</script>

<style scoped>
.box-size {
	@apply py-1 px-4 text-center transition-transform duration-300 transform;
}

li {
	@apply py-2;
}
</style>
