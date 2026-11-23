import { describe, expect, it } from "vitest";
import { decideAccess, isPublicPath } from "../app/utils/route-access";

describe("isPublicPath", () => {
	it.each([
		["/about", true],
		["/auth/login", true],
		["/auth/signup", true],
		["/", false],
		["/adr", false],
		["/about/team", false],
		["/authors", false],
	])("%s is public: %s", (path, expected) => {
		expect(isPublicPath({ path })).toBe(expected);
	});
});

describe("decideAccess", () => {
	it("lets a signed-in user open any page", () => {
		expect(decideAccess({ path: "/adr", hasSession: true })).toEqual({ kind: "allow" });
		expect(decideAccess({ path: "/", hasSession: true })).toEqual({ kind: "allow" });
	});

	it("sends a signed-out visitor of Home to About", () => {
		expect(decideAccess({ path: "/", hasSession: false })).toEqual({ kind: "redirect", to: "/about" });
	});

	it("sends a signed-out visitor of any other page to the login page", () => {
		expect(decideAccess({ path: "/adr", hasSession: false })).toEqual({ kind: "redirect", to: "/auth/login" });
		expect(decideAccess({ path: "/dashboard", hasSession: false })).toEqual({ kind: "redirect", to: "/auth/login" });
	});
});
