<template>
	<div class="text-center mb-16">
		<h1 class="text-4xl md:text-5xl font-bold mb-4 tracking-tight">
			ML-Driven Causality Assessment with Explainable Predictions
		</h1>
		<p class="text-lg text-gray-500 dark:text-gray-400 max-w-3xl mx-auto">
			Understand drug safety insights using AI-powered causality
			assessments and transparent, explainable results.
		</p>
		<p>
			Thanks to
			<NuxtLink to="https://www.intellisoftkenya.com" target="_blank">
				IntelliSOFT Consulting Ltd
			</NuxtLink>
			and
			<NuxtLink to="https://web.pharmacyboardkenya.org/" target="_blank">
				Pharmacy and Poisons Board
			</NuxtLink>
		</p>
	</div>

	<div class="flex space-x-8 p-8">
		<UCard>
			<template #header>
				<div class="flex items-center gap-4">
					<UIcon
						name="i-heroicons-exclamation-triangle"
						class="w-7 h-7 text-red-500"
					/>
					<h3 class="text-lg font-semibold">What is an ADR?</h3>
				</div>
			</template>
			<p class="text-gray-500 dark:text-gray-400">
				An ADR (Adverse Drug Reaction) is a harmful or unintended
				response to a medication. It occurs even when a drug is used
				correctly.
			</p>
		</UCard>

		<UCard>
			<template #header>
				<div class="flex items-center gap-4">
					<UIcon
						name="i-heroicons-cpu-chip"
						class="w-7 h-7 text-primary-500"
					/>
					<h3 class="text-lg font-semibold">
						What is a Causality Assessment?
					</h3>
				</div>
			</template>
			<p class="text-gray-500 dark:text-gray-400">
				Causality Assessment helps determine the likelihood that a drug
				caused a specific adverse reaction. It follows structured
				medical criteria.
			</p>
		</UCard>

		<UCard>
			<template #header>
				<div class="flex items-center gap-4">
					<UIcon
						name="i-heroicons-variable"
						class="w-7 h-7 text-blue-500"
					/>
					<h3 class="text-lg font-semibold">
						How is the ML Model Working?
					</h3>
				</div>
			</template>
			<p class="text-gray-500 dark:text-gray-400">
				Our machine learning model analyzes patient data and symptoms to
				classify ADRs using explainable AI techniques like SHAP.
			</p>
		</UCard>

		<UCard class="md:col-span-2 lg:col-span-1">
			<template #header>
				<div class="flex items-center gap-4">
					<UIcon
						name="i-heroicons-question-mark-circle"
						class="w-7 h-7 text-green-500"
					/>
					<h3 class="text-lg font-semibold">
						Why is This Important?
					</h3>
				</div>
			</template>
			<p class="text-gray-500 dark:text-gray-400">
				Timely ADR identification improves patient safety, reduces
				drug-related harm, and supports regulatory pharmacovigilance
				systems.
			</p>
		</UCard>
	</div>
</template>

<script setup lang="ts">
// Your script remains the same, as it was only setting the page title.
useHead({ title: "Home | MediLinda" });
</script>
