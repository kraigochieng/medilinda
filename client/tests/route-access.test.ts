import { describe, expect, it } from "vitest";
import { aboutLayout, decideAccess, isAuthPath, isPublicPath } from "../app/utils/route-access";

describe("isAuthPath", () => {
	it.each([
		["/auth/login", true],
		["/auth/signup", true],
		["/about", false],
		["/authors", false],
	])("%s is an auth path: %s", (path, expected) => {
		expect(isAuthPath({ path })).toBe(expected);
	});
});

describe("isPublicPath", () => {
	it.each([
		["/about", true],
		["/auth/login", true],
		["/", false],
		["/adr", false],
		["/about/team", false],
	])("%s is public: %s", (path, expected) => {
		expect(isPublicPath({ path })).toBe(expected);
	});
});

describe("decideAccess", () => {
	it("lets a signed-in user open any page", () => {
		expect(decideAccess({ path: "/adr", hasSession: true })).toEqual({ kind: "allow" });
		expect(decideAccess({ path: "/", hasSession: true })).toEqual({ kind: "allow" });
	});

	it("lets a signed-out visitor open About", () => {
		expect(decideAccess({ path: "/about", hasSession: false })).toEqual({ kind: "allow" });
	});

	it("sends a signed-out visitor of Home to About", () => {
		expect(decideAccess({ path: "/", hasSession: false })).toEqual({ kind: "redirect", to: "/about" });
	});

	it("sends a signed-out visitor of any other page to the login page", () => {
		expect(decideAccess({ path: "/adr", hasSession: false })).toEqual({ kind: "redirect", to: "/auth/login" });
		expect(decideAccess({ path: "/dashboard", hasSession: false })).toEqual({ kind: "redirect", to: "/auth/login" });
	});
});

describe("aboutLayout", () => {
	it("gives a signed-in user the default layout", () => {
		expect(aboutLayout({ hasSession: true })).toBe("default");
	});

	it("gives a visitor the layout without the sidebar", () => {
		expect(aboutLayout({ hasSession: false })).toBe("visitor");
	});
});
