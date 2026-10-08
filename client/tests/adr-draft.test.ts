import { describe, expect, it } from "vitest";
import {
	DRAFT_MAX_AGE_MS,
	DRAFT_VERSION,
	createDraftStore,
	draftKey,
	isDirty,
	isMeaningful,
	parseDraft,
	serializeDraft,
} from "../app/utils/adr-draft";
import { adrFormSchema, emptyFormState, sampleFormState } from "../app/utils/adr-form";

// A minimal in-memory sessionStorage.
function fakeStorage(initial: Record<string, string> = {}) {
	const data = new Map(Object.entries(initial));
	return {
		data,
		get length() {
			return data.size;
		},
		key: (i: number) => [...data.keys()][i] ?? null,
		getItem: (k: string) => data.get(k) ?? null,
		setItem: (k: string, v: string) => void data.set(k, v),
		removeItem: (k: string) => void data.delete(k),
	};
}

const NOW = new Date("2025-06-01T10:00:00Z");

describe("isDirty", () => {
	it("is false for equal states, however their keys are ordered", () => {
		expect(isDirty({ a: 1, b: 2 }, { b: 2, a: 1 })).toBe(false);
	});

	it("treats blank values as not filled in", () => {
		expect(isDirty({ a: "x" }, { a: "x", b: undefined, c: "", d: null })).toBe(false);
		expect(isDirty({ a: undefined }, { a: "" })).toBe(false);
	});

	it("notices a real change, including inside the medicines list", () => {
		expect(isDirty({ a: 1 }, { a: 2 })).toBe(true);
		const base = emptyFormState();
		const edited = emptyFormState();
		edited.medicines![1]!.suspected = true;
		expect(isDirty(base, edited)).toBe(true);
	});

	it("keeps false and 0 as real values", () => {
		expect(isDirty({ a: false }, { a: undefined })).toBe(true);
		expect(isDirty({ a: 0 }, { a: undefined })).toBe(true);
	});
});

describe("isMeaningful", () => {
	it("is false for the blank form", () => {
		expect(isMeaningful(emptyFormState())).toBe(false);
	});

	it("is false when a field was typed in and cleared again", () => {
		const form = emptyFormState();
		form.patient_name = "Jane";
		form.patient_name = "";
		expect(isMeaningful(form)).toBe(false);
	});

	it("is true once anything is entered", () => {
		const form = emptyFormState();
		form.patient_address = "Nairobi";
		expect(isMeaningful(form)).toBe(true);
		expect(isMeaningful(sampleFormState())).toBe(true);
	});
});

describe("serializeDraft and parseDraft", () => {
	it("round-trips a draft", () => {
		const state = { ...emptyFormState(), patient_name: "Jane Smith", patient_age: 45 };

		const draft = parseDraft(serializeDraft(state, false, NOW), NOW);

		expect(draft).toMatchObject({ version: DRAFT_VERSION, knowsDob: false });
		expect(draft!.state.patient_name).toBe("Jane Smith");
		expect(draft!.state.patient_age).toBe(45);
		expect(draft!.state.medicines).toHaveLength(4);
	});

	it("keeps no reference to the live form state", () => {
		const state = emptyFormState();
		const raw = serializeDraft(state, true, NOW);
		state.patient_name = "changed later";

		expect(parseDraft(raw, NOW)!.state.patient_name).toBe("");
	});

	it("ignores nothing, damaged data, or the wrong kind of data", () => {
		for (const bad of [null, undefined, "", "not json", "[]", "null", "{}", '{"version":1}']) {
			expect(parseDraft(bad as string, NOW)).toBeNull();
		}
	});

	it("ignores a draft from another version of the form", () => {
		const raw = JSON.parse(serializeDraft(emptyFormState(), true, NOW));
		raw.version = DRAFT_VERSION + 1;

		expect(parseDraft(JSON.stringify(raw), NOW)).toBeNull();
	});

	it("ignores a draft without a medicines list", () => {
		const raw = JSON.parse(serializeDraft(emptyFormState(), true, NOW));
		delete raw.state.medicines;

		expect(parseDraft(JSON.stringify(raw), NOW)).toBeNull();
	});

	it("expires old drafts", () => {
		const raw = serializeDraft(emptyFormState(), true, NOW);

		const justInside = new Date(NOW.getTime() + DRAFT_MAX_AGE_MS - 1000);
		const justOutside = new Date(NOW.getTime() + DRAFT_MAX_AGE_MS + 1000);
		expect(parseDraft(raw, justInside)).not.toBeNull();
		expect(parseDraft(raw, justOutside)).toBeNull();
	});
});

describe("draft store", () => {
	it("saves, loads and clears a draft per user", () => {
		const storage = fakeStorage();
		const store = createDraftStore(storage);
		const state = { ...emptyFormState(), patient_name: "Jane" };

		store.save("alice", state, true);

		expect(store.load("alice")!.state.patient_name).toBe("Jane");
		expect(store.load("bob")).toBeNull(); // another user sees nothing
		store.clear("alice");
		expect(store.load("alice")).toBeNull();
	});

	it("uses a key per user", () => {
		const storage = fakeStorage();
		createDraftStore(storage).save("alice", emptyFormState(), true);

		expect([...storage.data.keys()]).toEqual([draftKey("alice")]);
	});

	it("removes every draft on sign-out, and nothing else", () => {
		const storage = fakeStorage({ unrelated: "keep me" });
		const store = createDraftStore(storage);
		store.save("alice", emptyFormState(), true);
		store.save("bob", emptyFormState(), true);

		store.clearAll();

		expect([...storage.data.keys()]).toEqual(["unrelated"]);
	});

	it("never throws when storage is missing or broken", () => {
		const broken = {
			length: 1,
			key: () => {
				throw new Error("blocked");
			},
			getItem: () => {
				throw new Error("blocked");
			},
			setItem: () => {
				throw new Error("full");
			},
			removeItem: () => {
				throw new Error("blocked");
			},
		};

		for (const store of [createDraftStore(undefined), createDraftStore(broken)]) {
			expect(() => store.save("a", emptyFormState(), true)).not.toThrow();
			expect(store.load("a")).toBeNull();
			expect(() => store.clear("a")).not.toThrow();
			expect(() => store.clearAll()).not.toThrow();
		}
	});
});

describe("required fields on a blank form", () => {
	const blank = () => ({ ...emptyFormState(), patient_name: "Jane Smith" });

	it("asks for the fields the server has no default for", () => {
		const result = adrFormSchema.safeParse({
			...blank(),
			medical_institution_id: "8ade772c-0808-4681-a22c-34f99cb742e5",
		});

		expect(result.success).toBe(false);
		const messages = result.error!.issues.map((i) => i.message);
		expect(messages).toEqual(
			expect.arrayContaining([
				"Select the patient's gender.",
				"Select the pregnancy status.",
				"Select whether the patient has a known allergy.",
				"Select whether the reaction is serious.",
				"Select the criteria for seriousness.",
			]),
		);
	});

	it("accepts the form once they are answered", () => {
		const result = adrFormSchema.safeParse({
			...blank(),
			medical_institution_id: "8ade772c-0808-4681-a22c-34f99cb742e5",
			patient_gender: "female",
			pregnancy_status: "not pregnant",
			known_allergy: "no",
			is_serious: "no",
			criteria_for_seriousness: "hospitalisation",
		});

		expect(result.success, JSON.stringify(result.error?.issues)).toBe(true);
	});

	it("presets only what the server itself defaults to unknown", () => {
		const form = emptyFormState();

		expect(form).toMatchObject({
			rechallenge: "unknown",
			dechallenge: "unknown",
			severity: "unknown",
			action_taken: "unknown",
			outcome: "unknown",
		});
		expect(form.patient_gender).toBeUndefined();
		expect(form.is_serious).toBeUndefined();
	});
});
