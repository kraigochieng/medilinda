import { createTokenProvider } from "~/utils/token-provider";

// Short-lived Better Auth JWT for calling the FastAPI server.
const tokens = createTokenProvider({
	cache: import.meta.client,
	fetchToken: async () => {
		const headers = import.meta.server
			? useRequestHeaders(["cookie"])
			: undefined;
		const { token } = await $fetch<{ token: string }>("/api/auth/token", {
			headers,
		});
		return token;
	},
});

export default defineNuxtPlugin((nuxtApp) => {
	const serverFetch = $fetch.create({
		baseURL: `${useRuntimeConfig().public.serverApi}/api/v1`,
		async onRequest({ options }) {
			const token = await nuxtApp.runWithContext(() => tokens.get());
			const headers = new Headers(options.headers || {});

			if (token) {
				headers.set("Authorization", `Bearer ${token}`);
			}

			options.headers = headers;
		},
		async onResponseError({ response }) {
			if (response.status === 401) {
				tokens.clear();
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
