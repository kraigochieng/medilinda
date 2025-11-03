<template>
	<ADRMenu />
	<UForm
		:schema="schema"
		:state="state"
		@submit="onSubmit"
		@error="onFormError"
	>
		<UCard>
			<template #header>
				{{ props.mode == "create" ? "Add" : "Edit" }} an Adverse Drug
				Reaction (ADR) Report
			</template>
			<template #default>
				<div class="form-section">
					<div class="flex items-center gap-x-2">
						<!-- <Icon
							name="lucide:hospital"
							class="form-section-header-icon"
						/> -->
						<p id="institution-details" class="form-section-header">
							1. Institution Details
						</p>
					</div>
					<div class="flex items-center justify-between space-x-2">
						<div class="flex space-x-1">
							<UModal title="Add Medical Institution">
								<span class="underline hover:cursor-pointer">
									Create
								</span>
								<template #body>
									<p class="italic">Form to be added</p>
									<!-- <FormMedicalInstitution
										mode="create"
										:is-in-dialog="true"
										@submitted="
											handleMedicalInstitutionFormSubmitted
										"
									/> -->
								</template>
							</UModal>
							<span>or</span>
							<UModal
								title="Choose a medical institution"
								description="Choose an existing Medical Institution | Search for a medical institution"
							>
								<span class="underline hover:cursor-pointer">
									find
								</span>
								<template #body>
									<div>
										<UInput
											type="text"
											placeholder="Seach for a hospital, minimum 3 characters, by name, MFL Code or location"
											v-model="
												medicalInstitutionSearchInput
											"
										/>
										<URadioGroup
											v-if="
												medicalInstitutionList?.items &&
												medicalInstitutionList.items
													?.length > 0
											"
											v-model="
												state.medical_institution_id
											"
											:items="
												medicalInstitutionList?.items?.map(
													(item) => ({
														label: `${item.name} | ${item.county} | ${item.sub_county}`,
														value: item.id,
													})
												)
											"
										/>
										<div
											v-if="
												medicalInstitutionList?.items
													?.length == 0
											"
										>
											No hospitals
										</div>
									</div>
								</template>
							</UModal>
							<span>a Medical Institution</span>
						</div>
					</div>

					<div v-if="medicalInstitutionData">
						<div class="view-details-wrapper">
							<p>Name</p>
							<p>{{ medicalInstitutionData.name }}</p>
						</div>
						<USeparator />
						<div class="view-details-wrapper">
							<p>MFL Code</p>
							<p>{{ medicalInstitutionData.mfl_code }}</p>
						</div>
						<USeparator />
						<div class="view-details-wrapper">
							<p>DHIS Code</p>
							<p>
								{{ medicalInstitutionData.dhis_code ?? "None" }}
							</p>
						</div>
						<USeparator />
						<div class="view-details-wrapper">
							<p>County</p>
							<p>{{ medicalInstitutionData.county ?? "None" }}</p>
						</div>
						<USeparator />
						<div class="view-details-wrapper">
							<p>Sub County</p>
							<p>
								{{
									medicalInstitutionData.sub_county ?? "None"
								}}
							</p>
						</div>
					</div>
					<p
						v-if="!medicalInstitutionData"
						class="italic text-gray-400 text-center my-4"
					>
						No medical institution created/chosen
					</p>
				</div>
				<USeparator />
				<div class="form-section">
					<div class="flex items-center gap-x-2">
						<!-- <Icon
							name="lucide:user-round"
							class="form-section-header-icon"
						/> -->
						<p id="patient-details" class="form-section-header">
							2. Patient Details
						</p>
					</div>
					<UFormField label="Patient Name" name="patient_name">
						<UInput
							v-model="state.patient_name"
							placeholder="Patient Name"
						/>
					</UFormField>

					<div class="flex space-x-2 justify-between">
						<URadioGroup
							legend="Do you know the patient's date of birth?"
							:items="isDobItems"
							v-model="isDob"
						/>

						<USeparator orientation="vertical" />
						<!-- <UCalendar
							v-model="patientDobModel"
							v-if="isDob == 'dob-yes'"
						/> -->

						<div class="w-full" v-if="isDob == 'dob-no'">
							<UFormField
								label="Patient Age"
								name="patient_age"
								help="Patient Age in Years"
							>
								<UInputNumber
									v-model="state.patient_age"
									:min="1"
									:format-options="{
										style: 'unit',
										unit: 'year',
									}"
								/>
							</UFormField>
						</div>
					</div>

					<UFormField
						label="Patient Height (in cm)"
						name="patient_height_cm"
						help="Patient Height in centimeters (cm)"
					>
						<UInputNumber
							v-model="state.patient_height_cm"
							:min="100"
							:format-options="{
								style: 'unit',
								unit: 'centimeter',
							}"
						/>
					</UFormField>

					<UFormField
						label="Patient Weight (in kg)"
						name="patient_weight_kg"
						help="Patient Weight in kilograms (kg)"
					>
						<UInputNumber
							v-model="state.patient_weight_kg"
							:min="5"
							:format-options="{
								style: 'unit',
								unit: 'kilogram',
							}"
						/>
					</UFormField>
					<UFormField
						label="Inpatient/Outpatient Number"
						help="The inpatient or outpatient number of the patient"
						name="inpatient_or_outpatient_number"
					>
						<UInput
							type="text"
							v-model="state.inpatient_or_outpatient_number"
							placeholder="e.g IN-123456, OUT-654321"
						/>
					</UFormField>

					<UFormField
						label="Patient Address"
						help="The address of the patient"
						name="patient_address"
					>
						<UInput
							type="text"
							v-model="state.patient_address"
							placeholder="e.g Madaraka, Nairobi West, Nairobi"
						/>
					</UFormField>
					<UFormField
						label="Ward/Clinic"
						help="The ward or clinic the patient was in"
						name="ward_or_clinic"
					>
						<UInput
							type="text"
							v-model="state.ward_or_clinic"
							placeholder="e.g Main Ward"
						/>
					</UFormField>
					<UFormField
						name="patient_gender"
						label="Gender"
						help="The gender of the patient"
					>
						<URadioGroup
							v-model="state.patient_gender"
							:items="adrFormCategoricalValues.patientGender"
						/>
					</UFormField>
					<UFormField
						name="pregnancy_status"
						label="Pregnancy Status"
						help="The pregnancy status of the patient"
					>
						<URadioGroup
							v-model="state.pregnancy_status"
							:items="adrFormCategoricalValues.pregnancyStatus"
						/>
					</UFormField>
					<UFormField
						name="known_allergy"
						label="Known Allergy"
						help="If the patient has a known allergy or not"
					>
						<URadioGroup
							v-model="state.known_allergy"
							:items="adrFormCategoricalValues.knownAllergy"
						/>
					</UFormField>
				</div>
				<USeparator />
				<div class="form-section">
					<p
						id="suspected-adverse-reaction"
						class="form-section-header"
					>
						3. Suspected Adverse Reaction
					</p>
					<!-- <FormSelectDatePicker
						name="date_of_onset_of_reaction"
						label="Date Of Onset Of Reaction"
						description="The date of onset of reaction"
						v-model="selectedDateOfOnsetOfReaction"
						default-year="2025"
						default-month="1"
						default-day="1"
					/> -->
					<UFormField
						name="description_of_reaction"
						label="Description of Reaction"
						help="The description of the reaction(s) that took place"
					>
						<UTextarea
							v-model="state.description_of_reaction"
							label="Description Of Reaction"
							placeholder="Description of Reaction"
						/>
					</UFormField>
				</div>
				<USeparator />
				<div class="form-section">
					<p id="medicines" class="form-section-header">
						4. Medicines
					</p>
					<UTable
						:data="state.medicines"
						:columns="medicineColumns"
					/>
				</div>
				<USeparator />
				<div class="form-section">
					<p id="rechallenge" class="form-section-header">
						5. Rechallenge/Dechallenge
					</p>
					<UFormField
						name="rechallenge"
						label="Rechallenge"
						help="Was the drug reintroduced after it was previously discontinued?"
					>
						<URadioGroup
							v-model="state.rechallenge"
							:items="adrFormCategoricalValues.rechallenge"
						/>
					</UFormField>
					<UFormField
						name="dechallenge"
						label="Dechallenge"
						help="Was the drug withdrawn after a suspected ADR?"
					>
						<URadioGroup
							v-model="state.dechallenge"
							:items="adrFormCategoricalValues.dechallenge"
						/>
					</UFormField>
				</div>
				<USeparator />
				<div class="form-section">
					<p id="grading" class="form-section-header">
						6. Grading of the Event
					</p>
					<UFormField
						name="severity"
						label="Severity"
						help="Severity of the reaction"
					>
						<URadioGroup
							v-model="state.severity"
							:items="adrFormCategoricalValues.severity"
						/>
					</UFormField>
					<UFormField
						name="is_serious"
						label="Is Serious"
						help="Is the reaction serious"
					>
						<URadioGroup
							v-model="state.is_serious"
							:items="adrFormCategoricalValues.isSerious"
						/>
					</UFormField>
					<UFormField
						name="criteria_for_seriousness"
						label="Criteria for Seriousness"
						help="The criteria used to classify the reaction as serious"
					>
						<URadioGroup
							v-model="state.criteria_for_seriousness"
							:items="
								adrFormCategoricalValues.criteriaForSeriousness
							"
						/>
					</UFormField>
					<UFormField
						name="action_taken"
						label="Action Taken"
						help="The action taken in response to the ADR"
					>
						<URadioGroup
							v-model="state.action_taken"
							:items="adrFormCategoricalValues.actionTaken"
						/>
					</UFormField>
					<UFormField
						name="outcome"
						label="Outcome"
						help="The outcome of the ADR"
					>
						<URadioGroup
							v-model="state.outcome"
							:items="adrFormCategoricalValues.outcome"
						/>
					</UFormField>
				</div>
				<USeparator />
				<UFormField
					name="comments"
					label="Comments"
					help="The comments on the ADR overall"
				>
					<UTextarea
						v-model="state.comments"
						placeholder="Comments"
					/>
				</UFormField>
			</template>
			<template #footer>
				<UButton
					type="submit"
					class="w-full mx-auto my-4 justify-center"
				>
					{{ props.mode == "create" ? "Add ADR" : "Edit ADR" }}
				</UButton>
			</template>
		</UCard>
	</UForm>
</template>

<script setup lang="ts">
import { fetchCurrentUser } from "@/api/user";
import type { MedicalInstitutionGetResponseInterface } from "@/types/medical_institution";
import { adrFormCategoricalValues } from "@/values/adr";
import { CalendarDate, getLocalTimeZone } from "@internationalized/date";
import type {
	FormErrorEvent,
	FormSubmitEvent,
	RadioGroupItem,
	TableColumn,
} from "@nuxt/ui";
import { useMutation, useQuery } from "@tanstack/vue-query";
import { z } from "zod";
import { fetchMedicalInstitutions } from "~/api/medical_institution";
import type { PaginatedResponseInterface } from "~/types/pagination";
import type { UserDetails } from "@/types/user";
import { postAdr } from "@/api/adr";
import type {
	ADRGetResponseInterface,
	ADRPostRequestInterface,
} from "~/types/adr";

const toast = useToast();
const router = useRouter();
type MedicineRow = {
	name?: string;
	suspected?: boolean;
	batch_no?: string;
	manufacturer?: string;
	dose_amount?: number;
	route?: string;
	frequency_number?: number;
	start_date?: string;
	stop_date?: string;
};

const medicalInstitutionData =
	ref<MedicalInstitutionGetResponseInterface | null>();

// const medicalInstitutionId = ref<string | undefined>();
const medicalInstitutionSearchInput = ref<string>("");

const isDob = ref<string>("dob-yes");

const isDobItems = ref<RadioGroupItem[]>([
	{ label: "Yes", value: "dob-yes" },
	{ label: "No", value: "dob-no" },
]);

const schema = z.object({
	medical_institution_id: z
		.string()
		.uuid("Please select a medical institution."),
	patient_name: z.string().min(3, "Name must be at least 3 characters."),
	// patient_date_of_birth: z
	// 	.instanceof(CalendarDate, { message: "Please select a valid date." })
	// 	.transform((val) => val.toDate(getLocalTimeZone())),
	patient_date_of_birth: z.date(),
	patient_age: z.number().positive().min(0).max(120).optional(),
	patient_height_cm: z.number().positive().optional(),
	patient_weight_kg: z.number().positive().optional(),
	inpatient_or_outpatient_number: z.string().optional(),
	ward_or_clinic: z.string().optional(),
	patient_address: z.string().optional(),
	patient_gender: z.string().optional(),
	date_of_onset_of_reaction: z.string().optional(),
	pregnancy_status: z.string().optional(),
	description_of_reaction: z
		.string()
		.min(10, "Description is too short.")
		.optional(),
	medicines: z.array(
		z.object({
			name: z.string(),
			suspected: z.boolean().default(false),
			batch_no: z.string().optional(),
			manufacturer: z.string().optional(),
			dose_amount: z.number().positive().optional(),
			frequency_number: z.number().positive().optional(),
			route: z.string().optional(),
			start_date: z.string().optional(),
			stop_date: z.string().optional(),
		})
	),
	severity: z.string().optional(),
	outcome: z.string().optional(),

	known_allergy: z.string().optional(),
	rechallenge: z.string().optional(),
	dechallenge: z.string().optional(),
	is_serious: z.string().optional(),
	criteria_for_seriousness: z.string().optional(),
	action_taken: z.string().optional(),
	comments: z.string().optional(),
});

type AdrForm = z.infer<typeof schema>;

const state = reactive<Partial<AdrForm>>({
	medical_institution_id: undefined,
	patient_name: "Kraig Ochieng",
	patient_date_of_birth: undefined,
	inpatient_or_outpatient_number: "IP-123456",
	patient_weight_kg: 60,
	patient_gender: "male",
	patient_height_cm: 178,
	patient_address: "Kileleshwa, Nairobi",
	ward_or_clinic: "Main Clininc",
	date_of_onset_of_reaction: undefined,
	description_of_reaction: "Very disturbing. Vomiting",
	medicines: [
		{
			name: "Rifampicin",
			suspected: false,
			batch_no: "",
			manufacturer: "",
			dose_amount: undefined,
			route: "oral",
			frequency_number: undefined,
			start_date: "",
			stop_date: "",
		},
		{
			name: "Isoniazid",
			suspected: false,
			batch_no: "",
			manufacturer: "",
			dose_amount: undefined,
			route: "oral",
			frequency_number: undefined,
			start_date: "",
			stop_date: "",
		},
		{
			name: "Pyrazinamide",
			suspected: false,
			batch_no: "",
			manufacturer: "",
			dose_amount: undefined,
			route: undefined,
			frequency_number: undefined,
			start_date: "",
			stop_date: "",
		},
		{
			name: "Ethambutol",
			suspected: false,
			batch_no: "",
			manufacturer: "",
			dose_amount: undefined,
			route: "oral",
			frequency_number: undefined,
			start_date: "",
			stop_date: "",
		},
	],
	pregnancy_status: "not applicable",
	known_allergy: "no",
	rechallenge: "yes",
	dechallenge: "yes",
	is_serious: "no",
	criteria_for_seriousness: "hospitalisation",
	action_taken: "unknown",
	outcome: "recovered",
	comments: "Will be looked into",
});

const patientDobModel = ref(new CalendarDate(2022, 1, 1));

watch(
	patientDobModel,
	(newDate) => {
		if (newDate) {
			state.patient_date_of_birth = newDate.toDate(getLocalTimeZone());
		}
	},
	{ immediate: true }
);

const UFormField = resolveComponent("UFormField");
const UCheckbox = resolveComponent("UCheckbox");
const UInput = resolveComponent("UInput");
const USelect = resolveComponent("USelect");

const debouncedMedicalInstitutionSearchInput = refDebounced(
	medicalInstitutionSearchInput,
	500
);

const {
	data: medicalInstitutionList,
	isPending,
	isError,
	error,
	isFetching,
} = useQuery<
	PaginatedResponseInterface<MedicalInstitutionGetResponseInterface>,
	Error
>({
	queryKey: ["medicalInstitutions", debouncedMedicalInstitutionSearchInput],
	queryFn: () =>
		fetchMedicalInstitutions({
			size: 10,
			query: debouncedMedicalInstitutionSearchInput.value,
		}),
});

const { data: currentUser, isPending: isUserPending } = useQuery<
	UserDetails,
	Error
>({
	queryKey: ["currentUser"],
	queryFn: fetchCurrentUser,
});

const { mutate: createADR, isPending: isSubmitting } = useMutation<
	ADRGetResponseInterface,
	Error,
	ADRPostRequestInterface
>({
	mutationFn: (payload) => postAdr(payload),
	onSuccess: (data) => {
		toast.add({
			title: "Success",
			description: "ADR report created successfully.",
			color: "success",
		});
		// You can navigate away or reset the form
		router.push(`/adr/${data.id}`); // Example navigation
	},
	onError: (error) => {
		console.error("Failed to create ADR:", error);
		toast.add({
			title: "Error",
			description: `Failed to create ADR: ${error.message}`,
			color: "error",
		});
	},
});

const medicineColumns: TableColumn<MedicineRow>[] = [
	{
		accessorKey: "suspected",
		header: "Suspected",
		cell: ({ row }) =>
			h(
				UFormField,
				{
					// Removed `index` from here
					name: `medicines[${row.index}].suspected`, // Use `row.index` here
				},
				{
					default: () =>
						h(UCheckbox, {
							modelValue: row.original.suspected,
							"onUpdate:modelValue": (value: boolean) =>
								(row.original.suspected = value),
						}),
				}
			),
	},
	{
		accessorKey: "name",
		header: "INN/Generic Name",
	},
	{
		accessorKey: "batch_no",
		header: "Batch Number",
		cell: ({ row }) =>
			h(
				UFormField,
				{
					name: `medicines[${row.index}].batch_no`,
				},
				{
					default: () =>
						h(UInput, {
							modelValue: row.original.batch_no,
							"onUpdate:modelValue": (value: string) =>
								(row.original.batch_no = value),
							placeholder: "e.g B123456",
						}),
				}
			),
	},
	{
		accessorKey: "manufacturer",
		header: "Manufacturer",
		cell: ({ row }) =>
			h(
				UFormField,
				{
					name: `medicines[${row.index}].manufacturer`,
				},
				{
					default: () =>
						h(UInput, {
							modelValue: row.original.manufacturer,
							"onUpdate:modelValue": (value: string) =>
								(row.original.manufacturer = value),
							placeholder: "e.g Pfizer",
						}),
				}
			),
	},
	{
		accessorKey: "dose_amount",
		header: "Dose (mg)",
		cell: ({ row }) =>
			h(
				UFormField,
				{
					name: `medicines[${row.index}].dose_amount`,
				},
				{
					default: () =>
						h(UInput, {
							modelValue: row.original.dose_amount,
							"onUpdate:modelValue": (value: string) =>
								(row.original.dose_amount = Number(value)),
							type: "number",
							placeholder: "e.g 150",
						}),
				}
			),
	},
	{
		accessorKey: "route",
		header: "Route",
		cell: ({ row }) =>
			h(
				UFormField,
				{
					name: `medicines[${row.index}].route`,
				},
				{
					default: () =>
						h(USelect, {
							modelValue: row.original.route,
							"onUpdate:modelValue": (value: string) =>
								(row.original.route = value),
							items: adrFormCategoricalValues.route,
							placeholder: "Route",
						}),
				}
			),
	},
	{
		accessorKey: "frequency_number",
		header: "Frequency",
		cell: ({ row }) =>
			h(
				UFormField,
				{
					name: `medicines[${row.index}].frequency_number`,
				},
				{
					default: () =>
						h(UInput, {
							modelValue: row.original.frequency_number,
							"onUpdate:modelValue": (value: string) =>
								(row.original.frequency_number = Number(value)),
							type: "number",
							placeholder: "e.g 1",
						}),
				}
			),
	},
	{
		accessorKey: "start_date",
		header: "Start Date",
		cell: ({ row }) =>
			h(
				UFormField,
				{
					name: `medicines[${row.index}].start_date`,
				},
				{
					default: () =>
						h(UInput, {
							modelValue: row.original.start_date,
							"onUpdate:modelValue": (value: string) =>
								(row.original.start_date = value),
							type: "date",
						}),
				}
			),
	},
	{
		accessorKey: "stop_date",
		header: "Stop Date",
		cell: ({ row }) =>
			h(
				UFormField,
				{
					name: `medicines[${row.index}].stop_date`,
				},
				{
					default: () =>
						h(UInput, {
							modelValue: row.original.stop_date,
							"onUpdate:modelValue": (value: string) =>
								(row.original.stop_date = value),
							type: "date",
						}),
				}
			),
	},
];

// V-model for columns
const selectedDateOfOnsetOfReaction = ref<string>("");

const months = [
	"January",
	"February",
	"March",
	"April",
	"May",
	"June",
	"July",
	"August",
	"September",
	"October",
	"November",
	"December",
];

function transformDataToPayload(
	data: AdrForm,
	userId: string
): ADRPostRequestInterface {
	// 1. Destructure the `medicines` array out
	const { medicines, ...baseData } = data;

	// 2. Create a helper map for prefixes
	const medicineMap: { [key: string]: string } = {
		Rifampicin: "rifampicin",
		Isoniazid: "isoniazid",
		Pyrazinamide: "pyrazinamide",
		Ethambutol: "ethambutol",
	};

	const flatMedicineData: Partial<ADRPostRequestInterface> = {};

	// 3. Loop over the `medicines` array and flatten
	if (medicines) {
		for (const med of medicines) {
			const prefix = medicineMap[med.name as keyof typeof medicineMap];
			if (prefix) {
				// Assign each field with its prefix
				(flatMedicineData as any)[`${prefix}_suspected`] =
					med.suspected;
				(flatMedicineData as any)[`${prefix}_start_date`] =
					med.start_date || null;
				(flatMedicineData as any)[`${prefix}_stop_date`] =
					med.stop_date || null;
				(flatMedicineData as any)[`${prefix}_dose_amount`] =
					med.dose_amount;
				(flatMedicineData as any)[`${prefix}_frequency_number`] =
					med.frequency_number;
				(flatMedicineData as any)[`${prefix}_route`] = med.route;
				(flatMedicineData as any)[`${prefix}_batch_no`] = med.batch_no;
				(flatMedicineData as any)[`${prefix}_manufacturer`] =
					med.manufacturer;
			}
		}
	}

	// 4. Construct the final payload
	const payload: ADRPostRequestInterface = {
		...baseData,
		user_id: userId,
		medical_institution_id: baseData.medical_institution_id, // Ensure it's passed

		// Convert Date object to YYYY-MM-DD string
		patient_date_of_birth: baseData.patient_date_of_birth
			? baseData.patient_date_of_birth.toISOString().split("T")[0]
			: undefined,

		// Add the flattened medicine data
		...flatMedicineData,
	};

	return payload;
}

async function onSubmit(event: FormSubmitEvent<AdrForm>) {
	console.log("Form validated...");

	if (!currentUser.value?.id) {
		toast.add({
			title: "Error",
			description: "Could not find user. Please log in again.",
			color: "error",
		});
		return;
	}

	const payload = transformDataToPayload(event.data, currentUser.value.id);

	console.log("Submitting payload:", payload);

	if (props.mode === "create") {
		createADR(payload);
	} else if (props.mode === "update" && props.id) {
		// TODO: Implement update logic
		// You would need a `putADR` mutation and call it here
		console.warn("Update functionality is not yet implemented.");
	}
}

function onFormError(event: FormErrorEvent) {
	console.error("Form validation failed:", event.errors);
	toast.add({
        title: "Validation Error",
        description: "Please check the form for errors.",
        color: "error",
    });
	// You'll see an array of all validation issues here
}
const props = defineProps<{
	id?: string;
	mode: "create" | "update";
}>();
</script>
