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
import { z } from "zod";
import type { TelephonePostRequest } from "~/types/telephone";

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
		const institutionPayload: MedicalInstitutionPostRequestInterface = {
			name: data.name,
			mfl_code: data.mfl_code,
			dhis_code: data.dhis_code,
			county: data.county,
			sub_county: data.sub_county,
		};

		createMedicalInstitution({
			institutionData: institutionPayload,
			phoneNumbers: data.telephone_numbers,
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
