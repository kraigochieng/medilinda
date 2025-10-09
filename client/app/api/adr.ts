import type {
	ADRGetResponseInterface,
	ADRWithCausalityLevelAndReviewCountInterface,
} from "@/types/adr";
import type { CausalityAssessmentLevelWithReviewCountGetResponseInterface } from "@/types/cal";
import type { PaginatedResponseInterface } from "@/types/pagination";
import humps from "humps";
const path = "adrs";

export async function fetchAdrs(
	params = { offset: 0, limit: 10 }
): Promise<PaginatedResponseInterface<ADRGetResponseInterface>> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<
		PaginatedResponseInterface<ADRGetResponseInterface>
	>(`/${path}`, {
		method: "GET",
		query: params,
	});
}

export async function fetchAdrById(
	id: string
): Promise<ADRGetResponseInterface> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<ADRGetResponseInterface>(`/${path}/${id}`, {
		method: "GET",
	});
}

export async function deleteAdrById(
	id: string
): Promise<ADRGetResponseInterface> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<ADRGetResponseInterface>(`/${path}/${id}`, {
		method: "DELETE",
	});
}

export async function postAdr(body: any) {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch(`/${path}`, {
		method: "POST",
		body: humps.decamelizeKeys(body),
	});
}

export async function fetchAdrsWithCausalityAndReviewCount(params: {
	page?: number;
	size?: number;
	query?: string;
}): Promise<
	PaginatedResponseInterface<ADRWithCausalityLevelAndReviewCountInterface>
> {
	const { $serverFetch } = useNuxtApp();
	try {
		const data = await $serverFetch<
			PaginatedResponseInterface<ADRWithCausalityLevelAndReviewCountInterface>
		>(`/adrs-details/with-causality-and-review-count`, {
			method: "GET",
			query: params,
		});
		return data;
	} catch (error) {
		throw new Error(`${error}`);
	}
}

export async function fetchCausalityAssessmentByAdrId(
	id: string
): Promise<CausalityAssessmentLevelWithReviewCountGetResponseInterface> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<CausalityAssessmentLevelWithReviewCountGetResponseInterface>(
		`/${path}/${id}/causality-assessment-level`,
		{
			method: "GET",
		}
	);
}
