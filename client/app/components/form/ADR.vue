<template>
	<UForm :schema="schema" :state="state" @submit="onSubmit">
		<UCard>
			<template #header>
				{{ props.mode == "create" ? "Add" : "Edit" }} an Adverse Drug
				Reaction (ADR) Report
			</template>
			<template #default>
				<div
					class="fixed top-24 right-4 border rounded-sm bg-white p-2"
				>
					<UPopover>
						<Icon name="lucide:menu" />
						<template #content>
							<div>
								<p class="font-semibold">Form Sections</p>
								<p>
									<a href="#institution-details">
										1. Institution Details
									</a>
								</p>
								<p>
									<a href="#patient-details">
										2. Patient Details
									</a>
								</p>
								<p>
									<a href="#suspected-adverse-reaction">
										3. Suspected Adverse Reaction
									</a>
								</p>
								<p>
									<a href="#medicines"> 4. Medicines </a>
								</p>
								<p>
									<a href="#rechallenge">
										5. Rechallenge/Dechallenge
									</a>
								</p>
								<p>
									<a href="#grading">
										6. Grading of the Event
									</a>
								</p>
								<p>
									<a href="#submit">
										7.
										{{
											props.mode == "create"
												? "Add Adr"
												: "Edit ADR"
										}}
										Button
									</a>
								</p>
							</div>
						</template>
					</UPopover>
				</div>
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
							<UModal>
								<span class="underline hover:cursor-pointer">
									Create
								</span>
								<template #content>
									<!-- <MedicalInstitutionForm
										mode="create"
										:is-in-dialog="true"
										@submitted="
											handleMedicalInstitutionFormSubmitted
										"
									/> -->
								</template>
							</UModal>
							<span>or</span>
							<UModal>
								<span class="underline hover:cursor-pointer">
									find
								</span>
								<template #content>
									<UCard>
										<template #header>
											<p>
												Choose an existing Medical
												Institution | Search for a
												medical institution
											</p>
										</template>
										<template #default>
											<div>
												<UInput
													type="text"
													placeholder="Seach for a hospital, minimum 3 characters, by name, MFL Code or location"
													v-model="
														medicalInstitutionSearchInput
													"
												/>
												<!-- <div
													v-if="
														medicalInstitutionList &&
														medicalInstitutionList.length >
															0
													"
												>
													<RadioGroup
														v-model="
															medicalInstitutionId
														"
													>
														<div
															v-for="medicalInstitution in medicalInstitutionList"
														>
															<RadioGroupItem
																:id="
																	medicalInstitution.id
																"
																:value="
																	medicalInstitution.id
																"
															/>
															<Label
																:for="
																	medicalInstitution.id
																"
															>
																{{
																	medicalInstitution.name
																}}
																|
																{{
																	medicalInstitution.mfl_code
																}}</Label
															>
														</div>
													</RadioGroup>
												</div> -->
												<div
													v-if="
														medicalInstitutionList?.length ==
														0
													"
												>
													No hospitals
												</div>
											</div>
										</template>
									</UCard>
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
					<UFormField label="Patient Name" name="patientName">
						<UInput
							v-model="state.patientName"
							placeholder="Patient Name"
						/>
					</UFormField>

					<div class="flex items-center space-x-4">
						<div>
							<URadioGroup
								legend="Do you know the patient's date of birth?"
								:items="isDobItems"
								v-model="isDob"
							/>
						</div>
						<USeparator orientation="vertical" />
						<!-- <UCalendar
							v-model="patientDobModel"
							v-if="isDob == 'dob-yes'"
						/> -->

						<div class="w-full">
							<UFormField
								label="Patient Age"
								name="patientAge"
								help="Patient Age in Years"
								v-if="isDob == 'dob-no'"
							>
								<UInputNumber
									v-model="state.patientAge"
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
						name="patientHeightCm"
						help="Patient Height in centimeters (cm)"
					>
						<UInputNumber
							class="w-16 mx-auto"
							v-model="state.patientHeightCm"
							:min="100"
							:format-options="{
								style: 'unit',
								unit: 'centimeter',
							}"
						/>
					</UFormField>

					<UFormField
						label="Patient Weight (in kg)"
						name="patientWeightKg"
						help="Patient Weight in kilograms (kg)"
					>
						<UInputNumber
							v-model="state.patientWeightKg"
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
						name="inpatientOrOutpatientNumber"
					>
						<UInput
							type="text"
							v-model="state.inpatientOrOutpatientNumber"
							placeholder="e.g IN-123456, OUT-654321"
						/>
					</UFormField>

					<UFormField
						label="Patient Address"
						help="The address of the patient"
						name="patientAddress"
					>
						<UInput
							type="text"
							v-model="state.patientAddress"
							placeholder="e.g Madaraka, Nairobi West, Nairobi"
						/>
					</UFormField>
					<UFormField
						label="Ward/Clinic"
						help="The ward or clinic the patient was in"
						name="wardOrClinic"
					>
						<UInput
							type="text"
							v-model="state.wardOrClinic"
							placeholder="e.g Main Ward"
						/>
					</UFormField>
					<UFormField
						name="patientGender"
						label="Gender"
						help="The gender of the patient"
					>
						<URadioGroup
							v-model="state.patientGender"
							:items="adrFormCategoricalValues.patientGender"
						/>
					</UFormField>
					<UFormField
						name="pregnancyStatus"
						label="Pregnancy Status"
						help="The pregnancy status of the patient"
					>
						<URadioGroup
							v-model="state.pregnancyStatus"
							:items="adrFormCategoricalValues.pregnancyStatus"
						/>
					</UFormField>
					<UFormField
						name="knownAllergy"
						label="Known Allergy"
						help="If the patient has a known allergy or not"
					>
						<URadioGroup
							v-model="state.knownAllergy"
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
					<FormSelectDatePicker
						name="dateOfOnsetOfReaction"
						label="Date Of Onset Of Reaction"
						description="The date of onset of reaction"
						v-model="selectedDateOfOnsetOfReaction"
						default-year="2025"
						default-month="1"
						default-day="1"
					/>
					<FormTextArea
						name="descriptionOfReaction"
						label="Description Of Reaction"
						placeholder="Description of Reaction"
						description="The description of the reaction(s) that took place"
					/>
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
						name="isSerious"
						label="Is Serious"
						help="Is the reaction serious"
					>
						<URadioGroup
							v-model="state.isSerious"
							:items="adrFormCategoricalValues.isSerious"
						/>
					</UFormField>
					<UFormField
						name="criteriaForSeriousness"
						label="Criteria for Seriousness"
						help="The criteria used to classify the reaction as serious"
					>
						<URadioGroup
							v-model="state.criteriaForSeriousness"
							:items="
								adrFormCategoricalValues.criteriaForSeriousness
							"
						/>
					</UFormField>
					<UFormField
						name="actionTaken"
						label="Action Taken"
						help="The action taken in response to the ADR"
					>
						<URadioGroup
							v-model="state.actionTaken"
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
				<UButton id="submit" type="submit" class="w-full mx-auto my-4 justify-center">
					{{ props.mode == "create" ? "Add ADR" : "Edit ADR" }}
				</UButton>
			</template>
		</UCard>
	</UForm>
</template>

<script setup lang="ts">
import type { MedicalInstitutionGetResponseInterface } from "@/types/medical_institution";
import { adrFormCategoricalValues } from "@/values/adr";
import { CalendarDate, getLocalTimeZone } from "@internationalized/date";
import type { FormSubmitEvent, RadioGroupItem, TableColumn } from "@nuxt/ui";
import { z } from "zod";

type MedicineRow = {
	name?: string;
	suspected?: boolean;
	batchNo?: string;
	manufacturer?: string;
	doseAmount?: number;
	route?: string;
	frequencyNumber?: number;
	startDate?: string;
	stopDate?: string;
};

const medicalInstitutionData =
	ref<MedicalInstitutionGetResponseInterface | null>();
const medicalInstitutionList = ref<
	MedicalInstitutionGetResponseInterface[] | null
>();
const medicalInstitutionId = ref<string | undefined>();
const medicalInstitutionSearchInput = ref<string>("");
const isCreateMedicalInstitutionDialogOpen = ref(false);
// const authStore = useAuthStore();
const isDob = ref<string>("dob-yes");

const isDobItems = ref<RadioGroupItem[]>([
	{ label: "Yes", value: "dob-yes" },
	{ label: "No", value: "dob-no" },
]);

const schema = z.object({
	medicalInstitutionId: z
		.string()
		.uuid("Please select a medical institution."),
	patientName: z.string().min(3, "Name must be at least 3 characters."),
	// patientDateOfBirth: z
	// 	.instanceof(CalendarDate, { message: "Please select a valid date." })
	// 	.transform((val) => val.toDate(getLocalTimeZone())),
	patientDateOfBirth: z.date(),
	patientAge: z.number().positive().min(0).max(120),
	patientHeightCm: z.number().positive().optional(),
	patientWeightKg: z.number().positive().optional(),
	inpatientOrOutpatientNumber: z.string().optional(),
	wardOrClinic: z.string().optional(),
	patientAddress: z.string().optional(),
	patientGender: z.string().optional(),
	dateOfOnsetOfReaction: z.string().optional(),
	descriptionOfReaction: z
		.string()
		.min(10, "Description is too short.")
		.optional(),
	medicines: z.array(
		z.object({
			name: z.string(), // Not for submission, just for UI
			suspected: z.boolean().default(false),
			batchNo: z.string().optional(),
			manufacturer: z.string().optional(),
			doseAmount: z.number().positive().optional(),
			frequencyNumber: z.number().positive().optional(),
			route: z.string().optional(),
			startDate: z.string().optional(),
			stopDate: z.string().optional(),
		})
	),
	severity: z.string().optional(),
	outcome: z.string().optional(),
	pregnancyStatus: z.string().optional(),
	knownAllergy: z.string().optional(),
	rechallenge: z.string().optional(),
	dechallenge: z.string().optional(),
	isSerious: z.string().optional(),
	criteriaForSeriousness: z.string().optional(),
	actionTaken: z.string().optional(),
	comments: z.string().optional(),
});

type AdrForm = z.infer<typeof schema>;

const state = reactive<Partial<AdrForm>>({
	medicalInstitutionId: undefined,
	patientName: undefined,
	patientDateOfBirth: undefined,
	inpatientOrOutpatientNumber: undefined,
	patientAddress: undefined,
	wardOrClinic: undefined,
	medicines: [
		{
			name: "Rifampicin",
			suspected: false,
			batchNo: "",
			manufacturer: "",
			doseAmount: undefined,
			route: undefined,
			frequencyNumber: undefined,
			startDate: "",
			stopDate: "",
		},
		{
			name: "Isoniazid",
			suspected: false,
			batchNo: "",
			manufacturer: "",
			doseAmount: undefined,
			route: undefined,
			frequencyNumber: undefined,
			startDate: "",
			stopDate: "",
		},
		{
			name: "Pyrazinamide",
			suspected: false,
			batchNo: "",
			manufacturer: "",
			doseAmount: undefined,
			route: undefined,
			frequencyNumber: undefined,
			startDate: "",
			stopDate: "",
		},
		{
			name: "Ethambutol",
			suspected: false,
			batchNo: "",
			manufacturer: "",
			doseAmount: undefined,
			route: undefined,
			frequencyNumber: undefined,
			startDate: "",
			stopDate: "",
		},
	],
	pregnancyStatus: undefined,
	knownAllergy: undefined,
	rechallenge: undefined,
	dechallenge: undefined,
	isSerious: undefined,
	criteriaForSeriousness: undefined,
	actionTaken: undefined,
	comments: undefined,
});

// export const adrFormValidationSchema = z.object({
// 	// Personal Details
// 	medicalInstitutionId: z.string().default("uuid"),
// 	patientName: z.string().default("Kraig Ochieng"),
// 	inpatientOrOutpatientNumber: z.string().default("IP-123456"),
// 	patientDateOfBirth: z.string(),
// 	patientAge: z.number(),
// 	patientAddress: z.string().default("Kileleshwa, Nairobi"),
// 	patientWeightKg: z.number().default(60),
// 	patientHeightCm: z.number().default(178),
// 	wardOrClinic: z.string().default("Main Clinic"),
// 	patientGender: z
// 		.enum(
// 			adrFormCategoricalValues["patientGender"].map((x) => x.value) as [
// 				string,
// 				...string[]
// 			]
// 		)
// 		.default("male"),
// 	pregnancyStatus: z
// 		.enum(
// 			adrFormCategoricalValues["pregnancyStatus"].map((x) => x.value) as [
// 				string,
// 				...string[]
// 			]
// 		)
// 		.default("not applicable"),
// 	knownAllergy: z
// 		.enum(
// 			adrFormCategoricalValues["knownAllergy"].map((x) => x.value) as [
// 				string,
// 				...string[]
// 			]
// 		)
// 		.default("no"),
// 	// SuspeCted Adverse Reaction
// 	dateOfOnsetOfReaction: z.string(),
// 	descriptionOfReaction: z.string().default("Very disturbing. Vomiting"),
// 	// Medicines
// 	rifampicinSuspected: z.boolean().optional(),
// 	rifampicinBatchNo: z.string().optional(),
// 	rifampicinManufacturer: z.string().optional(),
// 	rifampicinDoseAmount: z.number().optional(),
// 	rifampicinRoute: z
// 		.enum(
// 			adrFormCategoricalValues["route"].map((x) => x.value) as [
// 				string,
// 				...string[]
// 			]
// 		)
// 		.default("oral"),
// 	rifampicinFrequencyNumber: z.number().optional(),
// 	rifampicinStartDate: z.string().optional(),
// 	rifampicinStopDate: z.string().optional(),

// 	isoniazidSuspected: z.boolean().optional(),
// 	isoniazidBatchNo: z.string().optional(),
// 	isoniazidManufacturer: z.string().optional(),
// 	isoniazidDoseAmount: z.number().optional(),
// 	isoniazidRoute: z
// 		.enum(
// 			adrFormCategoricalValues["route"].map((x) => x.value) as [
// 				string,
// 				...string[]
// 			]
// 		)
// 		.default("oral"),
// 	isoniazidFrequencyNumber: z.number().optional(),
// 	isoniazidStartDate: z.string().optional(),
// 	isoniazidStopDate: z.string().optional(),

// 	pyrazinamideSuspected: z.boolean().optional(),
// 	pyrazinamideBatchNo: z.string().optional(),
// 	pyrazinamideManufacturer: z.string().optional(),
// 	pyrazinamideDoseAmount: z.number().optional(),
// 	pyrazinamideRoute: z
// 		.enum(
// 			adrFormCategoricalValues["route"].map((x) => x.value) as [
// 				string,
// 				...string[]
// 			]
// 		)
// 		.default("oral"),
// 	pyrazinamideFrequencyNumber: z.number().optional(),
// 	pyrazinamideStartDate: z.string().optional(),
// 	pyrazinamideStopDate: z.string().optional(),

// 	ethambutolSuspected: z.boolean().optional(),
// 	ethambutolBatchNo: z.string().optional(),
// 	ethambutolManufacturer: z.string().optional(),
// 	ethambutolDoseAmount: z.number().optional(),
// 	ethambutolRoute: z
// 		.enum(
// 			adrFormCategoricalValues["route"].map((x) => x.value) as [
// 				string,
// 				...string[]
// 			]
// 		)
// 		.default("oral"),
// 	ethambutolFrequencyNumber: z.number().optional(),
// 	ethambutolStartDate: z.string().optional(),
// 	ethambutolStopDate: z.string().optional(),
// 	// Rechallenge/Dechallenge
// 	rechallenge: z
// 		.enum(
// 			adrFormCategoricalValues["rechallenge"].map((x) => x.value) as [
// 				string,
// 				...string[]
// 			]
// 		)
// 		.default("yes"),
// 	dechallenge: z
// 		.enum(
// 			adrFormCategoricalValues["dechallenge"].map((x) => x.value) as [
// 				string,
// 				...string[]
// 			]
// 		)
// 		.default("yes"),
// 	// Grading od Reaction/Event
// 	severity: z
// 		.enum(
// 			adrFormCategoricalValues["severity"].map((x) => x.value) as [
// 				string,
// 				...string[]
// 			]
// 		)
// 		.default("mild"),
// 	isSerious: z
// 		.enum(
// 			adrFormCategoricalValues["isSerious"].map((x) => x.value) as [
// 				string,
// 				...string[]
// 			]
// 		)
// 		.default("no"),
// 	criteriaForSeriousness: z
// 		.enum(
// 			adrFormCategoricalValues["criteriaForSeriousness"].map(
// 				(x) => x.value
// 			) as [string, ...string[]]
// 		)
// 		.default("hospitalisation"),
// 	actionTaken: z
// 		.enum(
// 			adrFormCategoricalValues["actionTaken"].map((x) => x.value) as [
// 				string,
// 				...string[]
// 			]
// 		)
// 		.default("unknown"),
// 	outcome: z
// 		.enum(
// 			adrFormCategoricalValues["outcome"].map((x) => x.value) as [
// 				string,
// 				...string[]
// 			]
// 		)
// 		.default("recovered"),
// 	comments: z.string().default("Will be looked into"),
// });


const patientDobModel = ref(new CalendarDate(2022, 1, 1));

watch(
	patientDobModel,
	(newDate) => {
		if (newDate) {
			state.patientDateOfBirth = newDate.toDate(getLocalTimeZone());
		}
	},
	{ immediate: true }
);
const UFormField = resolveComponent("UFormField");
const UCheckbox = resolveComponent("UCheckbox");
const UInput = resolveComponent("UInput");
const USelect = resolveComponent("USelect");

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
		accessorKey: "batchNo",
		header: "Batch Number",
		cell: ({ row }) =>
			h(
				UFormField,
				{
					name: `medicines[${row.index}].batchNo`,
				},
				{
					default: () =>
						h(UInput, {
							modelValue: row.original.batchNo,
							"onUpdate:modelValue": (value: string) =>
								(row.original.batchNo = value),
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
		accessorKey: "doseAmount",
		header: "Dose (mg)",
		cell: ({ row }) =>
			h(
				UFormField,
				{
					name: `medicines[${row.index}].doseAmount`,
				},
				{
					default: () =>
						h(UInput, {
							modelValue: row.original.doseAmount,
							"onUpdate:modelValue": (value: string) =>
								(row.original.doseAmount = Number(value)),
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
		accessorKey: "frequencyNumber",
		header: "Frequency",
		cell: ({ row }) =>
			h(
				UFormField,
				{
					name: `medicines[${row.index}].frequencyNumber`,
				},
				{
					default: () =>
						h(UInput, {
							modelValue: row.original.frequencyNumber,
							"onUpdate:modelValue": (value: string) =>
								(row.original.frequencyNumber = Number(value)),
							type: "number",
							placeholder: "e.g 1",
						}),
				}
			),
	},
	{
		accessorKey: "startDate",
		header: "Start Date",
		cell: ({ row }) =>
			h(
				UFormField,
				{
					name: `medicines[${row.index}].startDate`,
				},
				{
					default: () =>
						h(UInput, {
							modelValue: row.original.startDate,
							"onUpdate:modelValue": (value: string) =>
								(row.original.startDate = value),
							type: "date",
						}),
				}
			),
	},
	{
		accessorKey: "stopDate",
		header: "Stop Date",
		cell: ({ row }) =>
			h(
				UFormField,
				{
					name: `medicines[${row.index}].stopDate`,
				},
				{
					default: () =>
						h(UInput, {
							modelValue: row.original.stopDate,
							"onUpdate:modelValue": (value: string) =>
								(row.original.stopDate = value),
							type: "date",
						}),
				}
			),
	},
];
// watchEffect(async () => {
// 	if (medicalInstitutionSearchInput.value.length >= 3) {
// 		console.log(medicalInstitutionSearchInput.value);

// 		const { data, status, error } = await useFetch<
// 			PaginatedResponseInterface<MedicalInstitutionGetResponseInterface>
// 		>(`${useRuntimeConfig().public.serverApi}/medical_institution`, {
// 			method: "GET",
// 			headers: {
// 				Authorization: `Bearer ${authStore.accessToken}`,
// 			},
// 			params: {
// 				query: medicalInstitutionSearchInput.value,
// 				size: 10,
// 			},
// 		});

// 		if (data.value?.items) {
// 			medicalInstitutionList.value = data.value?.items;
// 		} else {
// 			medicalInstitutionList.value = [];
// 		}
// 	}
// });

function handleMedicalInstitutionFormSubmitted(
	success: boolean,
	medicalInstitutionIdFromForm?: string
) {
	// if (success) {
	// 	isCreateMedicalInstitutionDialogOpen.value = false; // ✅ Close the dialog only if successful
	// 	medicalInstitutionId.value = medicalInstitutionIdFromForm;
	// 	setFieldValue("medicalInstitutionId", medicalInstitutionId.value);
	// } else {
	// 	isCreateMedicalInstitutionDialogOpen.value = true;
	// }
}

watchEffect(async () => {
	// const runtimeConfig = useRuntimeConfig();
	// const serverApi = runtimeConfig.public.serverApi;
	// const authStore = useAuthStore();
	// if (medicalInstitutionId.value) {
	// 	setFieldValue("medicalInstitutionId", medicalInstitutionId.value);
	// 	const { data, status, error } =
	// 		await useFetch<MedicalInstitutionGetResponseInterface>(
	// 			`${serverApi}/medical_institution/${medicalInstitutionId.value}`,
	// 			{
	// 				method: "GET",
	// 				headers: {
	// 					Authorization: `Bearer ${authStore.accessToken}`,
	// 				},
	// 			}
	// 		);
	// 	medicalInstitutionData.value = data.value;
	// }
});

// Lifecycle hooks
onMounted(async () => {
	// const runtimeConfig = useRuntimeConfig();
	// const serverApi = runtimeConfig.public.serverApi;
	// const authStore = useAuthStore();
	// // If there is an id
	// if (props.id) {
	// 	// Get existing data
	// 	const response = await $fetch<adrFormTypeValidationSchema>(
	// 		`${serverApi}/adr/${props.id}`,
	// 		{
	// 			method: "GET",
	// 			headers: {
	// 				Authorization: `Bearer ${authStore.accessToken}`,
	// 			},
	// 		}
	// 	);
	// 	// Pre-fill form
	// 	const camel = humps.camelizeKeys(
	// 		response
	// 	) as adrFormTypeValidationSchema;
	// 	for (const key of Object.keys(camel) as Array<
	// 		keyof adrFormTypeValidationSchema
	// 	>) {
	// 		// The null check is to prevent errors
	// 		if (camel[key] != null) {
	// 			setFieldValue(key, camel[key]);
	// 		}
	// 	}
	// }
});

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

async function onSubmit(event: FormSubmitEvent<AdrForm>) {
	// const runtimeConfig = useRuntimeConfig();
	// const serverApi = runtimeConfig.public.serverApi;
	// const authStore = useAuthStore();
	// console.log("submitting");
	// if (props.mode == "create") {
	// 	const { data, status, error } = await useFetch<ADRCreateResponse>(
	// 		`${serverApi}/adr`,
	// 		{
	// 			method: "POST",
	// 			headers: {
	// 				Authorization: `Bearer ${authStore.accessToken}`,
	// 			},
	// 			body: humps.decamelizeKeys(values),
	// 		}
	// 	);
	// 	if (status.value == "success" && data.value) {
	// 		const {
	// 			data: calData,
	// 			status: calStatus,
	// 			error,
	// 		} = await useFetch<
	// 			PaginatedResponseInterface<CausalityAssessmentLevelGetResponseInterface>
	// 		>(`${serverApi}/adr/${data.value.id}/causality_assessment_level`, {
	// 			method: "GET",
	// 			headers: {
	// 				Authorization: `Bearer ${authStore.accessToken}`,
	// 			},
	// 			params: {
	// 				page: 1,
	// 				size: 50,
	// 			},
	// 		});
	// 		if (calStatus.value == "success" && calData.value?.items) {
	// 			navigateTo(`/adr/${data.value.id}/review`);
	// 		}
	// 	}
	// } else if (props.mode == "update") {
	// 	const { data, status, error } = await useFetch<ADRCreateResponse>(
	// 		`${serverApi}/adr/${props.id}`,
	// 		{
	// 			method: "PUT",
	// 			headers: {
	// 				Authorization: `Bearer ${authStore.accessToken}`,
	// 			},
	// 			body: humps.decamelizeKeys(values),
	// 		}
	// 	);
	// 	if (status.value == "success" && data.value) {
	// 		const {
	// 			data: calData,
	// 			status: calStatus,
	// 			error,
	// 		} = await useFetch<
	// 			PaginatedResponseInterface<CausalityAssessmentLevelGetResponseInterface>
	// 		>(`${serverApi}/adr/${data.value.id}/causality_assessment_level`, {
	// 			method: "GET",
	// 			headers: {
	// 				Authorization: `Bearer ${authStore.accessToken}`,
	// 			},
	// 			params: {
	// 				page: 1,
	// 				size: 50,
	// 			},
	// 		});
	// 		if (calStatus.value == "success" && calData.value?.items) {
	// 			navigateTo(`/adr/${props.id}/review`);
	// 		}
	// 	}
	// }
}

const props = defineProps<{
	id?: string;
	mode: "create" | "update";
}>();
</script>
