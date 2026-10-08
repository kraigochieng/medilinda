// Draft of an ADR report being filled in, and the check for unsaved changes.
//
// A draft holds patient data, so it is kept in sessionStorage (this browser
// tab only, gone when the tab closes) and under the signed-in user's id.
import { emptyFormState, type AdrForm } from "~/utils/adr-form";

export const DRAFT_VERSION = 1;
export const DRAFT_MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000;
const KEY_PREFIX = "medilinda:adr-draft:";

export interface Draft {
	version: number;
	savedAt: string;
	knowsDob: boolean;
	state: Partial<AdrForm>;
}

export const draftKey = (userId: string) => `${KEY_PREFIX}${userId}`;

// ---- comparing form states -------------------------------------------------

// Blank values (undefined, null, "") count as not filled in, so a field that was
// cleared equals a field that was never set.
function normalize(value: unknown): unknown {
	if (Array.isArray(value)) return value.map(normalize);

	if (value && typeof value === "object") {
		const out: Record<string, unknown> = {};
		for (const key of Object.keys(value as object).sort()) {
			const item = normalize((value as Record<string, unknown>)[key]);
			if (item !== undefined) out[key] = item;
		}
		return out;
	}

	return value === null || value === "" ? undefined : value;
}

export const stableString = (state: unknown) => JSON.stringify(normalize(state)) ?? "";

export function isDirty(baseline: unknown, current: unknown): boolean {
	return stableString(baseline) !== stableString(current);
}

// Has the user entered anything beyond the blank form?
export function isMeaningful(state: Partial<AdrForm>): boolean {
	return isDirty(emptyFormState(), state);
}

// ---- serialising -----------------------------------------------------------

export function serializeDraft(
	state: Partial<AdrForm>,
	knowsDob: boolean,
	now: Date = new Date(),
): string {
	const draft: Draft = {
		version: DRAFT_VERSION,
		savedAt: now.toISOString(),
		knowsDob,
		state: JSON.parse(JSON.stringify(state)),
	};
	return JSON.stringify(draft);
}

// Returns the draft, or null when it is missing, damaged, from another version
// of the form, or too old.
export function parseDraft(raw: string | null | undefined, now: Date = new Date()): Draft | null {
	if (!raw) return null;

	try {
		const draft = JSON.parse(raw) as Partial<Draft>;

		if (draft.version !== DRAFT_VERSION) return null;
		if (typeof draft.savedAt !== "string") return null;
		if (typeof draft.knowsDob !== "boolean") return null;
		if (!draft.state || typeof draft.state !== "object" || !Array.isArray(draft.state.medicines)) {
			return null;
		}

		const age = now.getTime() - new Date(draft.savedAt).getTime();
		if (!Number.isFinite(age) || age > DRAFT_MAX_AGE_MS) return null;

		return draft as Draft;
	} catch {
		return null;
	}
}

// ---- storage ---------------------------------------------------------------

type StorageLike = Pick<Storage, "getItem" | "setItem" | "removeItem" | "key" | "length">;

// Storage can be missing or throw (private windows, full disk, blocked cookies).
// A draft is a convenience, so every failure is ignored.
export function createDraftStore(storage: StorageLike | undefined) {
	const safe = <T>(fn: () => T, fallback: T): T => {
		try {
			return storage ? fn() : fallback;
		} catch {
			return fallback;
		}
	};

	return {
		load: (userId: string, now?: Date) =>
			parseDraft(safe(() => storage!.getItem(draftKey(userId)), null), now),
		save: (userId: string, state: Partial<AdrForm>, knowsDob: boolean) =>
			safe(() => storage!.setItem(draftKey(userId), serializeDraft(state, knowsDob)), undefined),
		clear: (userId: string) => safe(() => storage!.removeItem(draftKey(userId)), undefined),
		// On sign-out nothing of the last user's work should stay behind.
		clearAll: () =>
			safe(() => {
				const keys: string[] = [];
				for (let i = 0; i < storage!.length; i++) {
					const key = storage!.key(i);
					if (key?.startsWith(KEY_PREFIX)) keys.push(key);
				}
				keys.forEach((key) => storage!.removeItem(key));
			}, undefined),
	};
}
