import { aboutLayout, ABOUT_PATH, decideAccess, isAuthPath } from "~/utils/route-access";

export default defineNuxtRouteMiddleware(async (to) => {
	if (isAuthPath({ path: to.path })) return;

	// useRequestFetch forwards the browser's cookies when this runs on the
	// server. The Better Auth client cannot be used here because it needs an
	// absolute URL during server rendering.
	const requestFetch = useRequestFetch();
	const session = await requestFetch("/api/auth/get-session").catch(() => null);
	const hasSession = Boolean(session);

	if (to.path === ABOUT_PATH) setPageLayout(aboutLayout({ hasSession }));

	const access = decideAccess({ path: to.path, hasSession });
	if (access.kind === "redirect") {
		return navigateTo(access.to);
	}
});
