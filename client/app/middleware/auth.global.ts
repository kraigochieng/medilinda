export default defineNuxtRouteMiddleware(async (to) => {
	if (to.path.startsWith("/auth/")) return;

	// useRequestFetch forwards the browser's cookies when this runs on the
	// server. The Better Auth client cannot be used here because it needs an
	// absolute URL during server rendering.
	const requestFetch = useRequestFetch();
	const session = await requestFetch("/api/auth/get-session").catch(() => null);

	if (!session) {
		return navigateTo("/auth/login");
	}
});
