// The causality assessment levels: how each is described and coloured. One place,
// so the scale, the tables and the tooltips can never disagree.

export interface CausalityLevel {
	value: string; // as the server sends it
	label: string;
	description: string;
	badgeClass: string; // background and text colour
}

// In the order of the scale on the ADR page: least to most certain.
export const CAUSALITY_LEVELS: CausalityLevel[] = [
	{
		value: "unclassifiable",
		label: "Unclassifiable",
		description:
			"Insufficient or contradictory information prevents any judgment about the link to the drug.",
		badgeClass: "bg-slate-300 text-black",
	},
	{
		value: "unclassified",
		label: "Unclassified",
		description:
			"The event is noted, but more data or analysis is needed before a conclusion. For a new report, mark the suspected medicines and answer the rechallenge or dechallenge question.",
		badgeClass: "bg-slate-500 text-white",
	},
	{
		value: "unlikely",
		label: "Unlikely",
		description:
			"Timing and context make a link to the drug improbable, and other causes are more plausible.",
		badgeClass: "bg-yellow-300 text-black",
	},
	{
		value: "possible",
		label: "Possible",
		description:
			"The timing is reasonable, but the event could also be due to other factors, and the withdrawal data may be unclear.",
		badgeClass: "bg-yellow-500 text-black",
	},
	{
		value: "likely",
		label: "Likely",
		description:
			"A reasonable link to the drug. Other causes are unlikely, and the patient improved when the drug was withdrawn. A rechallenge is not needed.",
		badgeClass: "bg-red-400 text-black",
	},
	{
		value: "certain",
		label: "Certain",
		description:
			"A clear link to taking the drug, with no other explanation and strong evidence, including a positive withdrawal and rechallenge where needed.",
		badgeClass: "bg-red-500 text-white",
	},
];

export function causalityLevel(value?: string | null): CausalityLevel | undefined {
	if (!value) return undefined;
	const wanted = value.toLowerCase();
	return CAUSALITY_LEVELS.find((level) => level.value === wanted);
}
