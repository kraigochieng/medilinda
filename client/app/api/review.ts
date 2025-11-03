import type { PaginatedResponseInterface } from "~/types/pagination";
import type { ReviewGetResponse, ReviewStatsGetResponse } from "~/types/review";

const path = "reviews";
const statsPath = "reviews-details";

export async function fetchReviews(params: {
	page?: number;
	size?: number;
	causality_assessment_level_id?: string;
	user_id?: string;
}): Promise<PaginatedResponseInterface<ReviewGetResponse>> {
	const { $serverFetch } = useNuxtApp();

	return await $serverFetch<PaginatedResponseInterface<ReviewGetResponse>>(
		`/${path}/`,
		{
			method: "GET",
			query: params,
		}
	);
}

export async function fetchReviewStats(
	causality_assessment_level_id: string
): Promise<ReviewStatsGetResponse> {
	const { $serverFetch } = useNuxtApp();

	// Calls: GET /api/v1/reviews-details/{id}/stats
	return await $serverFetch<ReviewStatsGetResponse>(
		`/${statsPath}/${causality_assessment_level_id}/stats`,
		{
			method: "GET",
			// No query params are needed, as the ID is in the path
		}
	);
}
