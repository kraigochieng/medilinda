import type { AuditEvent } from "@/types/audit";
import type { PaginatedResponseInterface } from "@/types/pagination";

// Everything that happened to an ADR and the rows that belong to it
// (assessments, reviews, SMS messages), newest first.
export async function fetchAdrActivity(
	id: string,
	params: { page?: number; size?: number } = {}
): Promise<PaginatedResponseInterface<AuditEvent>> {
	const { $serverFetch } = useNuxtApp();

	return await $serverFetch<PaginatedResponseInterface<AuditEvent>>(
		`/adrs/${id}/activity`,
		{ method: "GET", query: params }
	);
}

// ADRs that are deleted right now. Restore one with `restoreAdrById`.
export async function fetchDeletedAdrs(
	params: { page?: number; size?: number } = {}
): Promise<PaginatedResponseInterface<AuditEvent>> {
	const { $serverFetch } = useNuxtApp();

	return await $serverFetch<PaginatedResponseInterface<AuditEvent>>(
		"/audit-logs/deleted-adrs",
		{ method: "GET", query: params }
	);
}
