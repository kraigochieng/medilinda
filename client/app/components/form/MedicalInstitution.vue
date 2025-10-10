<template>
	<UForm>
		<UCard>
			<template #header>
				<h1>Add Medical Institution</h1>
				<h2>
					Add an Medical Institution so that it can be part of an ADR
					Report
				</h2>
			</template>
			<template #default>
				<UFormField
					label="Institution Name"
					name="name"
					help="The official name of the medical institution"
				>
					<UInput
						type="text"
						v-model="state.name"
						placeholder="Enter institution name"
						class="w-full"
					/>
				</UFormField>

				<UFormField
					label="MFL Code"
					name="mfl_code"
					help="The Master Facility List (MFL) code of the institution"
				>
					<UInput
						type="text"
						v-model="state.mfl_code"
						placeholder="e.g. 999999"
						class="w-full"
					/>
				</UFormField>

				<UFormField
					label="DHIS Code"
					name="dhis_code"
					help="The District Health Information System (DHIS) code of the institution"
				>
					<UInput
						type="text"
						v-model="state.dhis_code"
						placeholder="e.g. DHIS12345"
						class="w-full"
					/>
				</UFormField>

				<UFormField
					label="County"
					name="county"
					help="The county where the institution is located"
				>
					<UInput
						type="text"
						v-model="state.county"
						placeholder="e.g. Nairobi"
						class="w-full"
					/>
				</UFormField>

				<UFormField
					label="Sub-County"
					name="sub_county"
					help="The sub-county where the institution is located"
				>
					<UInput
						type="text"
						v-model="state.sub_county"
						placeholder="e.g. Langata"
						class="w-full"
					/>
				</UFormField>
				<div>
					<Label>Telephone Numbers</Label>
					<div class="flex flex-col gap-2 my-4">
						<div
							v-if="state.telephone_numbers"
							v-for="(phone, index) in state.telephone_numbers"
							:key="index"
							class="flex items-center gap-2"
						>
							<UInput
								v-model="state.telephone_numbers[index]"
								:name="`telephone_number_${index}`"
								type="tel"
								pattern="^(\+254(1|7)\d{8}|0(1|7)\d{8})$"
								placeholder="e.g +254712345678 or 0712345678"
								class="flex-1"
								required
							/>

							<UButton
								type="button"
								@mouseup="removeTelephoneNumber(index)"
								:disabled="state.telephone_numbers.length <= 1"
							>
								-
							</UButton>
						</div>

						<UButton
							type="button"
							variant="outline"
							class="w-fit mx-auto my-2"
							@mouseup="addTelephoneNumber"
						>
							Add Telephone Number
						</UButton>
					</div>
				</div>
			</template>
			<template #footer>
				<UButton id="submit" type="submit" class="w-full mx-auto my-4">
					{{
						props.mode == "create"
							? "Add Medical Institution"
							: "Edit Medical Institution"
					}}
				</UButton>
			</template>
		</UCard>
	</UForm>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from "@nuxt/ui";
import { z } from "zod";

const props = withDefaults(
	defineProps<{
		id?: string;
		mode: "create" | "update";
		isInDialog?: boolean;
	}>(),
	{ isInDialog: false }
);

const schema = z.object({
	name: z.string().default("The default hospital name"),
	mfl_code: z.string().default("999999"),
	dhis_code: z.string().optional(),
	county: z.string().default("Nairobi").optional(),
	sub_county: z.string().default("Langata").optional(),
	telephone_numbers: z
		.array(z.string())
		.min(1, "At least one phone number is required")
		.default([]),
});

export type Schema = z.infer<typeof schema>;

const state = reactive<Partial<Schema>>({
	name: undefined,
	mfl_code: undefined,
	dhis_code: undefined,
	county: undefined,
	sub_county: undefined,
	telephone_numbers: ["+254777529295", "0787654321"],
});

const emit = defineEmits<{
	(
		e: "submitted",
		success: boolean,
		medicalInstitutionId?: string,
		message?: string
	): void;
}>();

// Lifecycle hooks
onMounted(async () => {
	// // If there is an id
	// if (props.id) {
	// 	// Get existing data
	// 	const response =
	// 		await $fetch<Schema>(
	// 			`${serverApi}/medical_institution/${props.id}`,
	// 			{
	// 				method: "GET",
	// 				headers: {
	// 					Authorization: `Bearer ${authStore.accessToken}`,
	// 				},
	// 			}
	// 		);
	// 	// Pre-fill form
	// 	const camel = humps.camelizeKeys(
	// 		response
	// 	) as Schema;
	// 	for (const key of Object.keys(camel) as Array<
	// 		keyof Schema
	// 	>) {
	// 		setFieldValue(key, camel[key]);
	// 	}
	// }
});

// Add new telephone number
function addTelephoneNumber() {
	state.telephone_numbers?.push("");
}

// Remove a telephone number
function removeTelephoneNumber(index: number) {
	if (state.telephone_numbers && state.telephone_numbers.length > 1) {
		state.telephone_numbers.splice(index, 1);
	}
}

async function onSubmit(event: FormSubmitEvent<Schema>) {
	// const runtimeConfig = useRuntimeConfig();
	// const serverApi = runtimeConfig.public.serverApi;
	// const authStore = useAuthStore();
	// if (props.mode == "create") {
	// 	const { data, status, error } =
	// 		await useFetch<MedicalInstitutionPostResponseInterface>(
	// 			`${serverApi}/medical_institution`,
	// 			{
	// 				method: "POST",
	// 				headers: {
	// 					Authorization: `Bearer ${authStore.accessToken}`,
	// 				},
	// 				body: {
	// 					name: values["name"],
	// 					mfl_code: values["mfl_code"],
	// 					dhis_code: values["dhis_code"],
	// 					county: values["county"],
	// 					subcounty: values["sub_county"],
	// 				},
	// 			}
	// 		);
	// 	if (status.value === "success" && data.value) {
	// 		const medicalInstitutionId = data.value.id; // or whatever field contains the ID
	// 		const telephonePayload = values.telephone_numbers.map((phone) => ({
	// 			medical_institution_id: medicalInstitutionId,
	// 			telephone: phone,
	// 		}));
	// 		console.log("telephonePayload", telephonePayload);
	// 		const {
	// 			data: telData,
	// 			status: telStatus,
	// 			error: telError,
	// 		} = await useFetch(
	// 			`${serverApi}/medical_institution_telephone`, // or your correct endpoint
	// 			{
	// 				method: "POST",
	// 				headers: {
	// 					Authorization: `Bearer ${authStore.accessToken}`,
	// 				},
	// 				body: {
	// 					telephones: telephonePayload,
	// 				},
	// 			}
	// 		);
	// 		if (telStatus.value === "success") {
	// 			console.log("Telephones added successfully!");
	// 			emit("submitted", true, data.value.id);
	// 		} else {
	// 			console.error("Failed to add telephones:", telError.value);
	// 			emit("submitted", false);
	// 		}
	// 	}
	// } else if (props.mode == "update") {
	// 	const { data, status, error } =
	// 		await useFetch<MedicalInstitutionPostResponseInterface>(
	// 			`${serverApi}/medical_institution/${props.id}`,
	// 			{
	// 				method: "PUT",
	// 				headers: {
	// 					Authorization: `Bearer ${authStore.accessToken}`,
	// 				},
	// 				body: humps.decamelizeKeys(values),
	// 			}
	// 		);
	// if (status.value == "success" && data.value) {
	// 	const {
	// 		data: calData,
	// 		status: calStatus,
	// 		error,
	// 	} = await useFetch<PaginatedCausalityAssessmentLevel>(
	// 		`${serverApi}/adr/${data.value.id}/causality_assessment_level`,
	// 		{
	// 			method: "GET",
	// 			headers: {
	// 				Authorization: `Bearer ${authStore.accessToken}`,
	// 			},
	// 			params: {
	// 				page: 1,
	// 				size: 50,
	// 			},
	// 		}
	// 	);
	// 	if (calStatus.value == "success" && calData.value?.items) {
	// 		navigateTo(
	// 			`/causality-assessment-level/${calData.value.items[0].id}/review`
	// 		);
	// 	}
	// }
}
</script>
