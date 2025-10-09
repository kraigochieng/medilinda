export default defineNuxtPlugin((nuxtApp) => {
	const serverFetch = $fetch.create({
		baseURL: `${useRuntimeConfig().public.serverApi}/api/v1`,
		onRequest({ request, options, error }) {
			// Read cookie
			const token = useCookie("medilindaBearerToken").value;

			// Normalize headers (works with Fetch type)
			const headers = new Headers(options.headers || {});

			if (token) {
				headers.set("Authorization", `Bearer ${token}`);
			}

			options.headers = headers;
		},
		async onResponseError({ response }) {
			if (response.status === 401) {
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
