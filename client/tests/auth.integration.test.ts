import { createLocalJWKSet, jwtVerify } from "jose";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { BASE_URL, createCaller, createTestAuth } from "./helpers/test-auth";

let ctx: Awaited<ReturnType<typeof createTestAuth>>;
let call: ReturnType<typeof createCaller>;

const signUp = (username: string, password = "supersecret1") =>
	call("/sign-up/email", {
		body: {
			email: `${username.toLowerCase()}@users.medilinda.local`,
			name: `${username} Tester`,
			password,
			username,
			firstName: username,
			lastName: "Tester",
		},
	});

beforeAll(async () => {
	ctx = await createTestAuth();
	call = createCaller(ctx.auth);
});

afterAll(() => ctx.cleanup());

describe("signup and username sign-in", () => {
	it("signs up and signs in, ignoring username case", async () => {
		const signup = await signUp("Kraig");
		expect(signup.status).toBe(200);
		expect(signup.json.user.username).toBe("kraig");
		expect(signup.json.user.displayUsername).toBe("Kraig");

		for (const username of ["kraig", "KRAIG", "Kraig"]) {
			const login = await call("/sign-in/username", {
				body: { username, password: "supersecret1" },
			});
			expect(login.status).toBe(200);
			expect(login.cookie).toContain("better-auth.session_token");
		}
	});

	it("rejects a wrong password", async () => {
		await signUp("wrongpw");
		const login = await call("/sign-in/username", {
			body: { username: "wrongpw", password: "not-the-password" },
		});
		expect(login.status).toBe(401);
		expect(login.cookie).toBe("");
	});

	it("rejects an unknown user", async () => {
		const login = await call("/sign-in/username", {
			body: { username: "nobodyhere", password: "supersecret1" },
		});
		expect(login.status).toBe(401);
	});

	it("allows one-letter usernames for migrated users", async () => {
		expect((await signUp("Q")).status).toBe(200);
		const login = await call("/sign-in/username", {
			body: { username: "Q", password: "supersecret1" },
		});
		expect(login.status).toBe(200);
	});

	it("rejects a duplicate username", async () => {
		await signUp("dupe");
		const again = await call("/sign-up/email", {
			body: {
				email: "other@users.medilinda.local",
				name: "Dupe Two",
				password: "supersecret1",
				username: "dupe",
			},
		});
		expect(again.status).not.toBe(200);
	});

	it("returns no session without a cookie, and a session with one", async () => {
		await signUp("sessionuser");
		const login = await call("/sign-in/username", {
			body: { username: "sessionuser", password: "supersecret1" },
		});

		expect((await call("/get-session")).json).toBeNull();
		const session = await call("/get-session", { cookie: login.cookie });
		expect(session.json.user.username).toBe("sessionuser");
	});

	it("ends the session on sign-out", async () => {
		await signUp("leaver");
		const login = await call("/sign-in/username", {
			body: { username: "leaver", password: "supersecret1" },
		});
		await call("/sign-out", { body: {}, cookie: login.cookie });
		expect((await call("/get-session", { cookie: login.cookie })).json).toBeNull();
	});
});

describe("JWT for the FastAPI server", () => {
	it("issues a token that verifies against the JWKS with the claims FastAPI reads", async () => {
		const signup = await signUp("jwtuser");
		const login = await call("/sign-in/username", {
			body: { username: "jwtuser", password: "supersecret1" },
		});

		const { json: tokenBody } = await call("/token", { cookie: login.cookie });
		const { json: jwks } = await call("/jwks");

		const { payload } = await jwtVerify(tokenBody.token, createLocalJWKSet(jwks), {
			issuer: BASE_URL,
			audience: "medilinda-api",
		});

		expect(payload.sub).toBe(signup.json.user.id);
		expect(payload.username).toBe("jwtuser");
		expect(payload.first_name).toBe("jwtuser");
		expect(payload.last_name).toBe("Tester");
		expect(payload.disabled).toBe(false);
		expect(payload.exp! - payload.iat!).toBeLessThanOrEqual(15 * 60);
	});

	it("refuses to issue a token without a session", async () => {
		const response = await call("/token");
		expect(response.status).toBe(401);
	});

	it("rejects a token from another audience", async () => {
		await signUp("aud");
		const login = await call("/sign-in/username", {
			body: { username: "aud", password: "supersecret1" },
		});
		const { json: tokenBody } = await call("/token", { cookie: login.cookie });
		const { json: jwks } = await call("/jwks");

		await expect(
			jwtVerify(tokenBody.token, createLocalJWKSet(jwks), { audience: "someone-else" }),
		).rejects.toThrow();
	});
});

describe("API keys", () => {
	async function loginAs(username: string) {
		const signup = await signUp(username);
		const login = await call("/sign-in/username", {
			body: { username, password: "supersecret1" },
		});
		return { userId: signup.json.user.id as string, cookie: login.cookie };
	}

	it("creates a key that resolves to its owner", async () => {
		const { userId, cookie } = await loginAs("keyowner");
		const created = await call("/api-key/create", { body: { name: "nightly" }, cookie });
		expect(created.status).toBe(200);

		const result = await ctx.auth.api.verifyApiKey({ body: { key: created.json.key } });
		expect(result.valid).toBe(true);
		expect(result.key?.referenceId).toBe(userId);
	});

	it("rejects an unknown key", async () => {
		const result = await ctx.auth.api.verifyApiKey({ body: { key: "not-a-real-key" } });
		expect(result.valid).toBe(false);
	});

	it("stops working as soon as it is revoked", async () => {
		const { cookie } = await loginAs("revoker");
		const created = await call("/api-key/create", { body: { name: "temp" }, cookie });
		const key = created.json.key as string;

		expect((await ctx.auth.api.verifyApiKey({ body: { key } })).valid).toBe(true);

		const revoked = await call("/api-key/delete", { body: { keyId: created.json.id }, cookie });
		expect(revoked.status).toBe(200);
		expect((await ctx.auth.api.verifyApiKey({ body: { key } })).valid).toBe(false);
	});

	it("rejects an expired key", async () => {
		const { cookie } = await loginAs("expirer");
		const created = await call("/api-key/create", { body: { name: "short" }, cookie });
		await ctx.db.execute({
			sql: "update apikey set expiresAt = ? where id = ?",
			args: [new Date(Date.now() - 1000).toISOString(), created.json.id],
		});

		const result = await ctx.auth.api.verifyApiKey({ body: { key: created.json.key } });
		expect(result.valid).toBe(false);
	});

	it("does not let a signed-out caller create a key", async () => {
		const response = await call("/api-key/create", { body: { name: "sneaky" } });
		expect(response.status).toBe(401);
	});

	it("lists only the caller's keys", async () => {
		const a = await loginAs("lista");
		const b = await loginAs("listb");
		await call("/api-key/create", { body: { name: "a-key" }, cookie: a.cookie });

		const listB = await call("/api-key/list", { cookie: b.cookie });
		const keys = Array.isArray(listB.json) ? listB.json : listB.json?.apiKeys ?? [];
		expect(keys).toHaveLength(0);
	});
});
