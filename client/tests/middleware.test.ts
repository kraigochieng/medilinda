import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const navigateTo = vi.fn((path: string) => ({ redirectedTo: path }));
let sessionResponse: () => Promise<unknown>;

async function runMiddleware(path: string) {
	const { default: middleware } = await import("../app/middleware/auth.global");
	return (middleware as unknown as (to: { path: string }) => Promise<unknown>)({ path });
}

beforeEach(() => {
	navigateTo.mockClear();
	vi.stubGlobal("defineNuxtRouteMiddleware", (fn: unknown) => fn);
	vi.stubGlobal("useRequestFetch", () => () => sessionResponse());
	vi.stubGlobal("navigateTo", navigateTo);
	vi.resetModules();
});

afterEach(() => vi.unstubAllGlobals());

describe("auth route middleware", () => {
	it("lets /auth pages through without checking the session", async () => {
		sessionResponse = () => Promise.reject(new Error("should not be called"));
		expect(await runMiddleware("/auth/login")).toBeUndefined();
		expect(navigateTo).not.toHaveBeenCalled();
	});

	it("redirects to login when there is no session", async () => {
		sessionResponse = async () => null;
		expect(await runMiddleware("/adr")).toEqual({ redirectedTo: "/auth/login" });
	});

	it("redirects to login when the session check fails", async () => {
		sessionResponse = () => Promise.reject(new Error("network"));
		expect(await runMiddleware("/dashboard")).toEqual({ redirectedTo: "/auth/login" });
	});

	it("lets a signed-in user through", async () => {
		sessionResponse = async () => ({ session: { id: "s" }, user: { id: "u" } });
		expect(await runMiddleware("/adr")).toBeUndefined();
		expect(navigateTo).not.toHaveBeenCalled();
	});
});
