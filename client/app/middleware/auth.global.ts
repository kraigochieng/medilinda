import { decideAccess, isPublicPath } from "~/utils/route-access";

export default defineNuxtRouteMiddleware(async (to) => {
	if (isPublicPath({ path: to.path })) return;

	// useRequestFetch forwards the browser's cookies when this runs on the
	// server. The Better Auth client cannot be used here because it needs an
	// absolute URL during server rendering.
	const requestFetch = useRequestFetch();
	const session = await requestFetch("/api/auth/get-session").catch(() => null);

	const access = decideAccess({ path: to.path, hasSession: Boolean(session) });
	if (access.kind === "redirect") {
		return navigateTo(access.to);
	}
});
