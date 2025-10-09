import type { MedicalInstitutionGetResponseInterface } from "~/types/medical_institution";

const path = "medical-institutions";

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
