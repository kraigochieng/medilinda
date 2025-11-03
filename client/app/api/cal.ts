import type { CausalityAssessmentLevelGetResponseInterface } from "@/types/cal";
import type { PaginatedResponseInterface } from "~/types/pagination";

const path = "causality-assessment-levels";

export async function fetchCausalityAssessmentLevels(params: {
	page?: number;
	size?: number;
	adr_id?: string;
}): Promise<
	PaginatedResponseInterface<CausalityAssessmentLevelGetResponseInterface>
> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<
		PaginatedResponseInterface<CausalityAssessmentLevelGetResponseInterface>
	>(`/${path}/`, {
		method: "GET",
		query: params,
	});
}
