import type { PaginatedResponseInterface } from "~/types/pagination";
import type {
	ReviewGetResponse,
	ReviewPostResponse,
	ReviewStatsGetResponse,
} from "~/types/review";

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

export interface ReviewPayload {
	causality_assessment_level_id: string;
	approved: boolean;
	proposed_causality_level?: string;
	reason?: string;
}

export type ReviewUpdatePayload = Omit<ReviewPayload, "causality_assessment_level_id">;

// The reviewer is the signed-in user. The server ignores any user id.
export async function postReview(data: ReviewPayload): Promise<ReviewPostResponse> {
	const { $serverFetch } = useNuxtApp();

	return await $serverFetch<ReviewPostResponse>(`/${path}/`, { method: "POST", body: data });
}

// Only the author can change a review, and only while its assessment is the newest.
export async function putReview(id: string, data: ReviewUpdatePayload): Promise<ReviewPostResponse> {
	const { $serverFetch } = useNuxtApp();

	return await $serverFetch<ReviewPostResponse>(`/${path}/${id}`, { method: "PUT", body: data });
}

export async function deleteReview(id: string): Promise<void> {
	const { $serverFetch } = useNuxtApp();

	return await $serverFetch<void>(`/${path}/${id}`, { method: "DELETE" });
}
