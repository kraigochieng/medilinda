import { LibsqlDialect } from "@libsql/kysely-libsql";
import { createClient } from "@libsql/client";
import { getMigrations } from "better-auth/db/migration";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { createAuth } from "../../server/utils/auth-factory";

export const BASE_URL = "http://localhost:3000";

// Real Better Auth instance on a throwaway libsql file, so tests exercise the
// same plugins, hashing and tables as production.
export async function createTestAuth() {
	const dir = mkdtempSync(join(tmpdir(), "medilinda-auth-"));
	const url = `file:${join(dir, "auth.db")}`;

	const auth = createAuth({
		baseURL: BASE_URL,
		secret: "test-secret-test-secret-test-secret-123",
		database: { dialect: new LibsqlDialect({ url }), type: "sqlite" },
	});

	const { runMigrations } = await getMigrations(auth.options);
	await runMigrations();

	const db = createClient({ url });

	return {
		auth,
		db,
		url,
		cleanup: () => {
			db.close();
			// Better Auth plugins run background tasks (e.g. expired api key
			// cleanup), so delete the files only when the process exits.
			process.once("exit", () => rmSync(dir, { recursive: true, force: true }));
		},
	};
}

type CallOptions = { body?: unknown; cookie?: string; method?: string };

// Calls the auth handler the way the browser would (same-origin request).
export function createCaller(auth: { handler: (r: Request) => Promise<Response> }) {
	return async function call(path: string, { body, cookie, method }: CallOptions = {}) {
		const response = await auth.handler(
			new Request(`${BASE_URL}/api/auth${path}`, {
				method: method ?? (body === undefined ? "GET" : "POST"),
				headers: {
					origin: BASE_URL,
					"content-type": "application/json",
					...(cookie ? { cookie } : {}),
				},
				body: body === undefined ? undefined : JSON.stringify(body),
			}),
		);

		const setCookie = response.headers
			.getSetCookie()
			.map((c) => c.split(";")[0])
			.join("; ");
		const text = await response.text();

		return {
			status: response.status,
			json: text ? JSON.parse(text) : null,
			cookie: setCookie,
		};
	};
}
