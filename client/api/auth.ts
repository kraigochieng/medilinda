import humps from "humps";
import type { ADRBaseModel } from "@/types/adr";
import type {
	TokenResponse,
	TokenRefreshResponse,
	LoginCredentials,
	SignUpDetails,
} from "@/types/auth";
import type { UserDetails } from "@/types/user";

function getServerApi() {
	const runtimeConfig = useRuntimeConfig();
	return runtimeConfig.public.serverApi;
}

export function postToken(credentials: LoginCredentials) {
	const body = new URLSearchParams();

	body.set("username", credentials.username);
	body.set("password", credentials.password);

	return useFetch<TokenResponse>(`${getServerApi()}/token`, {
		method: "POST",
		headers: {
			"Content-Type": "application/x-www-form-urlencoded",
		},
		body: body,
	});
}

export async function postTokenRefresh(refreshToken: string) {
	return await useFetch<TokenRefreshResponse>(
		`${getServerApi()}/token/refresh`,
		{
			method: "POST",
			query: { refreshToken },
		}
	);
}

export async function postSignup(user: SignUpDetails) {
	return await useFetch(`${getServerApi()}/signup`, {
		method: "POST",
		body: humps.decamelizeKeys(user),
	});
}

export async function getCurrentUser() {
	return await useFetch<UserDetails>(`${getServerApi()}/users/me`, {
		method: "GET",
	});
}
