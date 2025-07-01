<template>
	<form @submit="onSubmit">
		<Card>
			<CardHeader>
				<CardTitle>Add a Review</CardTitle>
				<CardDescription
					>Review the causality assessment level from the ML
					Model</CardDescription
				>
			</CardHeader>
			<CardContent>
				<FormSwitch
					name="approved"
					label="Approved"
					description="Turn on if approved, off if not"
				/>
				<Transition>
					<div v-if="!approved">
						<FormRadio
							name="proposedCausalityLevel"
							label="Proposed Causality Level"
							:options="filteredCausalityOptions"
							description="Proposed Level of Causality for you disapprove of the predicition"
						/>
						<FormTextArea
							name="reason"
							label="Reason"
							placeholder="Enter Reason"
							description="Justification for your proposed causality level if you disapprove of the prediciton"
						/>
					</div>
				</Transition>
			</CardContent>
			<CardFooter>
				<Button type="submit" class="w-full">{{
					props.mode == "create" ? "Add Review" : "Edit Review"
				}}</Button>
			</CardFooter>
		</Card>
	</form>
</template>

<script setup lang="ts">
// Imports
import type { ReviewPostResponse } from "@/types/review";
import humps from "humps";
import * as z from "zod";
import FormRadio from "./ui/custom/FormRadio.vue";
import FormSwitch from "./ui/custom/FormSwitch.vue";
import FormTextArea from "./ui/custom/FormTextArea.vue";
import type { CausalityAssessmentLevelEnum } from "@/types/adr";

const props = defineProps<{
	predicted_causality_assessment_level?: CausalityAssessmentLevelEnum;
	causality_assessment_level_id?: string;
	mode: "create" | "update";
}>();

// Stores
const authStore = useAuthStore();

// Form
const {
	values,
	errors,
	defineField,
	handleSubmit,
	isSubmitting,
	setFieldValue,
} = useForm({
	validationSchema: toTypedSchema(reviewFormValidationSchema),
});

// Form Fields
const [approved, approvedAttrs] = defineField("approved");
const [proposedCausalityLevel, proposedCausalityLevelAttrs] = defineField(
	"proposedCausalityLevel"
);
const [reason, reasonAttrs] = defineField("reason");

// Form Submission
const onSubmit = handleSubmit(async (values) => {
	try {
		const response = await $fetch<ReviewPostResponse>(
			`${
				useRuntimeConfig().public.serverApi
			}/causality_assessment_level/${
				props.causality_assessment_level_id
			}/review`,
			{
				method: "POST",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
					"Content-Type": "application/json",
				},
				body: humps.decamelizeKeys(values), // Sends form values as JSON
			}
		);
		console.log("Form submitted successfully:", response);
		navigateTo(`/adr`);
	} catch (error) {
		console.error("Error submitting form:", error);
	}
});

type typeValidationSchema = z.infer<typeof reviewFormValidationSchema>;

onMounted(async () => {
	const runtimeConfig = useRuntimeConfig();
	const serverApi = runtimeConfig.public.serverApi;
	const authStore = useAuthStore();

	if (props.mode == "update") {
		const response = await $fetch(
			`${serverApi}/review_for_specific_user_and_causality_assessment_level`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
				params: {
					causality_assessment_level_id:
						props.causality_assessment_level_id,
				},
			}
		);

		// Pre-fill form
		const camel = humps.camelizeKeys(response) as typeValidationSchema;

		for (const key of Object.keys(camel) as Array<
			keyof typeValidationSchema
		>) {
			setFieldValue(key, camel[key]);
		}
	}
});

const filteredCausalityOptions = computed(() => {
	return reviewFormCategoricalValues.proposedCausalityLevel.filter(
		(option) => option.value !== props.predicted_causality_assessment_level
	);
});

console.log(filteredCausalityOptions)
</script>
