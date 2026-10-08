<template>
	<div class="grid items-start gap-6 lg:grid-cols-[13rem_minmax(0,1fr)]">
		<ADRSectionNav
			v-if="!loadError && !loadingExisting"
			:statuses="statuses"
			:progress="progress"
			class="lg:sticky lg:top-4"
		/>
		<div class="min-w-0">
	<UAlert
		v-if="pendingDraft"
		color="info"
		variant="subtle"
		icon="i-lucide-file-clock"
		title="You have an unfinished report"
		:description="`Saved ${formatDateTime(pendingDraft.savedAt)} in this browser tab. Restore it to carry on where you stopped.`"
		:actions="[
			{ label: 'Restore draft', color: 'neutral', onClick: restoreDraft },
			{ label: 'Discard', color: 'neutral', variant: 'outline', onClick: discardDraft },
		]"
		class="mb-4"
	/>
	<UAlert
		v-if="loadError"
		color="error"
		variant="subtle"
		icon="i-lucide-triangle-alert"
		title="Could not load this ADR"
		:description="loadError.message"
		:actions="[
			{ label: 'Back to ADRs', color: 'neutral', to: '/adr' },
			{ label: 'Try again', color: 'neutral', onClick: () => refetchExisting() },
		]"
	/>
	<div v-else-if="loadingExisting" class="space-y-4" aria-busy="true">
		<USkeleton class="h-10 w-1/3" />
		<USkeleton class="h-64 w-full" />
		<USkeleton class="h-64 w-full" />
	</div>
	<UForm
		v-else
		:schema="schema"
		:state="state"
		:validate="validateExtra"
		@submit="onSubmit"
		@error="onFormError"
	>
		<UCard>
			<template #header>
				<div class="flex items-center justify-between gap-2">
					<span>
						{{ props.mode == "create" ? "Add" : "Edit" }} an Adverse Drug
						Reaction (ADR) Report
					</span>
					<UButton
						v-if="props.mode == 'create'"
						size="sm"
						color="neutral"
						variant="ghost"
						icon="i-lucide-flask-conical"
						label="Fill sample data"
						@click="fillSample"
					/>
				</div>
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
					<UFormField
						label="Medical institution"
						name="medical_institution_id"
						required
						help="Search by name, MFL code or county. If it is not listed, you can add it."
					>
						<InstitutionPicker v-model="state.medical_institution_id" />
					</UFormField>

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
						<div class="w-full" v-if="isDob == 'dob-yes'">
							<UFormField
								label="Date of Birth"
								name="patient_date_of_birth"
								help="The patient's date of birth"
							>
								<UInput
									v-model="state.patient_date_of_birth"
									type="date"
									:max="today"
									class="w-full"
								/>
							</UFormField>
						</div>

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
					<UFormField
						name="date_of_onset_of_reaction"
						label="Date Of Onset Of Reaction"
						help="The date the reaction started"
					>
						<UInput
							v-model="state.date_of_onset_of_reaction"
							type="date"
							:max="today"
							class="w-full"
						/>
					</UFormField>
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
				<div id="submit" class="scroll-mt-20">
					<UButton
						type="submit"
						class="w-full mx-auto my-4 justify-center"
						:loading="isSubmitting || isUpdating"
					>
						{{ props.mode == "create" ? "Add ADR" : "Save changes" }}
					</UButton>
				</div>
			</template>
		</UCard>
	</UForm>
		</div>
	</div>
</template>

<script setup lang="ts">
import { fetchCurrentUser } from "@/api/user";
import type { MedicalInstitutionGetResponseInterface } from "@/types/medical_institution";
import { adrFormCategoricalValues } from "@/values/adr";
import type {
	FormError,
	FormErrorEvent,
	FormSubmitEvent,
	RadioGroupItem,
	TableColumn,
} from "@nuxt/ui";
import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query";
import type { UserDetails } from "@/types/user";
import { fetchAdrById, postAdr, putAdr } from "@/api/adr";
import { fetchMedicalInstitutionById } from "@/api/medical_institution";
import {
	createDraftStore,
	isDirty,
	isMeaningful,
	stableString,
	type Draft,
} from "~/utils/adr-draft";
import { formatDateTime } from "~/utils/adr-table";
import {
	firstSectionWithProblems,
	requiredProgress,
	sectionStatuses,
	type FormIssue,
} from "~/utils/adr-sections";
import {
	adrFormSchema,
	adrToFormState,
	emptyFormState,
	formStateToPayload,
	sampleFormState,
	type AdrForm,
} from "~/utils/adr-form";
import type {
	ADRGetResponseInterface,
	ADRPostRequestInterface,
} from "~/types/adr";

const props = defineProps<{
	id?: string;
	mode: "create" | "update";
}>();

const toast = useToast();
const router = useRouter();
const queryClient = useQueryClient();
const today = new Date().toISOString().slice(0, 10);
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


// const medicalInstitutionId = ref<string | undefined>();

const isDob = ref<string>("dob-yes");

const isDobItems = ref<RadioGroupItem[]>([
	{ label: "Yes", value: "dob-yes" },
	{ label: "No", value: "dob-no" },
]);

const schema = adrFormSchema;

// Both modes start blank. Edit fills in from the record; Add can be filled with
// sample data on request, and offers back an unfinished draft.
const state = reactive<Partial<AdrForm>>(emptyFormState());

// What the form held when it was last "clean": blank, or the loaded record.
const baseline = ref<Partial<AdrForm>>(emptyFormState());
const dirty = computed(() => isDirty(baseline.value, state));
const submitted = ref(false);

// Replace every field, so nothing from the old values is left behind.
function replaceState(next: Partial<AdrForm>) {
	for (const key of Object.keys(state)) delete (state as Record<string, unknown>)[key];
	Object.assign(state, next);
}

function fillSample() {
	if (
		dirty.value &&
		!window.confirm("Replace what you have entered with sample data?")
	) {
		return;
	}
	replaceState(sampleFormState());
	isDob.value = "dob-yes";
}

const {
	data: existingAdr,
	isPending: loadingExistingRaw,
	error: loadError,
	refetch: refetchExisting,
} = useQuery({
	queryKey: ["adr", props.id],
	queryFn: () => fetchAdrById(props.id as string),
	enabled: props.mode === "update" && !!props.id,
});
const loadingExisting = computed(
	() => props.mode === "update" && loadingExistingRaw.value && !loadError.value
);

// Fill the form from the record, once.
watch(
	existingAdr,
	(adr) => {
		if (!adr) return;
		const loaded = adrToFormState(adr);
		replaceState(loaded);
		baseline.value = JSON.parse(JSON.stringify(loaded));
		isDob.value = adr.patient_date_of_birth ? "dob-yes" : "dob-no";
	},
	{ immediate: true }
);

// Details of the chosen institution, in both modes.
const { data: selectedInstitution } = useQuery({
	queryKey: [
		"medicalInstitution",
		computed(() => state.medical_institution_id),
	],
	queryFn: () => fetchMedicalInstitutionById(state.medical_institution_id as string),
	enabled: computed(() => !!state.medical_institution_id),
});
const medicalInstitutionData = computed<MedicalInstitutionGetResponseInterface | null>(
	() => selectedInstitution.value ?? null
);

const UFormField = resolveComponent("UFormField");
const UCheckbox = resolveComponent("UCheckbox");
const UInput = resolveComponent("UInput");
const USelect = resolveComponent("USelect");

const { data: currentUser, isPending: isUserPending } = useQuery<
	UserDetails,
	Error
>({
	queryKey: ["currentUser"],
	queryFn: fetchCurrentUser,
});

// ---- Draft (Add only) -------------------------------------------------------
// Kept in this browser tab only, because it holds patient data.
const draftStore = createDraftStore(import.meta.client ? window.sessionStorage : undefined);
const pendingDraft = ref<Draft | null>(null);
const draftChecked = ref(false);

watch(
	() => currentUser.value?.id,
	(userId) => {
		if (props.mode !== "create" || !userId || draftChecked.value) return;
		draftChecked.value = true;

		const draft = draftStore.load(userId);
		if (draft && isMeaningful(draft.state)) pendingDraft.value = draft;
	},
	{ immediate: true }
);

function restoreDraft() {
	if (!pendingDraft.value) return;
	replaceState(pendingDraft.value.state);
	isDob.value = pendingDraft.value.knowsDob ? "dob-yes" : "dob-no";
	pendingDraft.value = null;
}

function discardDraft() {
	if (currentUser.value?.id) draftStore.clear(currentUser.value.id);
	pendingDraft.value = null;
}

// Save as you type. A form that is blank again removes the draft.
watchDebounced(
	() => [stableString(state), isDob.value],
	() => {
		const userId = currentUser.value?.id;
		if (props.mode !== "create" || !userId || !draftChecked.value) return;
		if (pendingDraft.value || submitted.value) return; // the user has not decided yet

		if (isMeaningful(state)) draftStore.save(userId, state, isDob.value === "dob-yes");
		else draftStore.clear(userId);
	},
	{ debounce: 800 }
);

// ---- Unsaved changes ---------------------------------------------------------
// Edit has no draft, so leaving asks first. Add keeps a draft, so only closing the
// tab (which would lose it) asks.
onBeforeRouteLeave(() => {
	if (props.mode === "update" && dirty.value && !submitted.value) {
		return window.confirm("You have unsaved changes. Leave this page and lose them?");
	}
});

function warnBeforeUnload(event: BeforeUnloadEvent) {
	if (dirty.value && !submitted.value) {
		event.preventDefault();
		event.returnValue = "";
	}
}
onMounted(() => window.addEventListener("beforeunload", warnBeforeUnload));
onBeforeUnmount(() => window.removeEventListener("beforeunload", warnBeforeUnload));

const { mutate: createADR, isPending: isSubmitting } = useMutation<
	ADRGetResponseInterface,
	Error,
	ADRPostRequestInterface
>({
	mutationFn: (payload) => postAdr(payload),
	onSuccess: (data) => {
		submitted.value = true;
		if (currentUser.value?.id) draftStore.clear(currentUser.value.id);
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

const { mutate: updateADR, isPending: isUpdating } = useMutation<
	ADRGetResponseInterface,
	Error,
	ADRPostRequestInterface
>({
	mutationFn: (payload) => putAdr(props.id as string, payload),
	onSuccess: () => {
		submitted.value = true;
		queryClient.invalidateQueries({ queryKey: ["adrs"] });
		queryClient.invalidateQueries({ queryKey: ["adr", props.id] });
		queryClient.invalidateQueries({ queryKey: ["adr-activity", props.id] });
		queryClient.invalidateQueries({ queryKey: ["causality-assessment-levels"] });
		toast.add({
			title: "ADR updated",
			description:
				"The change is saved and kept in the history. If it changed anything the model reads, the causality level was re-assessed and needs a new review.",
			color: "success",
		});
		router.push(`/adr/${props.id}`);
	},
	onError: (error) => {
		toast.add({
			title: "Could not save the ADR",
			description: error.message,
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

async function onSubmit(event: FormSubmitEvent<AdrForm>) {
	if (!currentUser.value?.id) {
		toast.add({
			title: "Error",
			description: "Could not find user. Please log in again.",
			color: "error",
		});
		return;
	}

	const knowsDob = isDob.value === "dob-yes";

	const payload = formStateToPayload(event.data, currentUser.value.id, { knowsDob });

	if (props.mode === "create") {
		createADR(payload);
	} else if (props.mode === "update" && props.id) {
		updateADR(payload);
	}
}

// ---- Section list: what is done, what needs attention ---------------------------

// The schema cannot know whether the user chose "I know the date of birth".
const dobMissing = computed(
	() => isDob.value === "dob-yes" && !state.patient_date_of_birth
);

function validateExtra(): FormError[] {
	return dobMissing.value
		? [
				{
					name: "patient_date_of_birth",
					message: "Enter the date of birth, or choose No and give the age.",
				},
			]
		: [];
}

// Until the first failed save, only missing required fields are flagged.
const attempted = ref(false);

const issues = computed<FormIssue[]>(() => {
	const found: FormIssue[] = [...(adrFormSchema.safeParse(state).error?.issues ?? [])];
	if (dobMissing.value) found.push({ path: ["patient_date_of_birth"] });
	return found;
});
const statuses = computed(() => sectionStatuses(state, issues.value, attempted.value));
const progress = computed(() => requiredProgress(issues.value));

function onFormError(event: FormErrorEvent) {
	attempted.value = true;
	const sections = statuses.value.filter((status) => status.state === "error").length;

	toast.add({
		title: "Some fields need attention",
		description: `${event.errors.length} ${event.errors.length === 1 ? "problem" : "problems"} in ${sections} ${sections === 1 ? "section" : "sections"}. They are marked in the list.`,
		color: "error",
	});

	nextTick(() => {
		const first = firstSectionWithProblems(statuses.value);
		if (first) document.getElementById(first.id)?.scrollIntoView({ behavior: "smooth", block: "start" });
	});
}
</script>
