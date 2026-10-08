// Copy users from the old FastAPI SQLite database into Better Auth tables.
// User ids and bcrypt hashes are kept. Safe to run more than once.
import { randomUUID } from "node:crypto";

const iso = (value) => {
	const date = value
		? new Date(String(value).includes("Z") ? value : `${value}Z`)
		: new Date();
	return Number.isNaN(date.getTime()) ? new Date().toISOString() : date.toISOString();
};

export async function migrateUsers({ source, target, dryRun = false }) {
	const { rows: users } = await source.execute(
		"select id, username, password, first_name, last_name, disabled, created_at, updated_at from user",
	);

	const seenUsernames = new Set(
		(await target.execute("select username from user")).rows.map((r) => r.username),
	);
	const existingIds = new Set(
		(await target.execute("select id from user")).rows.map((r) => r.id),
	);

	const summary = { migrated: 0, alreadyThere: 0, skipped: [] };

	for (const row of users) {
		if (existingIds.has(row.id)) {
			summary.alreadyThere++;
			continue;
		}

		// Better Auth lowercases usernames, so two old names can collide.
		const username = String(row.username).toLowerCase();
		if (seenUsernames.has(username)) {
			summary.skipped.push({ id: row.id, username: row.username, reason: "username collision" });
			continue;
		}
		seenUsernames.add(username);

		const createdAt = iso(row.created_at);
		const updatedAt = iso(row.updated_at);
		const name = [row.first_name, row.last_name].filter(Boolean).join(" ") || row.username;

		if (!dryRun) {
			await target.batch(
				[
					{
						sql: `insert into user (id, name, email, emailVerified, createdAt, updatedAt,
							username, displayUsername, firstName, lastName, disabled)
							values (?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?)`,
						args: [
							row.id, name, `${username}@users.medilinda.local`, createdAt, updatedAt,
							username, row.username, row.first_name, row.last_name, row.disabled ? 1 : 0,
						],
					},
					{
						sql: `insert into account (id, accountId, providerId, userId, password, createdAt, updatedAt)
							values (?, ?, 'credential', ?, ?, ?, ?)`,
						args: [randomUUID(), row.id, row.id, row.password, createdAt, updatedAt],
					},
				],
				"write",
			);
		}
		summary.migrated++;
	}

	return summary;
}
