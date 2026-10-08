// Rules for a review of a causality assessment. They mirror the server's, so a
// mistake is shown next to the field instead of coming back as a failed request.
import { z } from "zod";
import { reviewFormCategoricalValues } from "~/values/review";

export const MIN_REASON_LENGTH = 3;

export interface ReviewFormState {
	approved?: boolean;
	proposed_causality_level?: string;
	reason?: string;
}

export function reviewFormSchema(predictedLevel?: string | null) {
	return z
		.object({
			approved: z.boolean({ error: "Choose whether you approve the prediction." }),
			proposed_causality_level: z.string().optional(),
			reason: z.string().optional(),
		})
		.superRefine((form, ctx) => {
			if (form.approved !== false) return;

			if (!form.proposed_causality_level) {
				ctx.addIssue({
					code: "custom",
					path: ["proposed_causality_level"],
					message: "Choose the causality level you propose instead.",
				});
			} else if (predictedLevel && form.proposed_causality_level === predictedLevel) {
				ctx.addIssue({
					code: "custom",
					path: ["proposed_causality_level"],
					message: "The proposed level must differ from the predicted level.",
				});
			}

			if (!form.reason || form.reason.trim().length < MIN_REASON_LENGTH) {
				ctx.addIssue({
					code: "custom",
					path: ["reason"],
					message: `Give a reason for not approving (at least ${MIN_REASON_LENGTH} characters).`,
				});
			}
		});
}

// The levels a reviewer can propose: every level except the one predicted.
export function proposableLevels(predictedLevel?: string | null) {
	return reviewFormCategoricalValues.proposedCausalityLevel.filter(
		(option) => option.value !== predictedLevel,
	);
}

// What the server needs. The reviewer is the signed-in user, so no user id is sent.
// An approval carries no proposed level.
export function toReviewUpdate(form: ReviewFormState) {
	const approved = form.approved === true;

	return {
		approved,
		proposed_causality_level: approved ? undefined : form.proposed_causality_level,
		reason: form.reason?.trim() || undefined,
	};
}

export function toReviewPayload(form: ReviewFormState, causalityAssessmentLevelId: string) {
	return { causality_assessment_level_id: causalityAssessmentLevelId, ...toReviewUpdate(form) };
}

// The server sends { "error": "..." }; a failed request also has a plain message.
export function apiErrorMessage(error: unknown, fallback = "Something went wrong. Try again."): string {
	const data = (error as { data?: { error?: unknown; detail?: unknown } } | null)?.data;

	if (typeof data?.error === "string") return data.error;
	if (typeof data?.detail === "string") return data.detail;

	const status = (error as { statusCode?: number } | null)?.statusCode;
	if (status === 404) return "That could not be found. It may have been deleted.";
	if (status === 403) return "You are not allowed to do that.";

	return fallback;
}
