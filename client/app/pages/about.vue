<template>
	<div class="mx-auto max-w-3xl space-y-10">
		<header class="space-y-3 text-center">
			<h1 class="text-3xl font-bold">From a suspected reaction to a safer patient</h1>
			<p class="mx-auto max-w-2xl text-lg text-muted">
				MediLinda helps health workers report harm from medicines, judge what caused it, and tell
				the facility what to do next. Follow one case through the six steps.
			</p>
		</header>

		<UTimeline :items="items" :default-value="0" size="xl" color="primary" class="px-2">
			<template #date="{ item }">
				<span class="font-medium text-primary">{{ item.date }}</span>
			</template>

			<template #description="{ item }">
				<div class="space-y-4 pb-8">
					<p>{{ steps[item.value as number]!.story }}</p>

					<div v-if="steps[item.value as number]!.levels" class="space-y-2">
						<p class="text-sm font-medium">The six levels. Point at one to read what it means.</p>
						<div class="flex flex-wrap gap-2">
							<CausalityTooltip v-for="level in steps[item.value as number]!.levels" :key="level" :value="level">
								<CausalityBadge :value="level" />
							</CausalityTooltip>
						</div>
					</div>

					<dl v-if="steps[item.value as number]!.definitions.length" class="space-y-2">
						<div
							v-for="definition in steps[item.value as number]!.definitions"
							:key="definition.term"
							class="rounded-md border border-default bg-elevated/40 p-3 text-sm"
						>
							<dt class="font-semibold">{{ definition.term }}</dt>
							<dd class="text-muted">{{ definition.text }}</dd>
						</div>
					</dl>

					<ul v-if="steps[item.value as number]!.where.length" class="space-y-2">
						<li v-for="place in steps[item.value as number]!.where" :key="place.to">
							<UButton
								:to="place.to"
								color="neutral"
								variant="outline"
								size="sm"
								trailing-icon="i-lucide-arrow-right"
								:label="place.label"
							/>
							<span class="ms-2 text-sm text-muted">{{ place.note }}</span>
						</li>
					</ul>
				</div>
			</template>
		</UTimeline>

		<div class="flex justify-center">
			<UButton to="/adr/add" icon="i-lucide-plus" size="lg" label="Report a case" />
		</div>
	</div>
</template>

<script setup lang="ts">
import { STORY } from "~/utils/about-story";

const steps = STORY;

// One timeline item for each step. The value is its position, so the slot can find the step.
const items = STORY.map((step, index) => ({
	value: index,
	date: step.stage,
	title: step.title,
	icon: step.icon,
}));

useHead({ title: "About | MediLinda" });
</script>
