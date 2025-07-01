const path = "adr";
import humps from "humps";
import type { ADRBaseModel } from "~/types/adr";

export async function fetchAdrs(params = { offset: 0, limit: 10 }) {
	return await useServerFetch<ADRGetResponseInterface[]>(`/${path}`, {
		method: "GET",
		query: params,
	});
}

export async function fetchAdrById(id: string) {
	return await useServerFetch(`/${path}/${id}`, {
		method: "GET",
	});
}
export async function postAdr(body: any) {
	return await useServerFetch(`/${path}`, {
		method: "POST",
		body: humps.decamelizeKeys(body),
	});
}
