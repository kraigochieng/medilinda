<template>
	<UCard class="my-4">
		<template #header>
			<h3 class="text-lg font-semibold">Your review</h3>
		</template>

		<div class="space-y-4">
			<div class="flex items-center justify-between">
				<p class="font-medium">Your vote</p>
				<ApprovedBadge :is-approved="data?.approved" />
			</div>
			<USeparator />

			<div class="flex items-center justify-between">
				<p class="font-medium">Proposed causality level</p>
				<CausalityBadge v-if="data?.proposed_causality_level" :value="data.proposed_causality_level" />
				<BlankBadge v-else />
			</div>
			<USeparator />

			<div class="flex items-start justify-between gap-4">
				<p class="font-medium">Reason</p>
				<p v-if="data?.reason" class="max-w-md text-right text-sm text-muted">{{ data.reason }}</p>
				<BlankBadge v-else />
			</div>
			<USeparator />

			<div class="flex items-center justify-between">
				<p class="font-medium">Reviewed</p>
				<p v-if="data?.created_at" class="text-sm text-muted">{{ formatDateTime(data.created_at) }}</p>
				<BlankBadge v-else />
			</div>
		</div>

		<template #footer>
			<div class="flex justify-end">
				<UButton
					:to="`/adr/${adrId}/review`"
					color="neutral"
					variant="outline"
					icon="i-lucide-pencil"
					label="Change my review"
				/>
			</div>
		</template>
	</UCard>
</template>

<script setup lang="ts">
import type { ReviewGetResponse } from "@/types/review";
import { formatDateTime } from "~/utils/adr-table";

// The signed-in user's own review of the current assessment.
defineProps<{
	data?: ReviewGetResponse;
	adrId: string;
}>();
</script>
