import type { UseFetchOptions } from "nuxt/app";

export function useServerApiUseFetch<T>(
	url: string | (() => string),
	options?: UseFetchOptions<T>
) {
	return useFetch(url, {
		...options,
		$fetch: useNuxtApp().$serverApiFetch as typeof $fetch,
	});
}
