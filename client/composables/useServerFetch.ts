// import type { UseFetchOptions, UseFetchReturn } from "#app";
// import type { NitroFetchRequest } from "nitropack";

/**
 * A composable for making API requests with automatic access token handling.
 */
function getServerApi() {
	const runtimeConfig = useRuntimeConfig();
	return runtimeConfig.public.serverApi;
}

// Define the custom useAPI function
export async function useServerFetch<T>(url: string, options: any = {}) {
	const authStore = useAuthStore();
	// Ensure headers exist
	if (!options.headers) options.headers = {};

	// Attach access token if available
	if (authStore.accessToken) {
		options.headers = {
			...options.headers,
			Authorization: `Bearer ${authStore.accessToken}`,
		};
	}

	// Make the request using useFetch
	let response = await useFetch<T>(url, {
		baseURL: getServerApi,
		...options,
	});

	if (response.status.value == "success") {
		// Access Token Valid
		return response;
	} else if (
		response.error.value?.statusCode === 401 &&
		authStore.refreshToken
	) {
		// Access Token Invalid
		const { data: refreshData, status: refreshStatus } =
			await postTokenRefresh(authStore.refreshToken);

		if (refreshStatus.value == "success" && refreshData.value) {
			// Refresh Token Valid
			authStore.accessToken = refreshData.value.accessToken;

			options.headers.Authorization = `Bearer ${authStore.accessToken}`;

			response = await useFetch<T>(url, {
				baseURL: getServerApi,
				...options,
			});
		} else if (refreshStatus.value == "error") {
			// Refresh Token Invalid
			authStore.logout();
		}

		return response;
	}
}
