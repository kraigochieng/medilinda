<template>
	<div>
		<UForm :schema="schema" :state="state" @submit="onSubmit">
			<UCard>
				<template #header>
					<h2 class="text-lg font-semibold">
						{{ existingReview ? "Change your review" : "Add your review" }}
					</h2>
					<p class="mt-1 flex flex-wrap items-center gap-1 text-sm text-muted">
						The model predicted
						<CausalityBadge :value="predictedLevel" />
						. Do you agree?
					</p>
				</template>

				<div class="space-y-6">
					<UFormField name="approved" label="Your decision" required>
						<URadioGroup
							v-model="decision"
							:items="decisions"
							variant="card"
							orientation="horizontal"
						/>
					</UFormField>

					<UFormField
						v-if="state.approved === false"
						name="proposed_causality_level"
						label="The level you propose instead"
						required
					>
						<URadioGroup
							v-model="state.proposed_causality_level"
							:items="levelItems"
						/>
					</UFormField>

					<UFormField
						v-if="state.approved !== undefined"
						name="reason"
						:label="state.approved === false ? 'Reason' : 'Note (optional)'"
						:required="state.approved === false"
						:help="
							state.approved === false
								? 'Explain why another level fits better.'
								: 'Add anything the next reviewer should know.'
						"
					>
						<UTextarea v-model="state.reason" :rows="3" class="w-full" />
					</UFormField>
				</div>

				<template #footer>
					<div class="flex flex-wrap items-center justify-between gap-2">
						<UButton
							v-if="existingReview"
							type="button"
							color="error"
							variant="ghost"
							icon="i-lucide-trash-2"
							label="Remove my review"
							@click="removeOpen = true"
						/>
						<UButton
							type="submit"
							class="ml-auto"
							:loading="isSaving"
							:label="existingReview ? 'Save changes' : 'Submit review'"
						/>
					</div>
				</template>
			</UCard>
		</UForm>

		<UModal v-model:open="removeOpen" title="Remove your review?">
			<template #body>
				<p>Your vote is removed from this assessment. You can add a new review afterwards.</p>
			</template>
			<template #footer>
				<div class="flex w-full justify-end gap-2">
					<UButton color="neutral" variant="outline" label="Cancel" @click="removeOpen = false" />
					<UButton color="error" label="Remove" :loading="isRemoving" @click="remove()" />
				</div>
			</template>
		</UModal>
	</div>
</template>

<script setup lang="ts">
import { deleteReview, postReview, putReview } from "@/api/review";
import type { ReviewGetResponse } from "@/types/review";
import type { FormSubmitEvent } from "@nuxt/ui";
import { useMutation, useQueryClient } from "@tanstack/vue-query";
import {
	apiErrorMessage,
	proposableLevels,
	reviewFormSchema,
	toReviewPayload,
	toReviewUpdate,
	type ReviewFormState,
} from "~/utils/review-form";

const props = defineProps<{
	causalityAssessmentLevelId: string;
	predictedLevel?: string | null;
	// The signed-in user's own review of this assessment, if they already gave one.
	existingReview?: ReviewGetResponse | null;
}>();

const emit = defineEmits<{ (e: "saved"): void; (e: "removed"): void }>();

const toast = useToast();
const queryClient = useQueryClient();

const schema = computed(() => reviewFormSchema(props.predictedLevel));
const levelItems = computed(() => proposableLevels(props.predictedLevel));

const state = reactive<ReviewFormState>({
	approved: props.existingReview?.approved,
	proposed_causality_level: props.existingReview?.proposed_causality_level ?? undefined,
	reason: props.existingReview?.reason ?? undefined,
});

const decisions = [
	{ value: "approve", label: "Approve", description: "The predicted level is right." },
	{ value: "reject", label: "Do not approve", description: "Another level fits better." },
];

const decision = computed({
	get: () => (state.approved === undefined ? undefined : state.approved ? "approve" : "reject"),
	set: (value) => {
		state.approved = value === "approve";
		if (state.approved) state.proposed_causality_level = undefined;
	},
});

// Everything the review pages show comes from these queries.
function refresh() {
	for (const key of ["my-review", "review-details", "reviews-stats", "reviews-by-causality-level", "adrs"]) {
		queryClient.invalidateQueries({ queryKey: [key] });
	}
}

const { mutate: save, isPending: isSaving } = useMutation({
	mutationFn: (form: ReviewFormState) =>
		props.existingReview
			? putReview(props.existingReview.id, toReviewUpdate(form))
			: postReview(toReviewPayload(form, props.causalityAssessmentLevelId)),
	onSuccess: () => {
		refresh();
		toast.add({
			title: props.existingReview ? "Review updated" : "Review saved",
			color: "success",
		});
		emit("saved");
	},
	onError: (error) =>
		toast.add({ title: "Could not save your review", description: apiErrorMessage(error), color: "error" }),
});

const removeOpen = ref(false);

const { mutate: remove, isPending: isRemoving } = useMutation({
	mutationFn: () => deleteReview(props.existingReview!.id),
	onSuccess: () => {
		refresh();
		removeOpen.value = false;
		toast.add({ title: "Your review was removed", color: "success" });
		emit("removed");
	},
	onError: (error) =>
		toast.add({ title: "Could not remove your review", description: apiErrorMessage(error), color: "error" }),
});

function onSubmit(event: FormSubmitEvent<ReviewFormState>) {
	save(event.data);
}
</script>
