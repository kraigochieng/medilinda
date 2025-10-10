<template>
	<UForm @submit="onSubmit">
		<UCard>
			<template #header>
				<h1>Add a Review</h1>
				<h2>Review the causality assessment level from the ML Model</h2>
			</template>
			<template #default>
				<UFormField
					name="approved"
					help="Turn on if approved, off if not"
				>
					<USwitch v-model="state.approved" label="Approved" />
					<Transition>
						<UFormField
							name="proposed_causality_level"
							help="Proposed Level of Causality for you disapprove of the predicition"
							v-if="!state.approved"
						>
							<URadioGroup
								legend="Proposed Causality Level"
								v-model="state.proposed_causality_level"
								:items="filteredCausalityOptions"
							/>
						</UFormField>
					</Transition>
				</UFormField>
				<UFormField
					name="help"
					help="Justification for your proposed causality level if you disapprove of the prediciton"
				>
					<UTextarea
						v-model="state.reason"
						name="reason"
						label="Reason"
						placeholder="Enter Reason"
					/>
				</UFormField>
			</template>
			<template #footer>
				<UButton type="submit" class="w-full">
					{{ props.mode == "create" ? "Add Review" : "Edit Review" }}
				</UButton>
			</template>
		</UCard>
	</UForm>
</template>

<script setup lang="ts">
// Imports
import type { CausalityAssessmentLevelEnum } from "@/types/adr";
import type { ReviewPostResponse } from "@/types/review";
import { reviewFormCategoricalValues } from "@/values/review";
import type { FormSubmitEvent } from "@nuxt/ui";
import humps from "humps";
import { z } from "zod";

const filteredCausalityOptions = computed(() => {
	return reviewFormCategoricalValues.proposedCausalityLevel.filter(
		(option) => option.value !== props.predicted_causality_assessment_level
	);
});

const props = defineProps<{
	predicted_causality_assessment_level?: CausalityAssessmentLevelEnum;
	causality_assessment_level_id?: string;
	mode: "create" | "update";
}>();

const schema = z.object({
	approved: z.boolean(),
	proposed_causality_level: z
		.enum(
			reviewFormCategoricalValues["proposedCausalityLevel"].map(
				(x) => x.value
			) as [string, ...string[]]
		)
		.optional(),
	reason: z
		.string()
		.min(3, "Reason must be at least 3 characters long")
		.optional(),
});

type Schema = z.infer<typeof schema>;

const state = reactive<Partial<Schema>>({
	approved: undefined,
	proposed_causality_level: undefined,
	reason: undefined,
});

async function onSubmit(event: FormSubmitEvent<Schema>) {
	// try {
	// 	const response = await $fetch<ReviewPostResponse>(
	// 		`${
	// 			useRuntimeConfig().public.serverApi
	// 		}/causality_assessment_level/${
	// 			props.causality_assessment_level_id
	// 		}/review`,
	// 		{
	// 			method: "POST",
	// 			headers: {
	// 				Authorization: `Bearer ${authStore.accessToken}`,
	// 				"Content-Type": "application/json",
	// 			},
	// 			body: humps.decamelizeKeys(values), // Sends form values as JSON
	// 		}
	// 	);
	// 	console.log("Form submitted successfully:", response);
	// 	navigateTo(`/adr`);
	// } catch (error) {
	// 	console.error("Error submitting form:", error);
	// }
}

onMounted(async () => {
	// const runtimeConfig = useRuntimeConfig();
	// const serverApi = runtimeConfig.public.serverApi;
	// const authStore = useAuthStore();
	// if (props.mode == "update") {
	// 	const response = await $fetch(
	// 		`${serverApi}/review_for_specific_user_and_causality_assessment_level`,
	// 		{
	// 			method: "GET",
	// 			headers: {
	// 				Authorization: `Bearer ${authStore.accessToken}`,
	// 			},
	// 			params: {
	// 				causality_assessment_level_id:
	// 					props.causality_assessment_level_id,
	// 			},
	// 		}
	// 	);
	// 	// Pre-fill form
	// 	const camel = humps.camelizeKeys(response) as typeValidationSchema;
	// 	for (const key of Object.keys(camel) as Array<
	// 		keyof typeValidationSchema
	// 	>) {
	// 		setFieldValue(key, camel[key]);
	// 	}
	// }
});
</script>
