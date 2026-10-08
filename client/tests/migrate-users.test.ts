import { createClient } from "@libsql/client";
import bcrypt from "bcryptjs";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { migrateUsers } from "../scripts/migrate-users-lib.mjs";
import { createCaller, createTestAuth } from "./helpers/test-auth";

let ctx: Awaited<ReturnType<typeof createTestAuth>>;
let source: ReturnType<typeof createClient>;
let dir: string;

beforeEach(async () => {
	ctx = await createTestAuth();
	dir = mkdtempSync(join(tmpdir(), "medilinda-legacy-"));
	source = createClient({ url: `file:${join(dir, "legacy.sqlite")}` });
	await source.execute(
		`create table user (username varchar not null, password varchar not null,
			first_name varchar, last_name varchar, disabled boolean not null,
			id varchar not null primary key, created_at datetime, updated_at datetime)`,
	);
	const hash = bcrypt.hashSync("oldpassword1", 4);
	const rows: [string, string, string, string, number, string, string | null][] = [
		["Alice", hash, "Alice", "W", 0, "legacy-1", "2025-01-02 03:04:05.000000"],
		["alice", hash, "Alicia", "X", 0, "legacy-2", null],
		["bob", hash, "Bob", "Y", 1, "legacy-3", "2025-02-02 03:04:05"],
		["Q", hash, "Q", "Q", 0, "legacy-4", null],
	];
	for (const [u, p, f, l, d, id, created] of rows) {
		await source.execute({
			sql: "insert into user values (?, ?, ?, ?, ?, ?, ?, ?)",
			args: [u, p, f, l, d, id, created, created],
		});
	}
});

afterEach(() => {
	source.close();
	ctx.cleanup();
	process.once("exit", () => rmSync(dir, { recursive: true, force: true }));
});

describe("migrateUsers", () => {
	it("copies users keeping ids, and reports username collisions", async () => {
		const summary = await migrateUsers({ source, target: ctx.db });

		expect(summary.migrated).toBe(3);
		expect(summary.skipped).toEqual([
			{ id: "legacy-2", username: "alice", reason: "username collision" },
		]);

		const { rows } = await ctx.db.execute("select id, username, displayUsername, disabled from user order by id");
		expect(rows.map((r) => r.id)).toEqual(["legacy-1", "legacy-3", "legacy-4"]);
		expect(rows[0]).toMatchObject({ username: "alice", displayUsername: "Alice", disabled: 0 });
		expect(rows[1]).toMatchObject({ username: "bob", disabled: 1 });
	});

	it("does not write anything on a dry run", async () => {
		const summary = await migrateUsers({ source, target: ctx.db, dryRun: true });
		expect(summary.migrated).toBe(3);
		const { rows } = await ctx.db.execute("select count(*) as n from user");
		expect(rows[0].n).toBe(0);
	});

	it("is safe to run twice", async () => {
		await migrateUsers({ source, target: ctx.db });
		const second = await migrateUsers({ source, target: ctx.db });

		expect(second.migrated).toBe(0);
		expect(second.alreadyThere).toBe(3);
		const { rows } = await ctx.db.execute("select count(*) as n from account");
		expect(rows[0].n).toBe(3);
	});

	it("keeps the old bcrypt hash so existing passwords still work", async () => {
		await migrateUsers({ source, target: ctx.db });
		const call = createCaller(ctx.auth);

		const login = await call("/sign-in/username", {
			body: { username: "Alice", password: "oldpassword1" },
		});
		expect(login.status).toBe(200);
		expect(login.json.user.id).toBe("legacy-1");

		const wrong = await call("/sign-in/username", {
			body: { username: "alice", password: "wrong-password" },
		});
		expect(wrong.status).toBe(401);
	});

	it("lets a migrated one-letter user sign in", async () => {
		await migrateUsers({ source, target: ctx.db });
		const login = await createCaller(ctx.auth)("/sign-in/username", {
			body: { username: "Q", password: "oldpassword1" },
		});
		expect(login.status).toBe(200);
	});
});
