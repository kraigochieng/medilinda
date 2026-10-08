<template>
	<div>
		<USelectMenu
			v-model="model"
			v-model:search-term="searchTerm"
			:items="items"
			value-key="value"
			ignore-filter
			:loading="isFetching"
			icon="i-lucide-hospital"
			placeholder="Search by name, MFL code or county"
			:search-input="{ placeholder: 'Type to search…', icon: 'i-lucide-search' }"
			class="w-full"
		>
			<template #item-label="{ item }">
				<span class="block truncate">{{ item.label }}</span>
				<span v-if="item.location" class="block truncate text-xs text-muted">
					{{ item.location }}
				</span>
			</template>

			<template #empty>
				<span v-if="isError">
					Could not load institutions.
					<button type="button" class="underline" @click="refetch()">Try again</button>
				</span>
				<span v-else-if="isFetching">Searching…</span>
				<span v-else-if="searchTerm">No institution matches “{{ searchTerm }}”.</span>
				<span v-else>No institutions yet.</span>
			</template>

			<template #content-bottom>
				<div class="border-t border-default p-2">
					<UButton
						block
						size="sm"
						color="neutral"
						variant="ghost"
						icon="i-lucide-plus"
						label="Can't find it? Add an institution"
						@click="createOpen = true"
					/>
				</div>
			</template>
		</USelectMenu>

		<UModal
			v-model:open="createOpen"
			title="Add a medical institution"
			description="It is selected for this report once it is saved. Alerts are sent to the phone numbers you give."
		>
			<template #body>
				<FormMedicalInstitution mode="create" :is-in-dialog="true" @submitted="onCreated" />
			</template>
		</UModal>
	</div>
</template>

<script setup lang="ts">
import { fetchMedicalInstitutionById, fetchMedicalInstitutions } from "@/api/medical_institution";
import { keepPreviousData, useQuery, useQueryClient } from "@tanstack/vue-query";
import { buildItems } from "~/utils/institution-picker";

// The id of the chosen institution.
const model = defineModel<string | undefined>();

const toast = useToast();
const queryClient = useQueryClient();

const searchTerm = ref("");
const debouncedSearch = refDebounced(searchTerm, 300);
const createOpen = ref(false);

const { data, isFetching, isError, refetch } = useQuery({
	queryKey: ["medicalInstitutions", debouncedSearch],
	queryFn: () => fetchMedicalInstitutions({ size: 20, query: debouncedSearch.value }),
	placeholderData: keepPreviousData,
});

// The chosen institution, so it shows by name even when the search does not list it.
const { data: selected } = useQuery({
	queryKey: ["medicalInstitution", model],
	queryFn: () => fetchMedicalInstitutionById(model.value as string),
	enabled: computed(() => !!model.value),
});

const items = computed(() => buildItems(data.value?.items ?? [], selected.value));

function onCreated(success: boolean, institutionId?: string, message?: string) {
	if (!success || !institutionId) {
		toast.add({ title: "Could not add the institution", description: message, color: "error" });
		return;
	}

	model.value = institutionId;
	createOpen.value = false;
	queryClient.invalidateQueries({ queryKey: ["medicalInstitutions"] });

	// The institution is saved even if its phone numbers failed, so say so.
	const phonesFailed = message?.includes("failed to add telephones");
	toast.add({
		title: "Institution added and selected",
		description: phonesFailed ? message : undefined,
		color: phonesFailed ? "warning" : "success",
	});
}
</script>
