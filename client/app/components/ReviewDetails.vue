<template>
	<UCard class="my-4">
		<template #header>
			<div class="flex flex-col">
				<h3 class="text-lg font-semibold">Review Details</h3>
			</div>
		</template>

		<div class="space-y-4">
			<!-- My Vote -->
			<div class="flex justify-between items-center">
				<p class="font-medium">My Vote</p>
				<ApprovedBadge :is-approved="data?.approved" />
			</div>
			<USeparator />

			<!-- Proposed Causality Assessment Level -->
			<div class="flex justify-between items-center">
				<p class="font-medium">Proposed Causality Assessment Level</p>
				<template v-if="data?.proposed_causality_level">
					<UBadge :class="proposedCalColor" size="md">
						{{ capitalize(data.proposed_causality_level) }}
					</UBadge>
				</template>
				<BlankBadge v-else />
			</div>
			<USeparator />

			<!-- Reason -->
			<div class="flex justify-between items-start">
				<p class="font-medium">Reason</p>
				<p
					v-if="data?.reason"
					class="text-sm text-neutral-700 dark:text-neutral-300 max-w-md text-right"
				>
					{{ data.reason }}
				</p>
				<BlankBadge v-else />
			</div>
			<USeparator />

			<!-- Created At -->
			<div class="flex justify-between items-center">
				<p class="font-medium">Created At</p>
				<p
					v-if="data?.created_at"
					class="text-sm text-neutral-600 dark:text-neutral-400"
				>
					{{
						`${data.created_at.slice(0, 10)} ${formatTime(
							data.created_at
						)}`
					}}
				</p>
				<BlankBadge v-else />
			</div>
		</div>

		<!-- <template #footer>
			<div class="flex justify-end gap-2">
				<UButton
					color="primary"
					variant="soft"
					@click="
						router.push({
							path: `/causality-assessment-level/${causality_assessment_level_id}/review`,
							query: { mode: 'update' },
						})
					"
				>
					<UIcon name="i-lucide-pencil" class="mr-1" /> Edit Review
				</UButton>

				<UAlertDialog>
					<UAlertDialogTrigger as-child>
						<UButton variant="soft">
							<UIcon name="i-lucide-trash-2" class="mr-1" /> Delete Review
						</UButton>
					</UAlertDialogTrigger>

					<UAlertDialogContent>
						<UAlertDialogHeader>
							<UAlertDialogTitle>Are you sure?</UAlertDialogTitle>
							<UAlertDialogDescription>
								This action cannot be undone. This will permanently delete this record.
							</UAlertDialogDescription>
						</UAlertDialogHeader>

						<UAlertDialogFooter>
							<UAlertDialogCancel>Cancel</UAlertDialogCancel>
							<UAlertDialogAction @click="handleDelete">Continue</UAlertDialogAction>
						</UAlertDialogFooter>
					</UAlertDialogContent>
				</UAlertDialog>
			</div>
		</template> -->
	</UCard>
</template>

<script setup lang="ts">
import { capitalize } from "lodash-es";

import type { CausalityAssessmentLevelEnum } from "@/types/adr";
import type { ReviewGetResponse } from "@/types/review";

const props = defineProps<{
	data?: ReviewGetResponse;
	causality_assessment_level_id?: string;
}>();

const router = useRouter();

const proposedCalColor = computed(() => {
	switch (props.data?.proposed_causality_level) {
		case "certain":
			return "bg-red-500 text-white";
		case "likely":
			return "bg-red-400";
		case "possible":
			return "bg-yellow-500";
		case "unlikely":
			return "bg-yellow-300";
		case "unclassified":
			return "bg-slate-500 text-white";
		case "unclassifiable":
			return "bg-slate-300";
		default:
			return "";
	}
});

async function handleDelete() {
	// const runtimeConfig = useRuntimeConfig();
	// const serverApi = runtimeConfig.public.serverApi;

	// await $fetch(`${serverApi}/review/${props.data?.id}`, {
	// 	method: "DELETE",
	// 	headers: {
	// 		Authorization: `Bearer ${authStore.accessToken}`,
	// 	},
	// });

	navigateTo("/adr");
}

function formatTime(isoString: string): string {
	const date = new Date(isoString);
	return new Intl.DateTimeFormat("en-US", {
		hour: "numeric",
		minute: "numeric",
		hour12: true,
	}).format(date);
}
</script>

<style scoped>
@reference "assets/css/main.css";

.card-footer {
	@apply flex space-x-2 justify-end w-full;
}
</style>
