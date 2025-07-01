<template>
	<p v-if="calStatus == 'pending'">Loading CAL...</p>
	<p v-else-if="calStatus == 'error'">{{ calError }}</p>
	<div v-else-if="calStatus == 'success'" class="page-wrapper">
		<CausalityAssessmentLevelComparison
			:value="calData?.causality_assessment_level_value"
		/>
		<Tabs default-value="review">
			<div class="w-max mx-auto">
				<TabsList>
					<TabsTrigger value="adr">
						Adverse Drug Reaction Report Details
					</TabsTrigger>
					<TabsTrigger
						value="causality-assessment"
						v-if="
							calData &&
							!['unclassified', 'unclassifiable'].includes(
								calData.causality_assessment_level_value ?? ''
							)
						"
					>
						Prediction Explanations
					</TabsTrigger>
					<TabsTrigger value="review">Review Form</TabsTrigger>
				</TabsList>
			</div>

			<TabsContent value="adr">
				<ADRDetails v-if="adrData" :data="adrData" />
			</TabsContent>
			<TabsContent
				value="causality-assessment"
				v-if="
					calData &&
					!['unclassified', 'unclassifiable'].includes(
						calData.causality_assessment_level_value ?? ''
					)
				"
			>
				<ClassRankings
					v-if="
						calData &&
						!['unclassified', 'unclassifiable'].includes(
							calData.causality_assessment_level_value ?? ''
						)
					"
					:base-values="calData.base_values"
					:shap-values="calData.shap_values_sum_per_class"
					:base-shap-values="
						calData.shap_values_and_base_values_sum_per_class
					"
				/>
				<FeatureRankings
					v-if="
						calData &&
						!['unclassified', 'unclassifiable'].includes(
							calData.causality_assessment_level_value ?? ''
						)
					"
					:base-values="calData.base_values"
					:shap-values="calData.shap_values_sum_per_class"
					:base-shap-values="
						calData.shap_values_and_base_values_sum_per_class
					"
					:shap-matrix="calData.shap_values_matrix"
					:feature-names="calData.feature_names"
					:feature-values="calData.feature_values"
				/>
			</TabsContent>
			<TabsContent value="review">
				<ADRReviewForm
					:predicted_causality_assessment_level="
						calData?.causality_assessment_level_value
					"
					:causality_assessment_level_id="calData?.id"
					:mode="mode"
				/>
			</TabsContent>
		</Tabs>
	</div>
</template>

<script setup lang="ts">
import type { ADRGetResponseInterface } from "@/types/adr";
import type { CausalityAssessmentLevelGetResponseInterface } from "@/types/cal";

const route = useRoute();
const id = route.params.id as string;

type ModeType = "create" | "update";
const mode: ModeType = (route.query.mode as ModeType) || "create"; // If the mode is not set, then the default is create
// Store
const authStore = useAuthStore();

const calData = ref<CausalityAssessmentLevelGetResponseInterface | null>(null);
const calError = ref<unknown | null>(null);
const calStatus = ref<"idle" | "pending" | "success" | "error">("idle");

const adrData = ref<ADRGetResponseInterface | null>(null);
const adrError = ref<unknown | null>(null);
const adrStatus = ref<"idle" | "pending" | "success" | "error">("idle");

onMounted(async () => {
	await fetchADR();
	await fetchCal();
});

async function fetchADR() {
	adrStatus.value = "pending";
	try {
		const data = await $fetch<ADRGetResponseInterface>(
			`${useRuntimeConfig().public.serverApi}/adr/${id}`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
			}
		);

		if (!data) throw new Error("No ADR data received");

		adrData.value = data;
		adrStatus.value = "success";
	} catch (error) {
		adrError.value = error;
		adrStatus.value = "error";
	}
}

async function fetchCal() {
	calStatus.value = "pending";
	try {
		const data = await $fetch<CausalityAssessmentLevelGetResponseInterface>(
			`${
				useRuntimeConfig().public.serverApi
			}/specific_adr/${id}/causality_assessment_level`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
			}
		);

		if (!data) throw new Error("No causality data received");

		calData.value = data;
		console.log(calData.value.causality_assessment_level_value);
		calStatus.value = "success";
	} catch (error) {
		calError.value = error;
		calStatus.value = "error";
	}
}
useHead({ title: "Review a Causality Assessment Level | MediLinda" });
</script>
