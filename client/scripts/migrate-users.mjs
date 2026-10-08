#!/usr/bin/env node
// Copy users from the old FastAPI SQLite database into Better Auth tables.
//
//   node scripts/migrate-users.mjs [--source <path>] [--dry-run]
//
// Target comes from TURSO_DATABASE_URL / TURSO_AUTH_TOKEN (default: file:auth.db).
import { createClient } from "@libsql/client";
import { resolve } from "node:path";
import { migrateUsers } from "./migrate-users-lib.mjs";

const args = process.argv.slice(2);
const dryRun = args.includes("--dry-run");
const sourceArg = args.includes("--source")
	? args[args.indexOf("--source") + 1]
	: "../server/src/server/db/db.sqlite";

const source = createClient({ url: `file:${resolve(sourceArg)}` });
const target = createClient({
	url: process.env.TURSO_DATABASE_URL || "file:auth.db",
	authToken: process.env.TURSO_AUTH_TOKEN,
});

const summary = await migrateUsers({ source, target, dryRun });

console.log(
	`${dryRun ? "[dry run] " : ""}migrated: ${summary.migrated}, already present: ${summary.alreadyThere}, skipped: ${summary.skipped.length}`,
);
for (const s of summary.skipped) console.log(`  skipped ${s.username} (${s.id}): ${s.reason}`);
