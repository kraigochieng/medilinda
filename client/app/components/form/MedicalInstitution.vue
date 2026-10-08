<template>
	<UForm @submit="onSubmit" :schema="schema" :state="state">
		<UCard>
			<template v-if="!isInDialog" #header>
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
					<p class="font-medium">Telephone Numbers</p>
					<div class="flex flex-col gap-2 my-4">
						<div
							v-if="state.telephone_numbers"
							v-for="(phone, index) in state.telephone_numbers"
							:key="index"
							class="flex items-center gap-2"
						>
							<UFormField :name="`telephone_numbers.${index}`" class="flex-1">
								<UInput
									v-model="state.telephone_numbers[index]"
									type="tel"
									autocomplete="tel"
									placeholder="e.g. 0712 345 678 or +254 712 345 678"
									class="w-full"
								/>
							</UFormField>

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
				<UButton
					id="submit"
					type="submit"
					class="w-full mx-auto my-4"
					:loading="isSubmitting"
				>
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
import { postMedicalInstitution } from "@/api/medical_institution";
import { postTelephones } from "@/api/telephone";
import type {
	MedicalInstitutionGetResponseInterface,
	MedicalInstitutionPostRequestInterface,
} from "@/types/medical_institution";
import type { FormSubmitEvent } from "@nuxt/ui";
import { useMutation } from "@tanstack/vue-query";
import {
	emptyInstitutionForm,
	institutionFormSchema,
	toInstitutionPayload,
	type InstitutionForm,
} from "~/utils/institution-form";
import type { TelephonePostRequest } from "~/types/telephone";

const props = withDefaults(
	defineProps<{
		id?: string;
		mode: "create" | "update";
		isInDialog?: boolean;
	}>(),
	{ isInDialog: false }
);

const schema = institutionFormSchema;

type Schema = InstitutionForm;

// Blank on purpose: SMS alerts go to these numbers, so nothing may be preset.
const state = reactive<Partial<Schema>>(emptyInstitutionForm());

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
	if (props.mode === "update" && props.id) {
		// Your logic to fetch and pre-fill data for update mode goes here
		// e.g., const data = await fetchMedicalInstitutionById(props.id);
		// Object.assign(state, data);
		console.log("Update mode: Fetching data for ID:", props.id);
	}
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

const { mutate: createTelephones, isPending: isTelephonesPending } =
	useMutation<TelephonePostRequest[], Error, TelephonePostRequest[]>({
		mutationFn: (telephones) => postTelephones(telephones),
	});

const { mutate: createMedicalInstitution, isPending: isInstitutionPending } =
	useMutation<
		MedicalInstitutionGetResponseInterface,
		Error,
		{
			institutionData: MedicalInstitutionPostRequestInterface;
			phoneNumbers: string[];
		}
	>({
		mutationFn: (vars) => postMedicalInstitution(vars.institutionData),

		onSuccess: (createdInstitution, variables) => {
			console.log("Institution created:", createdInstitution);

			const telephonePayload: TelephonePostRequest[] =
				variables.phoneNumbers.map((phone) => ({
					medical_institution_id: createdInstitution.id,
					telephone: phone,
				}));

			// Trigger the telephone mutation
			createTelephones(telephonePayload, {
				onSuccess: () => {
					console.log("Telephones added successfully!");
					emit(
						"submitted",
						true,
						createdInstitution.id,
						"Institution and telephones created."
					);
				},
				onError: (error) => {
					console.error("Failed to add telephones:", error);

					emit(
						"submitted",
						true,
						createdInstitution.id,
						`Institution created, but failed to add telephones: ${error.message}`
					);
				},
			});
		},
		onError: (error) => {
			console.error("Failed to create medical institution:", error);
			emit(
				"submitted",
				false,
				undefined,
				`Failed to create institution: ${error.message}`
			);
		},
	});

const { mutate: updateMedicalInstitution, isPending: isUpdatePending } =
	useMutation<
		MedicalInstitutionGetResponseInterface,
		Error,
		{ data: Schema; id: string }
	>({
		mutationFn: async (vars) => {
			// 1. Call your `putMedicalInstitution(vars.id, vars.data)`
			// 2. Call your logic to update telephones (e.g., `putTelephones(...)`)
			console.warn(
				"Update mutation logic is not fully implemented.",
				vars
			);
			// This is a placeholder. Replace with your actual update API call.
			// await putMedicalInstitution(vars.id, vars.data);
			// await updateTelephones(vars.id, vars.data.telephone_numbers);

			// Simulating a successful response for now
			return { id: vars.id, ...vars.data };
		},
		onSuccess: (updatedInstitution) => {
			console.log("Institution updated:", updatedInstitution);
			emit(
				"submitted",
				true,
				updatedInstitution.id,
				"Institution updated successfully."
			);
		},
		onError: (error) => {
			console.error("Failed to update institution:", error);
			emit(
				"submitted",
				false,
				undefined,
				`Failed to update: ${error.message}`
			);
		},
	});

// Combined loading state for the submit button
const isSubmitting = computed(
	() =>
		isInstitutionPending.value ||
		isTelephonesPending.value ||
		isUpdatePending.value
);
async function onSubmit(event: FormSubmitEvent<Schema>) {
	const { data } = event;

	if (props.mode === "create") {
		const { institution, phones } = toInstitutionPayload(data);

		createMedicalInstitution({
			institutionData: institution,
			phoneNumbers: phones,
		});
	} else if (props.mode === "update" && props.id) {
		updateMedicalInstitution({
			data: data,
			id: props.id,
		});
	} else {
		console.error(
			"Submission error: Invalid mode or missing ID for update."
		);
		emit("submitted", false, undefined, "Invalid form state.");
	}
}
</script>
