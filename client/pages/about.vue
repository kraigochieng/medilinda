<template>
	<section class="container mx-auto px-4 py-12">
		<!-- Header -->
		<div class="text-center mb-12">
			<h1 class="text-4xl font-bold mb-4">
				ML Driven Causality Assessment with Explainable Predictions
			</h1>
			<p class="text-muted-foreground text-lg max-w-2xl mx-auto">
				Understand drug safety insights using AI-powered causality
				assessments.
			</p>
		</div>

		<!-- Hero Image -->
		<!-- <div class="mb-16 flex justify-center">
			<img
				src="/images/microscope.jpg"
				alt="Microscope close-up"
				class="rounded-xl shadow-md w-full max-w-3xl object-cover"
			/>
		</div> -->

		<!-- FAQs Section -->
		<div class="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
			<Card>
				<CardHeader class="flex items-center gap-4">
					<Icon
						name="lucide:octagon-alert"
						class="w-6 h-6 text-destructive"
					/>
					<CardTitle>What is an ADR?</CardTitle>
				</CardHeader>
				<CardContent>
					<p class="text-muted-foreground">
						An ADR (Adverse Drug Reaction) is a harmful or
						unintended response to a medication. It occurs even when
						a drug is used correctly.
					</p>
				</CardContent>
			</Card>

			<Card>
				<CardHeader class="flex items-center gap-4">
					<Icon name="lucide:brain" class="w-6 h-6 text-primary" />
					<CardTitle>What is a Causality Assessment?</CardTitle>
				</CardHeader>
				<CardContent>
					<p class="text-muted-foreground">
						Causality Assessment helps determine the likelihood that
						a drug caused a specific adverse reaction. It follows
						structured medical criteria.
					</p>
				</CardContent>
			</Card>

			<Card>
				<CardHeader class="flex items-center gap-4">
					<Icon name="lucide:cpu" class="w-6 h-6 text-secondary" />
					<CardTitle>How is the ML Model Working?</CardTitle>
				</CardHeader>
				<CardContent>
					<p class="text-muted-foreground">
						Our machine learning model analyzes patient data and
						symptoms to classify ADRs using explainable AI
						techniques like SHAP.
					</p>
				</CardContent>
			</Card>

			<Card>
				<CardHeader class="flex items-center gap-4">
					<Icon
						name="lucide:circle-help"
						class="w-6 h-6 text-accent"
					/>
					<CardTitle>What is the Need for This?</CardTitle>
				</CardHeader>
				<CardContent>
					<p class="text-muted-foreground">
						Timely ADR identification improves patient safety,
						reduces drug-related harm, and supports regulatory
						pharmacovigilance systems.
					</p>
				</CardContent>
			</Card>
		</div>
	</section>
</template>

<script setup lang="ts">
useHead({ title: "About | MediLinda" });
</script>
