import { describe, expect, it } from "vitest";
import {
	NONE,
	daysBetween,
	formatDay,
	medicinesOf,
	optionLabel,
	show,
	summaryOf,
	timelineOf,
} from "../app/utils/adr-view";

const adr = (extra: Record<string, unknown> = {}) =>
	({
		id: "a1",
		patient_name: "Jane Doe",
		patient_gender: "female",
		patient_age: 34,
		date_of_onset_of_reaction: "2025-03-10",
		rifampicin_suspected: true,
		rifampicin_start_date: "2025-03-01",
		rifampicin_stop_date: "2025-03-12",
		rifampicin_dose_amount: 600,
		rifampicin_frequency_number: 1,
		rifampicin_route: "oral",
		isoniazid_suspected: false,
		isoniazid_start_date: "2025-02-20",
		...extra,
	}) as never;

describe("show", () => {
	it("shows a dash for anything missing", () => {
		for (const value of [undefined, null, "", "   "]) expect(show(value)).toBe(NONE);
	});

	it("keeps zero and false, which are real values", () => {
		expect(show(0)).toBe("0");
		expect(show(false)).toBe("No");
		expect(show(true)).toBe("Yes");
	});
});

describe("optionLabel", () => {
	it("gives the label of a chosen option", () => {
		expect(optionLabel("severity", "moderate")).toBe("Moderate");
	});

	it("shows a dash when nothing is chosen, and the raw value for an unknown one", () => {
		expect(optionLabel("severity", undefined)).toBe(NONE);
		expect(optionLabel("severity", "odd")).toBe("odd");
	});
});

describe("formatDay", () => {
	it("formats a date without moving it across timezones", () => {
		expect(formatDay("2025-03-01")).toBe("1 Mar 2025");
		expect(formatDay("2025-12-31")).toBe("31 Dec 2025");
	});

	it("shows a dash for none and leaves text it cannot read alone", () => {
		expect(formatDay(undefined)).toBe(NONE);
		expect(formatDay("not a date")).toBe("not a date");
	});
});

describe("daysBetween", () => {
	it("counts days from one date to another", () => {
		expect(daysBetween("2025-03-01", "2025-03-12")).toBe(11);
		expect(daysBetween("2025-03-10", "2025-03-01")).toBe(-9);
	});

	it("is null when either date is missing or unreadable", () => {
		expect(daysBetween(undefined, "2025-03-01")).toBeNull();
		expect(daysBetween("2025-03-01", "x")).toBeNull();
	});

	it("is not thrown off by a month with a daylight saving change", () => {
		expect(daysBetween("2025-03-29", "2025-04-02")).toBe(4);
	});
});

describe("medicinesOf", () => {
	it("lists the four medicines with their values", () => {
		const list = medicinesOf(adr());

		expect(list.map((m) => m.name)).toEqual(["Rifampicin", "Isoniazid", "Pyrazinamide", "Ethambutol"]);
		expect(list[0]).toMatchObject({ suspected: true, dose: 600, frequency: 1, route: "oral" });
	});

	it("works out the days on treatment, and leaves it empty without both dates", () => {
		const list = medicinesOf(adr());

		expect(list[0].days).toBe(11);
		expect(list[1].days).toBeNull();
	});

	it("treats a missing suspected flag as not suspected", () => {
		expect(medicinesOf(adr())[2].suspected).toBe(false);
	});
});

describe("timelineOf", () => {
	it("orders start, onset and stop by date", () => {
		const events = timelineOf(adr());

		expect(events.map((e) => [e.kind, e.date])).toEqual([
			["start", "2025-03-01"],
			["onset", "2025-03-10"],
			["stop", "2025-03-12"],
		]);
	});

	it("uses only suspected medicines, so the others do not crowd it", () => {
		const events = timelineOf(adr());

		expect(events.some((e) => e.label.includes("Isoniazid"))).toBe(false);
	});

	it("falls back to every medicine with a date when none is marked suspected", () => {
		const events = timelineOf(adr({ rifampicin_suspected: false }));

		expect(events.some((e) => e.label.includes("Isoniazid"))).toBe(true);
	});

	it("puts a start before an onset on the same day", () => {
		const events = timelineOf(adr({ date_of_onset_of_reaction: "2025-03-01" }));

		expect(events.map((e) => e.kind).slice(0, 2)).toEqual(["start", "onset"]);
	});

	it("says how many days after the start the reaction began", () => {
		const onset = timelineOf(adr()).find((e) => e.kind === "onset");

		expect(onset?.note).toBe("9 days after the first suspected medicine started");
	});

	it("warns when the reaction began before the medicine", () => {
		const onset = timelineOf(adr({ date_of_onset_of_reaction: "2025-02-25" })).find((e) => e.kind === "onset");

		expect(onset?.note).toBe("4 days before the first suspected medicine started");
	});

	it("is empty when there are no dates", () => {
		expect(timelineOf({ id: "x" } as never)).toEqual([]);
	});
});

describe("summaryOf", () => {
	it("gives the key facts, with dashes for missing ones", () => {
		const items = summaryOf(adr({ severity: "severe", outcome: "recovering" }));
		const byLabel = Object.fromEntries(items.map((i) => [i.label, i.value]));

		expect(byLabel.Patient).toBe("Jane Doe");
		expect(byLabel["Age and gender"]).toBe("34 yrs, Female");
		expect(byLabel.Onset).toBe("10 Mar 2025");
		expect(byLabel.Severity).toBe("Severe");
		expect(byLabel.Serious).toBe(NONE);
		expect(byLabel.Outcome).toBe("Recovering");
	});

	it("copes with no age or gender", () => {
		const byLabel = Object.fromEntries(
			summaryOf({ id: "x", patient_name: "A" } as never).map((i) => [i.label, i.value]),
		);

		expect(byLabel["Age and gender"]).toBe(NONE);
	});
});
