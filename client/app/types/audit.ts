export interface AuditChange {
	field: string;
	old?: unknown;
	new?: unknown;
}

// One recorded change, as the server's audit endpoints return it.
export interface AuditEvent {
	id: string;
	group_id: string;
	entity_type: string;
	entity_id: string;
	root_type?: string | null;
	root_id?: string | null;
	action: string; // create | update | delete | restore
	version: number;
	actor_id?: string | null;
	actor_username?: string | null;
	at: string;
	changes?: AuditChange[] | null;
	reason?: string | null;
	summary?: Record<string, any> | null;
	snapshot?: Record<string, any> | null;
}
