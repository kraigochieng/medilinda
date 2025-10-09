import type { ReviewGetResponse } from "~/types/review";

const path = "reviews-details";

export async function fetchReviewByUserAndCausalityLevel(
	causalityAssessmentLevelId: string
): Promise<ReviewGetResponse> {
	const { $serverFetch } = useNuxtApp();

	return await $serverFetch<ReviewGetResponse>(
		`/${path}/specific-user-and-causality-assessment-level`,
		{
			method: "GET",
			query: { causality_assessment_level_id: causalityAssessmentLevelId },
		}
	);
}
