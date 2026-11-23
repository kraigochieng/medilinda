// Decides where a visitor may go and which layout a page uses. Pure: the middleware reads the session and passes the facts in.

export type RouteAccess = { kind: "allow" } | { kind: "redirect"; to: string };
export type LayoutName = "default" | "visitor";

export const LOGIN_PATH = "/auth/login";
export const ABOUT_PATH = "/about";

/** True for the sign-in pages. The middleware does not read the session for them. */
export function isAuthPath({ path }: { path: string }): boolean {
	return path.startsWith("/auth/");
}

/** True when the page opens without a sign-in. */
export function isPublicPath({ path }: { path: string }): boolean {
	return isAuthPath({ path }) || path === ABOUT_PATH;
}

/** Decides what happens when a visitor opens a page. */
export function decideAccess({ path, hasSession }: { path: string; hasSession: boolean }): RouteAccess {
	if (hasSession || isPublicPath({ path })) return { kind: "allow" };
	if (path === "/") return { kind: "redirect", to: ABOUT_PATH };
	return { kind: "redirect", to: LOGIN_PATH };
}

/** Chooses the layout of the About page: the sidebar only for a signed-in user. */
export function aboutLayout({ hasSession }: { hasSession: boolean }): LayoutName {
	return hasSession ? "default" : "visitor";
}
