<template>
	<div class="grid items-start gap-6 lg:grid-cols-[11rem_minmax(0,1fr)]">
		<nav
			aria-label="Report sections"
			class="hidden rounded-lg border border-default p-3 text-sm lg:sticky lg:top-4 lg:block"
		>
			<ol class="space-y-0.5">
				<li v-for="section in sections" :key="section.id">
					<a
						:href="`#${section.id}`"
						class="block rounded-md px-2 py-1.5 hover:bg-elevated"
						:class="active === section.id ? 'bg-elevated font-medium' : ''"
						:aria-current="active === section.id ? 'location' : undefined"
						@click.prevent="go(section.id)"
					>
						{{ section.label }}
					</a>
				</li>
			</ol>
		</nav>

		<div class="min-w-0 space-y-4">
			<dl class="grid grid-cols-2 gap-x-6 gap-y-3 rounded-lg border border-default bg-elevated/40 p-4 sm:grid-cols-3 xl:grid-cols-6">
				<ADRField v-for="item in summary" :key="item.label" :label="item.label" :value="item.value" />
			</dl>

			<UCard id="view-institution" class="scroll-mt-4">
				<template #header><h3 class="font-semibold">Institution</h3></template>
				<dl class="grid gap-x-6 gap-y-4 sm:grid-cols-2 lg:grid-cols-3">
					<ADRField label="Name" :value="institution?.name" wide />
					<ADRField label="County" :value="institution?.county" />
					<ADRField label="Sub county" :value="institution?.sub_county" />
					<ADRField label="MFL code" :value="institution?.mfl_code" />
					<ADRField label="DHIS code" :value="institution?.dhis_code" />
				</dl>
			</UCard>

			<UCard id="view-patient" class="scroll-mt-4">
				<template #header><h3 class="font-semibold">Patient</h3></template>
				<dl class="grid gap-x-6 gap-y-4 sm:grid-cols-2 lg:grid-cols-3">
					<ADRField label="Name" :value="show(data?.patient_name)" />
					<ADRField label="Date of birth" :value="formatDay(data?.patient_date_of_birth)" />
					<ADRField label="Age" :value="data?.patient_age != null ? `${data.patient_age} yrs` : NONE" />
					<ADRField label="Gender" :value="optionLabel('patientGender', data?.patient_gender)" />
					<ADRField label="Pregnancy status" :value="optionLabel('pregnancyStatus', data?.pregnancy_status)" />
					<ADRField label="Known allergy" :value="optionLabel('knownAllergy', data?.known_allergy)" />
					<ADRField label="Height" :value="data?.patient_height_cm != null ? `${data.patient_height_cm} cm` : NONE" />
					<ADRField label="Weight" :value="data?.patient_weight_kg != null ? `${data.patient_weight_kg} kg` : NONE" />
					<ADRField label="Inpatient / outpatient no." :value="show(data?.inpatient_or_outpatient_number)" />
					<ADRField label="Address" :value="show(data?.patient_address)" />
					<ADRField label="Ward or clinic" :value="show(data?.ward_or_clinic)" />
				</dl>
			</UCard>

			<UCard id="view-reaction" class="scroll-mt-4">
				<template #header><h3 class="font-semibold">Suspected adverse reaction</h3></template>
				<dl class="grid gap-x-6 gap-y-4 sm:grid-cols-2 lg:grid-cols-3">
					<ADRField label="Date of onset" :value="formatDay(data?.date_of_onset_of_reaction)" />
					<ADRField label="Description" :value="show(data?.description_of_reaction)" wide />
				</dl>
			</UCard>

			<UCard id="view-medicines" class="scroll-mt-4">
				<template #header><h3 class="font-semibold">Medicines</h3></template>

				<ol v-if="timeline.length" class="mb-6 space-y-3" aria-label="Timeline of the medicines and the reaction">
					<li v-for="(event, index) in timeline" :key="index" class="flex gap-3">
						<span
							class="mt-1.5 size-2.5 shrink-0 rounded-full"
							:class="DOT[event.kind]"
							aria-hidden="true"
						/>
						<div class="min-w-0">
							<p class="text-sm">
								<span class="font-medium">{{ formatDay(event.date) }}</span>
								<span class="text-muted"> · {{ event.title }}</span>
								<span v-if="event.kind !== 'onset'">: {{ event.label }}</span>
							</p>
							<p v-if="event.note" class="text-xs text-muted">{{ event.note }}</p>
						</div>
					</li>
				</ol>

				<div class="overflow-x-auto">
					<table class="w-full min-w-[40rem] text-sm">
						<thead>
							<tr class="border-b border-default text-left text-xs uppercase tracking-wide text-muted">
								<th class="py-2 pr-4 font-medium">Medicine</th>
								<th class="py-2 pr-4 font-medium">Dose</th>
								<th class="py-2 pr-4 font-medium">Frequency</th>
								<th class="py-2 pr-4 font-medium">Route</th>
								<th class="py-2 pr-4 font-medium">Started</th>
								<th class="py-2 pr-4 font-medium">Stopped</th>
								<th class="py-2 pr-4 font-medium">Days</th>
								<th class="py-2 pr-4 font-medium">Batch</th>
								<th class="py-2 font-medium">Manufacturer</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="medicine in medicines"
								:key="medicine.key"
								class="border-b border-default last:border-0"
								:class="medicine.suspected ? '' : 'text-muted'"
							>
								<td class="py-2 pr-4">
									<span class="font-medium">{{ medicine.name }}</span>
									<UBadge v-if="medicine.suspected" color="warning" variant="subtle" size="sm" class="ml-2">
										Suspected
									</UBadge>
								</td>
								<td class="py-2 pr-4">{{ medicine.dose != null ? `${medicine.dose} mg` : NONE }}</td>
								<td class="py-2 pr-4">{{ medicine.frequency != null ? `${medicine.frequency} a day` : NONE }}</td>
								<td class="py-2 pr-4">{{ optionLabel("route", medicine.route) }}</td>
								<td class="py-2 pr-4 whitespace-nowrap">{{ formatDay(medicine.start) }}</td>
								<td class="py-2 pr-4 whitespace-nowrap">{{ formatDay(medicine.stop) }}</td>
								<td class="py-2 pr-4">{{ medicine.days != null ? medicine.days : NONE }}</td>
								<td class="py-2 pr-4">{{ show(medicine.batch) }}</td>
								<td class="py-2">{{ show(medicine.manufacturer) }}</td>
							</tr>
						</tbody>
					</table>
				</div>
			</UCard>

			<UCard id="view-rechallenge" class="scroll-mt-4">
				<template #header><h3 class="font-semibold">Rechallenge and dechallenge</h3></template>
				<dl class="grid gap-x-6 gap-y-4 sm:grid-cols-2 lg:grid-cols-3">
					<ADRField label="Rechallenge" :value="optionLabel('rechallenge', data?.rechallenge)" />
					<ADRField label="Dechallenge" :value="optionLabel('dechallenge', data?.dechallenge)" />
				</dl>
			</UCard>

			<UCard id="view-grading" class="scroll-mt-4">
				<template #header><h3 class="font-semibold">Grading of the event</h3></template>
				<dl class="grid gap-x-6 gap-y-4 sm:grid-cols-2 lg:grid-cols-3">
					<ADRField label="Severity" :value="optionLabel('severity', data?.severity)" />
					<ADRField label="Serious" :value="optionLabel('isSerious', data?.is_serious)" />
					<ADRField
						label="Criteria for seriousness"
						:value="optionLabel('criteriaForSeriousness', data?.criteria_for_seriousness)"
					/>
					<ADRField label="Action taken" :value="optionLabel('actionTaken', data?.action_taken)" />
					<ADRField label="Outcome" :value="optionLabel('outcome', data?.outcome)" />
					<ADRField v-if="data?.comments" label="Comments" :value="data.comments" wide />
				</dl>
			</UCard>

			<div class="flex justify-end gap-2">
				<UButton :to="`/adr/${data?.id}/edit`" icon="i-lucide-pencil" label="Edit ADR" />
				<UModal
					v-model:open="isDeleteModalOpen"
					title="Are you sure you want to delete it?"
					description="The report moves to Recently deleted. You can restore it from there."
				>
					<UButton color="error" variant="outline" icon="i-lucide-trash-2" label="Delete ADR" />
					<template #body>
						<UButton color="error" :loading="isDeleting" label="Delete ADR" @click="handleDelete" />
					</template>
				</UModal>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { deleteAdrById } from "@/api/adr";
import { fetchMedicalInstitutionById } from "@/api/medical_institution";
import type { ADRGetResponseInterface } from "@/types/adr";
import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query";
import {
	NONE,
	formatDay,
	medicinesOf,
	optionLabel,
	show,
	summaryOf,
	timelineOf,
	type TimelineKind,
} from "~/utils/adr-view";

const props = defineProps<{ data?: ADRGetResponseInterface }>();

const toast = useToast();
const queryClient = useQueryClient();
const router = useRouter();
const isDeleteModalOpen = ref(false);

const { data: institution } = useQuery({
	queryKey: ["medical-institution", props.data?.medical_institution_id],
	queryFn: () => fetchMedicalInstitutionById(props.data?.medical_institution_id as string),
	enabled: computed(() => !!props.data?.medical_institution_id),
});

const medicines = computed(() => (props.data ? medicinesOf(props.data) : []));
const timeline = computed(() => (props.data ? timelineOf(props.data) : []));
const summary = computed(() => (props.data ? summaryOf(props.data) : []));

const DOT: Record<TimelineKind, string> = {
	start: "bg-primary",
	onset: "bg-error",
	stop: "bg-neutral",
};

const sections = [
	{ id: "view-institution", label: "Institution" },
	{ id: "view-patient", label: "Patient" },
	{ id: "view-reaction", label: "Reaction" },
	{ id: "view-medicines", label: "Medicines" },
	{ id: "view-rechallenge", label: "Rechallenge" },
	{ id: "view-grading", label: "Grading" },
];

const active = ref("");

function go(id: string) {
	document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
	active.value = id;
}

// Highlight the section being read, as the form's list does.
let observer: IntersectionObserver | undefined;

onMounted(() => {
	observer = new IntersectionObserver(
		(entries) => {
			for (const entry of entries) if (entry.isIntersecting) active.value = entry.target.id;
		},
		{ rootMargin: "-10% 0px -75% 0px" },
	);
	for (const section of sections) {
		const element = document.getElementById(section.id);
		if (element) observer.observe(element);
	}
});

onBeforeUnmount(() => observer?.disconnect());

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
