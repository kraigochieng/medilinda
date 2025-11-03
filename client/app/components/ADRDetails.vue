<template>
	<UCard class="my-4">
		<template #header>
			<h3
				class="text-base font-semibold leading-6 text-gray-900 dark:text-white"
			>
				1. Institution Details
			</h3>
		</template>

		<div class="space-y-3">
			<div class="view-details-wrapper">
				<p class="view-details-header">Name</p>
				<div
					v-if="medicalInstitutionData?.name"
					class="view-details-content"
				>
					{{ medicalInstitutionData?.name }}
				</div>
				<UBadge v-else color="neutral">BLANK</UBadge>
			</div>
			<USeparator />
			<div class="view-details-wrapper">
				<p class="view-details-header">County</p>
				<div
					v-if="medicalInstitutionData?.county"
					class="view-details-content"
				>
					{{ medicalInstitutionData?.county }}
				</div>
				<UBadge v-else color="neutral">BLANK</UBadge>
			</div>
			<USeparator />
			<div class="view-details-wrapper">
				<p class="view-details-header">Sub County</p>
				<div
					v-if="medicalInstitutionData?.sub_county"
					class="view-details-content"
				>
					{{ medicalInstitutionData?.sub_county }}
				</div>
				<UBadge v-else color="neutral">BLANK</UBadge>
			</div>
			<USeparator />
			<div class="view-details-wrapper">
				<p class="view-details-header">MFL Code</p>
				<div
					v-if="medicalInstitutionData?.mfl_code != '0'"
					class="view-details-content"
				>
					{{ medicalInstitutionData?.mfl_code }}
				</div>
				<UBadge v-else color="neutral">BLANK</UBadge>
			</div>
			<USeparator />
			<div class="view-details-wrapper">
				<p class="view-details-header">DHIS Code</p>
				<div
					v-if="medicalInstitutionData?.dhis_code != '0'"
					class="view-details-content"
				>
					{{ medicalInstitutionData?.dhis_code }}
				</div>
				<UBadge v-else color="neutral">BLANK</UBadge>
			</div>
		</div>
	</UCard>

	<UCard class="my-4">
		<template #header>
			<h3
				class="text-base font-semibold leading-6 text-gray-900 dark:text-white"
			>
				2. Patient Details
			</h3>
		</template>
		<div class="space-y-3">
			<div class="view-details-wrapper">
				<p class="view-details-header">Name</p>
				<p class="view-details-content">
					{{ props.data?.patient_name }}
				</p>
			</div>
			<USeparator />
			<div v-if="props.data?.patient_date_of_birth">
				<div class="view-details-wrapper">
					<p class="view-details-header">Date of Birth</p>
					<p class="view-details-content">
						{{ props.data?.patient_date_of_birth }}
					</p>
				</div>
				<USeparator />
			</div>
			<div v-if="props.data?.patient_age">
				<div class="view-details-wrapper">
					<p class="view-details-header">Age (yrs)</p>
					<p class="view-details-content">
						{{ props.data?.patient_age }}
					</p>
				</div>
				<USeparator />
			</div>
			<div class="view-details-wrapper">
				<p class="view-details-header">Height (cm)</p>
				<div
					v-if="props.data?.patient_height_cm"
					class="view-details-content"
				>
					{{ props.data?.patient_height_cm }}
				</div>
				<UBadge v-else color="neutral">BLANK</UBadge>
			</div>
			<USeparator />
			<div class="view-details-wrapper">
				<p class="view-details-header">Weight (kg)</p>
				<div
					v-if="props.data?.patient_weight_kg"
					class="view-details-content"
				>
					{{ props.data?.patient_weight_kg }}
				</div>
				<UBadge v-else color="neutral">BLANK</UBadge>
			</div>
			<USeparator />
			<div class="view-details-wrapper">
				<p class="view-details-header">Inpatient/Outpatient Number</p>
				<div
					v-if="props.data?.inpatient_or_outpatient_number"
					class="view-details-content"
				>
					{{ props.data?.inpatient_or_outpatient_number }}
				</div>
				<UBadge v-else color="neutral">BLANK</UBadge>
			</div>
			<USeparator />
			<div class="view-details-wrapper">
				<p class="view-details-header">Patient Address</p>
				<div
					v-if="props.data?.patient_address"
					class="view-details-content"
				>
					{{ props.data?.patient_address }}
				</div>
				<UBadge v-else color="neutral">BLANK</UBadge>
			</div>
			<USeparator />
			<div class="view-details-wrapper">
				<p class="view-details-header">Ward/Clinic</p>
				<div
					v-if="props.data?.ward_or_clinic"
					class="view-details-content"
				>
					{{ props.data?.ward_or_clinic }}
				</div>
				<UBadge v-else color="neutral">BLANK</UBadge>
			</div>
			<USeparator />
			<div class="view-details-wrapper">
				<p class="view-details-header">Gender</p>
				<div class="flex flex-wrap gap-2">
					<UBadge
						v-for="value in adrFormCategoricalValues[
							'patientGender'
						]"
						:key="value.value"
						:color="
							value.value === props.data?.patient_gender
								? 'success'
								: 'neutral'
						"
						variant="solid"
					>
						{{ value.label }}
					</UBadge>
				</div>
			</div>
			<USeparator />
			<div class="view-details-wrapper">
				<p class="view-details-header">Pregnancy Status</p>
				<div class="flex flex-wrap gap-2">
					<UBadge
						v-for="value in adrFormCategoricalValues[
							'pregnancyStatus'
						]"
						:key="value.value"
						:color="
							value.value === props.data?.pregnancy_status
								? 'success'
								: 'neutral'
						"
						variant="solid"
					>
						{{ value.label }}
					</UBadge>
				</div>
			</div>
			<USeparator />
			<div class="view-details-wrapper">
				<p class="view-details-header">Known Allergy</p>
				<div class="flex flex-wrap gap-2">
					<UBadge
						v-for="value in adrFormCategoricalValues[
							'knownAllergy'
						]"
						:key="value.value"
						:color="
							value.value === props.data?.known_allergy
								? 'success'
								: 'neutral'
						"
						variant="solid"
					>
						{{ value.label }}
					</UBadge>
				</div>
			</div>
		</div>
	</UCard>

	<UCard class="my-4">
		<template #header>
			<h3
				class="text-base font-semibold leading-6 text-gray-900 dark:text-white"
			>
				3. Suspected Adverse Reaction
			</h3>
		</template>
		<div class="space-y-3">
			<div class="view-details-wrapper">
				<p class="view-details-header">Date of Onset of Reaction</p>
				<p class="view-details-content">
					{{ props.data?.date_of_onset_of_reaction }}
				</p>
			</div>
			<USeparator />
			<div class="view-details-wrapper">
				<p class="view-details-header">Description of Reaction</p>
				<p class="view-details-content">
					{{ props.data?.description_of_reaction }}
				</p>
			</div>
		</div>
	</UCard>

	<UCard class="my-4">
		<template #header>
			<h3
				class="text-base font-semibold leading-6 text-gray-900 dark:text-white"
			>
				4. Medicines
			</h3>
		</template>
		<UTable :data="medicines" :columns="medicineTableColumns" />
	</UCard>

	<UCard class="my-4">
		<template #header>
			<h3
				class="text-base font-semibold leading-6 text-gray-900 dark:text-white"
			>
				5. Rechallenge/Dechallenge
			</h3>
		</template>
		<div class="space-y-3">
			<div class="view-details-wrapper">
				<p class="view-details-header">Rechallenge</p>
				<div class="flex flex-wrap gap-2">
					<UBadge
						v-for="value in adrFormCategoricalValues['rechallenge']"
						:key="value.value"
						:color="
							value.value === props.data?.rechallenge
								? 'success'
								: 'neutral'
						"
						variant="solid"
					>
						{{ value.label }}
					</UBadge>
				</div>
			</div>
			<USeparator />
			<div class="view-details-wrapper">
				<p class="view-details-header">Dechallenge</p>
				<div class="flex flex-wrap gap-2">
					<UBadge
						v-for="value in adrFormCategoricalValues['dechallenge']"
						:key="value.value"
						:color="
							value.value === props.data?.dechallenge
								? 'success'
								: 'neutral'
						"
						variant="solid"
					>
						{{ value.label }}
					</UBadge>
				</div>
			</div>
		</div>
	</UCard>

	<UCard class="my-4">
		<template #header>
			<h3
				class="text-base font-semibold leading-6 text-gray-900 dark:text-white"
			>
				6. Grading of the Event
			</h3>
		</template>
		<div class="space-y-3">
			<div class="view-details-wrapper">
				<p class="view-details-header">Severity</p>
				<div class="flex flex-wrap gap-2">
					<UBadge
						v-for="value in adrFormCategoricalValues['severity']"
						:key="value.value"
						:color="
							value.value === props.data?.severity
								? 'success'
								: 'neutral'
						"
						variant="solid"
					>
						{{ value.label }}
					</UBadge>
				</div>
			</div>
			<USeparator />
			<div class="view-details-wrapper">
				<p class="view-details-header">Is Serious</p>
				<div class="flex flex-wrap gap-2">
					<UBadge
						v-for="value in adrFormCategoricalValues['isSerious']"
						:key="value.value"
						:color="
							value.value === props.data?.is_serious
								? 'success'
								: 'neutral'
						"
						variant="solid"
					>
						{{ value.label }}
					</UBadge>
				</div>
			</div>
			<USeparator />
			<div class="view-details-wrapper">
				<p class="view-details-header">Criteria for Seriousness</p>
				<div class="flex flex-wrap gap-2">
					<UBadge
						v-for="value in adrFormCategoricalValues[
							'criteriaForSeriousness'
						]"
						:key="value.value"
						:color="
							value.value === props.data?.criteria_for_seriousness
								? 'success'
								: 'neutral'
						"
						variant="solid"
					>
						{{ value.label }}
					</UBadge>
				</div>
			</div>
			<USeparator />
			<div class="view-details-wrapper">
				<p class="view-details-header">Action Taken</p>
				<div class="flex flex-wrap gap-2">
					<UBadge
						v-for="value in adrFormCategoricalValues['actionTaken']"
						:key="value.value"
						:color="
							value.value === props.data?.action_taken
								? 'success'
								: 'neutral'
						"
						variant="solid"
					>
						{{ value.label }}
					</UBadge>
				</div>
			</div>
			<USeparator />
			<div class="view-details-wrapper">
				<p class="view-details-header">Outcome</p>
				<div class="flex flex-wrap gap-2">
					<UBadge
						v-for="value in adrFormCategoricalValues['outcome']"
						:key="value.value"
						:color="
							value.value === props.data?.outcome
								? 'success'
								: 'neutral'
						"
						variant="solid"
					>
						{{ value.label }}
					</UBadge>
				</div>
			</div>
		</div>
	</UCard>

	<div class="flex space-x-2 justify-end">
		<UButton @click="router.push(`/adr/${props.data?.id}/edit`)">
			Edit ADR
		</UButton>
		<UModal
			v-model:open="isDeleteModalOpen"
			title="Are you sure you want to delete it?"
			description="This action cannot be undone. This will permanently delete this record."
		>
			<UButton color="error">Delete ADR</UButton>
			<template #body>
				<UButton color="error" @mouseup="handleDelete">
					Delete ADR
				</UButton>
			</template>
		</UModal>
	</div>
</template>

<script setup lang="ts">
import type { ADRGetResponseInterface } from "@/types/adr";
import { adrFormCategoricalValues } from "@/values/adr";

import { useQuery } from "@tanstack/vue-query";

import { deleteAdrById } from "@/api/adr";
import { fetchMedicalInstitutionById } from "@/api/medical_institution";
import type { TableColumn } from "@nuxt/ui";
import { useMutation, useQueryClient } from "@tanstack/vue-query";

const toast = useToast();
const queryClient = useQueryClient();
const router = useRouter();

const isDeleteModalOpen = ref(false);
const UBadge = resolveComponent("UBadge");
const UCheckbox = resolveComponent("UCheckbox");
const props = defineProps<{ data?: ADRGetResponseInterface }>();

const {
	data: medicalInstitutionData,
	isPending: isMedicalInstitutionPending,
	isError: isMedicalInstitutionError,
	error: medicalInstitutionError,
	status: medicalInstitutionStatus,
} = useQuery({
	queryKey: ["medical-institution", props.data?.medical_institution_id],
	queryFn: () =>
		fetchMedicalInstitutionById(
			props.data?.medical_institution_id as string
		),
	enabled: computed(() => !!props.data?.medical_institution_id), // only runs when id exists
});

interface MedicineInterface {
	name: string;
	suspected: boolean;
	batch_no?: string | null;
	manufacturer?: string | null;
	dose?: number | null;
	route?: string | null;
	frequency?: number | null;
	start_date?: string | null;
	stop_date?: string | null;
}
// Restructure medicine data for UTable
const medicines = computed(() => {
	if (!props.data) return [];
	return [
		{
			name: "Rifampicin",
			suspected: props.data.rifampicin_suspected,
			batch_no: props.data.rifampicin_batch_no,
			manufacturer: props.data.rifampicin_manufacturer,
			dose: props.data.rifampicin_dose_amount,
			route: props.data.rifampicin_route,
			frequency: props.data.rifampicin_frequency_number,
			start_date: props.data.rifampicin_start_date,
			stop_date: props.data.rifampicin_stop_date,
		},
		{
			name: "Isoniazid",
			suspected: props.data.isoniazid_suspected,
			batch_no: props.data.isoniazid_batch_no,
			manufacturer: props.data.isoniazid_manufacturer,
			dose: props.data.isoniazid_dose_amount,
			route: props.data.isoniazid_route,
			frequency: props.data.isoniazid_frequency_number,
			start_date: props.data.isoniazid_start_date,
			stop_date: props.data.isoniazid_stop_date,
		},
		{
			name: "Pyrazinamide",
			suspected: props.data.pyrazinamide_suspected,
			batch_no: props.data.pyrazinamide_batch_no,
			manufacturer: props.data.pyrazinamide_manufacturer,
			dose: props.data.pyrazinamide_dose_amount,
			route: props.data.pyrazinamide_route,
			frequency: props.data.pyrazinamide_frequency_number,
			start_date: props.data.pyrazinamide_start_date,
			stop_date: props.data.pyrazinamide_stop_date,
		},
		{
			name: "Ethambutol",
			suspected: props.data.ethambutol_suspected,
			batch_no: props.data.ethambutol_batch_no,
			manufacturer: props.data.ethambutol_manufacturer,
			dose: props.data.ethambutol_dose_amount,
			route: props.data.ethambutol_route,
			frequency: props.data.ethambutol_frequency_number,
			start_date: props.data.ethambutol_start_date,
			stop_date: props.data.ethambutol_stop_date,
		},
	] as MedicineInterface[];
});

const medicineTableColumns: TableColumn<MedicineInterface>[] = [
	{
		accessorKey: "suspected",
		header: "Suspected",
		cell: ({ row }) => {
			return h(UCheckbox, {
				modelValue: row.original.suspected,
				disabled: true,
			});
		},
	},
	{
		accessorKey: "name",
		header: "INN/Generic Name",
	},
	{
		accessorKey: "batch_no",
		header: "Batch Number",
		cell: ({ row }) => {
			return row.original.batch_no
				? h("div", {}, row.original.batch_no)
				: h(
						UBadge,
						{ color: "gray", variant: "italic" },
						() => "BLANK"
				  );
		},
	},
	{
		accessorKey: "manufacturer",
		header: "Manufacturer",
		cell: ({ row }) => {
			return row.original.manufacturer
				? h("div", {}, row.original.manufacturer)
				: h(
						UBadge,
						{ color: "gray", variant: "italic" },
						() => "BLANK"
				  );
		},
	},
	{
		accessorKey: "dose",
		header: "Dose",
		cell: ({ row }) => {
			return row.original.dose
				? h("div", {}, `${row.original.dose} mg`)
				: h(
						UBadge,
						{ color: "gray", variant: "italic" },
						() => "BLANK"
				  );
		},
	},
	{
		accessorKey: "route",
		header: "Route",
		cell: ({ row }) => {
			// Assumes `adrFormCategoricalValues` is accessible in this scope
			const badges = adrFormCategoricalValues["route"].map((value) =>
				h(
					UBadge,
					{
						color:
							value.value === row.original.route
								? "primary"
								: "gray",
						variant: "solid",
					},
					() => value.label
				)
			);
			return h("div", { class: "flex flex-wrap gap-2" }, badges);
		},
	},
	{
		accessorKey: "frequency",
		header: "Frequency",
		cell: ({ row }) => {
			return row.original.frequency
				? h("div", {}, `${row.original.frequency} daily`)
				: h(
						UBadge,
						{ color: "gray", variant: "italic" },
						() => "BLANK"
				  );
		},
	},
	{
		accessorKey: "start_date",
		header: "Treatment Start Date",
		cell: ({ row }) => {
			return row.original.start_date
				? h("div", {}, row.original.start_date)
				: h(
						UBadge,
						{ color: "gray", variant: "italic" },
						() => "BLANK"
				  );
		},
	},
	{
		accessorKey: "stop_date",
		header: "Treatment Stop Date",
		cell: ({ row }) => {
			return row.original.stop_date
				? h("div", {}, row.original.stop_date)
				: h(
						UBadge,
						{ color: "gray", variant: "italic" },
						() => "BLANK"
				  );
		},
	},
];
const { mutate: deleteAdr, isPending: isDeleting } = useMutation<
	void, // Return type from deleteAdrById
	Error, // Error type
	string // Variable type (the id)
>({
	mutationFn: (idToDelete) => deleteAdrById(idToDelete),

	onSuccess: () => {
		isDeleteModalOpen.value = false;

		// Show success toast
		toast.add({
			title: "ADR Deleted",
			description: "The ADR report has been successfully deleted.",
			color: "success",
			icon: "i-heroicons-check-circle",
		});

		// Invalidate the main ADR list query so it refetches on the next page
		queryClient.invalidateQueries({ queryKey: ["adrs"] });

		// Navigate back to the /adr list page
		router.push("/adr");
	},

	onError: (error) => {
		isDeleteModalOpen.value = false;
		// Show error toast
		toast.add({
			title: "Error Deleting ADR",
			description: error.message,
			color: "error",
			icon: "i-heroicons-exclamation-circle",
		});
	},
});

function handleDelete() {
	deleteAdr(props.data?.id as string);
}
</script>

<style scoped>
@reference "assets/css/main.css";

/* These custom styles can be kept for layout purposes */
.view-details-wrapper {
	display: flex;
	justify-content: space-between;
	align-items: center;
}
.view-details-header {
	font-weight: 500;
}
.view-details-content {
	text-align: right;
}
</style>
