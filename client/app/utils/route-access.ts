// Decides where a visitor may go. Pure: the middleware reads the session and passes the facts in.

export type RouteAccess = { kind: "allow" } | { kind: "redirect"; to: string };

export const LOGIN_PATH = "/auth/login";
export const ABOUT_PATH = "/about";

/** True when the page opens without a sign-in, so the middleware need not read the session. */
export function isPublicPath({ path }: { path: string }): boolean {
	return path.startsWith("/auth/") || path === ABOUT_PATH;
}

/** Decides what happens to a visitor of a page that is not public. */
export function decideAccess({ path, hasSession }: { path: string; hasSession: boolean }): RouteAccess {
	if (hasSession) return { kind: "allow" };
	if (path === "/") return { kind: "redirect", to: ABOUT_PATH };
	return { kind: "redirect", to: LOGIN_PATH };
}
