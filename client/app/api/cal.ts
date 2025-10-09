const path = "causality-assessment-levels";
import type { ReviewWithUserGetResponse } from "~/types/review";
import type { PaginatedResponseInterface } from "~/types/pagination";

export async function fetchReviewsByCausalityAssessmentLevelId(
	causalityAssessmentLevelId: string,
	page = 1,
	size = 50
): Promise<PaginatedResponseInterface<ReviewWithUserGetResponse>> {
	const { $serverFetch } = useNuxtApp();

	return await $serverFetch<
		PaginatedResponseInterface<ReviewWithUserGetResponse>
	>(`/${path}/${causalityAssessmentLevelId}/review`, {
		method: "GET",
		query: {
			page,
			size,
		},
	});
}
