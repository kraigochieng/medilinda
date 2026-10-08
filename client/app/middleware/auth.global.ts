import { authClient } from "~/lib/auth-client";

export default defineNuxtRouteMiddleware(async (to) => {
	if (to.path.startsWith("/auth/")) return;

	const headers = import.meta.server ? useRequestHeaders(["cookie"]) : undefined;
	const { data: session } = await authClient.getSession({
		fetchOptions: { headers },
	});

	if (!session) {
		return navigateTo("/auth/login");
	}
});
