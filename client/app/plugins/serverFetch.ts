// Short-lived Better Auth JWT for calling the FastAPI server.
// Cached in the browser only, so it can never leak between users on the server.
let cachedToken: { value: string; expiresAt: number } | null = null;

function readExpiry(token: string): number {
	try {
		const payload = JSON.parse(atob(token.split(".")[1] ?? ""));
		return payload.exp * 1000;
	} catch {
		return 0;
	}
}

export default defineNuxtPlugin((nuxtApp) => {
	async function getToken(): Promise<string | null> {
		if (import.meta.client && cachedToken && cachedToken.expiresAt - 30_000 > Date.now()) {
			return cachedToken.value;
		}

		try {
			const headers = import.meta.server
				? useRequestHeaders(["cookie"])
				: undefined;
			const { token } = await $fetch<{ token: string }>("/api/auth/token", {
				headers,
			});

			if (import.meta.client) {
				cachedToken = { value: token, expiresAt: readExpiry(token) };
			}
			return token;
		} catch {
			cachedToken = null;
			return null;
		}
	}

	const serverFetch = $fetch.create({
		baseURL: `${useRuntimeConfig().public.serverApi}/api/v1`,
		async onRequest({ options }) {
			const token = await nuxtApp.runWithContext(getToken);
			const headers = new Headers(options.headers || {});

			if (token) {
				headers.set("Authorization", `Bearer ${token}`);
			}

			options.headers = headers;
		},
		async onResponseError({ response }) {
			if (response.status === 401) {
				cachedToken = null;
				await nuxtApp.runWithContext(() => navigateTo("/auth/login"));
			}
		},
	});

	return {
		provide: {
			serverFetch,
		},
	};
});
