import type { UserDetails } from "@/types/user";

export async function fetchCurrentUser(): Promise<UserDetails> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<UserDetails>(`/users/me`, {
		method: "GET",
	});
}
