import type { TelephonePostRequest } from "~/types/telephone";

const path = "/telephones";
export async function postTelephones(
	data: TelephonePostRequest[]
): Promise<TelephonePostRequest[]> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<TelephonePostRequest[]>(`/${path}/`, {
		method: "POST",
		body: data,
	});
}
