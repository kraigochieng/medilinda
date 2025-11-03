import type {
	MedicalInstitutionGetResponseInterface,
	MedicalInstitutionPostRequestInterface,
} from "~/types/medical_institution";
import type { PaginatedResponseInterface } from "~/types/pagination";
const path = "medical-institutions";

export async function fetchMedicalInstitutions(params: {
	page?: number;
	size?: number;
	query?: string;
}): Promise<
	PaginatedResponseInterface<MedicalInstitutionGetResponseInterface>
> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<
		PaginatedResponseInterface<MedicalInstitutionGetResponseInterface>
	>(`/${path}/`, {
		method: "GET",
		query: params,
	});
}

export async function fetchMedicalInstitutionById(
	id: string
): Promise<MedicalInstitutionGetResponseInterface> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<MedicalInstitutionGetResponseInterface>(
		`/${path}/${id}`,
		{
			method: "GET",
		}
	);
}

export async function postMedicalInstitution(
	data: MedicalInstitutionPostRequestInterface
): Promise<MedicalInstitutionGetResponseInterface> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<MedicalInstitutionGetResponseInterface>(
		`/${path}`,
		{
			method: "POST",
			body: data,
		}
	);
}
