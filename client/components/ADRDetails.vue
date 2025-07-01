<template>
	<Card class="my-4">
		<CardHeader>
			<CardTitle>1. Institution Details</CardTitle>
		</CardHeader>
		<CardContent>
			<div class="view-details-wrapper">
				<p class="view-details-header">Name</p>
				
				<div
					v-if="medicalInstitutionData?.name"
					class="view-details-content"
				>
					{{ medicalInstitutionData?.name }}
				</div>
				<div v-else class="badge blank-badge italic">BLANK</div>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p class="view-details-header">County</p>
				<div
					v-if="medicalInstitutionData?.county"
					class="view-details-content"
				>
					{{ medicalInstitutionData?.county }}
				</div>
				<div v-else class="badge blank-badge italic">BLANK</div>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p class="view-details-header">Sub County</p>
				<div
					v-if="medicalInstitutionData?.sub_county"
					class="view-details-content"
				>
					{{ medicalInstitutionData?.sub_county }}
				</div>
				<div v-else class="badge blank-badge italic">BLANK</div>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p class="view-details-header">MFL Code</p>
				<div
					v-if="medicalInstitutionData?.mfl_code != '0'"
					class="view-details-content"
				>
					{{ medicalInstitutionData?.mfl_code }}
				</div>
				<div v-else class="badge blank-badge italic">BLANK</div>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p class="view-details-header">DHIS Code</p>
				<div
					v-if="medicalInstitutionData?.dhis_code != '0'"
					class="view-details-content"
				>
					{{ medicalInstitutionData?.dhis_code }}
				</div>
				<div v-else class="badge blank-badge italic">BLANK</div>
			</div>
		</CardContent>
	</Card>
	<Card class="my-4">
		<CardHeader>
			<CardTitle>2. Patient Details</CardTitle>
		</CardHeader>
		<CardContent>
			<div class="view-details-wrapper">
				<p class="view-details-header">Name</p>
				<p class="view-details-content">
					{{ props.data?.patient_name }}
				</p>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper" v-if="!props.data?.patient_age">
				<p class="view-details-header">Date of Birth</p>
				<p class="view-details-content">
					{{ props.data?.patient_date_of_birth }}
				</p>
			</div>
			<Separator class="my-2" v-if="!props.data?.patient_age" />
			<div
				class="view-details-wrapper"
				v-if="!props.data?.patient_date_of_birth"
			>
				<p class="view-details-header">Age (yrs)</p>
				<p class="view-details-content">
					{{ props.data?.patient_age }}
				</p>
			</div>
			<Separator class="my-2" v-if="!props.data?.patient_date_of_birth" />
			<div class="view-details-wrapper">
				<p class="view-details-header">Height (cm)</p>
				<div
					v-if="props.data?.patient_height_cm"
					class="view-details-content"
				>
					{{ props.data?.patient_height_cm }}
				</div>
				<div v-else class="badge blank-badge italic">BLANK</div>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p class="view-details-header">Weight (kg)</p>
				<div
					v-if="props.data?.patient_weight_kg"
					class="view-details-content"
				>
					{{ props.data?.patient_weight_kg }}
				</div>
				<div v-else class="badge blank-badge italic">BLANK</div>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p class="view-details-header">Inpatient/Outpatient Number</p>
				<div
					v-if="props.data?.inpatient_or_outpatient_number"
					class="view-details-content"
				>
					{{ props.data?.inpatient_or_outpatient_number }}
				</div>
				<div v-else class="badge blank-badge italic">BLANK</div>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p class="view-details-header">Patient Address</p>
				<div
					v-if="props.data?.patient_address"
					class="view-details-content"
				>
					{{ props.data?.patient_address }}
				</div>
				<div v-else class="badge blank-badge italic">BLANK</div>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p class="view-details-header">Ward/Clinic</p>
				<div
					v-if="props.data?.ward_or_clinic"
					class="view-details-content"
				>
					{{ props.data?.ward_or_clinic }}
				</div>
				<div v-else class="badge blank-badge italic">BLANK</div>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p class="view-details-header">Gender</p>
				<div class="flex flex-wrap gap-2">
					<div
						v-for="value in adrFormCategoricalValues[
							'patientGender'
						]"
						:key="value.value"
					>
						<p
							class="badge text-white"
							:class="{
								'bg-primary':
									value.value === props.data?.patient_gender,
								'bg-gray-300':
									value.value !== props.data?.patient_gender,
							}"
						>
							{{ value.label }}
						</p>
					</div>
				</div>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p class="view-details-header">Pregnancy Status</p>
				<div class="flex flex-wrap gap-2">
					<div
						v-for="value in adrFormCategoricalValues[
							'pregnancyStatus'
						]"
						:key="value.value"
					>
						<p
							class="badge text-white"
							:class="{
								'bg-primary':
									value.value ===
									props.data?.pregnancy_status,
								'bg-gray-300':
									value.value !==
									props.data?.pregnancy_status,
							}"
						>
							{{ value.label }}
						</p>
					</div>
				</div>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p class="view-details-header">Known Allergy</p>
				<div class="flex flex-wrap gap-2">
					<div
						v-for="value in adrFormCategoricalValues[
							'knownAllergy'
						]"
						:key="value.value"
					>
						<p
							class="badge text-white"
							:class="{
								'bg-primary':
									value.value === props.data?.known_allergy,
								'bg-gray-300':
									value.value !== props.data?.known_allergy,
							}"
						>
							{{ value.label }}
						</p>
					</div>
				</div>
			</div>
		</CardContent>
	</Card>
	<Card class="my-4">
		<CardHeader>
			<CardTitle>3. Suspected Adverse Reaction</CardTitle>
		</CardHeader>
		<CardContent>
			<div class="view-details-wrapper">
				<p class="view-details-header">Date of Onset of Reaction</p>
				<p class="view-details-content">
					{{ props.data?.date_of_onset_of_reaction }}
				</p>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p class="view-details-header">Description of Reaction</p>
				<p class="view-details-content">
					{{ props.data?.description_of_reaction }}
				</p>
			</div>
		</CardContent>
	</Card>
	<Card class="my-4">
		<CardHeader>
			<CardTitle>4. Medicines</CardTitle>
		</CardHeader>
		<CardContent>
			<Table>
				<TableHeader>
					<TableRow>
						<TableHead>Suspected</TableHead>
						<TableHead>INN/Generic Name</TableHead>
						<TableHead>Batch Number</TableHead>
						<TableHead>Manufacturer</TableHead>
						<TableHead>Dose</TableHead>
						<TableHead>Route</TableHead>
						<TableHead>Frequency</TableHead>
						<TableHead>Treatment Start Date</TableHead>
						<TableHead>Treatment Stop Date</TableHead>
					</TableRow>
				</TableHeader>
				<TableBody>
					<TableRow>
						<TableCell>
							<Checkbox
								:model-value="props.data?.rifampicin_suspected"
							/>
						</TableCell>
						<TableCell> Rifampicin </TableCell>
						<TableCell>
							<div v-if="props.data?.rifampicin_batch_no">
								{{ props.data?.rifampicin_batch_no }}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
						<TableCell>
							<div v-if="props.data?.rifampicin_manufacturer">
								{{ props.data?.rifampicin_manufacturer }}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
						<TableCell>
							<div
								v-if="props.data?.rifampicin_dose_amount"
								class="flex items-center space-x-2"
							>
								{{ `${props.data?.rifampicin_dose_amount} mg` }}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
						<TableCell>
							<div class="flex flex-wrap gap-2">
								<div
									v-for="value in adrFormCategoricalValues[
										'route'
									]"
									:key="value.value"
								>
									<p
										class="badge text-white"
										:class="{
											'bg-primary':
												value.value ===
												props.data?.rifampicin_route,
											'bg-gray-300':
												value.value !==
												props.data?.rifampicin_route,
										}"
									>
										{{ value.label }}
									</p>
								</div>
							</div>
						</TableCell>
						<TableCell>
							<div
								v-if="props.data?.rifampicin_frequency_number"
								class="flex items-center space-x-2"
							>
								{{
									`${props.data?.rifampicin_frequency_number} daily`
								}}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
						<TableCell>
							<div
								v-if="props.data?.rifampicin_start_date"
								class="flex items-center space-x-2"
							>
								{{ props.data?.rifampicin_start_date }}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
						<TableCell>
							<div
								v-if="props.data?.rifampicin_stop_date"
								class="flex items-center space-x-2"
							>
								{{ props.data?.rifampicin_stop_date }}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
					</TableRow>
					<TableRow>
						<TableCell>
							<Checkbox
								:model-value="props.data?.isoniazid_suspected"
							/>
						</TableCell>
						<TableCell> Isoniazid </TableCell>
						<TableCell>
							<div v-if="props.data?.isoniazid_batch_no">
								{{ props.data?.isoniazid_batch_no }}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
						<TableCell>
							<div v-if="props.data?.isoniazid_manufacturer">
								{{ props.data?.isoniazid_manufacturer }}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
						<TableCell>
							<div
								v-if="props.data?.isoniazid_dose_amount"
								class="flex items-center space-x-2"
							>
								{{ `${props.data?.isoniazid_dose_amount} mg` }}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
						<TableCell>
							<div class="flex flex-wrap gap-2">
								<div
									v-for="value in adrFormCategoricalValues[
										'route'
									]"
									:key="value.value"
								>
									<p
										class="badge text-white"
										:class="{
											'bg-primary':
												value.value ===
												props.data?.isoniazid_route,
											'bg-gray-300':
												value.value !==
												props.data?.isoniazid_route,
										}"
									>
										{{ value.label }}
									</p>
								</div>
							</div>
						</TableCell>
						<TableCell>
							<div
								v-if="props.data?.isoniazid_frequency_number"
								class="flex items-center space-x-2"
							>
								{{
									`${props.data?.isoniazid_frequency_number} daily`
								}}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
						<TableCell>
							<div
								v-if="props.data?.isoniazid_start_date"
								class="flex items-center space-x-2"
							>
								{{ props.data?.isoniazid_start_date }}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
						<TableCell>
							<div
								v-if="props.data?.isoniazid_stop_date"
								class="flex items-center space-x-2"
							>
								{{ props.data?.isoniazid_stop_date }}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
					</TableRow>
					<TableRow>
						<TableCell>
							<Checkbox
								:model-value="
									props.data?.pyrazinamide_suspected
								"
							/>
						</TableCell>
						<TableCell> Pyrazinamide </TableCell>
						<TableCell>
							<div v-if="props.data?.pyrazinamide_batch_no">
								{{ props.data?.pyrazinamide_batch_no }}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
						<TableCell>
							<div v-if="props.data?.pyrazinamide_manufacturer">
								{{ props.data?.pyrazinamide_manufacturer }}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
						<TableCell>
							<div
								v-if="props.data?.pyrazinamide_dose_amount"
								class="flex items-center space-x-2"
							>
								{{
									`${props.data?.pyrazinamide_dose_amount} mg`
								}}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
						<TableCell>
							<div class="flex flex-wrap gap-2">
								<div
									v-for="value in adrFormCategoricalValues[
										'route'
									]"
									:key="value.value"
								>
									<p
										class="badge text-white"
										:class="{
											'bg-primary':
												value.value ===
												props.data?.pyrazinamide_route,
											'bg-gray-300':
												value.value !==
												props.data?.pyrazinamide_route,
										}"
									>
										{{ value.label }}
									</p>
								</div>
							</div>
						</TableCell>
						<TableCell>
							<div
								v-if="props.data?.pyrazinamide_frequency_number"
								class="flex items-center space-x-2"
							>
								{{
									`${props.data?.pyrazinamide_frequency_number} daily`
								}}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
						<TableCell>
							<div
								v-if="props.data?.pyrazinamide_start_date"
								class="flex items-center space-x-2"
							>
								{{ props.data?.pyrazinamide_start_date }}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
						<TableCell>
							<div
								v-if="props.data?.pyrazinamide_stop_date"
								class="flex items-center space-x-2"
							>
								{{ props.data?.pyrazinamide_stop_date }}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
					</TableRow>
					<TableRow>
						<TableCell>
							<Checkbox
								:model-value="props.data?.ethambutol_suspected"
							/>
						</TableCell>
						<TableCell> Ethambutol </TableCell>
						<TableCell>
							<div v-if="props.data?.ethambutol_batch_no">
								{{ props.data?.ethambutol_batch_no }}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
						<TableCell>
							<div v-if="props.data?.ethambutol_manufacturer">
								{{ props.data?.ethambutol_manufacturer }}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
						<TableCell>
							<div
								v-if="props.data?.ethambutol_dose_amount"
								class="flex items-center space-x-2"
							>
								{{ `${props.data?.ethambutol_dose_amount} mg` }}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
						<TableCell>
							<div class="flex flex-wrap gap-2">
								<div
									v-for="value in adrFormCategoricalValues[
										'route'
									]"
									:key="value.value"
								>
									<p
										class="badge text-white"
										:class="{
											'bg-primary':
												value.value ===
												props.data?.ethambutol_route,
											'bg-gray-300':
												value.value !==
												props.data?.ethambutol_route,
										}"
									>
										{{ value.label }}
									</p>
								</div>
							</div>
						</TableCell>
						<TableCell>
							<div
								v-if="props.data?.ethambutol_frequency_number"
								class="flex items-center space-x-2"
							>
								{{
									`${props.data?.ethambutol_frequency_number} daily`
								}}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
						<TableCell>
							<div
								v-if="props.data?.ethambutol_start_date"
								class="flex items-center space-x-2"
							>
								{{ props.data?.ethambutol_start_date }}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
						<TableCell>
							<div
								v-if="props.data?.ethambutol_stop_date"
								class="flex items-center space-x-2"
							>
								{{ props.data?.ethambutol_stop_date }}
							</div>
							<div v-else class="badge blank-badge italic">
								BLANK
							</div>
						</TableCell>
					</TableRow>
				</TableBody>
			</Table>
		</CardContent>
	</Card>
	<Card class="my-4">
		<CardHeader>
			<CardTitle>5. Rechallenge/Dechallenge</CardTitle>
		</CardHeader>
		<CardContent>
			<div class="view-details-wrapper">
				<p class="view-details-header">Rechallenge</p>
				<div class="flex flex-wrap gap-2">
					<div
						v-for="value in adrFormCategoricalValues['rechallenge']"
						:key="value.value"
					>
						<p
							class="badge text-white"
							:class="{
								'bg-primary':
									value.value === props.data?.rechallenge,
								'bg-gray-300':
									value.value !== props.data?.rechallenge,
							}"
						>
							{{ value.label }}
						</p>
					</div>
				</div>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p class="view-details-header">Dechallenge</p>
				<div class="flex flex-wrap gap-2">
					<div
						v-for="value in adrFormCategoricalValues['dechallenge']"
						:key="value.value"
					>
						<p
							class="badge text-white"
							:class="{
								'bg-primary':
									value.value === props.data?.dechallenge,
								'bg-gray-300':
									value.value !== props.data?.dechallenge,
							}"
						>
							{{ value.label }}
						</p>
					</div>
				</div>
			</div>
		</CardContent>
	</Card>
	<Card class="my-4">
		<CardHeader>
			<CardTitle>6. Grading of the Event</CardTitle>
		</CardHeader>
		<CardContent>
			<div class="view-details-wrapper">
				<p class="view-details-header">Severity</p>
				<div class="flex flex-wrap gap-2">
					<div
						v-for="value in adrFormCategoricalValues['severity']"
						:key="value.value"
					>
						<p
							class="badge text-white"
							:class="{
								'bg-primary':
									value.value === props.data?.severity,
								'bg-gray-300':
									value.value !== props.data?.severity,
							}"
						>
							{{ value.label }}
						</p>
					</div>
				</div>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p class="view-details-header">Is Serious</p>
				<div class="flex flex-wrap gap-2">
					<div
						v-for="value in adrFormCategoricalValues['isSerious']"
						:key="value.value"
					>
						<p
							class="badge text-white"
							:class="{
								'bg-primary':
									value.value === props.data?.is_serious,
								'bg-gray-300':
									value.value !== props.data?.is_serious,
							}"
						>
							{{ value.label }}
						</p>
					</div>
				</div>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p class="view-details-header">Criteria for Seriousness</p>
				<div class="flex flex-wrap gap-2">
					<div
						v-for="value in adrFormCategoricalValues[
							'criteriaForSeriousness'
						]"
						:key="value.value"
					>
						<p
							class="badge text-white"
							:class="{
								'bg-primary':
									value.value ===
									props.data?.criteria_for_seriousness,
								'bg-gray-300':
									value.value !==
									props.data?.criteria_for_seriousness,
							}"
						>
							{{ value.label }}
						</p>
					</div>
				</div>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p class="view-details-header">Action Taken</p>
				<div class="flex flex-wrap gap-2">
					<div
						v-for="value in adrFormCategoricalValues['actionTaken']"
						:key="value.value"
					>
						<p
							class="badge text-white"
							:class="{
								'bg-primary':
									value.value === props.data?.action_taken,
								'bg-gray-300':
									value.value !== props.data?.action_taken,
							}"
						>
							{{ value.label }}
						</p>
					</div>
				</div>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p class="view-details-header">Outcome</p>
				<div class="flex flex-wrap gap-2">
					<div
						v-for="value in adrFormCategoricalValues['outcome']"
						:key="value.value"
					>
						<p
							class="badge text-white"
							:class="{
								'bg-primary':
									value.value === props.data?.outcome,
								'bg-gray-300':
									value.value !== props.data?.outcome,
							}"
						>
							{{ value.label }}
						</p>
					</div>
				</div>
			</div>
		</CardContent>
	</Card>
	<div class="flex space-x-2 justify-end">
		<Button @mouseup="router.push(`/adr/${props.data?.id}/edit`)"
			>Edit ADR</Button
		>
		<AlertDialog>
			<AlertDialogTrigger as-child>
				<Button>Delete ADR</Button>
			</AlertDialogTrigger>
			<AlertDialogContent>
				<AlertDialogHeader>
					<AlertDialogTitle>Are you sure?</AlertDialogTitle>
					<AlertDialogDescription>
						This action cannot be undone. This will permanently
						delete this record
					</AlertDialogDescription>
				</AlertDialogHeader>
				<AlertDialogFooter>
					<AlertDialogCancel>Cancel</AlertDialogCancel>
					<AlertDialogAction @mouseup="handleDelete">
						Continue</AlertDialogAction
					>
				</AlertDialogFooter>
			</AlertDialogContent>
		</AlertDialog>
	</div>
</template>

<script setup lang="ts">
import type { ADRGetResponseInterface } from "@/types/adr";
import type { MedicalInstitutionGetResponseInterface } from "@/types/medical_institution";
import { FetchError } from "ofetch";

const props = defineProps<{ data?: ADRGetResponseInterface }>();
const router = useRouter();
const authStore = useAuthStore();

const medicalInstitutionData =
	ref<MedicalInstitutionGetResponseInterface | null>(null);
const medicalInstitutionStatus = ref<"idle" | "success" | "pending" | "error">(
	"idle"
);

const medicalInsitutionError = ref<FetchError<any> | null>(null);

async function handleDelete() {
	const runtimeConfig = useRuntimeConfig();
	const serverApi = runtimeConfig.public.serverApi;

	const response = await $fetch(`${serverApi}/adr/${props.data?.id}`, {
		method: "DELETE",
		headers: {
			Authorization: `Bearer ${authStore.accessToken}`,
		},
	});

	navigateTo("/adr");
}

onMounted(async () => {
	fetchMedicalInstitution();
});

async function fetchMedicalInstitution() {
	const { data, status, error } =
		await useFetch<MedicalInstitutionGetResponseInterface>(
			`${useRuntimeConfig().public.serverApi}/medical_institution/${
				props.data?.medical_institution_id
			}`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
			}
		);

	medicalInstitutionData.value = data.value;
	medicalInstitutionStatus.value = status.value;
	medicalInsitutionError.value = error.value;
}
</script>
