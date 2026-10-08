<template>
	<section class="mx-auto max-w-6xl px-4 py-8">
		<div class="mb-10 text-center">
			<h1 class="mb-4 text-3xl font-bold">ML-driven causality assessment with explainable predictions</h1>
			<p class="mx-auto max-w-2xl text-lg text-muted">
				Understand drug safety with AI-powered causality assessments.
			</p>
		</div>

		<div class="grid gap-6 text-left md:grid-cols-2">
			<UCard>
				<template #header>
					<div class="flex items-center gap-3">
						<UIcon name="i-lucide:octagon-alert" class="size-6 text-error" />
						<h2 class="font-semibold">What is an ADR?</h2>
					</div>
				</template>
				<p class="text-muted">An ADR (Adverse Drug Reaction) is a harmful or unintended response to a medication. It occurs even when a drug is used correctly.</p>
			</UCard>

			<UCard>
				<template #header>
					<div class="flex items-center gap-3">
						<UIcon name="i-lucide:brain" class="size-6 text-primary" />
						<h2 class="font-semibold">What is a causality assessment?</h2>
					</div>
				</template>
				<p class="text-muted">A causality assessment estimates how likely it is that a drug caused a specific adverse reaction. It follows structured medical criteria.</p>
			</UCard>

			<UCard>
				<template #header>
					<div class="flex items-center gap-3">
						<UIcon name="i-lucide:cpu" class="size-6 text-info" />
						<h2 class="font-semibold">How does the model work?</h2>
					</div>
				</template>
				<p class="text-muted">The model reads the patient data and the report, predicts a causality level, and explains the prediction with SHAP values.</p>
			</UCard>

			<UCard>
				<template #header>
					<div class="flex items-center gap-3">
						<UIcon name="i-lucide:circle-help" class="size-6 text-warning" />
						<h2 class="font-semibold">Why is this needed?</h2>
					</div>
				</template>
				<p class="text-muted">Finding ADRs early improves patient safety, reduces drug-related harm, and supports pharmacovigilance.</p>
			</UCard>
		</div>
	</section>
</template>

<script setup lang="ts">
useHead({ title: "About | MediLinda" });
</script>
