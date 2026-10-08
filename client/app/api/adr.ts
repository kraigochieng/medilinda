import type {
	ADRGetResponseInterface,
	ADRPostRequestInterface,
	ADRWithCausalityLevelAndReviewCountInterface,
} from "@/types/adr";

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

export async function deleteAdrById(id: string): Promise<void> {
	const { $serverFetch } = useNuxtApp();

	return await $serverFetch<void>(`/${path}/${id}`, {
		method: "DELETE",
	});
}

export async function putAdr(
	id: string,
	data: ADRPostRequestInterface
): Promise<ADRGetResponseInterface> {
	const { $serverFetch } = useNuxtApp();

	return await $serverFetch<ADRGetResponseInterface>(`/${path}/${id}`, {
		method: "PUT",
		body: data,
	});
}

// Undoes a delete: brings back the ADR with its assessments and reviews.
export async function restoreAdrById(id: string): Promise<ADRGetResponseInterface> {
	const { $serverFetch } = useNuxtApp();

	return await $serverFetch<ADRGetResponseInterface>(`/${path}/${id}/restore`, {
		method: "POST",
	});
}

export async function postAdr(
	data: ADRPostRequestInterface
): Promise<ADRGetResponseInterface> {
	const { $serverFetch } = useNuxtApp();

	return await $serverFetch(`/${path}/`, {
		method: "POST",
		body: data,
	});
}

export async function fetchAdrsWithCausalityAndReviewCount(params: {
	page?: number;
	size?: number;
	query?: string;
	causality_level?: string;
	review_status?: string;
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
