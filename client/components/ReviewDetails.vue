<template>
	<Card class="my-4">
		<CardHeader>
			<CardTitle>Review Details</CardTitle>
		</CardHeader>
		<CardContent>
			<div class="view-details-wrapper">
				<p>My Vote</p>
				<p><ApprovedBadge :is-approved="data?.approved" /></p>
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p>Proposed Causality Assessment Level</p>
				<p
					v-if="data?.proposed_causality_level"
					class="badge"
					:class="proposedCalColor"
				>
					{{ capitalize(data.proposed_causality_level) }}
				</p>
				<BlankBadge v-else />
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p>Reason</p>
				<p v-if="data?.reason" class="view-details-content">
					{{ data?.reason }}
				</p>
				<BlankBadge v-else />
			</div>
			<Separator class="my-2" />
			<div class="view-details-wrapper">
				<p>Created At</p>
				<p v-if="data?.created_at" class="view-details-content">
					{{
						`${data.created_at.slice(0, 10) || ""} ${formatTime(
							data.created_at
						)}`
					}}
				</p>
				<BlankBadge v-else />
			</div>
		</CardContent>

		<CardFooter class="card-footer">
			<Button
				@mouseup="
					router.push({
						path: `/causality-assessment-level/${causality_assessment_level_id}/review`,
						query: { mode: 'update' },
					})
				"
			>
				Edit Review
			</Button>
			<AlertDialog>
				<AlertDialogTrigger as-child>
					<Button>Delete Review</Button>
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
							Continue
						</AlertDialogAction>
					</AlertDialogFooter>
				</AlertDialogContent>
			</AlertDialog>
		</CardFooter>
	</Card>
</template>

<script setup lang="ts">
import { capitalize } from "lodash";

// Props
const props = defineProps<{
	data?: Review;
	causality_assessment_level_id?: string;
}>();

// Stores
const authStore = useAuthStore();

// Routing
const router = useRouter();

const proposedCalColor = computed(() => {
	if (props.data?.proposed_causality_level) {
		if (props.data.proposed_causality_level == "certain") {
			return "bg-red-500 text-white";
		} else if (props.data.proposed_causality_level == "likely") {
			return "bg-red-400";
		} else if (props.data.proposed_causality_level == "possible") {
			return "bg-yellow-500";
		} else if (props.data.proposed_causality_level == "unlikely") {
			return "bg-yellow-300";
		} else if (props.data.proposed_causality_level == "unclassified") {
			return "bg-slate-500 text-white";
		} else if (props.data.proposed_causality_level == "unclassifiable") {
			return "bg-slate-300";
		}
	} else {
		return "";
	}
});
// Types
interface Review {
	id: string;
	user_id: string;
	causality_assessment_level?: CausalityAssessmentLevelEnum;
	approved: boolean;
	proposed_causality_level?: CausalityAssessmentLevelEnum;
	reason?: string;
	created_at: string;
	updated_at: string;
}

// Events
async function handleDelete() {
	const runtimeConfig = useRuntimeConfig();
	const serverApi = runtimeConfig.public.serverApi;

	const response = await $fetch(`${serverApi}/review/${props.data?.id}`, {
		method: "DELETE",
		headers: {
			Authorization: `Bearer ${authStore.accessToken}`,
		},
	});

	// navigateTo(
	// 	`/causality-assessment-level/${props.causality_assessment_level_id}`
	// );
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
.card-footer {
	@apply flex space-x-2 justify-end w-full;
}
</style>
